
import aud

class PlaylistSM:
    def __init__(self, ctx):
        self.ctx = ctx
        self.state = 0
        self.cycles = 0
        self.playlistRaw = ""
        self.playlist = None
        
    def poke(self):
        self.state = 1
        
    def cycle(self):
        if self.state == 1:
            self.cycles += 1
            if self.cycles > 2:
                self.cycles = 0
                self.state = 2
                self.updatePlaylist()
        elif self.state > 1 and self.state < 10:
            self.cycles += 1
            if self.cycles > 5:
                self.cycles = 0
                self.state += 1
                self.updatePlaylist()
        elif self.state >= 10:
            self.cycles += 1
            if self.cycles > 50:
                self.cycles = 0
                self.updatePlaylist()
        
    def updatePlaylist(self):
        out = aud.playlist_display()
        if self.playlistRaw != out:
            self.playlistRaw = out
            self.ctx.playlist.fromText(out)
            self.ctx.playlist.widget.update()
            
class PlaybackSM:
    def __init__(self, ctx):
        self.ctx = ctx
        self.state = 0
        self.cycles = 0
        
    def poke(self):
        self.state = 1
        
    def cycle(self):
        if self.state == 1:
            if self.updatePlayback():
                self.cycles = 0
                self.state = 2
            else:
                self.state = 0
        elif self.state == 2:
            self.cycles += 1
            if self.cycles > 2:
                self.state = 1
                
    def updatePlayback(self):
        changes = False
        position = aud.playlist_position()
        if position != self.ctx.playlist.position:
            self.ctx.playlist.position = position
            changes = True
        
        is_playing = aud.playback_playing()
        if not is_playing and self.ctx.playlist.position >= 0:
            self.ctx.playlist.position = -1
            changes = True
            
        if changes:
            self.ctx.playlist.widget.update()
        
        return is_playing

class Playlist:
    
    def __init__(self, ctx):
        self.ctx = ctx
        self.tracks = ()
        self.position = -1
        self.widget = False
        
    def fromText(self, text):
        lines = text.splitlines()
        self.tracks = []
        if len(lines) > 2:
            for line in lines[1:-1]:
                track, title, tlen = line.split('|')
                track = track.strip()
                title = title.strip()
                tlen = tlen.strip()
                self.tracks.append((track, title, tlen))
            
    def setWidget(self, widget):
        self.widget = widget

    
    

