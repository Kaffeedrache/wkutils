#!/usr/bin/env python
# encoding: utf-8

# (c) Wiltrud Kessler, 21.9.18

"""
Extract skype logs to custom location.
Works for Skype < Verison 8
"""

import os  # for traversing file directories
import sqlite3  # for accessing the data in the sqlite database
from datetime import datetime  # to compare dates


# Change these settings
skypefolder = "/home/willita/tmp/.Skype/"
copyfolder = "./Skype/"


searchfolder = skypefolder
contactfile = "contacts.txt"
dbfilename = "main.db"
sqlcontacts = "SELECT skypename, aliases, fullname from Contacts;"
sqlpartners = "SELECT DISTINCT(dialog_partner) FROM Messages;"
sqlmessages = "SELECT author, from_dispname, datetime(timestamp, 'unixepoch') as date, body_xml FROM Messages WHERE dialog_partner = '%s' ORDER BY timestamp;"



# ===== Create infrastructure, check stuff =====

if not os.path.exists(skypefolder):
    print("ERROR !! Skype folder does not exist: %s" % (skypefolder))
    exit(1)

# Create diretory to copy the files to
if not os.path.exists(copyfolder):
    os.makedirs(copyfolder)


# ===== Extract files from database =====

accountschecked = 0
filescreated = 0

# Use the main.db files for every skype account individually
for account in os.listdir(searchfolder):

    # Skip files
    if not os.path.isdir(os.path.join(searchfolder, account)):
        continue

    # Ignore the special folder for data
    if account == 'DataRv':
        continue

    # Extract stuff from this account
    accountschecked = accountschecked + 1

    # Find the file with the database and connect to it
    dbfile = os.path.join(searchfolder, account, dbfilename)
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()

    # Get all contacts and print them to a contact file
    # We use skype id, alias and full name.
    cursor.execute(sqlcontacts)
    result = cursor.fetchall()
    f = open(os.path.join(copyfolder, account + "_" + contactfile), "w+")
    for r in result:
        skypeid = r[0]
        alias = r[1] or u""
        name = r[2] or u""
        text = skypeid + u"\t" + alias + u"\t" + name + u"\n"
        f.write(text.encode('utf-8'))
    f.close()

    # Get all dialog partners
    cursor.execute(sqlpartners)
    partners = cursor.fetchall()

    # For each dialog partner, get all messages, sorted by date and extract them
    for person in partners:

        # Get all messages
        cursor.execute(sqlmessages % person[0])
        chats = cursor.fetchall()

        # Go through the messages and write them to one file per date
        lasttime = datetime.now()
        for chat in chats:

            # The actual chat message. Skip empty messages
            content = chat[3]
            if content is None:
                continue

            # Name to display (if none, use the Skype id)
            name = chat[1] or chat[0]

            # Time of the chat
            # Convert to datetime object to be able to compare
            time = chat[2]
            thetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

            # Check if we still have the same date
            # If not, create a new file with the filename
            # contactname_12-03-04.txt
            if not thetime.date() == lasttime.date():
                f.close()  # close old file
                filename = os.path.join(copyfolder, person[0] + "_" + thetime.date().strftime("%y-%m-%d") + ".txt")
                if os.path.isfile(filename):
                    print("WARNING !! File %s exists!" % (filename))
                print(filename)
                f = open(filename, "w+")  # create new file
                lasttime = thetime
                filescreated = filescreated + 1

            # Write the chat to the file
            text = name + u" [" + time + "]: " + content + "\n"
            f.write(text.encode('utf-8'))

        # Close the last file
        f.close()


    # Close connection to database
    connection.close()




# ===== Finished, cleanup =====

print("Done, checked %d accounts, created %d files." % (accountschecked, filescreated))
