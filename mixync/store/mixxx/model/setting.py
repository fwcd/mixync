from sqlalchemy import Column, Text, Integer

from mixync.store.mixxx.model import Base

class MixxxSetting(Base):
    __tablename__ = 'settings'

    name = Column(Text, primary_key=True)
    value = Column(Text)
    locked = Column(Integer, default=0)
    hidden = Column(Integer, default=0)
