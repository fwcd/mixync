from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from mixync.store.portable.model import Base

class PortablePlaylist(Base):
    __tablename__ = 'playlist'

    id = Column(Text, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    position = Column(Integer, nullable=True)
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)

    tracks = relationship('PortablePlaylistTrack')
