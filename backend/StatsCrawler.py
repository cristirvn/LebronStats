from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, Column, String, Integer, CHAR, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
import psycopg2

class Stat:
    def __init__(self, year, fg, three_p, ft, reb, ast, pts):
        self.year = year
        self.fg = fg
        self.three_p = three_p
        self.ft = ft
        self.reb = reb
        self.ast = ast
        self.pts = pts
        
       
def close_cookie_tab(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )

        accept_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        accept_button.click()

    except Exception as e:
        print(f"An error occurred: {e}")
    
def retrieve_stats(stats_list, driver):
    #close cookie tab if appears
    close_cookie_tab(driver)

    #retrieving the years of activity
    years_in_order = []
    years_table = driver.find_element(By.CSS_SELECTOR, '.Table--align-right .Table__TBODY')
    years = years_table.find_elements(By.TAG_NAME, 'tr')
    for year in years:
        date = year.find_element(By.TAG_NAME, 'td').text
        date = str(date)
        date = date.split('-')
        try:
            temp_year = int(date[0])
            date[0] = f"{temp_year}-{temp_year + 1}"
        except:
            pass
        years_in_order.append(date[0])

    #retrieve all the statistics/year
    table = driver.find_element(By.CSS_SELECTOR, '.Table__ScrollerWrapper .Table__Scroller .Table--align-right .Table__TBODY')
    table_rows = table.find_elements(By.TAG_NAME, 'tr')

    #itterate through every year stats
    index = 0
    for row in table_rows:
        statistics = row.find_elements(By.TAG_NAME, 'td')
        fg_procent = statistics[4].text
        three_points = statistics[6].text
        ft_procent = statistics[8].text
        reb = statistics[11].text
        ast = statistics[12].text
        pts = statistics[17].text

        stats_list.append(Stat(years_in_order[index], fg_procent, three_points, ft_procent, reb, ast, pts))
        index += 1

    return stats_list

def ensure_database_exists(db_name, db_user, db_password, db_host, db_port):
    try:
        # Connect to the PostgreSQL server without specifying a database
        connection = psycopg2.connect(
            database="postgres",  # Default database for initial connection
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        connection.autocommit = True
        cursor = connection.cursor()

        # Check if the database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cursor.fetchone()

        if not exists:
            # Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE {db_name};")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")

        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error ensuring database exists: {e}")

if __name__ == "__main__":
    #selenium initialize
    path = r"C:\Users\User\Desktop\workspace2\chromedriver-win64\chromedriver.exe"
    service = Service(path)
    driver = webdriver.Chrome(service=service)

    stats_url = "https://www.espn.com/nba/player/stats/_/id/1966/lebron-james"

    driver.get(stats_url)
    stats_list : List[Stat] = []

    retrieve_stats(stats_list, driver)
    driver.quit()

    stats_list.pop()
    

    #store the data in a postgresql database
    Base = declarative_base()
    config = ConfigParser()
    config.read("config.ini")

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
        __tablename__ = "overall_stats"

        id = Column("id", Integer, primary_key=True, autoincrement=True)
        year = Column("year", String)
        fg = Column("fg%", String)
        three_p = Column("3p%", String)  
        ft = Column("ft%", String)
        reb = Column("reb", String)
        ast = Column("ast", String)
        pts = Column("pts", String)
        Created_at = Column(TIMESTAMP, server_default=func.now())
        
        def __init__(self, year, fg, three_p, ft, reb, ast, pts):
            self.year = year
            self.fg = fg
            self.three_p = three_p
            self.ft = ft
            self.reb = reb
            self.ast = ast
            self.pts = pts
    
    engine = create_engine(database_url, echo = True)

    Base.metadata.create_all(bind = engine)

    Session = sessionmaker(bind = engine)
    session = Session()

    for stat in stats_list:
        element = Link(stat.year, stat.fg, stat.three_p, stat.ft, stat.reb, stat.ast, stat.pts)
        session.add(element)

    session.commit()
    session.close()
        