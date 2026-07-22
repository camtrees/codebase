##########################################################################################
## Program  : RUN_Set_Tree_Elevation_Data.py
##
## Purpose  : Update elevation_in_feet for trees with a NULL value.
##
## Note     : Gets data from the USGS
##
## Requires : pyhigh Python Package
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-03-05 Initial Version
##            2026-06-11 Now using Neon CAMorg 'camtrees' database as the master
##            2026-07-09 Use .env file to load database connection parameters
##            2026-07-20 Add capability to use either the Neon CAMTREES master
##                       database or the KENSTER backup database
##            2026-07-22 Changes for using config.py file
##########################################################################################

from pyhigh import get_elevation
import psycopg2

# load globals from config.py file
from config import *


def main():
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(host=DB_HOST_WRITE, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()

        # Select trees with NULL elevation
        ## get list of trees where gps coordinates are provided and elevation is missing (NULL)
        cur.execute("SELECT id, site_id, number, longitude, latitude FROM tree WHERE elevation_in_feet IS NULL AND longitude IS NOT NULL AND latitude IS NOT NULL;")
        # FOR TESTING - get Kim Colson's trees (site_id=23)
        # cur.execute("SELECT id, number, longitude, latitude FROM tree WHERE site_id = 23 ORDER BY number;")
        trees_to_update = cur.fetchall()

        if not trees_to_update:
            print(f"\n######################################################################"
                  f"\n## No trees found with NULL elevation and gps coordinates provided. ##"
                  f"\n######################################################################")
            return

        print(f"\n###########################################################################"
              f"\n## Found {len(trees_to_update)} trees with with NULL elevation and gps coordinates provided. ##"
              f"\n###########################################################################")

        trees_updated = 0
        for tree_id, site_id, tree_number, longitude, latitude in trees_to_update:
            print(f"Processing tree ID: {tree_id} (Site ID: {site_id}, Tree Number: {tree_number}, Longitude: {longitude}, Latitude: {latitude})")
            elevation = get_elevation(lat=latitude, lon=longitude) * 3.280839895 # We want elevation in Feet!
            # FOR TESTING
            # elevation = get_elevation(lat=0, lon=0)

            if elevation > -1:
                # Update the tree's elevation
                cur.execute("UPDATE tree SET elevation_in_feet = %s WHERE id = %s;", (float(elevation), tree_id))
                print(f"Updated Tree ID: {tree_id} (Site ID: {site_id}, Tree Number: {tree_number}, Longitude: {longitude}, Latitude: {latitude}) with Elevation: {elevation}")
                conn.commit()
                trees_updated += 1
            else:
                print(f"Skipping Update for tree ID: {tree_id} tree_number {tree_number}, (Longitude: {longitude}, Latitude: {latitude}) with elevation: {elevation} Feet")

        print(f"\n{trees_updated} trees' elevation data has been successfully updated.")

    except Exception as error:
        print(f"\n#######################################################"
              f"\n## Elevation Lookup Halted! An error occurred: {error}"
              f"\n#######################################################")

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()
