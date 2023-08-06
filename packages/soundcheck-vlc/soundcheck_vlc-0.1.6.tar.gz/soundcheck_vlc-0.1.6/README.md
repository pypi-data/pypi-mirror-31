# Soundcheck to VLC

This background process listen to Mastodon for a predefined 
hashtag (e.g. #SoundCheck) and will append any video link to your vlc playlist.

When a new message is posted, it will parse its content in search for links to 
supported video plateforms. When such a link is found, it will be then added to 
to a vlc playlist. If vlc is not already open, it will try to launch a new instance.



## Technical background
### Mastodon
The script connects to a mastodon instance using [mastodon.py](https://mastodonpy.readthedocs.io/en/latest/)
module.
New statuses are fetched using the [Streaming API](https://mastodonpy.readthedocs.io/en/latest/#streaming)

### VLC
This script interacts with VLC through an http connection.
See https://wiki.videolan.org/VLC_HTTP_requests/

## Requirements
- Vlc must be installed
- Vlc http must be set-up and configured
- The script has been written for python 3.6, required modules are listed in 
[requirements.txt](requirements.txt)


## Usage
Launch Soundcheck to VLC, sit back, relax and let the party begin!


## Installation
- Create a python3.6 virtual env
- Download this repository
- Install requirements

```
pip install -r requirements.txt
```
- add your settings:

```
cp soundcheck_vlc/config/settings_template.py soundcheck_vlc/config/settings_local.py
```

Edit `settings_local.py` and enter your details

### VLC configuration
Enable VLC HTTP and eventually change the listening port (default: 8080).
For VLC HTTP to work you will need add a password. This password will be stored
in plain text in your `settings_local.py` but it is already in your vlcrc file anyway!

## About Mastodon

[Mastodon](https://joinmastodon.org/) is a decentralized social
network, built on free software. Users can send short messages, called
"toots".


## About VLC
[VLC media player](https://videolan.org/vlc/), commonly known as VLC is a 
free and open-source, portable and cross-platform media player 
and streaming media server developed by the VideoLAN project.


## Misc
This project structure is based on 
[kennethreitz's repository structure](http://www.kennethreitz.org/essays/repository-structure-and-python)

