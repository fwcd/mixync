from sqlalchemy import Column, Text

from mixync.store.mixxx.model import Base, dict_convertible

@dict_convertible
class MixxxDirectory(Base):
    __tablename__ = 'directories'

    directory = Column(Text, primary_key=True)
