import os.path
import glob
import logging
import pickle
import argparse
import pickle

import mp3_tagger
from PIL import Image


def maybe_audio_file(pth):
    return pth.lower().endswith(".mp3")
    
def maybe_image_file(pth):
    pth = pth.lower()
    for ext in (".jpg", "jpeg", "png", "bmp", "gif"):
        if pth.endswith(ext):
            return True
    return False

def pth_cmp(image_path_a, image_path_b):
    sum = 0
    
    if "front" in image_path_a.lower():
        sum += 1
    elif "back" in image_path_a.lower():
        sum -= 1
    
    if "front" in image_path_b.lower():
        sum -= 1
    elif "back" in image_path_b.lower():
        sum += 1
        
    return sum

def choose_image(candidates):
    candidates.sort(pth_cmp)
    for candidate in candidates:
        try:
            im = Image(candidate)
            x, y = im.size()
            if x > 96 and y > 96:
                ratio = float(x) / float(y)
                if ratio > .5 and ratio < 2:
                    return candidate
        except:
            pass
            
def merge_libs(target, source):
    tartists = target.setdefault("artists", {})
    for name, artist in source.get("artists", {}).iteritems():
        tartist = tartists.setdefault(name, {})
        tsongs = tartist.setdefault("songs", [])
        talbums = tartist.setdefault("albums", {})
        for sg in artist.get("songs", ()):
            tsongs.append(sg)
        for name, ab in artist.get("albums", {}).iteritems():
            talbums[name] = ab
            
class Song:
    def __init__(self, pth, **props):
        self.pth = pth
        self.props = props
    
def inventorize_audio_file(pth, lib):
    try:
        mp3 = mp3_tagger.MP3File(pth)
        tags = mp3.get_tags()
        tags = tags.get("ID3TagV2", tags.get("ID3TagV1"))
        artist, album, song, track = ("???", "???", None, 0)
        if tags is not None:
            artist = tags.get("artist", "???")
            album = tags.get("album", "???")
            song = tags.get("song", os.path.splitext(os.path.split(pth)[-1])[0])
            track = tags.get("track", 0)
            
        obj = Song(pth, artist = artist, album = album, song = song, track = track)
        obj_artist = lib.setdefault("artists", {}).setdefault(artist, {})
        obj_artist.setdefault("songs", []).append(obj)
        obj_album = lib.setdefault("albums", {}).setdefault((artist, album), {})
        obj_album.setdefault("songs", []).append(obj)
        obj_artist.setdefault("albums", {}).setdefault(album, obj_album)
        
    except:
        logging.warning("Ignoring path \"" + str(pth) + "\"")

class Library:
    
    def __init__(self, location):
        self.location = location
        self.lib = {}

    def scan(self):
        self.lib.clear()
        self.recurse(self.location, self.lib)
        
    def recurse(self, dir, lib):
        
        album_art_candidates = []
        child_lib = {}
        
        try:
            for pth in glob.glob(os.path.join(dir, "*")):
                if os.path.isdir(pth):
                    self.recurse(pth, child_lib)
                    
                if maybe_audio_file(pth):
                    inventorize_audio_file(pth, child_lib)
                    
                elif maybe_image_file(pth):
                    album_art_candidates.append(pth)
        except:
            logging.warning("Ignoring dir \"" + str(pth) + "\"")

        album_art_path = choose_image(album_art_candidates)
        if album_art_path:
            for album in child_lib.get("albums", {}).itervalues():
                if not album.get("art"):
                    album["art"] = album_art_path
                    
        merge_libs(lib, child_lib)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invertorize music")
    parser.add_argument("directory")
    parser.add_argument("output_file", nargs="?", default="music.library")
    args = parser.parse_args()
    
    l = Library(args.directory)
    l.scan()

    with open(args.output_file, "w") as fp:
        pickle.dump(l, fp)
        
    for name, artist in l.lib["artists"].iteritems():
        print(name)
        for name, album in artist["albums"].iteritems():
            print("\t" + str(name))
            for song in album["songs"]:
                print("\t\t" + str(song.pth))

