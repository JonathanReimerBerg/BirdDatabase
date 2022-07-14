import sqlite3
import re
import csv
from sqlite3 import OperationalError

def birdApp():        #menu
    try:
        print("you have", countLifers(), "lifers", '\n')
    except:
        print("Database not yet created, try running 'DatabaseWriter.py' first")
    while True:
        option = input("i: import EBird data" + '\n' + "p: print personal list" +
        '\n' + "m: make a birding report" + '\n' + "e: end program" + '\n\n')
        print('\n')
        if option == 'i':
           importData()
        if option == 'p':
            printList()
        if option == 'm':
            makeReport() 
        if option == 'e':
            break
        print('\n')

def makeReport():  #manually add a report to the database
    data = input("What list would you like to see (year/county/state/country): ")
    data = data.split("/")
    if data[0] == "life":
        data[0] = "seen"
    elif data[0].isdigit():
        if 1900 < int(data[0]) < 2023:
            data[0] = "in_" + data[0]
        else:
            print("Invalid year")
            return
    else:
        print("Try giving a year or 'life' for life list")
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

def getID(county, state, country, create_if_none = True):   #get the county ID
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    command = "SELECT id FROM COUNTIES where county_name = '" + county + "' and belonging_state = '"
    command += state + "' and belonging_country = '" + country + "'"
    crsr.execute(command)
    county_id = crsr.fetchone()
    if (county_id is None) and (create_if_none):            #if it doesn't exist, at the county to the database
        county_id = addCounty(county, state, country)
    elif (create_if_none == False) and (county_id is None):
        print("\n", "Location not found")
        return
    county_id = str(county_id)
    numeric_filter = filter(str.isdigit, county_id)
    return("".join(numeric_filter))

def addBird(time, county, state, country, birdname):
    bird = birdname.replace("'", "''")   #birdname is used so future calls don't get changed twice
    if ("sp." in bird) or ("/" in bird) or ("Domestic" in bird) or (" x " in bird):
        return
    bird = re.sub(r" ?\([^)]+\)", "", bird)
    
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    command = "SELECT * from ALL_BIRDS where name = '" + bird + "'"  #check to make sure the bird is valid
    crsr.execute(command)
    exist = crsr.fetchone()
    if exist is None:
        print("Bird, " + bird + ", not found")
        return()    #if bird is invalid, skip it
    
    if len(county) > 0:
        addBird(time, "", state, country, birdname)
    elif len(state) > 0:
        addBird(time, "", "", country, birdname)
    if int(time[-4:]) < 1901:    
        time = "seen"    #Birds before 1901 are only added to life lists

    county = county.replace(" ", "_")
    county = county.replace(".", "")    
    county_id = getID(county, state, country)
    
    try:
        command = "UPDATE ALL_BIRDS set " + time + " = 1 WHERE name = '" + bird + "'"   #make sure lifer is seen in ALL_BIRDS
        crsr.execute(command)
        connection.commit()
    except OperationalError:    #if the year isn't found, add it to the table and then add the bird
        command = "ALTER TABLE ALL_BIRDS Add " + time + " varchar(1) not null DEFAULT 0"
        crsr.execute(command)
        connection.commit()
        command = "UPDATE ALL_BIRDS set " + time + " = 1 WHERE name = '" + bird + "'"
        crsr.execute(command)
        connection.commit()
    command = "UPDATE ALL_Birds set seen = 1 WHERE name = '" + bird + "'"
    crsr.execute(command)
    connection.commit()
    county_code = county + "_" + state + "_" + country + "_" + str(county_id)
    command = "SELECT * FROM " + county_code + " WHERE bird = '" + bird + "'" 
    crsr.execute(command)
    exist = crsr.fetchone()
    if exist is None:   #if the bird isn't in the specific county list
        command = "INSERT into " + county_code + "(bird) VALUES"
        command += '\n' + "('" + bird + "');"
        crsr.execute(command)
        connection.commit()
    command = "UPDATE " + county_code + " set seen = 1 WHERE bird = '" + bird + "'"  #add bird to county
    crsr.execute(command)
    connection.commit()
    try:
        command = "UPDATE " + county_code + " set " + time + " = 1 WHERE bird = '" + bird + "'"
        crsr.execute(command)
        connection.commit()
    except OperationalError:    #if the year isn't found, add it to the table and then add the bird
        command = "ALTER TABLE " + county_code + " Add " + time + " varchar(1) not null DEFAULT 0"
        crsr.execute(command)
        connection.commit()
        command = "UPDATE " + county_code + " set " + time + " = 1 WHERE bird = '" + bird + "'"
        crsr.execute(command)
        connection.commit()
    connection.close
    return


def printList():    #not currently functional with specific locations
    data = input("What list would you like to see (year/county/state/country): ")
    data = data.split("/")
    if data[0] == "life":
        data[0] = "seen"
    elif data[0].isdigit():
        if 1900 < int(data[0]) < 2023:
            data[0] = "in_" + data[0]
        else:
            print("Invalid year")
            return
    else:
        print("Try giving a year or 'life' for life list")
        return
    try:
        lyst = getList(data[0], data[1], data[2], data[3], None)
    except IndexError:
        print('\n')
        print("Make sure you input a time/location fitting the requested format (use '/' even with empty catergory)")
        return
    print('\n')
    if len(lyst) == 0:
        print(" No birds reported")
    else:
        for i in lyst:
            print(i)
        print('\n', "You have seen " + str(len(lyst)) + " birds")
    return   

def getList(time, county = None, state = None, country = None, sort = None): #sort not yet implemented
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    if county == "":
        command = "SELECT name from ALL_BIRDS where " + time + " = 1 order by name"
    else:
        county_id = getID(county, state, country, False)
        if county_id is None:
            return("")
        county_code = county + "_" + state + "_" + country + "_" + str(county_id)
        command = "SELECT bird from " + county_code + " where " + time + " = 1"
    crsr.execute(command)
    birds = str(crsr.fetchall())[3:-4]
    birds = birds.replace('"', "'")
    birds = birds.split("',), ('")
    connection.commit()
    connection.close()
    return(birds)  

def countLifers():   #runs when program is started
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    crsr.execute("SELECT count(*) from ALL_BIRDS where seen = 1")
    life_list = str(crsr.fetchall())
    numeric_filter = filter(str.isdigit, life_list)
    life_list = "".join(numeric_filter)
    connection.commit()
    connection.close()
    return(life_list)

def addCounty(county, state, country):
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    crsr.execute("SELECT count(*) from COUNTIES")
    countyID = str(crsr.fetchall())
    numeric_filter = filter(str.isdigit, countyID)
    countyID = int("".join(numeric_filter)) + 1
    command = "INSERT INTO COUNTIES(id, county_name, belonging_state, belonging_country) VALUES" #add county to county table
    command += '\n'
    command += "    ("+str(countyID)+", '"+county+"', '"+state+"', '"+country+"');"
    crsr.execute(command)
    connection.commit()
    county_code = county + "_" + state + "_" + country + "_" + str(countyID)
    command = "CREATE TABLE "+county_code+" ("+'\n'+"    bird varchar(64) not null unique," + '\n'  #create table for county sightings
    command += "    seen,"+'\n'+"    CONSTRAINT COUNTY_"+str(countyID)+"_PK PRIMARY KEY(bird)"
    command += '\n' + ");"
    crsr.execute(command)
    connection.commit()
    connection.close()
    print("The region "+county + "/" + state + "/" + country + " has been added" + '\n')
    return(countyID)

def importData():  #imports data from a downloaded ebird csv file
    names = []
    counts = []
    states = []
    countries = []
    counties = []
    years = []
    with open('MyEBirdData.csv', 'r', encoding='utf') as file:   #Name must match this
        reader = csv.reader(file)
        for row in reader:
            names.append(row[1])
            counts.append(row[4])
            states.append(row[5][3:])
            countries.append(row[5][0:2])
            counties.append(row[6])
            years.append(row[11][0:4])
    for i in range(1, len(names)):
        addBird("in_" + years[i], counties[i], states[i], countries[i], names[i])

    
    
birdApp()
