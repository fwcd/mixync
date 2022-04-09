from sqlalchemy import Column, Integer, String, ForeignKey, Text

from mixync.model import Base, dict_convertible

@dict_convertible
class MixxxCrateTrack(Base):
    __tablename__ = 'crate_tracks'

    crate_id = Column(ForeignKey('crates.id'), primary_key=True)
    track_id = Column(ForeignKey('library.id'), primary_key=True, index=True)
