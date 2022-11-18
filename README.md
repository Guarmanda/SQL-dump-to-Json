# SQL-dump-to-Json

This only takes the text from sql file and get everything for it, no need of a mysql database or anything worst
At the top of the file, there is three variables:
```
Json_file = "database.json"
sql_file = "traceforum.sql"
indent = 0 # little file with no indentation and no \n. intent > 0 = bigger file
```
Change these to what you want, and have fun.

This script should be able to handle any SQL-dump / creation script, storing all CREATE and INSERT commands in json.
I made it because I needed it for a university practical work, and I was like, oh, it's pretty good, let's share it, I found nothing good on the internet for this

```diff
- If you got a script that doesn't work with this script, please take the time to create an issue
- with the given script in it (or at least a part of it if datas are sensitive)
```

