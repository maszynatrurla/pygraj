
import sys
import pickle
import argparse


def litendu(data, blen):
    return sum((ord(data[i]) << (8 * i)) for i in xrange(blen))
    
def litendi(data, blen):
    uval = litendu(data, blen)
    if uval & (1 << (blen * 8 - 1)):
        return -1 * ((~uval + 1) & ((1 << blen * 8) - 1))
    return uval

CACHE_ENTRY_HEAD_FIELDS = (
    ("size", 4, litendu),
    ("play_count", 4, litendi),
    ("mtime", 8, litendi),
    ("duration", 4, litendi),
    ("bitrate", 4, litendi),
    ("bpm", 4, litendi),
)

CACHE_ENTRY_HEAD_LEN = sum(f[1] for f in CACHE_ENTRY_HEAD_FIELDS)
CACHE_ENTRY_RESERVED_LEN = 52

class MyUID:
    
    _UID = 0
    
    @staticmethod
    def getUid():
        MyUID._UID += 1
        return MyUID._UID

class TrackInfo:
    def __init__(self):
        self.uid = MyUID.getUid()
        self.mtime = 0
        self.duration = 0
        self.bitrate = 0
        self.bpm = -1
        self.play_count = 0
        self.filename = ""
        self.codec = None
        self.codec_profile = None
        self.comments = None
        
    def __str__(self):
        return "%s %d %d %d %d" % (self.filename, self.duration, self.bitrate, self.bpm, self.play_count)



def read_str(data, offset):
    idx = 0
    while offset + idx < len(data):
        if data[offset + idx] == '\x00':
            return (data[offset:offset+idx], idx)
        idx += 1
    return (data[offset:offset+idx], idx)

def read_entry(data, offset, out_arr):
    entry_fields = []
    eoff = offset
    for field in CACHE_ENTRY_HEAD_FIELDS:
        entry_fields.append(field[2](data[eoff:], field[1]))
        eoff += field[1]
        
    # size 
    available_data_size = len(data) - offset
    minimal_size = CACHE_ENTRY_HEAD_LEN + CACHE_ENTRY_RESERVED_LEN
    
    if available_data_size < minimal_size:
        raise Exception("cache corrupted, not enough data left")
        
    if (entry_fields[0] < minimal_size) or (entry_fields[0] > available_data_size):
        raise Exception("cache corrupted, entry size is wrong")
        
    str_size = entry_fields[0] - minimal_size
    eoff += CACHE_ENTRY_RESERVED_LEN
    
    track_info = TrackInfo()
    track_info.play_count = entry_fields[1]
    track_info.mtime = entry_fields[2]
    track_info.duration = entry_fields[3]
    track_info.bitrate = entry_fields[4]
    track_info.bpm = entry_fields[5]
    
    soff = eoff
    track_info.filename, slen = read_str(data, soff)
    soff += slen + 1

    track_info.codec, slen = read_str(data, soff)
    soff += slen + 1
    
    track_info.codec_profile, slen = read_str(data, soff)
    soff += slen + 1
    
    scnt = 0
    for i in xrange(eoff, eoff + str_size):
        if '\x00' == data[i]:
            scnt += 1
    scnt = (scnt - 3) / 2
    
    kv = {}
    for _ in xrange(scnt):
        k, slen = read_str(data, soff)
        soff += slen + 1
        
        v, slen = read_str(data, soff)
        soff += slen + 1
        
        kv[k] = v
    
    track_info.comments = kv
    
    eoff += str_size
    out_arr.append(track_info)
    return (offset + entry_fields[0] + 4 - 1) & 0xFFFFFFFC
    

def load(fname):
    cache_header = ""
    cache_entries = []
    
    with open(fname, "rb") as fp:
        data = fp.read()
        
        cache_header = data[:8]
        assert len(cache_header) == 8
        offset = 8
        
        while offset + CACHE_ENTRY_HEAD_LEN <= len(data):
            offset = read_entry(data, offset, cache_entries)
    
    return cache_header, cache_entries
    
def create_map(tracks):
    artists = {}
    
    for track in tracks:
        try:
            track_number = int(track.comments.get("tracknumber", "0"))
        except:
            track_number = 0
        
        title = track.comments.get("title", track.filename)
        artist_name = track.comments.get("artist", "???")
        album_name = track.comments.get("album", "???")
        
        tup = (track.filename, track_number, title, artist_name, album_name)
        
        artist_dir = artists.setdefault(artist_name, {})
        artist_dir.setdefault("songs", []).append(tup)
        
        
        artist_dir.setdefault("albums", {}).setdefault(album_name, []).append(tup)
    
    return artists
    
def sort_songs(a, b):
    return a[1] - b[1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invertorize music")
    parser.add_argument("cmus_cache")
    parser.add_argument("output_file", nargs="?", default="music.library")
    args = parser.parse_args()
    
    cache_header, entries = load(args.cmus_cache)

    artists = create_map(entries)
    
    with open(args.output_file, "wb") as fp:
        pickle.dump(artists, fp)
    
    artists_names = [k for k in artists.keys()]
    artists_names.sort()
    
    for name in artists_names:
        print(name)
        albums = artists[name].get("albums", {})
        album_names = [k for k in albums.keys()]
        album_names.sort()
        for album_name in album_names:
            print("    " + str(album_name))
            songs = [s for s in albums[album_name]]
            songs.sort(sort_songs)
            for song in songs:
                print("        %2d %s" % (song[1], song[2]))
    
    
