#!/usr/bin/env python
# original source: https://gist.github.com/0xF1/78b221a32bf4e0ef494a
# Modified by: Valentin Girod
# This file originally could not really handle sql dump and was designed for only one table
# Only parse_values, is_insert where kept, the rest was removed or modified a lot. parse_values was also modified a lot to handle multiple 
# tables
# Modifications: made it work with any dump sql file by:
# - concatenating lines not starting with create, set or insert, 
# - removing comments and empty lines
# - fixing lack of spaces after "VALUES" or before "("
# - removing the need of '`' character before VALUES word because many dump files aren't built like this
# - added managing of "CREATE TABLE" statements
# whole database datas (inserts) is in "transactions" dictionary after script execution and sent to a json file
# tables and columns are stored in 'tables' dictionary and sent to the same json file
import csv
import json
import sys
import re

# tables and rows
tables = {}
transactions = {}
Json_file = "database_content.json"
Json_file2 = "database_tables_and_columns.json"
sql_file = "traceforum.sql"
indent = 0

# method to handle CREATE TABLE statements and put them in tables dict as "key: [column_name, column_name, ...]"
# column_name can be found using findall separated by comas
def parse_create_table(line):
    table_name = re.search('`(.+?)`', line).group(1)
    columns =   re.findall('`(.+?)`', line)
    tables[table_name] = []
    tables[table_name].append(columns)
# This prevents prematurely closed pipes from raising
# an exception in Python
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

# The csv file might contain very huge fields,
# therefore increase the field_size_limit
csv.field_size_limit(sys.maxsize)

def is_create(line):
    """
    Returns true if the line begins a SQL create statement.
    """
    return line.startswith('CREATE TABLE') or False

def is_insert(line):
    """
    Returns true if the line begins a SQL insert statement.
    """
    return line.startswith('INSERT INTO') or False


def get_values(line):
    """
    Returns the portion of an INSERT statement containing values
    """
    return line.partition(' VALUES ')[2]

def get_table_name(line):
    """
    Given a line from a MySQL INSERT statement, return the table name
    """
    return line.partition('`')[2].partition('`')[0]


def parse_values(line, outfile):
    values = get_values(line)
    table_name = get_table_name(line)
    global transactions
    if table_name not in transactions.keys():
        transactions[table_name] = []
        # get table columns from line
        columns = re.findall('`(.+?)`', line)
        # remove first column (id) because it's table name
        columns.pop(0)
        print(table_name)
        print(columns)
        # add columns to transactions dict
        transactions[table_name].append(columns)


    """
    Given a file handle and the raw values from a MySQL INSERT
    statement, write the equivalent CSV to the file
    """
    latest_row = []

    reader = csv.reader([values], delimiter=',',
                        doublequote=False,
                        escapechar='\\',
                        quotechar="'",
                        strict=True
                        )

    for reader_row in reader:
        for column in reader_row:
            # If our current string is empty...
            if len(column) == 0:
                latest_row.append('""')
                continue
            # If our string starts with an open paren
            if column[0] == "(":
                # Assume that this column does not begin
                # a new row.
                new_row = False
                # If we've been filling out a row
                if len(latest_row) > 0:
                    # Check if the previous entry ended in
                    # a close paren. If so, the row we've
                    # been filling out has been COMPLETED
                    # as:
                    #    1) the previous entry ended in a )
                    #    2) the current entry starts with a (
                    if latest_row[-1][-1] == ")":
                        # Remove the close paren.
                        latest_row[-1] = latest_row[-1][:-1]
                        new_row = True
                # If we've found a new row, write it out
                # and begin our new one
                if new_row:
                    json_row = latest_row
                    transactions[table_name].append(json_row)
                    latest_row = []
                # If we're beginning a new row, eliminate the
                # opening parentheses.
                if len(latest_row) == 0:
                    column = column[1:]
            # Add our column to the row we're working on.
            latest_row.append(column)
        # At the end of an INSERT statement, we'll
        # have the semicolon.
        # Make sure to remove the semicolon and
        # the close paren.
        if latest_row[-1][-2:] == ");":
            latest_row[-1] = latest_row[-1][:-2]
            json_row = latest_row
            transactions[table_name].append(json_row)


def main():
    """
    Parse arguments and start the program
    """
    # Iterate over all lines in all files
    # listed in sys.argv[1:]
    # or stdin if no args given.
    # open and read sql file
    file = open(sql_file, "r")

    # replace all "\n(" with "(" in file
    file = [line.replace('\\n(', '(') for line in file]
    # remove all sql comments
    file = [line for line in file if not line.startswith('--')]
    # remove also /* comments
    file = [line for line in file if not line.startswith('/*')]
    # remove all empyt lines and \n at end of lines
    file = [line.strip() for line in file if line.strip() != '']
    # replace ") ENGINE.*;" with "); in lines"
    file = [re.sub(r'\) ENGINE.*;', ');', line) for line in file]
    # replace all ", " with ","
    file = [line.replace(', ', ',') for line in file]
    # If line doesn't start with create, set or insert, concatenante it with previous line and remove it
    # while there is lines not starting with create, set or insert
    decalage = 0
    for i in range(len(file)):
        if not file[i].startswith('CREATE') and not file[i].startswith('SET') and not file[i].startswith('INSERT'):
            file[i-decalage-1] = file[i-decalage-1] + file[i]
            file[i] = ''
            decalage += 1
        else:
            decalage = 0
    # after this, fix lack of spaces after "VALUES" or before "("
    file = [re.sub(r'VALUES\(', 'VALUES (', line) for line in file]
    # remove all empty lines
    file = [line for line in file if line != '']


    line_num = 1
    for line in file:
        # Look for an INSERT statement and parse it.
        if is_create(line):
            parse_create_table(line)

        if is_insert(line):
            parse_values(line, sys.stdout)
        line_num += 1

    # Write out the transactions in json file with indentation
    with open(Json_file, 'w') as fp:
        file2 = open(Json_file2, "w")
        if(indent > 0):
            json.dump(transactions, fp, indent=indent)
            json.dump(tables, file2, indent=indent)
        else:
            json.dump(transactions, fp)
            json.dump(tables, file2)




if __name__ == "__main__":
    main()
