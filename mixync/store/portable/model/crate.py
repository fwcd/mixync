from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from mixync.store.portable.model import Base

class PortableCrate(Base):
    __tablename__ = 'crate'

    id = Column(Text, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)

    tracks = relationship('PortableCrateTrack')
