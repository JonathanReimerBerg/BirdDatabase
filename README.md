# Bird Database
SQL Database with Python to store person bird sightings.

# Overview
This database is meant for storing EBird sightings in a locally stored database to view
the data in a more cutomizable way. Note that there currently aren't many features,
as the project is still in progress and even a few current features aren't fully
developed. 

# How to Use
To use, download the eBird_Taxonomy_v2021.csv, SQL_App.py, and DatabaseWriter.py files. The DB
file is only there to show you what the databse will look like once created. You will need to create 
a databse using SQLite (found here: https://sqlitebrowser.org/), and then run the DatabaseWrite.py to
create the Database structure. Then you can use the SQL_App.py's import data function to add your personal
data, which is obtained with EBird's "Download my data" function. Make sure the CSV file is named 
"MyEBirdData.csv", or change the default name in the python code. 

# License
[MIT](https://choosealicense.com/licenses/mit/)
