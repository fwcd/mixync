from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text

from mixync.store.portable.model import Base

class PortableCrateTrack(Base):
    __tablename__ = 'crate_tracks'

    crate_id = Column(ForeignKey('crates.id'), primary_key=True)
    track_id = Column(ForeignKey('tracks.id'), primary_key=True)
