# Sortify

Stupid simple script I wrote in an hour to sort my Spotify playlists the way I want it. Also that's a cool name

## Usage
Install the requirements.

```pip install -r requirements.txt```

Set up an app on your Spotify dev account. Save the Client ID and secret from there, and add a redirect URI in your whitelist.

Oh, you thought just signing into Spotify would do that for you? Too bad, I can't be bothered atm it's raining outside and I'm watching reruns of Law and Order's season 2. They really should've stopped after season 6, I think they're on 17 now and aiming to outdo the Simpsons. They had Logan Paul in an episode with gamers lolwtf.

Anyways, set up a `secret.py` and put the environment variables in:
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

CLIENT_ID = "BLABLABALBALBALBALBALblablablaBL"
CLIENT_SECRET = "HUNTER2HUNTER2HUNTER2HUNTER2HUNT"
REDIRECT_URI = "http://localhost:8000/billie_eilish_may_be_an_industry_plant_for_teen_girls_but_shes_way_better_than_cardi_b"
```

Run `sortify.py`. Of course it's in Python 3, get with the times boomer. Although I don't see why it shouldn't work with Python 2. Again, don't know why you would.

You'll get prompted for the redirect URI which you can copypasta from your browser you got redirected to. Bada bing bada boom you're done, you can now sort your Spotify playlist by time signatures, BPM and the length of the track names for all I care. :)
