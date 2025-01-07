from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stats(Base):
    __tablename__ = "overall_stats"  # Replace with your actual table name

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String, nullable=False)
    fg = Column("fg%", String, nullable=False)
    three_p = Column("3p%", String, nullable=False)
    ft = Column("ft%", String, nullable=False)
    reb = Column(String, nullable=False)
    ast = Column(String, nullable=False)
    pts = Column(String, nullable=False)

class Match(Base):
    __tablename__ = "all_matches_x"

    id = Column(Integer, primary_key=True, index=True)
    season = Column(String, nullable=False)
    date = Column(String, nullable=False)
    Home_Team = Column(String, nullable=False)
    Opp_Team = Column(String, nullable=False)
    Result = Column(String, nullable=False)
    Reb = Column(String, nullable=False)
    Ast = Column(String, nullable=False)