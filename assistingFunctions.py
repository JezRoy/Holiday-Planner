import time
import datetime
import glob
import os
import requests
import csv
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps

global EventSelected

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def TimeLeftCalculator(Enddate): # Time Calculating Algorithm
    """ Calculates the time between now and an endate. """
    dates = Enddate
    length = list(dates) # This algorithm can either handle a start and an endate...
    if len(length) == 17:
        enddate = dates.split('|')[-1]
        enddate = datetime.datetime.strptime(enddate, "%d/%m/%y") 
    else: # ... or between now and an endate
        enddate = dates
        enddate = datetime.datetime.strptime(enddate, "%d/%m/%y") 
    today = datetime.date.today() # Regardless the calculation is only between now and the endate.
    Days = (enddate.date() - today).days
    if Days <= 0:
        Days = 0
    return Days

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def getAllUsers():
    allUsers = []
    # Change this directory to be wherever the web app is stored.
    os.chdir(r'/Programming Work/COMPSCI_FINALPRJ/HolidayPlanner')
    with open('USERS.txt', mode='r') as csv_File:
            csv_reader = csv.reader(csv_File, delimiter=',')
            for row in csv_reader:
                if row != ['username', 'passwordHash']:
                    # Don't append the headings.
                    allUsers.append(row)
    csv_File.close()
    return allUsers

def OpenEvent(FileName):
    Event = []
    AllTasks = []
    num = 0
    JumbleElement = [] # Declaring all assisting lists to help compile and open this event.
    CombineReady = []
    Filter = ''
    CombineSet = []
    CombineFin = []
    File = open(FileName, "rt")
    EventSave = File.readlines() # Loads all its contents with each line as an element.
    File.close()
    for i in range(0, 9): # Sets up the length of the file (for files of different lengths).
        Tag = EventSave[i]
        Tag = Tag.replace('\n','')
        Event.append(Tag) # Saves all the Event's Primary Content.
    for i in range(9, len(EventSave)): # Prepares to load all the tasks from the save file
        ElementOrg = list(EventSave[i])# The string loaded in the save file needs to be fixed so it can be read by python properly.
        if '\n' in ElementOrg:
            ElementOrg.remove('\n')
        for i in ElementOrg: # The large list of organic text is seperated into all it's seperate string elements.
            if i == '|': # The seperator.
                num += 1
                CombineReady.append(JumbleElement)
                JumbleElement = []
            if i == '-': # Im case it reads a new line.
                num += 1
                JumbleElement = []
            else: # Adds the lettes in one element together.
                JumbleElement.append(i)
                num += 1
    for x in range(0, len(CombineReady)): # Joins the letters together as words and sentences.
        for i in CombineReady[x]:
            Filter = Filter + i
        CombineSet.append(Filter)
        Filter = ''
    for i in CombineSet: # Adds the words and sentences together as task elements.
        if '|' in i:
            TempStr = i.replace('|', '')
            CombineFin.append(TempStr)
        else:
            CombineFin.append(i)
    AllTasks = [CombineFin[x:x+6] for x in range(0, len(CombineFin), 6)] # Seperates each set of five elements into tasks.
    return Event, AllTasks

def ChangeTimeFormat(htmlform):
    # HTML for is YYYY-MM-DD
    # DD/MM/YY is needed
    change = list(htmlform)
    return change[8] + change[9] + "/" + change[5] + change[6] + "/" + change[2] + change[3]

def SaveEvent(Event, AllTasks):
    os.chdir(r'D:\Program Files\Python\WebApps\HolidayPlanner\saveFiles')
    SaveFile = "%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" % (Event[0], Event[1], Event[2], Event[3], Event[4], Event[5], Event[6], Event[7], Event[8])
    for i in range(len(AllTasks)):
        index = i - 1
        SaveTask = "%s|%s|%s|%s|%s|%s|\n-\n" % (AllTasks[index][0], AllTasks[index][1], AllTasks[index][2], AllTasks[index][3], AllTasks[index][4], AllTasks[index][5])
        SaveFile = SaveFile + SaveTask
    SaveFile = SaveFile + "FINISH"
    SaveName = Event[8] + ".txt"
    File = open(SaveName,"w+")
    File.write(SaveFile) # Loads all its contents with each line as an element.
    File.close()
