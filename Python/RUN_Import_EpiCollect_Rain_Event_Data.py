###############################################################################
## Program  : RUN_Import_EpiCollect_Rain_Event_Data.py
##
## Purpose  : Get EpiCollect Rain Event data not yet processed
##
## Requires : datetime to calculate date offsets from today
##            pandas - so EpiCollect results can be placed into a Pandas DataFrame
##            tabulate - prints the Pandas DataFrame
##            camtrees_sql - to access CAMTREES PostgreSQL database
##            epicollect_api - our functions for interacting with EpiCollect
##            execute_query - executes SQL queries on our CAMTREES database
##            print_functions - assists with printing
##            sys - in case we want to call sys.exit()
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-04-20 Initial Version
##            2026-05-07 Change EpiCollect 'Notes' filed to 'Note'
##            2026-06-06 <hkr> Allow for EpiCollect MAP_INDEX
##            2026-07-09 Use .env file to load EpiCollect access tokens
##            2026-07-20 Add capability to use either the Neon CAMTREES master
##                       database or the KENSTER backup database
###############################################################################

# Python libraries
from datetime import date, timedelta
import pandas
from tabulate import tabulate

# Kenster libraries
from camtrees_sql import *
from epicollect_api import *
from execute_query import execute_query
from print_functions import *

from dotenv import load_dotenv
import os

# import sys
# sys.exit()

#------------------------------------------------------------------------------------------
# Set to true so we can import EpiCollect data from TODAY!
#------------------------------------------------------------------------------------------
KR_TESTING = False

#------------------------------------------------------------------------------------------
# Connect to the CAMTREES database? If not, connect to the KENSTER backup database.
#------------------------------------------------------------------------------------------
DB_CAMTREES = True

#------------------------------------------------------------------------------------------
# From which EpiCollect (rain or maint) Project will we process records
#------------------------------------------------------------------------------------------
EPICOLLECT_PROJECT = 'rain'


def initialize_python_library_settings():
    """
    Set vars used with python libraries.
    """
    #------------------------------------------------------------------------------------------
    # Set Pandas to Print all columns
    #------------------------------------------------------------------------------------------
    pd.set_option('display.max_columns', None)


def epicollect_configure_attribs(filter_from, filter_to):
    """
    Define EpiCollect attributes needed to access the EpiCollect private project data.
    """
    # load .env into environment
    load_dotenv()

    epicollect_attribs = {
        # ------------------------------------------------------------------------------------------
        # Get EpiCollect project access tokens
        # ------------------------------------------------------------------------------------------
        'CLIENT_ID'     : os.getenv("RAIN_CLIENT_ID"),
        'CLIENT_SECRET' : os.getenv("RAIN_CLIENT_SECRET"),
        'PROJECT_NAME'  : os.getenv("RAIN_PROJECT_NAME"),
        'PROJECT_SLUG'  : os.getenv("RAIN_PROJECT_SLUG"),
        # ------------------------------------------------------------------------------------------
        # These are user specified to control which records will be returned
        # ------------------------------------------------------------------------------------------
        'FILTER_BY'     : 'uploaded_at',
        'FILTER_FROM'   : filter_from,
        'FILTER_TO'     : filter_to,
        'MAP_INDEX'     : 3,
        # ------------------------------------------------------------------------------------------
        # File that stores our access_token
        # ------------------------------------------------------------------------------------------
        'ACCESS_TOKEN'  : 'RAIN_ACCESS_TOKEN'
        }

    print(f"\nFILTER_BY   : {epicollect_attribs['FILTER_BY']}"
          f"\nFILTER_FROM : {epicollect_attribs['FILTER_FROM']}"
          f"\nFILTER_TO   : {epicollect_attribs['FILTER_TO']}")
    return epicollect_attribs


def epicollect_process_data(data):
    """
    Process the EpiCollect private project data.
    """
    #------------------------------------------------------------------------------------------
    # Put the EpiCollect data into a Pandas DataFrame
    #------------------------------------------------------------------------------------------
    df = pd.DataFrame(data)

    #------------------------------------------------------------------------------------------
    # If Kenster is testing, keep only data created by him
    #------------------------------------------------------------------------------------------
    if KR_TESTING:
        df.drop(df[df['created_by'] != 'ken.rosenberry@gmail.com'].index, inplace=True)

    #------------------------------------------------------------------------------------------
    # Sort the DataFrame by the 'created_at' column (before we convert it into just a date)
    #------------------------------------------------------------------------------------------
    df.sort_values(by='created_at', ascending=True, inplace=True)

    #------------------------------------------------------------------------------------------
    # Print the sorted DataFrame before any modifications
    #------------------------------------------------------------------------------------------
    print(tabulate(df, headers='keys', tablefmt='psql'))

    # ------------------------------------------------------------------------------------------
    # Convert Zulu datetime values to a Eastern
    # ------------------------------------------------------------------------------------------
    df = zulu_to_eastern(df)

    # ------------------------------------------------------------------------------------------
    # Prepare strings entered by EpiCollect volunteers for SQL
    # 1. Strip spaces.
    # 2. Replace single quotes with side-by-side single quotes ('').
    # 3. If empty string set to 'NULL'.
    # ------------------------------------------------------------------------------------------
    df['Note'] = prepare_string_for_sql(df['Note'])

    #------------------------------------------------------------------------------------------
    # Print the DataFrame after column string modification
    #------------------------------------------------------------------------------------------
    print(tabulate(df, headers='keys', tablefmt='psql'))

    #------------------------------------------------------------------------------------------
    # Iterate through the EpiCollect records using itertuples()
    #------------------------------------------------------------------------------------------
    for row in df.itertuples():
        match row.selectBY:
            case 'Site':
                process_epicollect_site_record(row)
            case 'Hub':
                process_epicollect_hub_record(row)
            case _:
                print_with_separator_line(f"Ignoring EpiCollect entry with UNKNOWN record type. selectBy = {row.selectBY}")


def process_epicollect_site_record(row):
    """
    Process a SITE Epicollect record.
    """
    if "TEST - Choose this when testing the EpiCollect App" in row.rainSites:
        print_with_separator_line(f"Ignoring EpiCollect TEST entry for Sites: {row.rainSites}")
        return

    print_with_separator_line(
        f"Processing EpiCollect SITE Record {row.Index}..."
        f"\n\t Sites: {row.rainSites}"
    )

    for rainSite in row.rainSites:
        # ------------------------------------------------------------------------------------------
        # Split the rainSite into cam_org and site
        # ------------------------------------------------------------------------------------------
        cam_org, site = rainSite.split(' - ', 1)
        site = prepare_string_for_sql(site)

        print(f"Processing Site: {site}")

        # ------------------------------------------------------------------------------------------
        # Add water event via SQL
        # ------------------------------------------------------------------------------------------
        sql_camtrees_add_care_action('rain', 'water', '001', '999', row.rainDate, row.created_by, site, row.Note)
    return


def process_epicollect_hub_record(row):
    """
    Process a HUB Epicollect record.
    """
    if "TEST - Choose this when testing the EpiCollect App" in row.rainHubs:
        print_with_separator_line(f"Ignoring EpiCollect TEST entry for Hubs: {row.rainHubs}")
        return

    print_with_separator_line(
        f"Processing EpiCollect HUB Record {row.Index}..."
        f"\n\t Hubs: {row.rainHubs}"
    )
    for rainHub in row.rainHubs:
        rainHub = prepare_string_for_sql(rainHub)
        # ------------------------------------------------------------------------------------------
        # Get the Sites linked to a given Hub
        # ------------------------------------------------------------------------------------------
        sql_command = f"SELECT site from cam_sites_hubs where hub = '{rainHub}' ;"
        sites_in_hub = execute_query(sql_command)

        # ------------------------------------------------------------------------------------------
        # Convert sites_in_hub (a list of single-element tuples) into a comma-separated string
        # ------------------------------------------------------------------------------------------
        sites = ", ".join(item[0] for item in sites_in_hub)
        sites = prepare_string_for_sql(sites)

        # ------------------------------------------------------------------------------------------
        # Add water event via SQL
        # ------------------------------------------------------------------------------------------
        sql_camtrees_add_care_action('rain', 'water', '001', '999', row.rainDate, row.created_by, sites, row.Note)
    return


if __name__ == "__main__":
    # initialize_constants()
    initialize_python_library_settings()

    #------------------------------------------------------------------------------------------
    # Set EpiCollect FILTER_FROM and FILTER_TO dates
    #------------------------------------------------------------------------------------------
    if KR_TESTING:
        filter_from = date.today()  # Set to Today to allow testing of today's EpiCollect data
        filter_to   = date.today() + timedelta(days=1) # Tomorrow
    else:
        filter_from = sql_get_epicollect_last_import_date(EPICOLLECT_PROJECT)
        filter_to = date.today() - timedelta(days=1) # Yesterday

    #------------------------------------------------------------------------------------------
    # Set EpiCollect attributes needed to access the EpiCollect private project data
    #------------------------------------------------------------------------------------------
    epicollect_attribs = epicollect_configure_attribs(filter_from, filter_to)

    #------------------------------------------------------------------------------------------
    # Get our EpiCollect Access Token from a file. Get a new token if necessary.
    #------------------------------------------------------------------------------------------
    access_token = epicollect_get_access_token(epicollect_attribs)

    # epicollect_print_project_info(epicollect_attribs)
    # epicollect_print_detailed_project_info(epicollect_attribs, access_token)

    #------------------------------------------------------------------------------------------
    # Get the EpiCollect private project data
    #------------------------------------------------------------------------------------------
    data = epicollect_get_project_data(epicollect_attribs, access_token)
    if not data:
        print('No data to process')
    else:
        epicollect_process_data(data)

    #------------------------------------------------------------------------------------------
    # Save the date we last processed EpiCollect entries into the epicollect_import_date table
    #------------------------------------------------------------------------------------------
    if not KR_TESTING:
        # ------------------------------------------------------------------------------------------
        # The FILTER_TO date as a string - so we can at end of program update the date in SQL
        # ------------------------------------------------------------------------------------------
        filter_to_as_str = f"{filter_to.strftime('%Y-%m-%d')}"

        updated_rows = execute_query(f"UPDATE epicollect_import_date SET date = '{filter_to_as_str}' WHERE epicollect_project = '{EPICOLLECT_PROJECT}';")
        print(f"\n{LINE_SEP}")
        print(f"Updated {updated_rows} row(s) in the epicollect_import_date table.")
