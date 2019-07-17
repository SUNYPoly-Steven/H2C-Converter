# HarvestToClockify.py
#
# python3
#
# A program to send times recorded in a Harvest account
# and put them on a Clockify account
#

# Requires python-harvest api:
# install with:
#     pip install "python-harvest-redux>=3.0"
import harvest

# Clockify uses REST API, so we will use the requests api
# install with:
#     pip install requests
import requests

# To parse json strings we will use the json package (part of python stdlib)
import json

# For date and time vaildation (part of python stdlib)
import datetime

# Used to get environment variables for configuration (part of python stdlib)
import os

# USed to parse commandline args
import argparse

# For handling SIGINT (aka: Ctrl + C)
import signal
import sys



# Global Constants
filterable_types = [ 'client', 'project', 'task' ]

# Global Vars
filters = { fType : [] for fType in filterable_types }
DRY_RUN_ENABLED = False




# Signal Handling
def signal_handler(sig, frame):
    # If you get an interupt, just exit
    sys.exit(1)

# Add the signal_handler
signal.signal(signal.SIGINT, signal_handler)



# Logging Functions
def TRACE(string):
    print("[H2C TRACE]: " + str(string))


def INFO(string):
    print("\033[0;32m[H2C INFO]:\033[0m " + str(string))


def WARN(string):
    print("\033[0;33m[H2C WARNING]:\033[0m " + str(string))


def ERROR(string):
    print("\033[0;31m[H2C ERROR]:\033[0m " + str(string))




# Utility Functions
def validateDate(date_text):
    try:
        return datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def validateTime(time_text):
    try:
        return datetime.datetime.strptime(time_text, '%H:%M:%S')
    except ValueError:
        raise ValueError("Incorrect data format, should be HH:MM:SS")


def AddTime(time_text, hours):
    time = validateTime(time_text)
    hoursInt = int(hours)
    minutesInt = (hours - hoursInt) * 60.0

    delta = datetime.timedelta(hours=hoursInt, minutes=minutesInt)

    return (time + delta).strftime("%H:%M:%S")

def GetCurrentWeek():
    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
    return dates

def applyFilters(filter_strings):
    if filter_strings == None:
        return None

    for criteria in filter_strings:
        # Split the filter on the '='
        strings = criteria.split('=')
        
        # Make sure criteria is vailid
        if (len(strings) != 2):
            WARN("Invalid filter criteria, the format should be '<type>=<string>'! '" + criteria + "'")
            return None
        # Strip any white space on both ends of the strings
        for index, x in enumerate(strings):
            strings[index] = x.strip()

        if strings[0] not in filterable_types:
            WARN("Filter Type '" + strings[0] + "' is NOT a valid type!")
            WARN("the valid filter types are:")
            for fType in filterable_types:
                WARN("    " + fType)
            return None
        
        filters[strings[0]].append(strings[1])
    INFO("Applied filters " + str(filters))








# Harvest Functions
def Harvest_GetTimeEntriesOnDay(harvestClient, date_text):
        date = validateDate(date_text)
        all_entries = harvestClient.get_day(int(date.timetuple().tm_yday), date.year)['day_entries']

        temp = []
        for entry in all_entries:
            for fType in filterable_types:
                for filt in filters[fType]:
                    if entry[fType] == filt:
                        temp.append(entry)
        return temp

# Clockify Functions
def Clockify_GetWorkspaceId():
    # Setup the GET Request
    url = CLOCKIFY_BASE_ENDPOINT + "/workspaces"
    headers = CLOCKIFY_AUTH_HEADER

    # Perform the GET Request
    resp = requests.get(url, headers=headers)

    if resp.status_code != requests.codes.ok:
        ERROR("Workspace GET request returned code " + str(resp.status_code))
        return None
    
    # As long as the response was good, load the content
    content = json.loads(resp.text)

    # NOTE: Only returns first workspace in the list
    return content[0]['id']



def Clockify_GetProjectId(projectName):
    # Setup the GET Request
    workspaceId = Clockify_GetWorkspaceId()
    if workspaceId == None:
        ERROR("Could not GET project id because of an INVALID workspaceId")
        return None

    url = CLOCKIFY_BASE_ENDPOINT + "/workspaces/" + workspaceId + "/projects" + (("?name=" + projectName) if projectName != None else "")
    headers = CLOCKIFY_AUTH_HEADER

    # Perform the GET Request
    resp = requests.get(url, headers=headers)

    if resp.status_code != requests.codes.ok:
        ERROR("Project GET request returned code " + str(resp.status_code))
        return None

    # As long as the response was good, load the content
    content = json.loads(resp.text)

    if not content:
        ERROR("There is no project by the name of '" + projectName + "' in the workspace with id '" + workspaceId + "'")
        return None    

    return content[0]['id']



def Clockify_GetTaskId(projectName, taskName):
    workspaceId = Clockify_GetWorkspaceId()
    if workspaceId == None:
        ERROR("Could not GET task id because of an INVALID workspaceId")
        return None

    projectId = Clockify_GetProjectId(projectName)
    if projectId == None:
        ERROR("Could not GET task id because of an INVALID projectId")
        return None

    url = CLOCKIFY_BASE_ENDPOINT + "/workspaces/" + workspaceId + "/projects/" + projectId + "/tasks" #+ (("?name=" + taskName) if taskName != None else "")
    headers = CLOCKIFY_AUTH_HEADER

    # Perform the GET Request
    resp = requests.get(url, headers=headers)

    if resp.status_code != requests.codes.ok:
        ERROR("Task GET request returned code " + str(resp.status_code))
        return None

    # As long as the response was good, load the content
    content = json.loads(resp.text)

    if not content:
        ERROR("There is no task by the name of '" + str(taskName) + "' in the '" + projectName + "' project")
        return None    

    return content[0]['id']

def Clockify_CreateTimer(harvestClient, projectName, date_text):
    projectId   = Clockify_GetProjectId(projectName)
    entries = Harvest_GetTimeEntriesOnDay(harvestClient, date_text)
    
    if DRY_RUN_ENABLED == True:
        INFO(entries)
        return

    ERROR("BAD RUN!")
    return None

    for entry in entries:
        data = HarvestTimeEntryToClockifyJson(entry, date_text, projectId)
        url = CLOCKIFY_BASE_ENDPOINT + "/workspaces/" + Clockify_GetWorkspaceId() + "/time-entries"
        headers = {"content-type" : "application/json", "X-Api-Key" : CLOCKIFY_API_KEY}

        resp = requests.post(url, headers=headers, data=data)

        if resp.status_code != 201:
            ERROR("POST request returned code " + str(resp.status_code))
            ERROR("POST Response was: " + resp.text)
            continue

        content = json.loads(resp.text)
        INFO("Successfully Created Time Entry:")
        INFO( json.dumps(content, indent=4, sort_keys=True) )
        INFO("")








# Conversion Functions
def HarvestTimeEntryToClockifyJson(harvestTimeEntry, date_text, clockifyProjectId):
    json = '{'
    json += '  "start": "' + date_text + 'T' + DEFAULT_START_TIME + '.000Z",'
    json += '  "billable": "true",'
    json += '  "description": "' + harvestTimeEntry['notes'] + '",'
    json += '  "projectId": "' + clockifyProjectId + '",'
    json += '  "taskId": null,'
    json += '  "end": "' + date_text + 'T' + \
        AddTime(DEFAULT_START_TIME, harvestTimeEntry['hours']) + '.000Z",'
    json += '  "tagIds": []'
    json += '}'
    INFO (json)
    return json


# Print Functions
def PrintTimeEntry(harvestTimeEntry):
    INFO(harvestTimeEntry['project'] + " : " + harvestTimeEntry['task'])
    INFO("\tHours: " + str(harvestTimeEntry['hours']))
    INFO("\tNotes: " + harvestTimeEntry['notes'])
    INFO("")


def PrintDateInfo(client, date_text):
    INFO("----- " + date_text + " -----")
    entries = Harvest_GetTimeEntriesOnDay(client, date_text)
    if entries is not None:
        for entry in entries:
            PrintTimeEntry(entry)
    INFO("")



def main():
    client = harvest.Harvest(
        "https://" + COMPANY_NAME + ".harvestapp.com", EMAIL, PASSWORD)
    # PrintDateInfo(client, "2019-07-08")
    # PrintDateInfo(client, "2019-07-09")
    dates = GetCurrentWeek()
    
    for date in dates:
        Clockify_CreateTimer(client, CLOCKIFY_PROJECT_NAME, str(date))



# Entry Point
# Commandline argument parser
parser = argparse.ArgumentParser(description="Convert Harvest time entries into Clockify time entries.")

# Add's argument for filtering harvest timers based on criteria
parser.add_argument('-f', '--filter', nargs='+', metavar='string', help='Filter Harvest timers based on criteria (i.e. -f client=client_name)')
parser.add_argument('--dry-run', action='store_true', default=False, help='Go through the entire time entry fetch process but do not post the entries to Clockify, just print then to stdout.')


# Parse the commandline options
cmdl = parser.parse_args()

try:

    # Environment Variables to configure system
    # Harvest
    COMPANY_NAME = os.environ['H2C_HARVEST_COMPANY_NAME']
    EMAIL = os.environ['H2C_HARVEST_EMAIL']
    PASSWORD = os.environ['H2C_HARVEST_PASSWORD']

    # Clockify
    DEFAULT_START_TIME = os.environ['H2C_CLOCKIFY_START_TIME']
    CLOCKIFY_API_KEY = os.environ['H2C_CLOCKIFY_API_KEY']
    CLOCKIFY_PROJECT_NAME = os.environ['H2C_CLOCKIFY_PROJECT_NAME']


    # Constants
    CLOCKIFY_BASE_ENDPOINT = "https://api.clockify.me/api/v1"
    CLOCKIFY_AUTH_HEADER = { "X-Api-Key" : CLOCKIFY_API_KEY }

except:
    ERROR("Missing environment variable!")

# Apply any filters that may have been specified
applyFilters(cmdl.filter)
print (cmdl.dry_run)
DRY_RUN_ENABLED = cmdl.dry_run



# Call main function IFF this program is the main python program being run
if __name__ == '__main__':
    main()
