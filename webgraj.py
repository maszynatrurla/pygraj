#!/usr/bin/env python

import web
import os.path
import json
import pickle

import aud
import playlist

urls = (
    '/', 'Index',
    '/acmd', 'AudCommand',
    '/nowplay', 'NowPlaying',
    '/artist', 'Artist',
    '/play_artist', 'PlayArtist',
    '/play_album', 'PlayAlbum',
    '/play_song', 'PlaySong',
    '/([a-zA-Z_0-9\.]+)+', 'Resource',
)

TEMPLATE_FOLDER = "templates"
RES_FOLDER = "web"

render = web.template.render(TEMPLATE_FOLDER)

def init_lib():
    with open("music.library") as fp:
        return pickle.load(fp)

library = init_lib()

def contentOf(file):
    fle = file.lower()
    if fle.endswith('.html') or fle.endswith('.htm'):
        return "text/html"
    if fle.endswith('.jpeg') or fle.endswith('.jpg'):
        return "image/jpeg"
    if fle.endswith('.css'):
        return "text/css"
    if fle.endswith('.png'):
        return "image/png"
    if fle.endswith('.js'):
        return "text/javascript"
        
def sort_song(songx, songy):
    try:
        return songx[1] - songy[1]
    except:
        return 0

class Index:
    
    def GET(self):
        #return render.index()
        web.header('Content-type', 'text/html')
        with open(os.path.join(TEMPLATE_FOLDER, "index.html")) as fp:
            return fp.read()
        
class Resource:
    
    def GET(self, requestedFile):
        path = os.path.join(RES_FOLDER, requestedFile)
        if os.path.exists(path):
            with open(path, "rb") as fp:
                contentType = contentOf(requestedFile)
                if contentType:
                    web.header('Content-type', contentType)
                return fp.read()
        else:
            raise web.notfound()
            
class AudCommand:
    
    def GET(self):
        ipt = web.input()
        cmd = ipt.cmd
        if "prev" == cmd:
            aud.playlist_reverse()
            return "OK\n"
        elif "next" == cmd:
            aud.playlist_advance()
            return "OK\n"
        elif "playpause" == cmd:
            aud.playback_playpause()
            return "OK\n"
        elif "stop" == cmd:
            aud.playback_stop()
            return "OK\n"
        elif "setpos" == cmd:
            pos = int(ipt.pos)
            aud.playlist_jump(pos + 1)
            aud.playback_play()
            return "OK\n"
        elif "clear" == cmd:
            aud.playlist_clear()
            return "OK\n"
        else:
            raise web.notfound()
            
class NowPlaying:
    
    def GET(self):
        current_song = aud.current_song()
        pl = playlist.Playlist(None)
        pl.fromText(aud.playlist_display())
        position = aud.playlist_position()
        
        tracks = []
        
        obj = {
            "current_song" : current_song,
            "position" : position,
            "tracks" : tracks
        }
        
        for n, t, l in pl.tracks:
            tracks.append({"track" : n, "title" : t, "time_length" : l})
            
        return json.dumps(obj)
            
            
class Artist:
    
    def __init__(self):
        self.artists = [artist for artist in library.keys()]
        self.artists.sort()
    
    def GET(self):
        ipt = web.input(idx="-1")
        idx = int(ipt.idx)
        
        if idx >= 0:
            if idx < len(self.artists):
                artist = library[self.artists[idx]]
                
                items = []
                album_dir = artist.get("albums", {})
                albums = [name for name in album_dir.keys()]
                albums.sort()
                for name in albums:
                    songs = [song for song in album_dir[name]]
                    songs.sort(sort_song)
                    
                    items.append({"name" : name, "songs" : [{"url": song[0], "title" : song[2], "no" : song[1]} for song in songs]})
                    
                return json.dumps(items)
                
            else:
                raise web.notfound()
        else:
            return json.dumps(self.artists)
            
class PlayArtist:
    def GET(self):
        ipt = web.input()
        idx = int(ipt.artist)
        
        artists = [artist for artist in library.keys()]
        artists.sort()
        
        if int(ipt.queue) == 0:
            aud.playlist_clear()
        
        artist = library[artists[idx]]
        album_dir = artist.get("albums", {})
        albums = [name for name in album_dir.keys()]
        albums.sort()
        for name in albums:
            songs = [song for song in album_dir[name]]
            songs.sort(sort_song)
            
            for song in songs:
                aud.playlist_addurl(song[0])
                
        if int(ipt.queue) == 0:
            aud.playback_play()
                
        return "OK\n"
        
    
class PlayAlbum:
    def GET(self):
        ipt = web.input()
        idx = int(ipt.artist)
        
        artists = [artist for artist in library.keys()]
        artists.sort()
        
        if int(ipt.queue) == 0:
            aud.playlist_clear()
        
        artist = library[artists[idx]]
        album_dir = artist.get("albums", {})
        albums = [name for name in album_dir.keys()]
        albums.sort()
        album_name = albums[int(ipt.album)]
        
        songs = [song for song in album_dir[album_name]]
        songs.sort(sort_song)
            
        for song in songs:
            aud.playlist_addurl(song[0])
            
        if int(ipt.queue) == 0:
            aud.playback_play()
                
        return "OK\n"
        
    
class PlaySong:
    def GET(self):
        ipt = web.input()
        idx = int(ipt.artist)
        
        artists = [artist for artist in library.keys()]
        artists.sort()
        
        if int(ipt.queue) == 0:
            aud.playlist_clear()
        
        artist = library[artists[idx]]
        album_dir = artist.get("albums", {})
        albums = [name for name in album_dir.keys()]
        albums.sort()
        album_name = albums[int(ipt.album)]
        
        songs = [song for song in album_dir[album_name]]
        songs.sort(sort_song)
        
        aud.playlist_addurl(songs[int(ipt.song)][0])
        
        if int(ipt.queue) == 0:
            aud.playback_play()
                
        return "OK\n"
        
if __name__ == "__main__":
    init_lib()
    app = web.application(urls, globals())
    app.run()

