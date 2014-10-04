#!/usr/bin/env python
"""Desktop Tasks app using Tkinter.

This uses a background thread to be notified of incoming changes.

It demonstrates, among others:

- How to call await() in a loop in a background thread efficiently:
  Use make_cursor_map() to feed the 'deltamap' return value back
  into the 'datastores' parameter for the next await() call.

- How to communicate in a safe way between the background thread and
  the Tk main loop: Use a Queue plus a virtual event.

- How to avoid duplicate screen updates: Keep track of the revision
  that was displayed.

- How to save and restore a datastore to/from a disk file.

- How to detect whether the network goes offline or comes back online
  (in approximation).
"""

import json
import os
import sys
import time
import random
from threading import Thread
from Queue import Queue, Empty

from Tkinter import Tk, Frame, Button, Checkbutton, Entry, Label, BooleanVar
from Tkconstants import W, E, BOTH, END

# We use HTTPError as an approximation for "no network", even though
# this isn't always true -- sometimes it means "bad request" and
# sometimes we may get other exceptions.
from urllib3.exceptions import HTTPError

from dropbox.client import (
    DropboxClient,
    ErrorResponse,
    )
from dropbox.datastore import (
    DatastoreManager, Date,
    DatastoreError, DatastoreNotFoundError,
    )

# Virtual event to wake up the Tk main loop.
REFRESH_EVENT = '<<refresh-datastore>>'

# Filename where to store the data.
SERIALIZED_DATASTORE = 'my_tasks.json'


class TaskList(Frame):

    def __init__(self, master, client):
        Frame.__init__(self, master)
        # Connect to Dropbox and open datastore.
        self.manager = DatastoreManager(client)
        # Try to load serialized datastore first.
        datastore = self.load_serialized_datastore(SERIALIZED_DATASTORE)
        if datastore is not None:
            try:
                datastore.load_deltas()
            except DatastoreNotFoundError:
                print 'This datastore has been deleted. Exiting now.'
                sys.exit(1)
            except HTTPError:
                print 'We are offline. Proceed with caution.'
        else:
            datastore = self.manager.open_default_datastore()
        self.datastore = datastore
        self.table = self.datastore.get_table('tasks')
        # Set up communication with background thread.
        self.queue = Queue()  # Holds deltas sent from background thread.
        self.display_rev = 0  # Last revision displayed.
        self.refresh()  # Initial display update.
        self.bind(REFRESH_EVENT, self.refresh)  # Respond to background thread.
        # Create, configure and start background thread.
        self.bg_thread = Thread(name='bgthread', target=self.bg_run)
        self.bg_thread.setDaemon(True)
        self.bg_thread.start()

    def load_serialized_datastore(self, filename):
        try:
            f = open(filename, 'rb')
        except IOError as exc:
            # Don't print an error if the file doesn't exist.
            if os.path.exists(filename):
                print 'Cannot load saved datastore:', exc
            return None
        with f:
            try:
                data = json.load(f)
                id, handle, rev, snapshot = data
            except ValueError as exc:
                print 'Bad JSON on %s: %s' % (filename, exc)
                return None
            datastore = self.manager.open_raw_datastore(id, handle)
            # If this fails, the save file is bad -- you must manually delete it.
            datastore.apply_snapshot(rev, snapshot)
        print 'Loaded datastore from', filename
        return datastore

    def save_serialized_datastore(self, datastore, filename):
        id = datastore.get_id()
        handle = datastore.get_handle()
        rev = datastore.get_rev()
        snapshot = datastore.get_snapshot()
        data = [id, handle, rev, snapshot]
        try:
            f = open(filename, 'wb')
        except IOError as exc:
            print 'Cannot save datastore:', exc
            return
        with f:
            json.dump(data, f)
        print 'Saved datastore to', filename

    def bg_run(self):
        # This code runs in a background thread.  No other code does.
        deltamap = None
        backoff = 0
        while True:
            cursor_map = DatastoreManager.make_cursor_map([self.datastore], deltamap)
            try:
                _, _, deltamap = self.manager.await(datastores=cursor_map)
            except Exception as exc:
                if isinstance(exc, HTTPError):
                    if not backoff:
                        print 'We have gone offline.'
                    else:
                        print 'We are still offline.'
                else:
                    print 'bg_run():', repr(exc), str(exc)
                # Randomized exponential backoff, clipped to 5 minutes.
                backoff = min(backoff*2, 300) + random.random()
                time.sleep(backoff)
                continue
            else:
                if backoff:
                    print 'We have come back online.'
                    backoff = 0
            if deltamap and self.datastore in deltamap:
                deltas = deltamap[self.datastore]
                if deltas is None:
                    # Stop the bg thread.
                    print 'This datastore has been deleted.'
                    print 'Please exit.'
                    break
                if deltas:
                    self.queue.put(deltas)
                    self.event_generate(REFRESH_EVENT, when='tail')

    def save(self, event=None):
        self.save_serialized_datastore(self.datastore, SERIALIZED_DATASTORE)

    def refresh(self, event=None):
        # This is called directly when we have made a change,
        # and when the background thread sends a REFRESH_EVENT.
        self.load_queue()  # Update the datastore.
        if self.datastore.get_rev() == self.display_rev:
            return  # Nothing to do.
        self.forget()  # Hide the frame to reduce flashing.
        for w in self.winfo_children():
            w.destroy()  # Delete the old widgets.
        self.redraw()  # Create new widgets.
        self.pack(fill=BOTH, expand=1)  # Show the frame.
        self.display_rev = self.datastore.get_rev()
        title = self.datastore.get_title()
        mtime = self.datastore.get_mtime()
        if not title:
            title = 'My Tasks'
        if mtime:
            fmtime = mtime.to_datetime_local().strftime('%H:%M, %d %b %Y')
            title = '%s (%s)' % (title, fmtime)
        self.master.title(title)
        self.input.focus_set()

    def load_queue(self):
        # Incorporate queued deltas into the datastore.
        while True:
            try:
                deltas = self.queue.get_nowait()
            except Empty:
                break
            else:
                self.datastore.apply_deltas(deltas)

    def redraw(self):
        # Even though there are never more than three widgets per row,
        # we have four columns, to allow the taskname label and the
        # input widget to stretch.
        self.grid_columnconfigure(2, weight=1)
        row = 0
        # Add a new row of widgets for each task.
        for rec in sorted(self.table.query(), key=lambda rec: rec.get('created')):
            # Extract the fields we need.
            completed = rec.get('completed')
            taskname = rec.get('taskname')
            # Create a button with an 'X' in it, to delete the task.
            close_btn = Button(self, text='X',
                               command=lambda rec=rec: self.delete_rec(rec))
            close_btn.grid(row=row, column=0)
            # Create a checkbox, to mark it completed (or not).
            var = BooleanVar(self, value=completed)
            completed_btn = Checkbutton(self, variable=var,
                                        command=lambda rec=rec, var=var:
                                                self.toggle_rec(rec, var))
            completed_btn.grid(row=row, column=1)
            # Create a label showing the task name.
            taskname_lbl = Label(self, text=taskname, anchor=W)
            taskname_lbl.grid(row=row, column=2, columnspan=2, sticky=W)
            row += 1  # Bump row index.
        # Add a final row with the input and button to add new tasks.
        self.input = Entry(self)
        self.input.bind('<Return>', self.add_rec)
        self.input.grid(row=row, column=0, columnspan=3, sticky=W+E)
        add_btn = Button(self, text='Add Task', command=self.add_rec)
        add_btn.grid(row=row, column=3)
        # Add save button.  (Auto-save is left as an exercise.)
        save_btn = Button(self, text='Save local snapshot', command=self.save)
        save_btn.grid(row=row+1, column=0, columnspan=3, sticky=W)

    def add_rec(self, event=None):
        # Callback to add a new task.
        self.do_transaction(self.table.insert,
                            completed=False, taskname=self.input.get(), created=Date())

    def delete_rec(self, rec):
        # Callback to delete a task.
        self.do_transaction(rec.delete_record)

    def toggle_rec(self, rec, var):
        # Callback to toggle a task's completed flag.
        try:
            self.do_transaction(rec.set, 'completed', var.get())
        finally:
            # In case the transaction failed, flip the variable back.
            var.set(rec.get('completed'))

    def do_transaction(self, func, *args, **kwds):
        self.update_idletasks()  # Refresh screen without handling more input.
        def call_func():
            func(*args, **kwds)
        try:
            self.datastore.transaction(call_func, max_tries=4)
        except Exception as exc:
            # Maybe the server is down, or we experience extreme conflicts.
            # NOTE: A more user-friendly way would be to show an error dialog.
            print 'do_transaction():', repr(exc)
        else:
            self.refresh()


def main():
    if not sys.argv[1:]:
        print >>sys.stderr, 'Usage: tktasks.py ACCESS_TOKEN'
        print >>sys.stderr, 'You can use shtasks.py to get an access token.'
        sys.exit(2)

    access_token = sys.argv[1]
    client = DropboxClient(access_token)

    root = Tk()
    root.title('My Tasks')
    root.geometry('250x300+10+10')
    task_list = TaskList(root, client)
    root.mainloop()


if __name__ == '__main__':
    main()
