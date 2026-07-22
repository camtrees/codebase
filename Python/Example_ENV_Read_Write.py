##########################################################################################
## File     : Example_ENV_Read_Write.py
##
## Purpose  : Example program to READ and WRITE Environment key values
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-07-11 Initial Version
##########################################################################################

from env_read_write import *

#------------------------------------------------------------------------------------------
# Read Env Key
#------------------------------------------------------------------------------------------
TEST_KEY_FOR_READING = env_read_key("TEST_KEY_FOR_READING")

print(TEST_KEY_FOR_READING)

#------------------------------------------------------------------------------------------
# Write Env Key
#------------------------------------------------------------------------------------------
success = env_write_key("TEST_KEY_FOR_WRITING", "WRITE")

if success:
    print("Key=TEST_KEY_FOR_WRITING saved successfully!")
