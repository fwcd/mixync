from sqlalchemy import Column, Text

from mixync.store.portable.model import Base

class PortableDirectory(Base):
    __tablename__ = 'directories'

    id = Column(Text, primary_key=True)
    location = Column(Text, unique=True, nullable=False)
