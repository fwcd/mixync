from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text

from mixync.store.portable.model import Base

class PortablePlaylistTrack(Base):
    __tablename__ = 'playlist_track'

    playlist_id = Column(ForeignKey('playlist.id'), primary_key=True)
    track_id = Column(ForeignKey('track.id'), primary_key=True)
    position = Column(Integer, nullable=False)
