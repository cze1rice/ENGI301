"""
ABOUT:
    
    SpotifyWidget class to display the currently playing track, pause/play, and skip to the next or previous track.
    Not intended to be run directly.
    See documentation at https://github.com/rcheeter/ticker for setting up this widget.
        
LICENSE:
    
    Copyright 2023, Robert Heeter.
    See LICENSE (GNU General Public License, version 3).
    
"""

from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

import requests
import time

from widget import Widget, add_image

class SpotifyWidget(Widget):
    check_time = None
    
    def __init__(self, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, refresh_rate=20, interval=1, verbose=False):
        self.SPOTIFY_CLIENT_ID = SPOTIFY_CLIENT_ID # Spotify API client ID
        self.SPOTIFY_CLIENT_SECRET = SPOTIFY_CLIENT_SECRET # Spotify API client secret
        self.SPOTIPY_REDIRECT_URI = SPOTIPY_REDIRECT_URI # Spotify API redirect URI
        self.refresh_rate = refresh_rate # refresh rate of display
        self.interval = interval # interval pixel shift for text scrolling
        self.verbose = verbose # toggles printing information to terminal

    def setup(self):
        print("SpotifyWidget.setup()")
        
        self.width = Widget.width
        self.height = Widget.height
        self.image = Image.new('RGBX', (self.width, self.height), 'black') # black/blank screen

        self.currently_playing = 'currently_playing'
        self.prev_currently_playing = 'prev_currently_playing'
        self.index = 0
        
        scope='user-read-currently-playing user-read-playback-state user-modify-playback-state' # scope of Spotify permissions for Ticker application
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=self.SPOTIFY_CLIENT_ID, client_secret=self.SPOTIFY_CLIENT_SECRET, redirect_uri=self.SPOTIPY_REDIRECT_URI))
        
        self.is_playing = True

        self.check_time = time.time()
    
    def update(self, action_state):
        if self.verbose == True:
            print(f"SpotifyWidget.update(action_state={int(action_state)})")
        
        time.sleep(1/self.refresh_rate)

        # check action_state
        try:
            try:
                if action_state == 1: # pause/play track
                    if self.is_playing == False:
                        self.sp.start_playback()
                        self.is_playing = True
                    elif self.is_playing == True:
                        self.sp.pause_playback()
                        self.is_playing = False
            except:
                if action_state == 1: # if track is already paused/playing, play/pause track
                    if self.is_playing == False:
                        self.sp.pause_playback()
                        self.is_playing = False
                    elif self.is_playing == True:
                        self.sp.start_playback()
                        self.is_playing = True
                        
            if action_state == 2: # switch to next track
                self.sp.next_track()
                self.index = 0
                self.is_playing = True
                time.sleep(0.5)

            if action_state == 0:
                # print("action state 0")
                if (time.time() - self.check_time) > 0.001:
                    self.check_time = time.time()
                    track = self.sp.current_user_playing_track()['item']['id']
                    # print(track)
                    if self.currently_playing['item']['id'] != track:
                        self.index = 0
                        self.currently_playing['item']['id'] = track
                        print("CHANGED SONGGGGG")
                    
            elif action_state == 3: # switch to previous track
                self.sp.previous_track()
                self.index = 0
                self.is_playing = True
                time.sleep(0.5)
            
        except Exception as e:
            print(f"ERROR: SpotifyWidget.update(): {e}")
        
        # update currently playing track (album artwork, track information)
    
        try:
            if self.is_playing == True:
                if self.index == 0:
                    self.image.paste('black', (0, 0, self.width, self.height)) # clear screen
                
                    try:
                        self.currently_playing = self.sp.current_user_playing_track() # get currently playing track information
                        self.is_playing = self.currently_playing['is_playing']
                        self.song_name = self.currently_playing['item']['name']
                        artists = self.currently_playing['item']['artists']
                        self.artist_names = []
                        for artist in artists:
                            self.artist_names.append(artist['name'])
                        self.album_name = self.currently_playing['item']['album']['name']
                        self.image_url = self.currently_playing['item']['album']['images'][2]['url']
                        #print(json.dumps(self.currently_playing, sort_keys=True, indent=4))
                        self.id = self.currently_playing['item']['id']
                        self.progress = self.currently_playing['progress_ms']
                        self.analysis = self.sp.audio_analysis(self.id)
                        self.correct_segment = False
                        self.anal_index = -1
                        
                    except Exception as e:
                        print(f"ERROR: SpotifyWidget.update(): {e}")
                        self.image.paste('LimeGreen', (2, 2, 30, 30)) # failed to use API; green screen
                        self.index = 0
                        return self.image
                        
                    if self.currently_playing != self.prev_currently_playing:
                        self.prev_currently_playing = self.currently_playing
                        
                        image_file = requests.get(self.image_url, stream=True).raw # get album artwork data from web URL
                        image_size = (28, 28)
                        image_album = add_image(image_file, image_size) # add image
                        self.image.paste(image_album, (2, 2))
                
                text = [self.song_name, ', '.join(self.artist_names)]
                window_size = (30, 20)
                text_track, reset_index = self.add_text_hscroll(text, window_size, self.index, self.interval) # add scrolling text of currently playing track information
                self.image.paste(text_track, (32, 0))

                # DO NOT UNCOMMENT, IDK WHY IT BREAKS 
                # self.currently_playing = self.sp.current_user_playing_track()
                self.progress = self.sp.current_user_playing_track()['progress_ms']
                print(self.anal_index, self.analysis['segments'][self.anal_index]['start'], self.progress)

                self.anal_index += 1
                if self.correct_segment == False:
                    start_time = time.time()
                    
                    if self.analysis['segments'][self.anal_index]['start']*1000 <= self.progress:
                        self.pitches = self.analysis['segments'][self.anal_index]['pitches']
                        self.pitches = [round(x * 10) for x in self.pitches]
                        print(len(self.analysis['segments']))
                        self.image.paste('black',(32,20,57,30))
                        for self.ind in range(12):
                            self.image.paste('white', (32+self.ind*2, 30-self.pitches[self.ind], 33+self.ind*2, 30))
                end_time = time.time()
                seconds = end_time - start_time
                print(" % f seconds" % seconds)
                
                if reset_index == True:
                    self.index = 0
                    self.correct_segment = True
                else:
                    self.index += 1
                    
                if self.verbose == True:
                    print(f"SpotifyWidget.song_name = {self.song_name}")
                    print(f"SpotifyWidget.artist_names = {self.artist_names}")
                    print(f"SpotifyWidget.album_name = {self.album_name}")
                    print(f"SpotifyWidget.index = {self.index}")
                    print(f"SpotifyWidget.is_playing = {self.is_playing}")
            
            else:
                try:
                    self.currently_playing = self.sp.current_user_playing_track() # get currently playing track information
                    self.is_playing = self.currently_playing['is_playing'] # check if song is currently playing
                    
                except Exception as e:
                    print(f"ERROR: SpotifyWidget.update(): {e}")
                    self.image.paste('LimeGreen', (2, 2, 30, 30)) # failed to use API; green screen
                    self.index = 0
                    return self.image
                    
        except Exception as e:
            print(f"ERROR: SpotifyWidget.update(): {e}")
            self.image.paste('red', (2, 2, 30, 30)) # error; red screen
            return self.image
        
        return self.image
    
    """
    add_text_hscroll
        assists with creating 2 lines of horizontal-scrolling text by iteratively cropping a text frame
        assumes height of 32 pixels and text formatting
        
        PARAMS:
        - text = list of 3 strings for each line of text
        - window_size = dimensions of sliding window of text in pixels
        - index = pixel index of current window location
        - interval = pixel shift between sequential windows of text
        
        RETURNS:
        - image_cropped = PIL Image object of current text window
        - reset_index = indicates when window reaches end of text and index must be reset
    """
    def add_text_hscroll(self, text, window_size=(32, 15), index=0, interval=1):
        text_length, _ = max([(len(line), line) for line in text])
        text_length = text_length*8 + (2*window_size[0])
    
        image = Image.new('RGBX', (text_length , window_size[1]), 'black')
        image_draw = ImageDraw.Draw(image)
        
        image_draw.text((window_size[0], 2), text[0], font=Widget.font_bold8, fill='white')
        image_draw.text((window_size[0], 11), text[1], font=Widget.font_bold8, fill='white')
        
        image_cropped = image.crop((index*interval, 0, index*interval + window_size[0], window_size[1]))
        
        if index > (text_length - window_size[0])/interval:
            reset_index = True
        else:
            reset_index = False
        
        return image_cropped, reset_index
        
if __name__ == '__main__':

    SPOTIFY_CLIENT_ID = '4f05fc77c6194e819d037515423871c2'
    SPOTIFY_CLIENT_SECRET = 'e7c52f54890d4df49e12d2118ea258ea'
    SPOTIPY_REDIRECT_URI = 'https://localhost:8888/callback'

    widget = SpotifyWidget(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
    widget.setup()

    display = tk.Tk()
    display.title("Video")

    win_width = 640*2
    win_height = 320*2

    scale_factor = min(win_width/widget.width, win_height/widget.height)

    label = tk.Label(display, width=win_width, height=win_height)
    label.pack()

    while True:
        im = widget.update(0)
        im = im.resize((win_width, win_height))
        frame = ImageTk.PhotoImage(im)
        label.config(image=frame)
        label.image = frame

        time.sleep(0.1)
        display.update()