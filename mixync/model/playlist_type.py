from enum import IntEnum

# These types correspond to Mixxx's playlist hidden types:
# https://github.com/mixxxdj/mixxx/blob/313c6b8dc11c7fef294817eabb0fb0366ccb0787/src/library/dao/playlistdao.h

class PlaylistType(IntEnum):
    DEFAULT = 0
    AUTO_DJ = 1
    SET_LOG = 2
