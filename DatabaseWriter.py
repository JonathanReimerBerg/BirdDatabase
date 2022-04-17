import csv
import sqlite3

names = []
sci_names = []
groups = []

  
with open('eBird_Taxonomy_v2021.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if ("(" in row[3]) or (" x " in row[3]) or ("/" in row[3]) or ("sp." in row[3]):  #removes non-valid birds, like subspecies
                continue
            if row[6] == "FAMILY":   #don't count first row
                continue
            names.append(row[3].replace("'", "''"))  #for SQL grammer
            sci_names.append(row[4])
            group = row[6]
            groups.append(group[group.find("(")+1:group.find(")")].replace("'", "''")) #just add what is in parenthesis

connection = sqlite3.connect("BirdingDatabase.db")
crsr = connection.cursor()

command = "DROP TABLE IF exists ALL_BIRDS;"   #writing command to create table ALL_BIRDS in database
crsr.execute(command)
connection.commit()

command = """CREATE TABLE ALL_BIRDS (
    scientific_name varchar(64),
    seen INTEGER varchar(1) not null,
    type varchar(64),
    name varchar(64) not null UNIQUE,
    in_2018 varchar(1) not null,
    in_2019 varchar(1) not null,
    in_2020 varchar(1) not null,
    in_2021 varchar(1) not null,
    in_2022 varchar(1) not null,
    CONSTRAINT ALL_BIRDS_PK Primary KEY(name)
    );"""

crsr.execute(command)
connection.commit()
	
command = "INSERT INTO ALL_BIRDS(name, scientific_name, type, seen, in_2018, in_2019, in_2020, in_2021, in_2022) VALUES"

for i in range(0, len(names)):
    command += '\n'
    command += ("    ('" + names[i] + "', '" + sci_names[i] + "', '" + groups[i] + "', 0, 0, 0, 0, 0, 0),") # 0 -> not seen, 1 -> seen

command = command[:-1] #remove final comma

crsr.execute(command)
connection.commit()

command = "DROP TABLE IF exists COUNTIES;"  #create county table
crsr.execute(command)
connection.commit()

command = """CREATE TABLE COUNTIES (
    id INTEGER not null UNIQUE,
    county_name varchar(64) not null,
    belonging_state varchar(64) not null,
    belonging_country varchar(64) not null,
    CONSTRAINT COUNTIES_PK Primary KEY(id)
    );"""

crsr.execute(command)
connection.commit()

connection.close()               








    
