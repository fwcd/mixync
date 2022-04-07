from sqlalchemy.orm import declarative_base

Base = declarative_base()

def dict_convertible(cls):
    """A decorator that adds dict conversions to a model class."""

    @classmethod
    def from_dict(cls, d: dict):
        obj = cls.__new__(cls)
        obj.__init__(**d)
        return obj

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    cls.from_dict = from_dict
    cls.to_dict = to_dict

    return cls
