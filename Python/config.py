##########################################################################################
## File     : config.py
##
## Purpose  : Create non-private global variables and loads the .env secret globals
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-07-22 Initial Version
##            2026-07-22 Changes for using config.py file
##########################################################################################

import os
from dotenv import load_dotenv

# ------------------------------------------------------------------------------------------
# 1. Load the .env file into the operating system environment
# ------------------------------------------------------------------------------------------
load_dotenv()

#------------------------------------------------------------------------------------------
# Connect to the CAMTREES database? If not, connect to the KENSTER backup database.
#------------------------------------------------------------------------------------------
DB_CAMTREES = True

#------------------------------------------------------------------------------------------
# Set to true so we can import any of Kenster's EpiCollect data from TODAY!
#------------------------------------------------------------------------------------------
KR_TESTING = False

# ------------------------------------------------------------------------------------------
# Extract secret globals
# ------------------------------------------------------------------------------------------
CAMTREES_DB_HOST_WRITE = os.getenv("CAMTREES_DB_HOST_WRITE")
CAMTREES_DB_USER       = os.getenv("CAMTREES_DB_USER")
CAMTREES_DB_PASSWORD   = os.getenv("CAMTREES_DB_PASSWORD")

KENSTER_DB_HOST_WRITE  = os.getenv("KENSTER_DB_HOST_WRITE")
KENSTER_DB_USER        = os.getenv("KENSTER_DB_USER")
KENSTER_DB_PASSWORD    = os.getenv("KENSTER_DB_PASSWORD")

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

# ------------------------------------------------------------------------------------------
# SQL CAMTREES Database Connection Parameters
# ------------------------------------------------------------------------------------------
# Use DB_HOST_READ for READ ONLY access
CAMTREES_DB_HOST_READ = 'ep-purple-cloud-amjk21pv-pooler.c-5.us-east-1.aws.neon.tech'
# These parameters are the same for both READ ONLY and WRITE access
CAMTREES_DB_NAME      = 'camtrees'
CAMTREES_DB_PORT      = '5432'

# ------------------------------------------------------------------------------------------
# SQL KENSTER Database Connection Parameters
# ------------------------------------------------------------------------------------------
KENSTER_DB_HOST_READ = 'ep-morning-tree-ahrvmdic-pooler.c-3.us-east-1.aws.neon.tech'
# These parameters are the same for both READ ONLY and WRITE access
KENSTER_DB_NAME      = 'camtrees'
KENSTER_DB_PORT      = '5432'

# ------------------------------------------------------------------------------------------
# Set database globals based upon which database user selected to use (at top of this file)
# ------------------------------------------------------------------------------------------
if DB_CAMTREES == True:
    # Get CAMTREES master database connection parameters from .env
    DB_HOST_WRITE = CAMTREES_DB_HOST_WRITE
    DB_HOST_READ  = CAMTREES_DB_HOST_READ
    DB_NAME       = CAMTREES_DB_NAME
    DB_USER       = CAMTREES_DB_USER
    DB_PASSWORD   = CAMTREES_DB_PASSWORD
    DB_PORT       = CAMTREES_DB_PORT
else:
    # Get KENSTER backup database connection parameters from .env
    DB_HOST_WRITE = KENSTER_DB_HOST_WRITE
    DB_HOST_READ  = KENSTER_DB_HOST_READ
    DB_NAME       = KENSTER_DB_NAME
    DB_USER       = KENSTER_DB_USER
    DB_PASSWORD   = KENSTER_DB_PASSWORD
    DB_PORT       = KENSTER_DB_PORT
