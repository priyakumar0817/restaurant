"""
Priya Senthilkumar, ECE 140A Winter 2023
Technical Assignment 6 - Challenge 1
Python file to initialize our database with the current menu items
"""
# Add the necessary imports
import mysql.connector as mysql
import os
from dotenv import load_dotenv
# Ensure we can open our database
load_dotenv("credentials.env")

# Read Database connection variables
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']

# Connect to the db and create a cursor object
db = mysql.connect(user=db_user, password=db_pass, host=db_host)
cursor = db.cursor()
# Create TechAssignment6 database and needed tables
cursor.execute("CREATE DATABASE if not exists TechAssignment6;")
cursor.execute("USE TechAssignment6;")
cursor.execute("drop table if exists Menu_Items;")
cursor.execute("drop table if exists Orders;")
# ensure the creation was successful or return error
try:
    cursor.execute("""
    CREATE TABLE Menu_Items (
       item_id         integer  AUTO_INCREMENT PRIMARY KEY,
       name            VARCHAR(100) NOT NULL, 
       price            DECIMAL(10,3) NOT NULL
   );
 """)
except RuntimeError as err:
    print("runtime error: {0}".format(err))

try:
    cursor.execute("""
   CREATE TABLE Orders (
       order_id         integer  AUTO_INCREMENT PRIMARY KEY,
       item_id          INT NOT NULL,
       name             VARCHAR(100) NOT NULL, 
       quantity         INT NOT NULL,
       status           VARCHAR(8) NOT NULL,
       FOREIGN KEY(item_id) REFERENCES Menu_Items(item_id)
   );
 """)
except RuntimeError as err:
    print("runtime error: {0}".format(err))

query = "insert into Menu_Items (name, price) values (%s, %s)"
values = [
    ('Hamburger', 5),
    ('Fries', 3),
    ('Soda', 1),
    ('Hotdog', 2),
    ('Pizza', 3),

]
# execute all menu items and commit to database
cursor.executemany(query, values)
db.commit()
db.close()
