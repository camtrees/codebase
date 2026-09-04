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
##            2026-07-20 Add capability to use either the Neon CAMTREES master
##                       database or the KENSTER backup database
##            2026-07-22 Changes for using config.py file
###############################################################################

import psycopg

# load globals from config.py file
from config import *

def execute_query(query, params=None):
    """
    Executes a single SQL query and returns the results.
    """

    results = None

    # ------------------------------------------------------------------------------------------
    # Establish the connection
    # ------------------------------------------------------------------------------------------
    with psycopg.connect(DB_HOST_WRITE) as conn:
        with conn.cursor() as cur:
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

    return results
