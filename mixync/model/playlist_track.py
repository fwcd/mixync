from sqlalchemy import Column, Integer, ForeignKey, DateTime

from mixync.model import Base, dict_convertible

@dict_convertible
class PlaylistTrack(Base):
    __tablename__ = 'PlaylistTracks'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(ForeignKey('playlists.id'))
    track_id = Column(ForeignKey('library.id'), index=True)
    position = Column(Integer)
    pl_datetime_added = Column(DateTime)
