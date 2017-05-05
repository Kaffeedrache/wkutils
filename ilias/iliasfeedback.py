#!/usr/bin/env python
# encoding: utf-8

# (c) Wiltrud Kessler, 13.11.15

"""
From a file with feedback for all students,
create the folder structure ILIAS wants for feedback files.
"""

import sys
import os
import zipfile


def writeFeedbackFile (outputFolder, sheet, exercise, filename, studentname, feedbacktext, points, simulate = False):

      print "Create feeback file for student %s" % studentname

      # Set names
      foldername =  outputFolder + os.sep + studentname
      outputFilename = foldername + os.sep
      index = studentname.find("_")
      if index > 0:
         nametouse = studentname[0:studentname.find("_")].replace(" ","")
      else:
         nametouse = studentname.replace(" ","")
      if sheet != None and exercise != None:
         outputFilename +=  filename + "_%s-%s_%s.txt" % (sheet, exercise, nametouse)
      else:
         outputFilename += filename + "_%s.txt" % (nametouse)
      print outputFilename

      # Create feedback folder and file
      if not simulate:
         if not os.path.exists(foldername): # it shouldn't exist, but you never know
               os.makedirs(foldername)
         outputFile = open(outputFilename, "w")

      if feedbacktext.strip() == "":
         print "Warning: Feedback for student %s is empty!" % studentname

      if points == "":
         print "Warning: Student %s has no total points!" % studentname


      # Write the feedback to the file and close the file
      if not simulate:
         outputFile.write("# %s \n" % studentname)
         outputFile.write("%s" % feedbacktext)
         outputFile.write("= %s" % points)
         outputFile.close()



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


def getILIASID(iliasIDs, studentname):
   #  studentname = studentname.replace("  "," ")
   #  names = studentname.split(" ")
   #  if len(names) > 2:
      #  print "ERROR!! Student has more than 2 names!"
   #  nametuple = (names[0].strip(), names[1].strip())
   id = iliasIDs.get(studentname)
   if id != None:
      return id
   #  nametuple = (names[1].strip(), names[2].strip())
   #  id = iliasIDs.get(nametuple)
   #  return id




#### MAIN ####

#  simulate = True
simulate = False

sheet = None
exercise = None

if len(sys.argv)<4:
    print "Usage: python iliasfeedback.py iliasIDfile inputFilename outputFilename"
    print "                     [-s sheetnumber] [-e exercisenumber] [-d]"
    sys.exit(1)

iliasIDfile = sys.argv[1]
inputFilename = sys.argv[2]
outputFilename = sys.argv[3]

for i in range(4,len(sys.argv)):
    arg = sys.argv[i]
    print i, arg
    if arg == "-s":
        sheet = sys.argv[i+1]
    if arg == "-e":
        exercise = sys.argv[i+1]
    if arg == "-d":
        simulate = True



# -- start --

# Read ILIAS ids
# File format: <Name as written in feedback file> \t <name that ILIAS wants>
print "Read ILIAS ids from: " + iliasIDfile
iliasIDs = {}
for line in open(iliasIDfile):
   parts = line.split("\t")
   if len(parts) >= 2:
      iliasIDs[parts[0]] = parts[1].strip()


# Open the file with the feedback text
print "Read input file " + inputFilename
inputFile = open(inputFilename) or die

# Create the output folder only if it doesn't exist,
# otherwise throw an error to avoid overwriting anything important
outputFolder = outputFilename.replace(".txt","")
outputZipFilename = outputFolder + ".zip"
if not simulate:
   if not os.path.exists(outputFolder):
      os.makedirs(outputFolder)
      print "Create folder " + outputFolder
   else:
      print "ERROR!! The output folder %s already exists!" % outputFolder
      exit(1)
else:
   print "SIMULATE, Would create folder " + outputFolder


preamble = True
studentname = None
instudent = False
feedbacktext = ""
lineno = 0

# Iterate through it
for line in inputFile:

   lineno += 1

   # Look for end of preamble and start of evaluation document
   if line.strip() =="#==start==":
      preamble = False
      print "Preamble ends in line %d\n" % (lineno)
      continue


   # Look for end of document
   if line.strip() =="#==end==":
      print "Document ends in line %d\n" % (lineno)
      break

   # Skip whatever is written in the preamble
   if preamble:
      continue


   # == <student> start ==
   # Name of student is in a line that starts with #
   if line[0] == "#":
      studentname = line[1:].strip()
      if instudent:
         print "ERROR!! New student %s started in line %d before old one was done! Now what??" % (studentname, lineno)
         # TODO and now??
      instudent = True
      continue


   # == <student> end ==
   # Student official part ends with =
   if  line[0] == "=" and instudent:
      if studentname == "":
         print "ERROR!! The student has no name!"
      else:
         thename = getILIASID(iliasIDs,studentname)
         if thename == None:
            print "ERROR!! No ILIAS ID found for student '" + studentname + "'"
            thename = studentname
         else:
            writeFeedbackFile(outputFolder, sheet, exercise, outputFilename, thename, feedbacktext, line[1:].strip(), simulate)

      feedbacktext = ""
      instudent = False
      studentname = ""
      continue

   # == <student> content ==
   # The feedback text for this student
   if instudent: # and not the start
      feedbacktext += line


   # Ignore empty lines outside of <student>
   #  if line == "" and not instudent:
      #  continue

   # Ignore comment lines outside of <student>
   #  if line[0] == "%" and not instudent:
      #  continue


if instudent:
   print "ERROR!! Have leftover student %s!" % (studentname)
   writeFeedbackFile(outputFolder, sheet, exercise, outputFilename, studentname, feedbacktext, "", simulate)




# Zip the whole folder
if not simulate:
   print '\nCreate zip archive ' + outputZipFilename
   zf = zipfile.ZipFile(outputZipFilename, mode='w')
   try:
      addFolderToZip(zf, outputFolder)
   finally:
      zf.close()

print "\ndone!"
