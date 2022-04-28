from sqlalchemy import Column, DateTime, Integer, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from mixync.store.portable.model import Base

class PortablePlaylist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    position = Column(Integer, nullable=True)
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)
    type = Column(Integer, default=0, nullable=False)
    locked = Column(Boolean, default=False, nullable=False)

    tracks = relationship('PortablePlaylistTrack')
