from sqlalchemy import Column, Integer, ForeignKey, DateTime

from mixync.model import Base, dict_convertible

@dict_convertible
class MixxxPlaylistTrack(Base):
    __tablename__ = 'PlaylistTracks'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(ForeignKey('Playlists.id'))
    track_id = Column(ForeignKey('library.id'), index=True)
    position = Column(Integer)
    pl_datetime_added = Column(DateTime)
