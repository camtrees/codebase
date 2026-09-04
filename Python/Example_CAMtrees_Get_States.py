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
##            2026-09-04 Changes for using updated config.py and .env files
##            2026-09-04 Using psycopg (version 3) vs psycopg2
##########################################################################################

# load globals from config.py file
from config import *

import psycopg

def main():
    # Establish the connection
    with psycopg.connect(DB_HOST_READ) as conn:
        with conn.cursor() as cur:
            # Execute a simple query
            cur.execute("SELECT version();")

            # Fetch the result
            db_version = cur.fetchone()
            print(f"PostgreSQL database version: {db_version[0]}")

            # Example: Querying data
            # get the state table
            cur.execute("SELECT code, name FROM state ORDER BY name ASC;")
            # get Kimski's trees (site_id = 23)
            # cur.execute("SELECT id, longitude, latitude FROM tree WHERE site_id = 23 ORDER BY id;")
            rows = cur.fetchall()
            print("\nStates:")
            for row in rows:
                print(row)

if __name__ == "__main__":
    main()
