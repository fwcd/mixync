from sqlalchemy import Column, Integer, String

from mixync.store.mixxx.model import Base

class MixxxTrackLocation(Base):
    __tablename__ = 'track_locations'

    id = Column(Integer, primary_key=True)
    location = Column(String(512), unique=True)
    filename = Column(String(512))
    directory = Column(String(512))
    filesize = Column(Integer)
    fs_deleted = Column(Integer)
    needs_verification = Column(Integer)
