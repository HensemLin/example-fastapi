from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from .config import settings

load_dotenv() 

#mysql://root:rootuser@localhost:3306/datasciencedb

SQLALCHEMY_DATABASE_URL = f"mysql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# db = database('FastAPI')
# db.create_database()
# # define the table columns
# columns = [
#     'id INT AUTO_INCREMENT PRIMARY KEY',
#     'title VARCHAR(255) NOT NULL',
#     'content VARCHAR(255)', 
#     'published BOOL DEFAULT true', 
#     'date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'
# ]

# # create the table
# table_name = "test"
# db.createTable(table_name=table_name, columns=columns)
# db.deleteTable(table_name=table_name)

# my_posts = [{"title": "title of post 1", "content": "content of post 1"}, {"title": "title of post 2", "content": "content of post 2 "}]

# for post in my_posts:
#     db.insert_data(table_name=table_name, data=post)

# def find_post(id):
#     for p in my_posts:
#         if p["id"] == id:
#             return p
