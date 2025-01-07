from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from configparser import ConfigParser
from sqlalchemy import create_engine
from models import Stats, Match

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_overall_stats():
    config = ConfigParser()
    config.read("config.ini")

    if "database" not in config:
        raise KeyError("The 'database' section is missing in the configuration file.")

    db_user = config["database"]["user"]
    db_password = config["database"]["password"]
    db_host = config["database"]["host"]
    db_port = config["database"]["port"]
    db_name = config["database"]["dbname"]

    # Create the database URL dynamically
    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_season_matches():
    config = ConfigParser()
    config.read("config_1.ini")

    if "database" not in config:
        raise KeyError("The 'database' section is missing in the configuration file.")

    db_user = config["database"]["user"]
    db_password = config["database"]["password"]
    db_host = config["database"]["host"]
    db_port = config["database"]["port"]
    db_name = config["database"]["dbname"]

    # Create the database URL dynamically
    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/overall_stats/")
async def overall_stats(season: str, db: Session = Depends(get_overall_stats)):
    stats = db.query(Stats).filter(Stats.year == season)
    if not stats:
        raise HTTPException(status_code=404, detail="No stats found")
    
    simplified_stats = [
        f"{stat.year}, {stat.fg}, {stat.three_p}, {stat.ft}, {stat.reb}, {stat.ast}, {stat.pts}"
        for stat in stats
    ]

    return simplified_stats

@app.get("/season_matches/")
async def season_matches(season: str, db: Session = Depends(get_season_matches)):
    matches = db.query(Match).filter(Match.season == season).all()
    if not matches:
        raise HTTPException(status_code=404, detail= "No matches found")
    
    simplified_matches = [
        f"{match.season}, {match.Home_Team}, {match.Opp_Team}, {match.Result}, {match.Reb}, {match.Ast}"
        for match in matches
    ]
    
    return simplified_matches
