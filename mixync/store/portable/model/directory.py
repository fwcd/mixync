from sqlalchemy import Column, Text, Integer

from mixync.store.portable.model import Base

class PortableDirectory(Base):
    __tablename__ = 'directories'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    location = Column(Text, unique=True, nullable=False)
