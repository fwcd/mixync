from sqlalchemy import Column, Text, Integer

from mixync.store.portable.model import Base

class PortableDirectory(Base):
    __tablename__ = 'directories'

    id = Column(Integer, primary_key=True)
    location = Column(Text, unique=True, nullable=False)
