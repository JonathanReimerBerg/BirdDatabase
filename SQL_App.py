import sqlite3
import re
import urllib.request
import requests
import csv

def birdApp():        #menu
    print("you have", countLifers(), "lifers", '\n')
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
    while True:
        time = input("When would you like to make a list for? ")
        if time.isdigit():
            if (time == '2018' or time == '2019' or time == '2020' or time == '2021'):
                time = "in_" + time
                break
            else:
                print("not a valid year")
        else:
            time = "seen"
            break
        
    location = []
    county = input("What county was this seen in? ")
    state = input("What state was this seen in? ")
    country = input("What country was this seen in? ")
    print("Enter your list to report: ")
    birds = []
    while True:
        line = input()
        if line:
            birds.append(line)
        else:
            break
    for bird in birds:
        addBird(time, county, state, country, bird)

def getID(county, state, country):   #get the county ID
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    command = "SELECT id FROM COUNTIES where county_name = '" + county + "' and belonging_state = '"
    command += state + "' and belonging_country = '" + country + "'"
    crsr.execute(command)
    county_id = crsr.fetchone()
    if county_id is None:            #if it doesn't exist, at the county to the database
        county_id = addCounty(county, state, country)
    county_id = str(county_id)
    numeric_filter = filter(str.isdigit, county_id)
    return("".join(numeric_filter))
    
def addBird(time, county, state, country, bird):
    if int(time[-4:]) < 2018:    #sql formatting stuff
        time = "seen"
    bird = bird.replace("'", "''")
    if ("sp." in bird) or ("/" in bird) or ("Domestic" in bird) or (" x " in bird):
        return
    bird = re.sub(r" ?\([^)]+\)", "", bird)
    county = county.replace(" ", "_")
    county = county.replace(".", "")
    
    county_id = getID(county, state, country)
    
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    command = "SELECT * from ALL_BIRDS where name = '" + bird + "'"  #check to make sure the bird is valid
    crsr.execute(command)
    exist = crsr.fetchone()
    if exist is None:
        print("Bird, " + bird + " not found")
        return
    command = "UPDATE ALL_BIRDS set " + time + " = 1 WHERE name = '" + bird + "'"   #make sure lifer is seen in ALL_BIRDS
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
        command = "INSERT into " + county_code + "(bird, in_2018, in_2019, in_2020, in_2021, in_2022, seen) VALUES"
        command += '\n' + "('" + bird + "', 0,0,0,0,0,0);"
        crsr.execute(command)
        connection.commit()
    command = "UPDATE " + county_code + " set seen = 1 WHERE bird = '" + bird + "'"  #add bird to county
    crsr.execute(command)
    connection.commit()
    command = "UPDATE " + county_code + " set " + time + " = 1 WHERE bird = '" + bird + "'"
    crsr.execute(command)
    connection.commit()
    connection.close
    return


def printList():    #not currently functional with specific locations
    timePeriod = input("What list would you like to see: ")
    if timePeriod == "life":
        timePeriod = "seen"
    elif timePeriod.isdigit():
        if 2017 < int(timePeriod) < 2023:
            timePeriod = "in_" + timePeriod
        else:
            print("Invalid year")
            return
    else:
        print("Try giving a year or 'life' for life list")
        return
    print(getList(time, None, None, None, None)
    return   

def getList(time, county = None, state = None, country = None, sort = None): #sort not yet implemented
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    if county is None:
        command = "SELECT name from ALL_BIRDS where " + time + " = 1 order by name"
    else:
        county_id = getID(county, state, country)
        county_code = county + "_" + state + "_" + country + "_" + str(county_id)
        command = "SELECT bird from " + county_code + " where " + time + " = 1"
    crsr.execute(command)
    birds = str(crsr.fetchall())[2:-3]
    birds = birds.replace('"', "'")
    birds = birds.split(',), (')
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

def liferCheck(bird):  #returns boolean depending on if the bird has been seen
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    for i in range(2018, 2022):
        crsr.execute("SELECT in_" + str(i) + " from ALL_BIRDS where name = '" + bird + "'")
        if "".join(str(crsr.fetchall()))[3] == '1':
            connection.commit()
            connection.close()
            return(1)
    connection.commit()
    connection.close()
    return(0)

def addCounty(county, state, country):
    connection = sqlite3.connect("BirdingDatabase.db")
    crsr = connection.cursor()
    crsr.execute("SELECT count(*) from COUNTIES")
    countyID = str(crsr.fetchall())
    numeric_filter = filter(str.isdigit, countyID)
    countyID = int("".join(numeric_filter)) + 1
    command = "INSERT INTO COUNTIES(id, county_name, belonging_state, belonging_country) VALUES". #add county to county table
    command += '\n'
    command += "    ("+str(countyID)+", '"+county+"', '"+state+"', '"+country+"');"
    crsr.execute(command)
    connection.commit()
    county_code = county + "_" + state + "_" + country + "_" + str(countyID)
    command = "CREATE TABLE "+county_code+" ("+'\n'+"    bird varchar(64) not null unique," + '\n'  #create table for county sightings
    command += "    in_2018,"+'\n'+"    in_2019,"+'\n'+"    in_2020,"+'\n'+"    in_2021,"+'\n'
    command += "    in_2022,"+'\n'+"    seen,"+'\n'+"    CONSTRAINT COUNTY_"+str(countyID)+"_PK PRIMARY KEY(bird)"
    command += '\n' + ");"
    crsr.execute(command)
    connection.commit()
    connection.close()
    print("The county " + county + " has been added" + '\n')
    return(countyID)

def importData():  #imports data from a downloaded ebird csv file
    names = []
    counts = []
    states = []
    countries = []
    counties = []
    years = []
    with open('MyEBirdData.csv', 'r') as file:   #Name must match this
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
