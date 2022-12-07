# SQL-dump-to-Json

This only takes the text from sql file and get everything for it, no need of a mysql database or anything worst
At the top of the file, there is three variables:
```
Json_file = "database_content.json"
Json_file2 = "database_tables_and_columns.json"
sql_file = "traceforum.sql"
indent = 0 # little file with no indentation and no \n. intent > 0 = bigger file
```

The output is a little bit particular, but th file is slightly smaller than other json outputs, here's why:
```
#table name
"activite": [
        # column names
        [
            "IDAct",
            "Titre",
            "TypeAct",
            "IDCat"
        ],
        # all other lines are column values
        [
            "1",
            "Visiter un lien hypertexte",
            "0",
            "1"
        ],
 ```
 
 With this, column names are written only one time, but you have to get then manually when taking the data with a script
 
 

Change these to what you want, and have fun.

This script should be able to handle any SQL-dump / creation script, storing all columns in CREATE commands and table contents in INSERT commands in json.
I made it because I needed it for a university practical work, and I was like, oh, it's pretty good, let's share it, I found nothing good on the internet for this

```diff
- If you got a script that doesn't work with this script, please take the time to create an issue
- with the given script in it (or at least a part of it if datas are sensitive)
```

