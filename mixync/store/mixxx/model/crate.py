from sqlalchemy import Column, Integer, String, ForeignKey, Text

from mixync.model import Base, dict_convertible

@dict_convertible
class Crate(Base):
    __tablename__ = 'crates'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), unique=True, nullable=False)
    count = Column(Integer, default=0)
    show = Column(Integer, default=1)
    locked = Column(Integer, default=0)
    autodj_source = Column(Integer, default=0)
