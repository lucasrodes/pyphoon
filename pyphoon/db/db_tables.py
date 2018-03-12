import datetime

from sqlalchemy import Column, Integer, DateTime, Numeric, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BestTrack(Base):
    """

    """
    __tablename__ = 'besttrack'
    typ_id = Column(Integer, primary_key=True)
    obs_time = Column(DateTime, primary_key=True, default=datetime.datetime.min)
    typ_class = Column(Integer)
    lat = Column(Numeric)
    lng = Column(Numeric)
    pressure = Column(Numeric)
    max_wind = Column(Numeric)
    gust = Column(Numeric)
    storm_dir = Column(Integer)
    storm_rad_maj = Column(Integer)
    storm_rad_min = Column(Integer)
    gale_dir = Column(Integer)
    gale_rad_maj = Column(Integer)
    gale_rad_min = Column(Integer)
    landfall = Column(Integer)
    speed = Column(Integer)
    direction = Column(Integer)
    interpolated = Column(Boolean)


class Images(Base):
    """

    """
    __tablename__ = 'images'
    typ_id = Column(Integer, primary_key=True)
    obs_time = Column(DateTime, primary_key=True, default=datetime.datetime.min)
    file = Column(String, nullable=False)
