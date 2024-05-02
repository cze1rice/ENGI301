## SpotiBox: Desktop Spotify box with real-time visualizer

## **License**
Copyright 2024, Cameron Erber.

See LICENSE (GNU General Public License, version 3).

## Hardware Setup
See this [Hackster page](https://www.hackster.io/cze1/spotibox-realtime-spotify-music-visualizer-583779) for hardware setup and project description / inspiration

## Software Setup
### Libraries
With a working PocketBeagle, first install the packages below using the Cloud9 IDE terminal:
- `sudo apt-get update`
- `sudo apt-get install python-pip -y`
- `sudo apt-get install python3-pip -y`
- `sudo apt-get install python3-pillow -y`
- `sudo apt-get install zip -y`
- `sudo apt-get install libopenjp2-7 -y`
- `sudo pip3 install --upgrade Pillow`
- `sudo pip3 install --upgrade spotipy`
- `sudo pip3 install --upgrade Adafruit-Blinka`
- `sudo pip3 install --upgrade adafruit-circuitpython-bh1750`

### Code Installation
Once done, download the 'ticker' folder within 'spotibox' and place in a folder named 'projects' on PocketBeagle sd card. The final destination should be `/var/lib/cloud9/projects/ticker/` on the PocketBeagle sd card as seen in Cloud9.

### PRU Mode
The PRU mode on the PocketBeagle must also be changed. This can be done through the Cloud9 terminal with the following commands:
1. `cd /boot`
2. `sudo nano uEnv.txt`
3. Comment out PRU RPOC line `uboot_overlay_pru=AM335X-PRU-RPROC-4-19-TI-00A0.dtbo` or `uboot_overlay_pru=AM335X-PRU-RPROC-4-14-TI-00A0.dtbo` (they should be both commented out)
4. Uncomment PRU UIOC line `uboot_overlay_pru=AM335X-PRU-UIO-00A0.dtbo`
5. Press "ctrl+X" and then "Y"
6. Press "Enter"
7. Restart PocketBeagle to boot into new PRU mode

### Wifi Adapter Initialization
To initialize the USB wifi adapter, execute the following commands in the Cloud9 terminal:
1. `lsub`
2. `sudo connmanctl`
3. `enable wifi`
4. `scan wifi`
5. `services`
6. Copy network ID of desired wifi network
7. `agent on`
8. `connect [network ID]` (input previously copied network ID in [])
9. `services`
10. If there is a `*AR` or `*AO` next to the desired network, connection is successful
11. `quit`

### Running on boot
The program can be run manually by changing the directory to `/var/lib/cloud9/projects/ticker/` and typing the command
`sudo python3 ticker.py`

To test or run soley the SpotiBox widget, `sudo python3 ticker_test.py` can be executed in the terminal.

To run the program automatically after the BeagleBoard boots, execute the follow commands in the Cloud9 terminal:
1. `cd /var/lib/cloud9`
2. `mkdir logs`
3. `sudo chmod 777 /var/lib/cloud9/logs`
4. `sudo crontab -e`
5. Add `@reboot sleep 60 && sh /var/lib/cloud9/projects/ticker/run.sh > /var/lib/cloud9/logs/cronlog 2>&1` line to file
6. Press "ctrl+X" and then "Y"
7. Press "Enter"

### SpotiBox Widget
#### Initialization
1. Create a Spotify Developer account at [developer.spotify.com/](https://developer.spotify.com/)
2. Create a new app with a redirect URI of `https://localhost:8888/callback`
3. Go to the app's settings and copy the `Client ID`, `Client Secret`, and `Redirect URI`
2. On a non-PocketBeagle computer install spotipy using `pip install spotipy --upgrade` in a terminal
3. Download the [**spotify_setup.py**](https://github.com/cze1rice/ENGI301/blob/main/project_01/spotibox/setup/spotify_setup.py) script
4. Open `spotify_setup.py` and add saved parameters from Spotify
5. Run `spotify_setup.py` and accept authorization prompt
6. Copy and save the full URL that you are redirected to
7. Modify `ticker.py` by inputting `Client ID`, `Client Secret`, and `Redirect URI` on lines 203 to 205
8. Run `ticker.py` from Cloud9 on the PocketBeagle
9. Enter the full URL saved on step 6 in terminal when prompted.

### Features
The SpotiBox widget uses Spotify API to get realtime playback data from a user. This data is used to display the currently playing track info such as the album cover, track title, arist name, and pitches. The real-time visualizer works by getting an audio analysis of the full song from Spotify API. It then determines which segment the song currently is in based on the track progress and displays the pitches vector for that segment. For the music theory inclined, the pitches chroma vector corresponds to the 12 possible notes and the magnitude of each note is determined using the real-time Fast Fourier Transform (FFT) of the track. Further details can be read [here](https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis)

## Acknowledgements & References
- Erik Welsh and Robert Heeter
- [PIL documentation](https://pillow.readthedocs.io/en/stable/reference/index.html)
- [Spotipy documentation](https://spotipy.readthedocs.io/en/2.22.1/)
- [Spotify API documentation](https://developer.spotify.com/documentation/web-api)
- For more details regarding other available Ticker widgets see [here](https://github.com/robertheeter/ticker)