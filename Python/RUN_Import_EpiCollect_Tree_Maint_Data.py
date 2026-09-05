###############################################################################
## Program  : RUN_Import_EpiCollect_Tree_Maint_Data.py
##
## Purpose  : Get EpiCollect Tree Maintenance data not yet processed
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
## Revised  : 2026-04-22 <hkr> Initial Version
##            2026-05-07 <hkr> Change from CAMWILD to WildCAM
##            2026-05-07 <hkr> Change from DENTATA to WildTACF
##            2026-05-07 <hkr> Change EpiCollect 'Notes' field to 'Note'
##            2026-05-16 <hkr> Changes required to process WildTACF trees
##            2026-06-06 <hkr> Allow for EpiCollect MAP_INDEX
##            2026-07-11 Use .env file to load EpiCollect access tokens
##            2026-07-22 Changes for using config.py file
###############################################################################

# Python libraries
from datetime import date, timedelta
import pandas as pd
from tabulate import tabulate

# load globals from config.py file
from config import *

# Kenster libraries
from camtrees_sql import *
from epicollect_api import *
from execute_query import execute_query
from print_functions import *

# import sys
# sys.exit()

#------------------------------------------------------------------------------------------
# From which EpiCollect (rain or maint) Project will we process records
#------------------------------------------------------------------------------------------
EPICOLLECT_PROJECT = 'maint'


def initialize_python_library_settings():
    """
    Set vars used with python libraries.
    """
    #------------------------------------------------------------------------------------------
    # Set Pandas to Print all columns
    #------------------------------------------------------------------------------------------
    pd.set_option('display.max_columns', None)

    return ## END FUNCTION: initialize_python_library_settings


def epicollect_configure_attribs(filter_from, filter_to):
    """
    Define EpiCollect attributes needed to access the EpiCollect private project data.
    """

    epicollect_attribs = {
        # ------------------------------------------------------------------------------------------
        # Get EpiCollect project access tokens
        # ------------------------------------------------------------------------------------------
        'CLIENT_ID'     : MAINT_CLIENT_ID,
        'CLIENT_SECRET' : MAINT_CLIENT_SECRET,
        'PROJECT_NAME'  : MAINT_PROJECT_NAME,
        'PROJECT_SLUG'  : MAINT_PROJECT_SLUG,
        # ------------------------------------------------------------------------------------------
        # These are user specified to control which records will be returned
        # ------------------------------------------------------------------------------------------
        'FILTER_BY'     : 'uploaded_at',
        'FILTER_FROM'   : filter_from,
        'FILTER_TO'     : filter_to,
        'MAP_INDEX'     : 1,
        # ------------------------------------------------------------------------------------------
        # File that stores our access_token
        # ------------------------------------------------------------------------------------------
        'TOKEN_FILE'    : 'epicollect_cam_tree_maintenance_access_token'
        }

    print(f"\nFILTER_BY   : {epicollect_attribs['FILTER_BY']}"
          f"\nFILTER_FROM : {epicollect_attribs['FILTER_FROM']}"
          f"\nFILTER_TO   : {epicollect_attribs['FILTER_TO']}")

    return epicollect_attribs ## END FUNCTION: epicollect_configure_attribs


def epicollect_process_data(data):
    """
    Process the EpiCollect private project data.
    """
    #------------------------------------------------------------------------------------------
    # Put the EpiCollect data into a Pandas DataFrame
    #------------------------------------------------------------------------------------------
    df = pd.DataFrame(data)

    #------------------------------------------------------------------------------------------
    # Print the DataFrame before any modifications
    #------------------------------------------------------------------------------------------
    print('\nThe DataFrame as received from EpiCollect...')
    print(tabulate(df, headers='keys', tablefmt='psql'))

    #------------------------------------------------------------------------------------------
    # If Kenster is testing, keep only data created by him
    #------------------------------------------------------------------------------------------
    if KR_TESTING:
        print('\nKenster is TESTING. The DataFrame with only Kenster data...')
        df.drop(df[df['created_by'] != 'ken.rosenberry@gmail.com'].index, inplace=True)
        print(tabulate(df, headers='keys', tablefmt='psql'))

    #------------------------------------------------------------------------------------------
    # Sort the DataFrame by the 'created_at' column (before we convert it into just a date)
    #------------------------------------------------------------------------------------------
    df.sort_values(by='created_at', ascending=True, inplace=True)

    #------------------------------------------------------------------------------------------
    # Print the sorted DataFrame
    #------------------------------------------------------------------------------------------
    print("\nThe DataFrame sorted by the 'created_at' column...")
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
    df['Access_Note_WILD']  = prepare_string_for_sql(df['Access_Note_WILD'])
    df['Access_Note_PLANT'] = prepare_string_for_sql(df['Access_Note_PLANT'])
    df['Tree_Form']         = prepare_string_for_sql(df['Tree_Form'])
    df['Access_Method_ONE'] = prepare_string_for_sql(df['Access_Method_ONE'])
    df['Tree_Photo']        = prepare_string_for_sql(df['Tree_Photo'])
    df['Tree_Photo2']       = prepare_string_for_sql(df['Tree_Photo2'])
    df['Note']              = prepare_string_for_sql(df['Note'])

    # ------------------------------------------------------------------------------------------
    # Convert some data frame columns to upper case
    # ------------------------------------------------------------------------------------------
    df['WildTACF_Tree_ID'] = df['WildTACF_Tree_ID'].str.upper()

    #------------------------------------------------------------------------------------------
    # Print the DataFrame ready to be processed
    #------------------------------------------------------------------------------------------
    print('\nThe DataFrame NOW READY to be processed...')
    print(tabulate(df, headers='keys', tablefmt='psql'))

    #------------------------------------------------------------------------------------------
    # Iterate through the EpiCollect records using itertuples()
    #------------------------------------------------------------------------------------------
    for row in df.itertuples():
        # ------------------------------------------------------------------------------------------
        # Split the CAM_Org_Site into cam_org and site
        # ------------------------------------------------------------------------------------------
        cam_org, site = row.CAM_Org_Site.split(' - ', 1)
        site = prepare_string_for_sql(site)

        # ------------------------------------------------------------------------------------------
        # Skip EpiCollect TEST records
        # ------------------------------------------------------------------------------------------
        if cam_org == 'TEST':
            print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. cam_org = '{cam_org}', site = '{site}' ")
            print(f"\t ***** NOTE *****: Skipping EpiCollect TEST entry.")
            continue # Skip to next record

        # ------------------------------------------------------------------------------------------
        # Process the WildCAM, WildTACF, ALL, GPS, ONE, or PLANT EpiCollect record
        # ------------------------------------------------------------------------------------------
        match (cam_org, row.Record_Type):
            case (any_value, 'ALL'):
                process_epicollect_all(row, site)
            case (any_value, 'GPS'):
                process_epicollect_gps(row, site)
            case (any_value, 'ONE'):
                process_epicollect_one(row, site)
            case (any_value, 'PLANT'):
                process_epicollect_plant(row, site)
            case ('WildCAM', any_value):
                process_epicollect_wildcam(row, site)
            case ('WildTACF', any_value):
                process_epicollect_wildtacf(row, site)
            case _, _:
                print_with_separator_line(f"***** Skipping UNKNOWN EpiCollect record for cam_org = '{cam_org}' record_type = '{row.Record_Type}'")

    return ## END FUNCTION: epicollect_process_data


def process_epicollect_all(row, site):
    record_type = 'ALL'
    tree_number = 'NULL' # We don't use a tree_number when processing an EpiCollect ALL record.

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}'")

    check_for_care_actions(row, record_type, site, tree_number)

    return ## END FUNCTION: process_epicollect_all


def process_epicollect_gps(row, site):
    record_type = 'GPS'
    tree_number = prepare_string_for_sql(row.Tree_Number_GPS)
    longitude = prepare_string_for_sql(str(row.Tree_Location_GPS["longitude"]))
    latitude = prepare_string_for_sql(str(row.Tree_Location_GPS["latitude"]))

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}', tree_number = '{tree_number}', longitude = '{longitude}', latitude = '{latitude}'  ")

    if longitude == 'NULL' or latitude == 'NULL':
        print(f"\t ***** ERROR *****: Missing GPS data for tree number = '{tree_number}'.")
        return ## EARLY EXIT

    if not sql_tree_exists(site, tree_number):
        print(f"\t ***** ERROR *****: Tree number = '{tree_number}' DOES NOT exist.")
        return ## EARLY EXIT

    if sql_gps_locked(site, tree_number):
        print(f"\t ***** ERROR *****: GPS is 'locked' for tree number = '{tree_number}'.")
        return ## EARLY EXIT

    sql_update_gps(site, tree_number, longitude, latitude, row.Note)

    return ## END FUNCTION: process_epicollect_gps


def process_epicollect_one(row, site):
    record_type = 'ONE'
    tree_number = prepare_string_for_sql(row.Tree_Number_ONE)

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}' tree_number = '{tree_number}'")

    if not sql_tree_exists(site, tree_number):
        print(f"\t ***** ERROR *****: Tree number = '{tree_number}' DOES NOT exist.")
        return ## EARLY EXIT

    if row.Tree_Form != 'NULL':
        sql_update_tree_form(site, tree_number, row.Tree_Form)
    else:
        print(f"\t***** Ignoring a NULL tree_form for tree number = '{tree_number}'.")

    if row.Access_Method_ONE != 'NULL':
        sql_update_access_method(site, tree_number, row.Access_Method_ONE)
    else:
        print(f"\t***** Ignoring a NULL access_method for tree number = '{tree_number}'.")

    sql_camtrees_add_health_assessment(row, record_type, site, tree_number)

    check_for_care_actions(row, record_type, site, tree_number)

    check_for_tree_photos(row, record_type, site, tree_number)

    return ## END FUNCTION: process_epicollect_one


def process_epicollect_plant(row, site):
    record_type = 'PLANT'
    tree_number = prepare_string_for_sql(row.Tree_Number_PLANT)

    longitude = prepare_string_for_sql(str(row.Tree_Location_PLANT["longitude"]))
    latitude = prepare_string_for_sql(str(row.Tree_Location_PLANT["latitude"]))

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}', tree_number = '{tree_number}', longitude = '{longitude}', latitude = '{latitude}'")

    if sql_tree_exists(site, tree_number):
        print(f"\t ***** ERROR *****: Tree number = '{tree_number}' at Site = '{site}' ALREADY exists.")
        return ## EARLY EXIT

    sql_camtrees_add_tree(row, record_type, site, tree_number)

    sql_camtrees_add_tree_initial_health(row, record_type, site, tree_number)

    check_for_care_actions(row, record_type, site, tree_number)

    check_for_tree_photos(row, record_type, site, tree_number)

    return ## END FUNCTION: process_epicollect_plant


def process_epicollect_wildcam(row, site):
    record_type = 'WildCAM'
    longitude = prepare_string_for_sql(str(row.Tree_Location_WILD["longitude"]))
    latitude = prepare_string_for_sql(str(row.Tree_Location_WILD["latitude"]))

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}', longitude = '{longitude}', latitude = '{latitude}' ")

    # ------------------------------------------------------------------------------------------
    # Skip EpiCollect Wild TEST record
    # ------------------------------------------------------------------------------------------
    if row.LIVE_or_TEST_WILD == 'TEST':
        print(f"\t ***** NOTE *****: Skipping EpiCollect WildCAM TEST entry.")
        return

    if longitude == 'NULL' or latitude == 'NULL':
        print(f"\t ERROR *****: Missing GPS data for WildCAM tree. Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}', longitude = '{longitude}', latitude = '{latitude}' ")
        return ## EARLY EXIT

    # Calculate distance to closest WildCAM tree
    distance, tree_id, wildcam_longitude, wildcam_latitude = sql_camtrees_get_distance_to_closest_wildcam_tree(longitude, latitude)
    if distance <= 50:
        # EpiCollect tree considered to be same as an existing tree
        tree_number = prepare_string_for_sql(f"{wildcam_longitude} {wildcam_latitude}")
        print(f"\t ***** NOTE *****: {record_type} tree '{tree_number}' considered to be same tree as tree_id: {tree_id} since the distance between the two is: {distance} feet. Will continue processing the record.")
    else:
        # EpiCollect tree considered to be a new tree
        tree_number = prepare_string_for_sql(f"{longitude} {latitude}")
        print(f"\t ***** NOTE *****: {record_type} tree '{tree_number}' does not exist and is not closer than 50 feet to an existing WildCAM tree. Will add the new tree and continue processing the record.")
        sql_camtrees_add_tree(row, record_type, site, tree_number)

    sql_camtrees_add_health_assessment(row, record_type, site, tree_number)

    check_for_care_actions(row, record_type, site, tree_number)

    check_for_tree_photos(row, record_type, site, tree_number)

    return  ## END FUNCTION: process_epicollect_wildcam


def process_epicollect_wildtacf(row, site):
    record_type = 'WildTACF'

    tree_number = prepare_string_for_sql(row.WildTACF_Tree_ID)

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}', tree_number = '{tree_number}' ")

    # ------------------------------------------------------------------------------------------
    # Skip EpiCollect Wild TEST record
    # ------------------------------------------------------------------------------------------
    if row.LIVE_or_TEST_WILD == 'TEST':
        print(f"\t ***** NOTE *****: Skipping EpiCollect WildTACF TEST entry.")
        return

    if sql_tree_exists(site, tree_number):
        print(f"\t ***** NOTE *****: {record_type} tree '{tree_number}' ALREADY exists. Will continue processing the record.")
    else:
        print(f"\t ***** NOTE *****: {record_type} tree '{tree_number}' does not exist. Will add it and then continue processing the record.")
        sql_camtrees_add_tree(row, record_type, site, tree_number)

    sql_camtrees_add_health_assessment(row, record_type, site, tree_number)

    check_for_care_actions(row, record_type, site, tree_number)

    check_for_tree_photos(row, record_type, site, tree_number)

    return  ## END FUNCTION: process_epicollect_wildtacf


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
        print('***** No data to process')
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
        print(f"***** Updated {updated_rows} row(s) in the epicollect_import_date table.")
