
import os
import subprocess

def current_song():
    process = subprocess.Popen(['audtool', 'current-song'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out.strip()

def current_song_filename():
    process = subprocess.Popen(['audtool', 'current-song-filename'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out.strip()    

def playback_stop():
    os.system("audtool playback-stop")

def playback_playpause():
    os.system("audtool playback-playpause")
    
def playback_play():
    os.system("audtool playback-play")
    
def playback_playing():
    return 0 == os.system('audtool playback-playing')
    
def playlist_advance():
    os.system("audtool playlist-advance")
    
def playlist_reverse():
    os.system("audtool playlist-reverse")
    
def playlist_jump(pos):
    os.system("audtool playlist-jump %d" % pos)

def playlist_clear():
    os.system("audtool playlist-clear")
    
def playlist_addurl(url):
    os.system("audtool playlist-addurl \"" + url + "\"")
    
def playlist_display():
    process = subprocess.Popen(['audtool', 'playlist-display'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out

def playlist_position():
    process = subprocess.Popen(['audtool', 'playlist-position'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    try:
        return int(out)
    except:
        return -1

        
