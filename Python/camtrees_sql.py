###############################################################################
## Program  : camtrees_sql.py
##
## Purpose  : SQL routines for updating the CAMTREES database
##
## Requires : datetime to calculate date offsets from today
##            math to convert circumferance to diameter
##            pandas - EpiCollect results are in a Pandas DataFrame
##            execute_query - executes SQL queries on our CAMTREES database
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-04-24 <hkr> Initial Version
##          : 2026-05-16 <hkr> Changes required to process WildTACF trees
##          : 2026-06-13 <hkr> Removed location_note column from SQL tree table
##          : 2026-07-11 <hkr> Add return statements at end of all functions
##                             even if there is an earlier return
###############################################################################

# Python libraries
from   datetime import date, timedelta
import math
import pandas as pd

# Kenster libraries
from execute_query import execute_query


def check_for_care_actions(row, record_type, site, tree_number):
    """
    If there are care_actions available, add them to the SQL 'tree_care_action' table.
    """
    if record_type == 'ALL':
        # Set min and max to include ALL trees at the given site
        tree_number_min = '000'
        tree_number_max = '999'
    else:
        # Set min and max to include just ONE tree at the given site
        tree_number_min = tree_number
        tree_number_max = tree_number

    if row.Water and row.Water[0] == 'Yes':
        print('***** Processing a Water care action')
        sql_camtrees_add_care_action(record_type, 'Water',     tree_number_min, tree_number_max, row.created_at, row.created_by, site, row.Note)
    if row.Weed and row.Weed[0] == 'Yes':
        print('***** Processing a Weed care action')
        sql_camtrees_add_care_action(record_type, 'Weed',      tree_number_min, tree_number_max, row.created_at, row.created_by, site, row.Note)
    if row.Fertilize and row.Fertilize[0] == 'Yes':
        print('***** Processing a Fertilize care action')
        sql_camtrees_add_care_action(record_type, 'Fertilize', tree_number_min, tree_number_max, row.created_at, row.created_by, site, row.Note)
    if row.Prune and row.Prune[0] == 'Yes':
        print('***** Processing a Prune care action')
        sql_camtrees_add_care_action(record_type, 'Prune',     tree_number_min, tree_number_max, row.created_at, row.created_by, site, row.Note)

    return  ## END FUNCTION: check_for_care_actions


def check_for_tree_photos(row, record_type, site, tree_number):
    """
    If there are tree photos available, add them to the SQL 'tree_photos' table.
    """
    if row.Tree_Photo != 'NULL':
        sql_camtrees_add_tree_photo(record_type, site, tree_number, row.created_at, row.created_by, row.Tree_Photo)
    if row.Tree_Photo2 != 'NULL':
        sql_camtrees_add_tree_photo(record_type, site, tree_number, row.created_at, row.created_by, row.Tree_Photo2)

    return  ## END FUNCTION: check_for_tree_photos


def prepare_string_for_sql(data):
    """
    1. Strip spaces.
    2. Replace single quotes with side-by-side single quotes ('').
    3. If empty string set to 'NULL'.
    """
    def process_logic(val):
        if pd.isna(val) or str(val).strip() == "":
            return "NULL"

        # Strip spaces and change single quotes into two side-by-side single quotes
        return str(val).strip().replace("'", "''")

    if isinstance(data, pd.Series):
        # Apply the logic to every element in the column efficiently
        return data.map(process_logic)
    elif isinstance(data, str):
        # Directly apply the logic to the single string
        return process_logic(data)
    else:
        raise TypeError("Input must be a pandas Series or a string.")

    return  ## END FUNCTION: prepare_string_for_sql


def sql_camtrees_add_care_action(epicollect_record_type, care_action, tree_number_min, tree_number_max, action_date, created_by, site, note):
    """
    Add a care_action for tree(s) in one site or a list of sites.
    """
    # ------------------------------------------------------------------------------------------
    # Create SQL command
    # ------------------------------------------------------------------------------------------
    sql_command = f"""
        SELECT camtrees_add_care_action(
            p_epicollect_record_type => '{epicollect_record_type}' ,
            p_care_action_type       => '{care_action}' ,
            p_tree_number_min        => '{tree_number_min}' ,
            p_tree_number_max        => '{tree_number_max}' ,
            p_date                   => '{action_date}'  ,
            p_volunteer_email        => '{created_by}'  ,
            p_sites                  => '{site}' ,
            p_note                   => '{note}'
            );
        """
    print(f"\t SQL: {sql_command}")

    # ------------------------------------------------------------------------------------------
    # Execute the SQL command
    # ------------------------------------------------------------------------------------------
    updated_rows = execute_query(sql_command)
    print(f"\t +++++ Updated {updated_rows[0][0]} row(s) in the tree_care_action table.")

    return  ## END FUNCTION: sql_camtrees_add_care_action


def sql_camtrees_add_health_assessment(row, record_type, site, tree_number):
    """
    Add a health_assessment to the SQL 'tree_health_assessment' table.
    """
    blight        = prepare_string_for_sql(row.Blight)
    stump_sprouts = prepare_string_for_sql(row.Stump_Sprouts)

    # ------------------------------------------------------------------------------------------
    # Calculate the tree height
    # ------------------------------------------------------------------------------------------
    total_height_in_inches = 0
    if row.Height_Feet:
        total_height_in_inches = int(row.Height_Feet) * 12
    if row.Height_Inches:
        total_height_in_inches = total_height_in_inches + int(row.Height_Inches)
    if total_height_in_inches ==0:
        total_height_in_inches = 'NULL'

    # ------------------------------------------------------------------------------------------
    # Calculate the tree diameter
    # ------------------------------------------------------------------------------------------
    if row.Tree_DIAMETER:
        diameter_in_inches = row.Tree_DIAMETER
    elif row.Tree_CIRCUMFERENCE:
        diameter_in_inches = round(float(row.Tree_CIRCUMFERENCE) / math.pi, 2)
    else:
        diameter_in_inches = 'NULL'

    # ------------------------------------------------------------------------------------------
    # Special handling of catkins since it is a list
    # ------------------------------------------------------------------------------------------
    if not row.Catkins:
        catkins = 'NULL'
    elif row.Catkins[0] == 'Yes':
        catkins='Yes'
    else:
        catkins='No'

    # ------------------------------------------------------------------------------------------
    # Special handling of blossoms since it is a list
    # ------------------------------------------------------------------------------------------
    if not row.Blossoms:
        blossoms = 'NULL'
    elif row.Blossoms[0] == 'Yes':
        blossoms='Yes'
    else:
        blossoms='No'

    # ------------------------------------------------------------------------------------------
    # Create SQL command
    # ------------------------------------------------------------------------------------------
    sql_command = f"""
        select camtrees_add_health_assessment(
            p_epicollect_record_type => '{record_type}' ,
            p_site_name              => '{site}' ,
            p_tree_number            => '{tree_number}' ,
            p_date                   => '{row.created_at}' ,
            p_volunteer_email        => '{row.created_by}' ,
            p_health                 => '{row.Health}' ,
            p_height_in_inches       => '{total_height_in_inches}' ,
            p_diameter_in_inches     => '{diameter_in_inches}' ,
            p_blight                 => '{blight}' ,
            p_stump_sprouting        => '{stump_sprouts}' ,
            p_catkins                => '{catkins}' ,
            p_blossoms               => '{blossoms}' ,
            p_nuts                   => '{row.Nut_Production}' ,
            p_note                   => '{row.Note}'
            );
            """
    print(f"\t SQL: {sql_command}")

    # ------------------------------------------------------------------------------------------
    # Execute the SQL command
    # ------------------------------------------------------------------------------------------
    updated_row = execute_query(sql_command)
    print(f"\t +++++ Updated row {updated_row[0][0]} in the tree_health_assessment table.")

    return  ## END FUNCTION: sql_camtrees_add_health_assessment


def sql_camtrees_add_tree_initial_health(row, record_type, site, tree_number):
    """
    Add record to the tree_health_assessment table reporting the tree's health as 'good'.
    """
    # ------------------------------------------------------------------------------------------
    # Create SQL command
    # ------------------------------------------------------------------------------------------
    sql_command = f"""
        SELECT camtrees_add_tree_initial_health(
            p_epicollect_record_type => '{record_type}' ,
            p_site_name              => '{site}' ,
            p_tree_number            => '{tree_number}' ,
            p_date                   => '{row.created_at}' ,
            p_volunteer_email        => '{row.created_by}' ,
            p_health                 => 'good'
            );
        """
    print(f"\t SQL: {sql_command}")

    # ------------------------------------------------------------------------------------------
    # Execute the SQL command
    # ------------------------------------------------------------------------------------------
    updated_rows = execute_query(sql_command)
    print(f"\t +++++ Updated {updated_rows[0][0]} row(s) in the tree_health_assessment table.")

    return  ## END FUNCTION: sql_camtrees_add_care_action


def sql_camtrees_add_tree(row, record_type, site, tree_number):
    """
    Add a tree to the SQL 'tree' table.
    """
    mother_tree_other = prepare_string_for_sql(row.Mother_Tree_OTHER)
    father_tree_other = prepare_string_for_sql(row.Father_Tree_OTHER)
    parent_tree_note  = prepare_string_for_sql(row.Parent_Tree_Note)
    wire_fence        = prepare_string_for_sql(row.Wire_Fence)

    if record_type == 'PLANT':
        longitude = prepare_string_for_sql(str(row.Tree_Location_PLANT["longitude"]))
        latitude  = prepare_string_for_sql(str(row.Tree_Location_PLANT["latitude"]))
        access_path  = row.Access_Path_PLANT
        access_level = row.Access_Level_PLANT
        access_note  = row.Access_Note_PLANT
    elif record_type == 'WildCAM' or record_type == 'WildTACF':
        longitude = prepare_string_for_sql(str(row.Tree_Location_WILD["longitude"]))
        latitude  = prepare_string_for_sql(str(row.Tree_Location_WILD["latitude"]))
        access_path  = row.Access_Path_WILD
        access_level = row.Access_Level_WILD
        access_note  = row.Access_Note_WILD
    else:
        print(f"\t ***** ERROR *****: Invalid Record Type: record_type = {record_type}.")
        return

    if longitude == 'NULL' or latitude == 'NULL':
        # Set both longitude and latitude to NULL
        longitude  = 'NULL'
        latitude   = 'NULL'
        # Set gps_locked to False so we can update the GPS coordinates at a later time.
        gps_locked = 'false'
    else:
        # We will be setting the GPS coordinates now. Set gps_locked to True so we don't mistakenly replace the values later.
        gps_locked = 'true'

    # ------------------------------------------------------------------------------------------
    # Create SQL command
    # ------------------------------------------------------------------------------------------
    sql_command = f"""
        select camtrees_add_tree(
            p_epicollect_record_type => '{record_type}' ,
            p_site_name              => '{site}' ,
            p_tree_number            => '{tree_number}' ,
            p_date                   => '{row.created_at}' ,
            p_volunteer_email        => '{row.created_by}' ,
            p_longitude              => '{longitude}' ,
            p_latitude               => '{latitude}' ,
            p_gps_locked             => '{gps_locked}' ,
            p_access_path            => '{access_path}' ,
            p_access_level           => '{access_level}' ,
            p_access_note            => '{access_note}' ,
            p_planting_method        => '{row.Planting_Method}' ,
            p_wire_fence             => '{wire_fence}' ,
            p_mother_tree            => '{row.Mother_Tree}' ,
            p_mother_tree_other      => '{mother_tree_other}' ,
            p_father_tree            => '{row.Father_Tree}' ,
            p_father_tree_other      => '{father_tree_other}' ,
            p_parent_tree_note       => '{parent_tree_note}' ,
            p_note                   => '{row.Note}'
            );
            """
    print(f"\t SQL: {sql_command}")

    # ------------------------------------------------------------------------------------------
    # Execute the SQL command
    # ------------------------------------------------------------------------------------------
    tree_id = execute_query(sql_command)
    print(f"\t +++++ Added tree_id {tree_id[0][0]} to the 'tree' table.")

    return  ## END FUNCTION: sql_camtrees_add_tree


def sql_camtrees_add_tree_photo(record_type, site, tree_number, date, created_by, filename):
    """
    Add a tree_photo filename to the SQL tree_photo table.
    """
    if not sql_tree_exists(site, tree_number):
        print(f"\t ***** ERROR *****: Not sure how this could possibly happen, but, Tree number = '{tree_number}' DOES NOT exist.")
        return

    sql_command = f"""
        select camtrees_add_tree_photo(
            p_epicollect_record_type => '{record_type}' ,
            p_site_name              => '{site}' ,
            p_tree_number            => '{tree_number}' ,
            p_date                   => '{date}' ,
            p_volunteer_email        => '{created_by}' ,
            p_filename               => '{filename}'
            );
            """
    print(f"\t SQL: {sql_command}")

    # ------------------------------------------------------------------------------------------
    # Execute the SQL command
    # ------------------------------------------------------------------------------------------
    tree_photo_id = execute_query(sql_command)
    print(f"\t +++++ Added tree_photo_id {tree_photo_id[0][0]} to the 'tree_photo' table.")

    return  ## END FUNCTION: sql_camtrees_add_tree_photo


def sql_camtrees_get_distance_to_closest_wildcam_tree(longitude, latitude):
    """
    Does the tree already exist in the SQL 'tree' table?
    """
    sql_command = f"""
        SELECT * from camtrees_get_distance_to_closest_wildcam_tree(
            p_longitude => '{longitude}' ,
            p_latitude  => '{latitude}'
            );
        """
    result = execute_query(sql_command)[0] # result will be a tuple with (distance_in_feet, closest_tree_id, longitude, latitude)

    return result ## END FUNCTION: sql_tree_exists


def sql_get_epicollect_last_import_date(epicollect_project):
    """
    Set the EpiCollect FILTER_FROM date to one day later than the last time we processed EpiCollect data.
    """
    fetched_date = execute_query(f"SELECT date FROM epicollect_import_date WHERE epicollect_project = '{epicollect_project}';")
    filter_from = fetched_date[0][0] + timedelta(days=1) # One day later

    return filter_from ## END FUNCTION: sql_get_epicollect_last_import_date


def sql_gps_locked(site, tree_number):
    """
    Is the tree's gps location locked?
    """
    sql_command = f"""
        SELECT camtrees_tree_gps_locked(
            p_site_name   => '{site}' ,
            p_tree_number => '{tree_number}'
            );
        """
    rc = execute_query(sql_command)
    if rc[0][0]:
        return True ## END FUNCTION: sql_gps_locked
    else:
        return False ## END FUNCTION: sql_gps_locked

    return  ## END FUNCTION: sql_gps_locked


def sql_tree_exists(site, tree_number):
    """
    Does the tree already exist in the SQL 'tree' table?
    """
    sql_command = f"""
        SELECT camtrees_tree_exists(
            p_site_name   => '{site}' ,
            p_tree_number => '{tree_number}'
            );
        """
    rc = execute_query(sql_command)
    if rc[0][0]:
        return True ## END FUNCTION: sql_tree_exists
    else:
        return False ## END FUNCTION: sql_tree_exists

    return  ## END FUNCTION: sql_tree_exists


def sql_update_gps(site, tree_number, longitude, latitude, note):
    """
    Update GPS data for a tree in the SQL 'tree' table.
    """
    sql_command = f"""
        SELECT camtrees_update_tree_gps(
            p_site_name     => '{site}' ,
            p_tree_number   => '{tree_number}',
            p_longitude     => '{longitude}',
            p_latitude      => '{latitude}',
            p_access_note   => '{note}'
            );
        """
    rc = execute_query(sql_command)
    if rc[0][0]:
        print(f"\t +++++ Updated GPS data for tree number = '{tree_number}'.")
    else:
        print(f"\t ***** ERROR *****: Something went wrong. Unable to update GPS data for tree number = '{tree_number}'")

    return ## END FUNCTION: sql_update_gps

def sql_update_access_method(site, tree_number, access_method):
    """
    Update access_method for a tree in the SQL 'tree' table.
    """
    sql_command = f"""
        SELECT camtrees_update_access_method(
            p_site_name     => '{site}' ,
            p_tree_number   => '{tree_number}',
            p_access_method => '{access_method}'
            );
        """
    rc = execute_query(sql_command)
    if rc[0][0]:
        print(f"\t +++++ Updated access_method = '{access_method}' for tree number = '{tree_number}'.")
    else:
        print(f"\t ***** ERROR *****: Something went wrong. Unable to update access_method for tree number = '{tree_number}'")

    return  ## END FUNCTION: sql_update_access_method

def sql_update_tree_form(site, tree_number, tree_form):
    """
    Update tree_form for a tree in the SQL 'tree' table.
    """
    sql_command = f"""
        SELECT camtrees_update_tree_form(
            p_site_name     => '{site}' ,
            p_tree_number   => '{tree_number}',
            p_tree_form     => '{tree_form}'
            );
        """
    rc = execute_query(sql_command)
    if rc[0][0]:
        print(f"\t +++++ Updated tree_form = '{tree_form}' for tree number = '{tree_number}'.")
    else:
        print(f"\t ***** ERROR *****: Something went wrong. Unable to update tree_form for tree number = '{tree_number}'")

    return  ## END FUNCTION: sql_update_tree_form
