##########################################################################################
## File     : config.py
##
## Purpose  : Create non-private global variables and loads the .env secret globals
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-07-22 Initial Version
##            2026-07-22 Changes for using config.py file
##            2026-09-04 Move some globals to .env file
##########################################################################################

import os
from dotenv import load_dotenv

# ------------------------------------------------------------------------------------------
# 1. Load the .env file into the operating system environment
# ------------------------------------------------------------------------------------------
load_dotenv()

#------------------------------------------------------------------------------------------
# Set to true so we can import any of Kenster's EpiCollect data from TODAY!
#------------------------------------------------------------------------------------------
KR_TESTING = False

#------------------------------------------------------------------------------------------
# Connect to the CAMTREES database? If not, connect to the KENSTER backup database.
#------------------------------------------------------------------------------------------
USE_CAMTREES_DATABASE = False

# ------------------------------------------------------------------------------------------
# Extract secret database globals based upon which database user selected to use
# ------------------------------------------------------------------------------------------
if USE_CAMTREES_DATABASE == True:
    # Get CAMTREES master database connection parameters from .env
    DB_HOST_WRITE = os.getenv("CAMTREES_WRITE_URL")
    DB_HOST_READ  = os.getenv("CAMTREES_READ_URL")
else:
    # Get KENSTER backup database connection parameters from .env
    DB_HOST_WRITE = os.getenv("KENSTER_WRITE_URL")
    DB_HOST_READ  = os.getenv("KENSTER_READ_URL")


MAINT_CLIENT_SECRET    = os.getenv("MAINT_CLIENT_SECRET")

RAIN_CLIENT_SECRET     = os.getenv("RAIN_CLIENT_SECRET")


# ------------------------------------------------------------------------------------------
# Following groups define non-secret globals
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# EpiCollect CAM TREE MAINTENANCE project "API" and "Apps" data from project dashboard
# ------------------------------------------------------------------------------------------
MAINT_CLIENT_ID     = '7568'
MAINT_PROJECT_NAME  = 'CAM_Tree_Maintenance'
MAINT_PROJECT_SLUG  = 'cam-tree-maintenance'
# ------------------------------------------------------------------------------------------
# EpiCollect CAM TREE RAIN EVENT project "API" and "Apps" data from project dashboard
# ------------------------------------------------------------------------------------------
RAIN_CLIENT_ID     = '7571'
RAIN_PROJECT_NAME  = 'CAM_Tree_Rain_Event'
RAIN_PROJECT_SLUG  = 'cam-tree-rain-event'


