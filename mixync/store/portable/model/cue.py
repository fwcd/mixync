from sqlalchemy import Column, Integer, ForeignKey, Text, Integer

from mixync.store.portable.model import Base

class PortableCue(Base):
    __tablename__ = 'cues'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    track_id = Column(ForeignKey('tracks.id'), nullable=False)
    type = Column(Integer, default=0, nullable=False)
    position_ms = Column(Integer, nullable=True)
    length_ms = Column(Integer, default=0, nullable=False)
    hotcue = Column(Integer, nullable=True)
    label = Column(Text, nullable=True)
    color = Column(Integer, default=0xFFFF0000, nullable=False)
