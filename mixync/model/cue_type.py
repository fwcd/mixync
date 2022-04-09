from enum import IntEnum

# These cue types correspond to Mixxx's cue types:
# https://github.com/mixxxdj/mixxx/blob/313c6b8dc11c7fef294817eabb0fb0366ccb0787/src/track/cueinfo.h#L11-L22

class CueType(IntEnum):
    INVALID = 0
    HOT_CUE = 1
    MAIN_CUE = 2
    BEAT = 3 # unused, added for compatibility
    LOOP = 4
    JUMP = 5
    INTRO = 6
    OUTRO = 7
    AUDIBLE_SOUND = 8
