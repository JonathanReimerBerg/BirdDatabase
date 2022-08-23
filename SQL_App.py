import sqlite3
import re
import csv
from sqlite3 import OperationalError
import datetime

def birdApp():        #menu
    try:
        print("you have", countLifers(), "lifers", '\n')
    except:
        print("Database not yet created, try running 'DatabaseWriter.py' first")
    while True:
        option = input("i: import EBird data" + '\n' + "p: print personal list" +
        '\n' + "m: make a birding report" + '\n' + "c: compare two lists" +
        '\n' + "e: end program" + '\n\n')
        print('\n')
        if option == 'i':
           importData()
        if option == 'p':
            printList()
        if option == 'm':
            makeReport()
        if option == 'c':
            compareLists()
        if option == 'e':
            break  
        print('\n')

#Helper Functions

def runCommand(command, fetchone = False, fetchall = False):
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    crsr.execute(command)
    if fetchone:
        return(crsr.fetchone())
    elif fetchall:
        return(crsr.fetchall())
    connection.commit()
    connection.close

def inputLocation(getLyst = False):
    inp = input("What list would you like to see (year/county/state/country): ")
    data = inp.split("/")
    if data[0].isdigit():
        if 1900 < int(data[0]) < 2023:
            data[0] = "in_" + data[0]
        else:
            print("Invalid year")
            return("")
    elif (data[0] != 'life') and (data[0] != 'Life'):
        print("Try giving a year or 'life' for life list")
        return("")
    if len(data) == 0:
        return("")
    if getLyst:
        try:
            lyst = getList(data[0], data[1], data[2], data[3])
        except IndexError:
            print('\n' + "Make sure you input a time/location fitting the requested format (use '/' even with empty catergory)")
            return("")
        return(inp, lyst)
    return(data)

def getList(time, county = None, state = None, country = None): 
    if country == "":
        command = "SELECT name from ALL_BIRDS where " + time + " = 1 order by name"
    else:
        county_id = getID(county, state, country, False)
        if county_id is None:
            return("")
        county_code = county + "_" + state + "_" + country + "_" + str(county_id)
        command = "SELECT bird from " + county_code + " where " + time + " = 1"
    try:
        birds = str(runCommand(command, False, True))[3:-4]
    except OperationalError:
        return("")
    birds = birds.replace('"', "'")
    birds = birds.split("',), ('")
    return(birds)

def getID(county, state, country, create_if_none = True):   #get the county ID
    command = "SELECT id FROM COUNTIES where county_name = '" + county + "' and belonging_state = '"
    command += state + "' and belonging_country = '" + country + "'"
    county_id = runCommand(command, True)
    if (county_id is None) and (create_if_none):            #if it doesn't exist, at the county to the database
        county_id = addCounty(county, state, country)
    elif (create_if_none == False) and (county_id is None):
        print("\n", "Location not found")
        return
    county_id = str(county_id)
    numeric_filter = filter(str.isdigit, county_id)
    return("".join(numeric_filter))

def addCounty(county, state, country):
    countyID = str(runCommand("SELECT count(*) from COUNTIES", False, True))
    numeric_filter = filter(str.isdigit, countyID)
    countyID = int("".join(numeric_filter)) + 1
    command = "INSERT INTO COUNTIES(id, county_name, belonging_state, belonging_country) VALUES" #add county to county table
    command += '\n' + "    ("+str(countyID)+", '"+county+"', '"+state+"', '"+country+"');"
    runCommand(command)
    county_code = county + "_" + state + "_" + country + "_" + str(countyID)
    command = "CREATE TABLE "+county_code+" ("+'\n'+"    bird varchar(64) not null unique," + '\n'  #create table for county sightings
    command += "    life,"+'\n'+"    CONSTRAINT COUNTY_"+str(countyID)+"_PK PRIMARY KEY(bird)" + '\n' + ");"
    runCommand(command)
    print("The region "+county + "/" + state + "/" + country + " has been added" + '\n')
    return(countyID)

#Features

def makeReport():  #manually add a report to the database
    data = inputLocation()
    if len(data) == 0:
        return
    print("Enter your list to report: ")
    birds = []
    while True:
        line = input()
        if line:
            birds.append(line)
        else:
            break
    for bird in birds:
        addBird(data[0], data[1], data[2], data[3], bird)

def addBird(time, county, state, country, birdname):
    bird = birdname.replace("'", "''")   #birdname is used so future calls don't get changed twice
    if ("sp." in bird) or ("/" in bird) or ("Domestic" in bird) or (" x " in bird):
        return
    bird = re.sub(r" ?\([^)]+\)", "", bird)

    exist = runCommand("SELECT * from ALL_BIRDS where name = '" + bird + "'", True) #check to make sure the bird is valid
    if exist is None:
        print("Bird, " + bird + ", not found")
        return()    #if bird is invalid, skip it
    
    if len(county) > 0:   #add bird to the state/province of that county
        addBird(time, "", state, country, birdname)
    elif len(state) > 0:
        addBird(time, "", "", country, birdname)
    if int(time[-4:]) < 1901:    
        time = "life"    #Birds before 1901 are only added to life lists

    county = county.replace(" ", "_")
    county = county.replace(".", "")    
    county_id = getID(county, state, country)
    
    try:
        runCommand("UPDATE ALL_BIRDS set " + time + " = 1 WHERE name = '" + bird + "'") #make sure bird is seen in ALL_BIRDS
    except OperationalError:    #if the year isn't found, add it to the table and then add the bird
        runCommand("ALTER TABLE ALL_BIRDS Add " + time + " varchar(1) not null DEFAULT 0")
        runCommand("UPDATE ALL_BIRDS set " + time + " = 1 WHERE name = '" + bird + "'")
    runCommand("UPDATE ALL_Birds set life = 1 WHERE name = '" + bird + "'")
    
    county_code = county + "_" + state + "_" + country + "_" + str(county_id)
    exist = runCommand("SELECT * FROM " + county_code + " WHERE bird = '" + bird + "'", True)
    if exist is None:   #if the bird isn't in the specific county list
        runCommand("INSERT into " + county_code + "(bird) VALUES" + '\n' + "('" + bird + "');")
    runCommand("UPDATE " + county_code + " set life = 1 WHERE bird = '" + bird + "'")  #add bird to county

    try:
        runCommand("UPDATE " + county_code + " set " + time + " = 1 WHERE bird = '" + bird + "'")
    except OperationalError:    #if the year isn't found, add it to the table and then add the bird
        runCommand("ALTER TABLE " + county_code + " Add " + time + " varchar(1) not null DEFAULT 0")
        runCommand("UPDATE " + county_code + " set " + time + " = 1 WHERE bird = '" + bird + "'")
    return


def printList():    #not currently functional with specific locations
    data = inputLocation(True)
    if len(data) == 0:
        return
    print('\n')
    if len(data[1]) == 0:
        print(" No birds reported")
    else:
        for i in data[1]:
            print(i)
        print('\n', "You have seen " + str(len(data[1])) + " birds")
    return     

def countLifers():   #runs when program is started\
    life_list = str(runCommand("SELECT count(*) from ALL_BIRDS where life = 1", False, True))
    numeric_filter = filter(str.isdigit, life_list)
    life_list = "".join(numeric_filter)
    return(life_list)

def importData():  #imports data from a downloaded ebird csv file
    names = []
    counts = []
    states = []
    countries = []
    counties = []
    dates = []
    with open('MyEBirdData.csv', 'r', encoding='utf') as file:   #Name must match this
        reader = csv.reader(file)
        for row in reader:
            names.append(row[1])
            counts.append(row[4])
            states.append(row[5][3:])
            countries.append(row[5][0:2])
            counties.append(row[6])
            dates.append(row[11])
    if input("Import birds from a certain date forward? ") in ['y','Y','Yes','yes','YES']:
        date = input("From what date would you like to import? mm/dd/yyyy: ")
        try:
            date = datetime.datetime(int(date[6:]), int(date[0:2]), int(date[3:5]))
            for i in range(1, len(names)):
                if datetime.datetime(int(dates[i][0:4]), int(dates[i][5:7]), int(dates[i][8:])) >= date:
                    addBird("in_" + dates[i][0:4], counties[i], states[i], countries[i], names[i])
        except:
            print("Not a valid year" + '\n')
    else:   
        for i in range(1, len(names)):
            addBird("in_" + dates[i][0:4], counties[i], states[i], countries[i], names[i])


def compareLists():
    data1 = inputLocation(True)
    if len(data1) == 0:
        return
    data2 = inputLocation(True)
    if len(data2) == 0:
        return
    print("\nBirds in " + str(data1[0]) + " not in " + str(data2[0]) + ':\n')
    count1 = 0
    for bird in data1[1]:
        if bird not in data2[1]:
            print(bird)
            count1 += 1
    print("\n\nBirds in " + str(data2[0]) + " not in " + str(data1[0]) + ':\n')
    count2 = 0
    for bird in data2[1]:
        if bird not in data1[1]:
            print(bird)
            count2 += 1
    print('\n\n' + str(count1) + " not in " + str(data2[0]))
    print(str(count2) + " not in " + str(data1[0]))
    return
    


    
    
birdApp()
