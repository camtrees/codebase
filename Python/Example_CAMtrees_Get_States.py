##########################################################################################
## Program  : Example_CAMtrees_Get_States.py
##
## Purpose  : Test program - access the state table
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-03-05 Initial Version
##            2026-06-11 Now using Neon CAMorg 'camtrees' database as the master
##            2026-07-09 Use .env file to load database connection parameters
##########################################################################################

import psycopg2

from dotenv import load_dotenv
import os

# load .env into environment
load_dotenv()

# Get database connection parameters from .env
DB_HOST     = os.getenv("DB_HOST_READ")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT     = os.getenv("DB_PORT")

conn = None
cur = None

try:
    # Establish the connection
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    # Create a cursor object
    cur = conn.cursor()

    # Execute a simple query
    cur.execute("SELECT version();")

    # Fetch the result
    db_version = cur.fetchone()
    print(f"PostgreSQL database version: {db_version[0]}")

    # Example: Querying data
    # get the state table
    cur.execute("SELECT code, name FROM state ORDER BY name ASC;")
    # get Kimski's 9 trees (site_id = 23)
    # cur.execute("SELECT id, longitude, latitude FROM tree WHERE site_id = 23 ORDER BY id;")
    rows = cur.fetchall()
    print("\nStates:")
    for row in rows:
        print(row)

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL database: {e}")

finally:
    # Close the cursor and connection
    if cur:
        cur.close()
    if conn:
        conn.close()
    print("\nDatabase connection closed.")
