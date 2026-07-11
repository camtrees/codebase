###############################################################################
## Program  : execute_query.py
##
## Purpose  : Execute an SQL query
##
## Requires : psycopg2 - PostgreSQL database adapter
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-04-23 Initial Version
##            2026-06-11 Now using Neon CAMorg 'camtrees' database as the master
##            2026-07-11 Use .env file to load database connection parameters
###############################################################################

import psycopg2

from dotenv import load_dotenv
import os

def execute_query(query, params=None):
    """
    Executes a single SQL query and returns the results.
    """

    # ------------------------------------------------------------------------------------------
    # Get NEON.COM Database connection parameters
    # ------------------------------------------------------------------------------------------
    # load .env into environment
    load_dotenv()

    # Get database connection parameters from .env
    DB_HOST     = os.getenv("DB_HOST_WRITE")
    DB_NAME     = os.getenv("DB_NAME")
    DB_USER     = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT     = os.getenv("DB_PORT")

    conn    = None
    cur     = None
    results = None

    try:
        # ------------------------------------------------------------------------------------------
        # Establish the connection
        # ------------------------------------------------------------------------------------------
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )

        # ------------------------------------------------------------------------------------------
        # Create a cursor object
        # ------------------------------------------------------------------------------------------
        cur = conn.cursor()

        # ------------------------------------------------------------------------------------------
        # Execute the query, using parameters safely to prevent SQL injection
        # ------------------------------------------------------------------------------------------
        cur.execute(query, params)

        # ------------------------------------------------------------------------------------------
        # If it's a SELECT query, fetch the results. Else get the number of rows updated.
        # ------------------------------------------------------------------------------------------
        if cur.description:
            results = cur.fetchall()
        else:
            results = cur.rowcount

        # ------------------------------------------------------------------------------------------
        # Commit the transaction - must also commit SELECT (since using a function to update tables)
        # ------------------------------------------------------------------------------------------
        conn.commit()
        cur.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()  # Roll back in case of error

    finally:
        # ------------------------------------------------------------------------------------------
        # Close the cursor and connection
        # ------------------------------------------------------------------------------------------
        if cur:
            cur.close()
        if conn:
            conn.close()

    return results
