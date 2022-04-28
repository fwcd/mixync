from sqlalchemy import Column, Integer, Float, Text, DateTime, LargeBinary
from sqlalchemy.orm import relationship

from mixync.store.portable.model import Base

class PortableTrack(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    title = Column(Text, default='', nullable=False)
    artist = Column(Text, default='', nullable=False)
    location = Column(Text, default='', nullable=False)
    album = Column(Text, default='', nullable=False)
    year = Column(Text, default='', nullable=False)
    genre = Column(Text, default='', nullable=False)
    comment = Column(Text, default='', nullable=False)
    duration_ms = Column(Integer, nullable=True)
    track_number = Column(Integer, nullable=True)
    url = Column(Text, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    bpm = Column(Float, nullable=True)
    beats = Column(LargeBinary, nullable=True)
    beats_version = Column(Text, nullable=True)
    beats_sub_version = Column(Text, nullable=True)
    channels = Column(Integer, nullable=True)
    times_played = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True)
    key = Column(Text, nullable=True)
    keys = Column(LargeBinary, nullable=True)
    keys_version = Column(Text, nullable=True)
    keys_sub_version = Column(Text, nullable=True)
    color = Column(Integer, nullable=True)
    last_played_at = Column(DateTime, nullable=True)

    cues = relationship('PortableCue')
