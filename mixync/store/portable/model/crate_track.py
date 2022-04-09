from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text

from mixync.store.mixxx.model import Base

class PortableCrateTrack(Base):
    __tablename__ = 'crate_track'

    crate_id = Column(ForeignKey('crate.id'), primary_key=True)
    track_id = Column(ForeignKey('track.id'), primary_key=True)
