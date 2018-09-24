#!/usr/bin/env python
# encoding: utf-8

# (c) Wiltrud Kessler, 20.9.18

"""
Extract pidgin log files to custom location.
"""

import os  # for traversing file directories
import shutil  # for copying files
import string  # for string substitutions
import re  # for regular expressions
import xml.etree.ElementTree as ET  # for reading the xml file

# Change these settings
pidginfolder = "/home/willita/.purple/"
copyfolder = "./Messenger/"

# Pidgin stores the logs in a subfolder "logs"
logsfolder = os.path.join(pidginfolder, "logs")

# and the accounts in an xml file on the root level of its folder.
accountsfile = os.path.join(pidginfolder, "blist.xml")

# Regex for replacing the timestamp with only the date
# used for the names of the log files (see below in copying)
regex = re.compile(r"\.[-0-9+]+CES*T", re.IGNORECASE)

# Enable debug messages
debug = True

# ===== Create infrastructure, check stuff =====

if not os.path.exists(pidginfolder):
    print("ERROR !! Pidgin folder does not exist: %s" % (pidginfolder))
    exit(1)

if not os.path.exists(logsfolder):
    print("ERROR !! Pidgin log folder does not exist: %s" % (logsfolder))
    exit(1)

# Create diretory to copy the files to
if not os.path.exists(copyfolder):
    os.makedirs(copyfolder)


# ===== Get account names from xml file =====

# Dictionary for names
names = {}

# Read accounts xml file to find names to the messenger ids
# Format:
# <contact>
#   <buddy account="1234" proto='prpl-icq'>
#       <name>54321</name>
#       <alias>Horst</alias>
#       ...
#   </buddy>
# </contact>
if os.path.isfile(accountsfile):

    tree = ET.parse(accountsfile)
    root = tree.getroot()

    # Put all the ids and aliases into a dictionary
    for buddy in root.iter('buddy'):
        id = buddy.find('name').text
        alias = id
        if not buddy.find('alias') is None:
            alias = buddy.find('alias').text
            alias = alias.replace(" ", "_")
        names[id] = alias
else:
    print("Warning ! Account file not found: %s" % (accountsfile))

# ===== Copy the log files =====

# Count how many files we create
filescopied = 0
filesappended = 0

# Go through the directory tree below the log folder.
# The first level is protocol (icq, jabber, ...)
for protocol in os.listdir(logsfolder):
    path = os.path.join(logsfolder, protocol)

    # Each protocol then has a folder for each account I have there.
    for account in os.listdir(path):
        path = os.path.join(path, account)

        # Then we have folders for each contact and these folders
        # contain the actual log files.
        for contact in os.listdir(path):

            # Skip ".system" folder with system logs
            if contact.startswith('.'):
                continue

            path = os.path.join(path, contact)

            # Replace the id of the contact with the name.
            # If the name does not exist, use the contact id.
            if contact in names:
                name = names[contact]
            else:
                name = contact
                print("Warning ! Contact %s not found!" % (contact))

            # Now for the actual files!
            for logf in os.listdir(path):

                # Replace the timestamp with only the date.
                # Pidgin format: 2018-08-02.164514+0200CEST.txt
                # Our format: name_18-08-02.txt
                date = string.replace(logf, '20', '', 1)
                date = regex.sub("", date)

                # Get name of the new file and check if it exists
                newfilename = os.path.join(copyfolder, name + "_" + date)

                # If the file already exists, append the current file content
                # to the existing file (separated by newline).
                # Otherwise, just copy the file to the new location.
                if os.path.isfile(newfilename):
                    thefile = open(newfilename, 'a')
                    thefile.write("\n")
                    shutil.copyfileobj(open(os.path.join(path, logf)), thefile)
                    thefile.close()
                    filesappended = filesappended + 1
                    if debug:
                        print("Debug: Append to file %s for original file %s." %
                                (newfilename, os.path.join(path, logf)))
                else:
                    shutil.copy(os.path.join(path, logf), newfilename)
                    filescopied = filescopied + 1
                    if debug:
                        print("Debug: Create file %s for original file %s." %
                                (newfilename, os.path.join(path, logf)))

            # Reset path (remove contact name)
            path = os.path.dirname(path)

        # Reset path (remove account name) -- usually shouldn't matter
        path = os.path.dirname(path)


# ===== Finished, cleanup =====

print("Done, wrote %d files, appeded %d times." % (filescopied, filesappended))
