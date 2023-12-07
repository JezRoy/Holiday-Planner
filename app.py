## When running flask, ENSURE YOU ARE DIRECTORY OF APPLICATION.PY
## Run using Cmd use the following commands:
## FLASK_APP=application.py
## FLASK_ENV=development
## python3.10 -m flask run
## Web App runs on http://127.0.0.1:5000/

import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import datetime
import glob
import time
import csv
from csv import writer
from assistingFunctions import login_required, TimeLeftCalculator, apology, getAllUsers, OpenEvent, ChangeTimeFormat, SaveEvent


# Decelerations
app = Flask(__name__)
now = datetime.now() # The current time of using the program.
global EventSelected
EventSelected = False
Event = []
AllTasks = []

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.jinja_env.globals.update(TimeLeftCalculator=TimeLeftCalculator)
app.secret_key = b'P\x87\xfc\xa9\xe6qQ~)8\x90D\x11\n\xb9\xa1'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    global EventSelected
    global task
    task = []
    if EventSelected == True:
        if request.method == "POST":
            # See which button was pressed by getting their inputs.
            edit = request.form.get("edit")
            delete = request.form.get("delete")
            for item in [edit, delete]:
                if item != None:
                    chosen = [edit, delete].index(item) # Find whichever had an input so that it can tell Python which method to run.
            tasktobe = [edit, delete][chosen]
            for item in AllTasks:
                if item[0] == tasktobe:
                    task = item
            # Now we have decided which task to edit or delete.
            if chosen == 0:
                return redirect("/editTask")
            else:
                AllTasks.remove(task)
                flash("Task deleted!")
                return redirect("/")
        else:
            # Deciding what phase the event is in.
            timePre = TimeLeftCalculator(Event[4])
            timeDur = TimeLeftCalculator(Event[5])
            timePos = TimeLeftCalculator(Event[6])
            if timePre > 0:
                time = timePre
                phase = "Pre-Event"
            elif timePre == 0 and timeDur > 0:
                time = timeDur
                phase = "During-Event"
            elif timePre == 0 and timeDur > 0 and timePos > 0:
                time = timeDur
                phase = "Post-Event"
            else:
                time = 0
                phase = "Post Event"
            if time == 3:
                flash("The next phase is beginning in 3 days!")
            elif time == 3:
                flash("The next phase is beginning in 2 days!")
            elif time == 1:
                flash("The next phase is begins tomorrow!")
            elif time == 0:
                flash("The Event has finished.")
            return render_template("task_list.html", EventSelected=True, Event=Event, AllTasks=AllTasks, phase=phase, time=time)
    else:
        # If an event has not been selected for the Task List, the user is redirected to the event page to choose one.
        flash("Please select an event.")
        return redirect("/events")

@app.route("/help")
@login_required
def help():
    return render_template("help.html")

@app.route("/notepad", methods=["GET","POST"])
@login_required
def notepad():
    global Event
    if request.method == "POST":
        Event[7] = request.form.get("notepad")
        return redirect("/")
    else:
        notepad = Event[7]
        return render_template("notepad.html", EventSelected=True, notepad=notepad)
            
@app.route("/addTask", methods=["GET","POST"])
@login_required
def addTask():
    global Event
    global AllTasks
    if request.method == "POST":
        task=[]
        task.append(request.form.get("task name"))
        task.append(request.form.get("member responsible"))
        if request.form.get("member email") == None or request.form.get("member email") == "NONE":
            task.append("NONE")
        else:
            task.append(request.form.get("member email"))
        ## task.append(ChangeTimeFormat(request.form.get("due date")))
        task.append(request.form.get("due date"))
        task.append(request.form.get("extra details"))
        task.append(request.form.get("progress"))
        AllTasks.append(task)
        return redirect("/")
    else:
        return render_template("add_task.html", EventSelected=True)

@app.route("/editTask", methods=["GET","POST"])
@login_required
def editTask():
    global task
    if request.method == "POST":
        task=[]
        task.append(request.form.get("task name"))
        task.append(request.form.get("member responsible"))
        if request.form.get("member email") == None or request.form.get("member email") == "NONE":
            task.append("NONE")
        else:
            task.append(request.form.get("member email"))
        ## task.append(ChangeTimeFormat(request.form.get("due date")))
        task.append(request.form.get("due date"))
        task.append(request.form.get("extra details"))
        task.append(request.form.get("progress"))
        found = False
        for item in AllTasks:
            if item[0] == task[0]:
                # Save changes
                found = True
                i = AllTasks.index(item)
                AllTasks[i] = task
        # In case the task name is not found, the task will just be added instead.
        if found == False:
            AllTasks.append(task)
        return redirect("/")
    else:
        return render_template("edit_task.html", task=task, EventSelected=True)

@app.route("/saveEvent")
@login_required
def saveEvent():
    global Event
    global AllTasks
    SaveEvent(Event, AllTasks)
    flash("Saved!")
    return redirect("/")

@app.route("/exitEvent")
@login_required
def exitEvent():
    global Event
    global AllTasks
    global EventSelected
    SaveEvent(Event, AllTasks)
    flash("Saved and exited event!")
    Event = []
    AllTasks = []
    EventSelected = False
    return redirect("/events")

@app.route("/events", methods=["GET","POST"])
@login_required
def eventSelect():
    global Event
    global AllTasks
    global EventSelected
    if request.method == "POST":
        # Recieving inputs on which button was clicked.
        edit = request.form.get("eventEdited")
        choose = request.form.get("eventChosen")
        delete = request.form.get("eventDeleted")
        for item in [edit, choose, delete]:
            if item != None:
                chosen = [edit, choose, delete].index(item) # Find whichever had an input so that it can tell Python which method to run.
        os.chdir(r'D:\Program Files\Python\WebApps\HolidayPlanner\saveFiles')
        eventtoBe = [edit, choose, delete][chosen]
        if chosen == 0:
            Event, AllTasks = OpenEvent(eventtoBe)
            return redirect("/editEvent")
        elif chosen == 1:
            Event, AllTasks = OpenEvent(eventtoBe)
            EventSelected = True
            return redirect("/")
        else:
            os.remove(eventtoBe)
            flash("Deleted.")
            return redirect("/")
    else:
        EventSelected = False
        noEvents = False
        # Find all saved events and present them to the user.
        os.chdir(r'D:\Program Files\Python\WebApps\HolidayPlanner\saveFiles')
        savedEvents = glob.glob('*.txt')
        userEvents = []
        # Present only the files which include the current user.
        for i in range(0, len(savedEvents)):
            myFile = open(savedEvents[i], 'r')
            contents = myFile.readlines() # Stored as a list of lines.
            if session['username'] + '\n' == contents[1]:
                userEvents.append(savedEvents[i]) # Maintain a list of all events owned by the user.
            myFile.close()
        if len(userEvents) == 0:
            noEvents = True
        return render_template("events.html", EventSelected=False, noEvents=noEvents, events=userEvents)

@app.route("/createEvent", methods=["GET","POST"])
@login_required
def createEvent():
    global Event
    global EventSelected
    if request.method == "POST":
        # Reading data from the create event page from the post request.
        Event.append(request.form.get("event name"))
        Event.append(session['username'])
        Event.append(request.form.get("organiser email"))
        Event.append(request.form.get("location"))
        for i in ["pre-event", "during-event", "post-event"]:
            # time1 = ChangeTimeFormat(request.form.get(i + " start"))
            # time2 = ChangeTimeFormat(request.form.get(i + " end"))
            time1 = request.form.get(i + " start")
            time2 = request.form.get(i + " end")
            Event.append(time1 + "|" + time2)
        Event.append(request.form.get("notepad"))
        Event.append(request.form.get("save name"))
        EventSelected = True
        return redirect("/")
    else:
        return render_template("create_event.html", EventSelected=False)

@app.route("/editEvent", methods=["GET","POST"])
@login_required
def editEvent():
    global Event
    global EventSelected
    if request.method == "POST":
        Event=[]
        # Reading data from the edit event page from the post request.
        Event.append(request.form.get("event name"))
        Event.append(session['username'])
        Event.append(request.form.get("organiser email"))
        Event.append(request.form.get("location"))
        for i in ["pre-event", "during-event", "post-event"]:
        ##    time1 = ChangeTimeFormat(request.form.get(i + " start"))
        ##    time2 = ChangeTimeFormat(request.form.get(i + " end"))
            time1 = request.form.get(i + " start")
            time2 = request.form.get(i + " end")
            Event.append(time1 + "|" + time2)
        Event.append(request.form.get("notepad"))
        Event.append(request.form.get("save name"))
        EventSelected = True
        return redirect("/")
    else:
        time=[]
        for i in range(4,7):
            temp = Event[i].split("|")
            time.append(temp)
            print(time)
        return render_template("edit_event.html", EventSelected=False, Event=Event, time=time)

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Logs in a user """
    global Event
    global AllTasks
    Event = []
    AllTasks = []
    allUsers = []
    session.clear()

    if request.method == "POST":
        # Uses the function declared in helpers.py to get all the registered users.
        allUsers = getAllUsers()
                    
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Check the user exists
        locate = None
        for row in allUsers:
            if request.form.get("username") == row[0]:
                locate = allUsers.index(row)
                break
        if locate == None:
            return apology("User does not exist", 403)
        if not check_password_hash(allUsers[locate][1], request.form.get("password")):
            return apology("Invalid password", 403)

        # Creates a session for the users and remembers them.
        session["username"] = allUsers[locate][0]
        flash("Logged in!")
        return redirect("/events")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Registers a user """
    allUsers = []
    global Event
    global AllTasks
    Event = []
    AllTasks = []
    session.clear()
    if request.method == "POST":
        # Uses the function declared in helpers.py to get all the registered users.
        allUsers = getAllUsers()
                    
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password and a repeat was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide repeat password", 400)
        
        # Check the user doesnt exist
        for row in allUsers:
            if request.form.get("username") == row[0]:
                return apology("username already taken", 400)
        # Ensures the passwords entered indeed match.
        if check_password_hash(generate_password_hash(request.form.get("password")), request.form.get("confirmation")) == False:
            return apology("passwords do not match", 400)
        
        # Creates a session for the users and remembers them.
        os.chdir(r'D:\Program Files\Python\WebApps\HolidayPlanner')
        csv_File = open('USERS.txt','a')
        csv_File.write('\n' + request.form.get('username') + ',' + generate_password_hash(request.form.get('password')))
        csv_File.close()
        session['username'] = request.form.get("username")
        flash("Registered!")
        return redirect("/events")
    else:
        return render_template("register.html")

@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    if request.method == "POST":
        allUsers = getAllUsers()
        # Ensure password and a repeat was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide repeat password", 400)
        # Ensures the passwords entered indeed match.
        if check_password_hash(generate_password_hash(request.form.get("password")), request.form.get("confirmation")) == False:
            return apology("passwords do not match", 400)
        for user in allUsers:
            if session['username'] == user[0]:
                user[1] = generate_password_hash(request.form.get("password"))
        os.chdir(r'D:\Program Files\Python\WebApps\HolidayPlanner')
        print(allUsers)
        file = open("USERS.txt", "w+")
        for user in allUsers:
            if allUsers.index(user) == len(allUsers)-1:
                temp = user[0] + ',' + user[1]
                file.write(temp)
            else:
                temp = user[0] + ',' + user[1]
                file.write(temp)
                file.write("\n")
        file.close()
        flash("Password changed!")
        return redirect("/")
    else:
        return render_template("changePassword.html")
@app.route("/logout")
def logout():
    """ Log user out """
    global Event
    global AllTasks
    flash("Logged out.")
    session.clear()
    EventSelected = False
    Event = []
    AllTasks = []
    return redirect("/")
