
import dbus
from threading import Lock
import urllib

class _Audctl:
    _lock = Lock()
    _iface = None
    
    @staticmethod
    def _getIface():
        if _Audctl._iface is None:
            with _Audctl._lock:
                bus = dbus.SessionBus()
                proxy = bus.get_object("org.atheme.audacious", "/org/atheme/audacious")
                _Audctl._iface = dbus.Interface(proxy, dbus_interface = "org.atheme.audacious")
                
        return _Audctl._iface


def current_song():
    iface = _Audctl._getIface()
    return iface.SongTitle(iface.Position())

def current_song_filename():
    iface = _Audctl._getIface()
    sln = str(iface.SongFilename(iface.Position()))
    sln = urllib.unquote(sln)
    if sln.startswith("file:///"):
        return sln[7:]
    return sln

def playback_stop():
    iface = _Audctl._getIface()
    iface.Stop()

def playback_playpause():
    iface = _Audctl._getIface()
    iface.PlayPause()
    
def playback_play():
    iface = _Audctl._getIface()
    iface.Play()
    
def playback_playing():
    iface = _Audctl._getIface()
    return iface.Playing()
    
def playlist_advance():
    iface = _Audctl._getIface()
    iface.Advance()
    
def playlist_reverse():
    iface = _Audctl._getIface()
    iface.Reverse()
    
def playlist_jump(pos):
    iface = _Audctl._getIface()
    iface.Jump(pos - 1)
    
def playlist_delete(pos):
    iface = _Audctl._getIface()
    iface.Delete(pos - 1)

def playlist_clear():
    iface = _Audctl._getIface()
    iface.Clear()
    
def playlist_addurl(url):
    if url.startswith("/"):
        url = "file://" + urllib.pathname2url(url)
    iface = _Audctl._getIface()
    iface.AddUrl(url)
    
def playlist_display():
    iface = _Audctl._getIface()
    playlist_length = iface.Length()
    total = 0
    txt = ["%d track%s" % (playlist_length, "s" if playlist_length > 1 else "")]
    
    for entry in range(playlist_length):
        title = iface.SongTitle(entry)
        length = int(iface.SongFrames(entry) / 1000)
        
        total += length
        
        txt.append("%4d | %s | %d:%.2d" % (entry, title, int(length / 60), int(length % 60)))
    
    txt.append("Total length: %d:%.2d" % (int(total / 60), int(total % 60)))
    return "\n".join(txt)

def playlist_position():
    iface = _Audctl._getIface()
    return iface.Position() + 1
