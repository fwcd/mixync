from sqlalchemy import Column, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from mixync.store.portable.model import Base

class PortableCrate(Base):
    __tablename__ = 'crates'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)
    locked = Column(Boolean, default=False, nullable=False)

    tracks = relationship('PortableCrateTrack')
