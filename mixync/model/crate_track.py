from sqlalchemy import Column, Integer, String, ForeignKey, Text

from mixync.model import Base, dict_convertible

@dict_convertible
class CrateTrack(Base):
    __table__ = 'crate_tracks'

    crate_id = Column(ForeignKey('crates.id'))
    track_id = Column(ForeignKey('library.id'), index=True)
