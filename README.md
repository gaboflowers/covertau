# covertau

A lightweight radio manager, streaming client wrapper. Written in Python 3.x. Tested on a \*nix system.

## Dependencies:
- mpv (strongly encouraged)
- mplayer (optional)
It actually works with *any* player that can be run from the command line in this way:
```my_favourite_player [stream_source] [params]```

## Use:
```python covertau.py```

## Tips:
- Generate the default configuration file. Start from there.
- Many things only can be done editing the configuration file (like named items in playlists)
- Learn Spanish. The UI is in Spanish. I speak Spanish. Can't be bothered.

## Warning:
- The default player is `mpv`. If you generate the default configuration file, and then change the player to `mplayer`, it will complain due to the `--no-video` global parameter (that's an mpv thing). You might want to remove it.

## Why *Covertau*?
It is a radio thing. You'll see:
```
\[
\pi = \frac{C}{d}
d = \frac{C}{\pi}     % using tau = 2pi
d = \frac{2C}{\tau}   % using d = 2r
2r = \frac{2C}{\tau}  % simplifying
r = \frac{C}{\tau}
\]```

