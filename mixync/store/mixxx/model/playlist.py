from sqlalchemy import Column, Integer, String, DateTime

from mixync.store.mixxx.model import Base, dict_convertible

@dict_convertible
class MixxxPlaylist(Base):
    __tablename__ = 'Playlists'

    id = Column(Integer, primary_key=True)
    name = Column(String(48))
    position = Column(Integer)
    hidden = Column(Integer, default=0, nullable=False)
    date_created = Column(DateTime)
    date_modified = Column(DateTime)
    locked = Column(Integer, default=0)
