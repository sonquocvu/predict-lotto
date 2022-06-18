from sqlalchemy import Column, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from .database import Base


class HCMLotto(Base):
    __tablename__ = "HCMLotto"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    date = Column(DateTime)
    result = Column(ARRAY(Integer, dimensions=1))
    is_last_day = Column(Boolean, default=False)


class Vietlott645(Base):
    __tablename__ = "Vietlott645"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    date = Column(DateTime)
    result = Column(ARRAY(Integer, dimensions=1))
    is_last_day = Column(Boolean, default=False)
