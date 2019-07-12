#!/bin/sh

# A simple shell script to setup and run the 'Harvest 2 Clockify' converter
# 

# Needs Harvest Information
#
# This is the company you are under in harvest, it shows up
# in the URL for the harvest website and is used to fill that
# in. (Harvest URL: 'https://COMPANY_NAME.harvestapp.com')
export H2C_HARVEST_COMPANY_NAME=""

# This is the email address used to sign into harvest
export H2C_HARVEST_EMAIL=""

# This is the password used to sign into harvest
# This will be updated to use a more secure authentication method 
# in the future
export H2C_HARVEST_PASSWORD=""


# Needs Clockify Information
#
# This is the time you begin your work day and will be the start time
# used in the clockify timer (24 hour clock, formatted as: HH:MM:SS)
export H2C_CLOCKIFY_START_TIME=""

# This is the API key that can be generated on the clokcify website
# found at the bottom of the page here: 'https://clockify.me/user/settings'
export H2C_CLOCKIFY_API_KEY=""

# This is the name of the clockify project to put the time under
export H2C_CLOCKIFY_PROJECT_NAME=""



# Run the H2C program (should be located in the same directory as this file)
python3 "HarvestToClockify.py"