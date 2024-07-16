from sqlalchemy.orm import declarative_base
import os
from configparser import ConfigParser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


current_dir = os.path.dirname(os.path.abspath(__file__))
alembic_ini_path = os.path.join(current_dir, '..', 'alembic.ini')


config_parser = ConfigParser()
config_parser.read(alembic_ini_path)


sqlalchemy_url = config_parser.get('alembic', 'sqlalchemy.url')

engine = create_engine(sqlalchemy_url)


Session = sessionmaker(bind=engine)
session = Session()

db_metadata = declarative_base()


from .company import company
from .campaign import campaign
from .content import content 