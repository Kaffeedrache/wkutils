#!/usr/bin/env python
# encoding: utf-8

# (c) Wiltrud Kessler, 13.11.15

"""
From a file with information about an exercise with sheets, deadlines and so on,
create the folder structure ILIAS needs to import an exercise.
"""

import sys
import os
import zipfile
from datetime import datetime
from lxml import etree


# Do not use pretty_print=True, as these files cannot be read by ILIAS
def writeXmlFile(xmlDom, filename):
   outFile = open(filename, 'w')
   xmlDom.write(outFile, encoding='utf-8', xml_declaration=True, pretty_print=True)
   outFile.close()


def writeXmlManifest (title, filename):
   print("Write xml manifest into %s" % (filename))

   # Create DOM
   x = etree.Element('Manifest',
         MainEntity="exc",
         Title=title,
         TargetRelease="5.2.0",
         InstallationId="0",
         InstallationUrl="https://ilias3.uni-stuttgart.de")
   doc = etree.ElementTree(x)
   etree.SubElement(x, 'ExportFile',
         Component="Modules/Exercise",
         Path="Modules/Exercise/set_1/export.xml")

   # Write to file
   writeXmlFile(doc, filename)


def writeXmlDescription (title, description, assignments, filename):
   print("Write xml description into %s" % (filename))
   id = '1629130'

   # Create DOM - first some intro stuff
   ns_exp = "http://www.ilias.de/Services/Export/exp/4_1"
   ns_ds = "http://www.ilias.de/Services/DataSet/ds/4_3"
   ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
   etree.register_namespace("exp", ns_exp)
   etree.register_namespace("ds", ns_ds)
   etree.register_namespace("xsi", ns_xsi)
   schemaLocation = "http://www.ilias.de/Services/Export/exp/4_1 https://ilias3.uni-stuttgart.de/xml/ilias_export_4_1.xsd http://www.ilias.de/Modules/Exercise/exc/5_2 https://ilias3.uni-stuttgart.de/xml/ilias_exc_5_2.xsd http://www.ilias.de/Services/DataSet/ds/4_3 https://ilias3.uni-stuttgart.de/xml/ilias_ds_4_3.xsd"
   x = etree.Element('{%s}Export' % (ns_exp),
         InstallationId="0",
         InstallationUrl="https://ilias3.uni-stuttgart.de",
         Entity="exc",
         SchemaVersion="5.2.0",
         TargetRelease="5.2.0",
         #xsi:schemaLocation=,
         xmlns="http://www.ilias.de/Modules/Exercise/exc/5_2",
         attrib={"{%s}schemaLocation" % (ns_xsi): schemaLocation}
         )
   doc = etree.ElementTree(x)
   y = etree.SubElement(x, '{%s}ExportItem' % (ns_exp), Id=id) # TODO ID
   z = etree.SubElement(y, '{%s}DataSet' % (ns_ds),
         InstallationId="0",
         InstallationUrl="https://ilias3.uni-stuttgart.de",
         TopEntity="exc")

   # Title and desription of the whole exercise
   t = etree.SubElement(z, '{%s}Rec' % (ns_ds), Entity="exc")
   u = addXmlSubnode(t, 'Exc')
   addXmlSubnode(u, 'Id', id)
   addXmlSubnode(u, 'Title', title)
   addXmlSubnode(u, 'Description', description)
   addXmlSubnode(u, 'PassMode', 'all')
   addXmlSubnode(u, 'PassNr')
   addXmlSubnode(u, 'ShowSubmissions', '0')
   addXmlSubnode(u, 'ComplBySubmission', '0')
   addXmlSubnode(u, 'Tfeedback', '7')

   # Each individual assignment
   exnr = 1;
   for a in assignments:
      t = etree.SubElement(z, '{%s}Rec' % (ns_ds), Entity="exc_assignment")
      u = addXmlSubnode(t, 'ExcAssignment')
      addXmlSubnode(u, 'Id', '1234%d' % (exnr))
      addXmlSubnode(u, 'ExerciseId', id)
      addXmlSubnode(u, 'Type', '1')
      addXmlSubnode(u, 'Deadline', getStringDate(a.endDate)) # Deadline
      addXmlSubnode(u, 'Deadline2', getStringDate(a.graceDate)) # Grace period for late submissions
      addXmlSubnode(u, 'Instruction', a.description)
      addXmlSubnode(u, 'Title', a.title)
      addXmlSubnode(u, 'StartTime', getStringDate(a.startDate)) # Start of visibility for exercise
      addXmlSubnode(u, 'Mandatory', '0') # 0 = optional, 1 = mandatory
      addXmlSubnode(u, 'OrderNr', str(exnr*10)) # Sorting of exercises
      addXmlSubnode(u, 'TeamTutor', '0')
      addXmlSubnode(u, 'MaxFile')
      addXmlSubnode(u, 'Peer', '0')
      addXmlSubnode(u, 'PeerMin', '2')
      addXmlSubnode(u, 'PeerDeadline')
      addXmlSubnode(u, 'PeerFile', '0')
      addXmlSubnode(u, 'PeerPersonal', '0')
      addXmlSubnode(u, 'PeerChar')
      addXmlSubnode(u, 'PeerUnlock', '0')
      addXmlSubnode(u, 'PeerValid', '1')
      addXmlSubnode(u, 'PeerText', '1')
      addXmlSubnode(u, 'PeerRating', '1')
      addXmlSubnode(u, 'PeerCritCat')
      addXmlSubnode(u, 'FeedbackFile')
      addXmlSubnode(u, 'FeedbackCron', '0')
      addXmlSubnode(u, 'FeedbackDate', '1')
      addXmlSubnode(u, 'Dir', 'Modules/Exercise/set_1/expDir_1/dsDir_%d' % (exnr*2-1))
      addXmlSubnode(u, 'FeedbackDir', 'Modules/Exercise/set_1/expDir_1/dsDir_%d'  % (exnr*2))
      exnr = exnr + 1

   # Write to file
   writeXmlFile(doc, filename)


class Assignment:
   title = None
   description = None
   startDate = None
   endDate = None
   graceDate = None


def addXmlSubnode(parent, name, text = None):
   f = etree.SubElement(parent, name)
   if text != None:
      f.text = text
   return f


def addFolderToZip(zip_file, folder):

   for file in os.listdir(folder):
      full_path = os.path.join(folder, file)
      #  full_path = file
      if os.path.isfile(full_path):
         print 'File added: ' + str(full_path)
         zip_file.write(full_path)
      elif os.path.isdir(full_path):
         print 'Entering folder: ' + str(full_path)
         addFolderToZip(zip_file, full_path)


def convertToDate(datestring):
   if datestring != "":
      return datetime.strptime(datestring, '%Y-%m-%d')
   else:
      return None

# Write out to Xml in ILIAS-conform format
# Date format: 2017-10-17 15:50:00
def getStringDate(date):
   if date == None:
      return None
   else:
      return date.strftime('%Y-%m-%d %H:%M:%S')


#### MAIN ####


# -- parse command line arguments --

if len(sys.argv)<2:
    print "Usage: python iliasfeedback.py inputFilename outputFilename"
    sys.exit(1)

inputFilename = sys.argv[1]
outputFilename = sys.argv[2]


# -- start --


# Open the input file with the exercise definition
print "Read input file " + inputFilename
inputFile = open(inputFilename) or die

# Create the output folder only if it doesn't exist,
# otherwise throw an error to avoid overwriting anything important
outputFolder = outputFilename.replace(".txt","")
outputZipFilename = outputFolder + ".zip"
if not os.path.exists(outputFolder):
   os.makedirs(outputFolder)
   print "Create folder " + outputFolder
#else:
#   print "ERROR!! The output folder %s already exists!" % outputFolder
#   exit(1)


# Read the input file and get the information
title = ""
description = ""
assignments = []
thisassignment = None
lineno = 0

for line in inputFile:

   lineno += 1
   line = line.strip().decode('utf-8')

   # Skip empty lines
   if line == "":
      continue;

   # Title of exercise
   if line[0] == "#":
      title = line[1:].strip()
      continue;

   # Core data for an assignment
   elif line[0] == "*":

      # Add the old assignment to the list of assignments
      if thisassignment != None:
         assignments.append(thisassignment) # add

      # Read the new assignment
      thisassignment = Assignment() # reset
      parts = line[1:].strip().split("\t")
      print parts
      thisassignment.title = parts[0] # name
      if len(parts) > 1: # start date
         thisassignment.startDate = convertToDate(parts[1])
      if len(parts) > 2: # end date
         thisassignment.endDate = convertToDate(parts[2])
      if len(parts) > 3: # grace date
         thisassignment.graceDate = convertToDate(parts[3])
      print thisassignment

   # Description for an assignment or the whole exercise
   # (may contain several lines)
   else:
      if thisassignment == None: # are not inside an assignment = for whole
         description += line
      else:
         if thisassignment.description == None:
            thisassignment.description = line
         else:
            thisassignment.description += line
         pass


# Treat last assignment
if thisassignment != []:
      assignments.append(thisassignment) # add

print title
print description
print assignments

writeXmlManifest(title, outputFolder + "/manifest.xml")
writeXmlDescription(title, description, assignments, outputFolder + "/export.xml")


# Zip the whole folder
simulate = True
if not simulate:
   print '\nCreate zip archive ' + outputZipFilename
   zf = zipfile.ZipFile(outputZipFilename, mode='w')
   try:
      addFolderToZip(zf, outputFolder)
   finally:
      zf.close()

print "\ndone!"
