from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
from StatsCrawler import ensure_database_exists
from sqlalchemy import create_engine, Column, String, Integer, CHAR, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser

class Match:
    def __init__(self, season,date, team, opp, result, reb, ast):
        self.season = season
        self.date = date
        self.team = team
        self.opp = opp
        self.result = result
        self.reb = reb
        self.ast = ast

def close_cookie_tab(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'fc-cta-consent'))
        )

        accept_button = driver.find_element(By.CLASS_NAME, 'fc-cta-consent')
        accept_button.click()

    except Exception as e:
        print(f"An error occurred: {e}")

def matches_retrieve(driver, match_list, season):
    close_cookie_tab(driver)
    team = ''
    data = driver.find_elements(By.CLASS_NAME, 'd-inline-block.a-middle')
    for t in data:
        if "Team" in t.text:
            team = t.text
    
    team = team.split(':')
    his_team = team[1].strip()
   
    tables = driver.find_elements(By.CSS_SELECTOR, ".clearfix.clear.overflow-x-auto.margen-y10.max-000.by")
    for table in tables:
        rows = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.CLASS_NAME, 'a-top')
        
        for row in rows:
            stats = row.find_elements(By.TAG_NAME, 'td')
            with open("stats.txt", "w") as file:
                for stat in stats:
                    file.write(stat.text + '\n')
            
            stat_list = []
            
            with open("stats.txt", "r", encoding="utf-8") as file:
                for line in file:
                    stat_list.append(line.strip())
            date = '-'
            opp = '-'
            score = '-'
            reb = '-'
            ast ='-'
            try:
                date = stat_list[1]
                opp = stat_list[2]
                score = stat_list[3] + stat_list[4]
                reb = stat_list[9]
                ast = stat_list[10]
            except:
                pass
            match_list.append(Match(season, date, his_team, opp, score, reb, ast))

if __name__ == "__main__":
    if not os.path.exists("stats.csv"):

        #selenium initialize
        path = r"C:\Users\User\Desktop\workspace2\chromedriver-win64\chromedriver.exe"
        service = Service(path)
        driver = webdriver.Chrome(service=service)
        years_list = [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 
                    2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
        match_list : List[Match] = []

        #itterate through every season
        for year in years_list:
            matches_url = f"https://www.landofbasketball.com/nba_players_game_logs/{year}/lebron_james_full.htm"
            driver.get(matches_url)
            season = f"{year-1}-{year}"
            
            matches_retrieve(driver, match_list, season)
        
        data = [
        [match.season, match.date, match.team, match.opp, match.result, match.reb, match.ast]
        for match in match_list
                ]
        column = ["Season", "Date", "Home Team", "Opp team", "Result", "Rebounds", "Assists"]
        df = pd.DataFrame(data, columns=column)
        df.to_csv('stats.csv', index=False)

        driver.quit()
        #fixing some dataframe errors
        df = pd.read_csv('stats.csv')
        df["Opp team"] = df["Opp team"].str.replace('@ ', '').str.replace('vs. ', '')
        df.to_csv('modified_file.csv', index=False)

    
    #store the data in a postgresql database
    Base = declarative_base()
    config = ConfigParser()
    config.read("config_1.ini")

    db_user = config["database"]["user"]
    db_password = config["database"]["password"]
    db_host = config["database"]["host"]
    db_port = config["database"]["port"]
    db_name = config["database"]["dbname"]

    # Create the database URL dynamically
    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}" 

    #check if the database exists
    ensure_database_exists(db_name, db_user, db_password, db_host, db_port)

    class Link(Base):
        __tablename__ = "all_matches_x"

        id = Column("id", Integer, primary_key=True, autoincrement=True)
        season = Column("season", String)
        date = Column("date", String)
        home_team = Column("Home_Team", String)  
        opp = Column("Opp_Team", String)
        result = Column("Result", String)
        reb = Column("Reb", String)
        ast = Column("Ast", String)
        Created_at = Column(TIMESTAMP, server_default=func.now())
        
        def __init__(self, season, date, home_team, opp, result, reb, ast):
            self.season = season
            self.date = date
            self.home_team = home_team
            self.opp = opp
            self.result = result
            self.reb = reb
            self.ast = ast
        
    engine = create_engine(database_url, echo = True)

    Base.metadata.create_all(bind = engine)

    Session = sessionmaker(bind = engine)
    session = Session()

    df = pd.read_csv("modified_file.csv")
    
    for _, row in df.iterrows():
        element = Link(row["Season"], row["Date"], row["Home Team"], row["Opp team"], row["Result"], row["Rebounds"], 
              row["Assists"])
        session.add(element)

    session.commit()
    session.close()