from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text

from mixync.store.mixxx.model import Base

class PortableDirectory(Base):
    __tablename__ = 'directory'

    id = Column(Text, primary_key=True)
    location = Column(Text, unique=True, nullable=False)
