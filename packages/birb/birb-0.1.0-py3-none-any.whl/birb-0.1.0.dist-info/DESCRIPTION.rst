
# birb

![birb](images/birb.png)

birb is a minimalist app that lets you tweet from your CLI. No timeline, no search, no mentions: only posting.

## But why?

Twitter is noisy, and even a quick post can end up being distracting with your timeline and mentions popping up.
birb is limited on purpose so you don't fall into that timesink: post now from your CLI, and deal with the rest later on.

## Usage

[![asciicast](https://asciinema.org/a/177047.png)](https://asciinema.org/a/177047)

```sh
Usage: birb.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  oops   delete your most recent tweet
  tweet  send a tweet
```

Using the app without any command or parameter automatically triggers the `tweet` command.
You can delete your most recent tweet with `birb oops` if needed.
Be aware that this will delete your tweet regardless of where or when it has been posted.

If you want to repost right away, `birb oops --resend` will trigger the `tweet` command after deletion.

## Compatibility

birb has only been tested with Linux, and works with any version of Python3.

## Installation

Create an app on [apps.twitter.com](https://apps.twitter.com) with a name of your liking, and run `pip`:

```sh
pip install --user birb
```

When launching `birb` for the first time, you will be prompted to copy/paste the consumer keys and access tokens of the app you just created.
Those credentials will be locally stored and obfuscated in `birb_keys.py` and nowhere else.
Be aware however that this is only obfuscation: do not store that file online or share its content.

You're all set and ready to use birb!

## Todo

* tweet threads
* tweet with media files

