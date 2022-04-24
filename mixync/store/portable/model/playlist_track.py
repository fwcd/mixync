from sqlalchemy import Column, Integer, ForeignKey

from mixync.store.portable.model import Base

class PortablePlaylistTrack(Base):
    __tablename__ = 'playlist_tracks'

    playlist_id = Column(ForeignKey('playlists.id'), primary_key=True)
    track_id = Column(ForeignKey('tracks.id'), primary_key=True)
    position = Column(Integer, nullable=False)
