from sqlalchemy import Column, Integer, ForeignKey, Text

from mixync.store.mixxx.model import Base

class MixxxCue(Base):
    __tablename__ = 'cues'

    id = Column(Integer, primary_key=True)
    track_id = Column(ForeignKey('library.id'), nullable=False)
    type = Column(Integer, default=0, nullable=False)
    position = Column(Integer, default=-1, nullable=False)
    length = Column(Integer, default=0, nullable=False)
    hotcue = Column(Integer, default=-1, nullable=False)
    label = Column(Text, default='', nullable=False)
    color = Column(Integer, default=0xFFFF0000, nullable=False)
