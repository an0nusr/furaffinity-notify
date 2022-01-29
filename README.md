# FurAffinity Notify - FurAffinity Notification Tool

Receive FurAffinity notifications via email, Discord, Telegram, and more!

## About

This tool reaches out to FurAffinity, gets your current notifications,
and then sends you a message on your preferred platform when there are
new things to check out! 

We send the message using the [Apprise](https://github.com/caronc/apprise)
library, which supports a wide range of platforms and services.

## Requirements

This tool is designed to poll for notifications, so ideally it should be
setup on a system that is always on, such as a Raspberry Pi. You'll also 
need:

  - Your FurAffinity login cookies in a `cookies.txt` file (you can use browser
    extensions like
    [Ganbo for Firefox](https://addons.mozilla.org/en-US/firefox/addon/ganbo/)
    or
    [GetCookies.txt for Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en)
    to get this file for you.)
  - The Apprise URL for notifications - you can check out [their wiki for the list of 
    services and how to write the URLs](https://github.com/caronc/apprise/wiki). 
  - Python 3.6 or higher

## Configuration

Rename the included `config_example.toml` to `config.toml`, and
change:

  - `cookieFile` - this should be the path to your `cookies.txt` file
  - `notificationUrl` - set this to the Apprise URL

You may also want to adjust other options, such as `notifyOn`, to specify
what sort of FurAffinity notifications trigger an alert - by default you'll
get notifications for everything (including new submissions), which might
not be what you want.

## Running

Once you've set the configuration to your liking, install python dependencies
with `pip install -r requirements.txt`, and then run the program with `python faNotify.py`

The program will then periodically check for notifications, and alert you
when it sees new ones.

## Troubleshooting

If you have trouble getting notifications, you can set the `logLevel` in
the config file to `DEBUG`. This will output a lot more information on the
console, including what notifications the tool currently sees, what it 
saw on the last check, and the output from the notification attempt. 

