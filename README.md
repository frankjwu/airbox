# Airbox - Airbnb for Dropbox

Do you have too much Dropbox space? Or do you need more?

Enter Airbox.

We allow you to lend out your unused Dropbox space to other users. Of course, putting your files on other users' Dropbox accounts seems like a huge privacy problem, so we fix the process by encrypting your file, breaking it up into multiple pieces, and sending them out to different lenders on our network -- meaning that no one can read your files because 1) they're encrypted and 2) they only have a small piece of your file.

When it comes time for you to retrieve your files again, you can come back to us and download the file. We'll find all the individual pieces, piece them together bit by bit, and then decrypt it, giving you your original file.

So why would you ever use this when you could just keep making new, free Dropbox accounts? Well, with Airbox, you only need one account and one interface -- no need to login and logout.

![Airbox](http://i.imgur.com/vkGXblD.png)

![Dashboard](http://i.imgur.com/3HqUrpW.png)

## Install

In config.py, change `app.secret_key` - instructions on how to generate one are available [here](http://flask.pocoo.org/docs/0.10/quickstart/#sessions).

You also need to change `AIRBOX_DROPBOX_APP_KEY` and `AIRBOX_DROPBOX_APP_SECRET`. This needs to be a [Dropbox API app](https://www.dropbox.com/developers/apps) with a redirect_uri of `http://localhost:5000/authenticate-finish`

## Run

    source airbox/bin/activate
    python db.py
    python run.py