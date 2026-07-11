###############################################################################
## Program  : epicollect_api.py
##
## Purpose  : EpiCollect API calls and functions
##
## Requires : pandas - EpiCollect results are in a Pandas DataFrame
##            pyepicollect - for reading EpiCollect 5 data
##            print_functions - to assist with printing
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-03-09 Initial Version
##            2026-06-06 <hkr> Allow for EpiCollect MAP_INDEX
###############################################################################

# Python libraries
import pandas as pd
import pyepicollect as pyep

# Kenster libraries
from env_read_write import *
from print_functions import *\


def epicollect_get_access_token(epicollect_attribs) -> str:
    """
    Validate our access_token. If it's not valid, get a new one.
    """

    # Read our current access_token from our .env file
    access_token = env_read_key(epicollect_attribs['ACCESS_TOKEN'])

    # # Read our current access_token from a local file.
    # file_path = epicollect_attribs['TOKEN_FILE']
    # try:
    #     # Open the file in read mode ('r' is the default)
    #     with open(file_path, 'r', encoding='utf-8') as file:
    #         # Read the entire content into a single string variable
    #         access_token = file.read()
    # except FileNotFoundError:
    #     print(f"Error: The file at {file_path} was not found.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    # Try using the access_token to see if it's valid
    project = pyep.api.get_project(epicollect_attribs['PROJECT_SLUG'], access_token)
    # If the project dict has an 'errors' key, our access_token is not valid
    key_to_check = 'errors'
    if key_to_check in project:
        # We need a new access_token
        print(f"\nWe need a new access_token...")
        access_token = epicollect_get_new_access_token(epicollect_attribs)
    else:
        print(f"\nOur current access_token is still valid...")

    return access_token


def epicollect_get_new_access_token(epicollect_attribs):
    """
    Get (and save) a new Epicollect access_token.
    """
    print('Getting a new access token...')
    new_access_token = pyep.auth.request_token(epicollect_attribs['CLIENT_ID'], epicollect_attribs['CLIENT_SECRET'])
    access_token = new_access_token['access_token']

    # Store the new access_token in our .env file
    success = env_write_key(epicollect_attribs['ACCESS_TOKEN'], access_token)
    if success:
        print(f"Key={epicollect_attribs['ACCESS_TOKEN']} saved successfully!")

    return access_token


def epicollect_print_detailed_project_info(epicollect_attribs, access_token):
    #-----------------------------------------------------------------------------------------
    # Get EpiCollect detailed Project Info (forms, mapping, stats)
    #-----------------------------------------------------------------------------------------
    project = pyep.api.get_project(epicollect_attribs['PROJECT_SLUG'], access_token)
    my_pretty_print(project)


def epicollect_print_project_info(epicollect_attribs):
    """
    Get EpiCollect project info.
    """
    project = pyep.api.search_project(epicollect_attribs['PROJECT_NAME'])
    my_pretty_print(project)


def epicollect_get_project_data(epicollect_attribs, access_token):
    #-----------------------------------------------------------------------------------------
    # Gets the first 50 data entries
    #
    # Note: EpiCollect paginates returned data with 50 (by default) records per page.
    #       We could specify upp to 1000 entries per page.
    #       But lets leave it at 50 so we know how to step through multiple pages.
    #-----------------------------------------------------------------------------------------
    entries = pyep.api.get_entries(
        epicollect_attribs['PROJECT_SLUG'],
        access_token,
        filter_by=epicollect_attribs['FILTER_BY'],
        filter_from=epicollect_attribs['FILTER_FROM'],
        filter_to=epicollect_attribs['FILTER_TO'],
        map_index=epicollect_attribs['MAP_INDEX'],
    )

    #-----------------------------------------------------------------------------------------
    # Show user total number of entries and number of pages
    #-----------------------------------------------------------------------------------------
    print('\n' + 'Number of EpiCollect entries: ' + str(entries['meta']['total']))
    print('Number of pages: ' + str(entries['meta']['last_page']) + '\n')
    data = entries['data']['entries']

    #-----------------------------------------------------------------------------------------
    # Collect the data for the first 50 records from the entries
    #-----------------------------------------------------------------------------------------
    data = entries['data']['entries']

    #-----------------------------------------------------------------------------------------
    # Get the rest of the data from the remaining pages (if any)
    #-----------------------------------------------------------------------------------------
    while entries['meta']['current_page'] < entries['meta']['last_page']:
        entries = pyep.api.get_entries(
            epicollect_attribs['PROJECT_SLUG'],
            access_token,
            filter_by=epicollect_attribs['FILTER_BY'],
            filter_from=epicollect_attribs['FILTER_FROM'],
            filter_to=epicollect_attribs['FILTER_TO'],
            map_index=epicollect_attribs['MAP_INDEX'],
            page=(entries['meta']['current_page'] + 1)
        )
        data = data + entries['data']['entries']

    return data


def zulu_to_eastern(df):
    """
    Convert the 'created_at' and 'uploaded_at' columns of a pandas dataframe to Eastern time zone.
    Also, keep only the date part of the 'created_at' column.
    """
    # Ensure the columns are a datetime object (Zulu 'Z' is automatically recognized as UTC)
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['uploaded_at'] = pd.to_datetime(df['uploaded_at'], utc=True)

    # Convert to Eastern Time and format as a date string
    # 'US/Eastern' handles both EST and EDT automatically
    df['created_at'] = df['created_at'].dt.tz_convert('US/Eastern').dt.strftime('%Y-%m-%d')
    df['uploaded_at'] = df['uploaded_at'].dt.tz_convert('US/Eastern') # Keep the time on this column

    return df
