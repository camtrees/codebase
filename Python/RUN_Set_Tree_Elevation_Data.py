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
##            2026-09-04 Changes for using updated config.py and .env files
##            2026-09-04 Using psycopg (version 3) vs psycopg2
##########################################################################################

from pyhigh import get_elevation
import psycopg

# load globals from config.py file
from config import *


def main():
    with psycopg.connect(DB_HOST_WRITE) as conn:
        with conn.cursor() as cur:
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


if __name__ == "__main__":
    main()
