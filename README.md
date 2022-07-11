# Bird Database
SQL Database with Python to store person bird sightings.

# Overview
This database is meant for storing EBird sightings in a locally stored database to view
the data in a more customizable way. Note that there currently aren't many features,
as the project is still in progress and even a few current features aren't fully
developed. 

# How to Use
To use, download all the files and place them in the same directory. The DB file is an 
empty database that will be created for you later. You will need to download a recent 
version of SQLite (found here: https://sqlitebrowser.org/), and then run the DatabaseWrite.py to
create the Database structure. Then you will need to download your eBird data, which is obtained 
with EBird's "Download my data" function. Make sure the CSV file is named "MyEBirdData.csv", or \
change the default name in the python code. Finally, run the SQL_App.py file's import data tool to 
import the data into the database (this may take a while if it hasn't been done before). 

# License
[MIT](https://choosealicense.com/licenses/mit/)
