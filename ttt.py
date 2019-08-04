

TEXT_DIR = {
    "TT_SRC_ITEM_LOCAL_STORAGE"         : u"Karta",
    "TT_SRC_ITEM_CD"                    : u"P\u0142yta",
    "TT_SRC_ITEM_INTERNET_RADIO"        : u"Sie\u0107",
    "TT_SRC_ITEM_PODCASTS"              : u"Podcasty",
}

    
def get_text(key):
    return TEXT_DIR.get(key, "???")
