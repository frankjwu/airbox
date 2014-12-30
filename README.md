# Airbox
### Airbnb for Dropbox

Do you have too much Dropbox space? Or do you need more?

Enter Airbox.

We allow you to lend out your unused Dropbox space to other users. Of course, putting your files on other users' Dropbox accounts seems like a huge privacy problem, so we fix the process by encrypting your file, breaking it up into multiple pieces, and sending them out to different lenders on our network -- meaning that no one can read your files because 1) they're encrypted and 2) they only have a small piece of your file.

When it comes time for you to retrieve your files again, you can come back to us and download the file. We'll find all the individual pieces, piece them together bit by bit, and then decrypt it, giving you your original file.

So why would you ever use this when you could just keep making new, free Dropbox accounts? Well, with Airbox, you only need one account and one interface -- no need to login and logout.

![Airbox](http://i.imgur.com/vkGXblD.png)

![Dashboard](http://i.imgur.com/3HqUrpW.png)

*Note: this is a proof of concept created in a 24 hour hackathon. This is a demonstration of a secure, distributed, secondary marketplace for Dropbox space, but no space is actually being sold. You can only test Airbox locally.*

## Install

In config.py, change `app.secret_key` - instructions on how to generate one are available [here](http://flask.pocoo.org/docs/0.10/quickstart/#sessions).

You also need to change `AIRBOX_DROPBOX_APP_KEY` and `AIRBOX_DROPBOX_APP_SECRET`. This needs to be a [Dropbox API app](https://www.dropbox.com/developers/apps) with a redirect_uri of `http://localhost:5000/authenticate-finish`

## Run

    source airbox/bin/activate
    python db.py
    python run.py

## Usage

First, on each account you want to test Airbox with, you'll need to go to the "Rent out your space" section and specify how much Dropbox space you want to make available for Airbox files.

Then, you can upload files in the "Find space" section and watch as the file is split into encrypted, 1 MB pieces ('SPLIT_FILESIZE' in views.py) and uploaded to Dropbox.

To retrieve your files, click the appropriate file name in the "Your Downloads" section. The pieces will be decrypted and pieced back together.

## Improvements to be made

- Add redundancy for files
- Don't upload your own files to your own Dropbox if we can avoid it
- Improve algorithm for finding space: currently it just finds the person with the most space available for rent (attempting to put consecutive blocks on different accounts if available)
- Improve stability: sometimes, decryption fails
- Add more documentation
