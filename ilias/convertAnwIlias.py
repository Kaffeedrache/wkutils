#!/usr/bin/env python
# encoding: utf-8

# (c) Wiltrud Kessler, 12.12.16

"""
Converts the information about attendance from ANW files (csv)
into a feedback file that I can then upload to ILIAS.
"""

from datetime import date
import os, sys

limitNonattendance = 20 # maximum non-attendence percentage
limitNonattendanceWithE = 25 # maximum non-attendence percentage



#### MAIN ####

if len(sys.argv)<3:
    print "Usage: python convertAnwIlias outputFilename inputFilename+"
    sys.exit(1)

outputFilename = sys.argv[1]
inputFilenames = sys.argv[2:]


# Create the output folder only if it doesn't exist,
# otherwise throw an error to avoid overwriting anything important
if os.path.isfile(outputFilename):
   print sys.argv
   if len(sys.argv) <= 1 or sys.argv[1] != "f": # force with parameter 'f'
      print "file exists, force overwrite [f]?"
      a = input()
      if a != 'f':
         die
outputFile = open(outputFilename,"w")
outputFile.write( "#==start==\n\n\n" )


for inputFilename in inputFilenames:

   print "Read input file " + inputFilename
   inputFile = open(inputFilename) or die

   firstline = True
   dates = {}

   # Iterate through it
   for linebyte in inputFile:

      line = linebyte.decode('latin-1')

      # Skip empty lines
      if line == "":
         continue

      # We have a ; separated file, split
      line = line.strip()
      parts = line.split(";")

      # Get the number of dates for the course and the
      # dates themselves from the first line
      if firstline:
         firstline = False
         for i in range(12,len(parts)):
            dates[i] = parts[i]
         total = float(len(parts[12:]))-1 # there's a ; at the end!
         continue

      # Get the easy parts from csv (name, attendances)
      name = parts[2] + " " + parts[3]
      csvAttendanceTimes = int(parts[8])
      csvAttendancePercentage = float(parts[10].replace(",","."))
      csvAttendanceTimesWithE = int(parts[9])
      csvAttendancePercentageWithE = float(parts[11].replace(",","."))

      # Get the attendance for each date
      # csv has "x" for attended, "." for did not attend,
      # "e" for sick with doctor's note
      # "?" for future dates or dates not entered
      there = 0
      away = 0
      sick = 0
      sessionsHad = 0
      datesNotPresent = ""
      datesNotPresentWithE = ""
      for i in range(12,len(parts)):
         part = parts[i]
         if part == "x":
            there = there + 1
            sessionsHad = sessionsHad + 1
         elif part == ".":
            away = away + 1
            sessionsHad = sessionsHad + 1
            datesNotPresent += dates[i] + ", "
         elif part == "e":
            sick = sick + 1
            sessionsHad = sessionsHad + 1
            datesNotPresentWithE +=  dates[i] + ", "


      # Write name
      outputFile.write( "# %s \n" % (name.encode('utf-8')) )
      outputFile.write( "Stand %s \n" % (date.today()) )


      # Calcuate attendance
      if sessionsHad == 0: # has never been there, nothing entered
         attendancePercentage = 0
         attendancePercentageWithE = 0
         nonqualified = True
      else:
         attendancePercentage = float(there) / sessionsHad * 100
         attendancePercentageWithE = float(there+sick) / sessionsHad * 100
         maximumNonAttendance = limitNonattendance * total / 100
         maximumNonAttendanceWithE = limitNonattendanceWithE * total / 100
         nonqualified = (away > maximumNonAttendance) or (there == 0) or ((away+sick) > maximumNonAttendanceWithE)

      # Sanity checks
      if csvAttendanceTimes != there:
         print "-- Fehler Anwesenheit, nicht gleich wie csv: %d (ich) vs. %d (csv)" % (there, csvAttendanceTimes)
      if csvAttendancePercentage != round(attendancePercentage,2):
         print "-- Fehler Anwesenheit Prozent, nicht gleich wie csv: %f (ich) vs. %f (csv)" % (attendancePercentage, csvAttendancePercentage)

      if csvAttendanceTimesWithE != (there+sick):
         print "-- Fehler Anwesenheit, nicht gleich wie csv: %d (ich) vs. %d (csv)" % (there, csvAttendanceTimes)
      if csvAttendancePercentageWithE != round(attendancePercentageWithE,2):
         print "-- Fehler Anwesenheit Prozent, nicht gleich wie csv: %f (ich) vs. %f (csv)" % (attendancePercentage, csvAttendancePercentage)



      # Print statistics (stdout and file)
      if sessionsHad > 0:
         if datesNotPresent == "":
            datesNotPresent = "-"
         outputFile.write( "Anzahl eingetragene Termine = %d; Anwesend = %d; Abwesend/entschuldigt = %d; Abwesend/unentschuldigt = %d;\n" % (sessionsHad, there, sick, away) )
         if sick > 0:
            outputFile.write("Anwesenheit = %.2f %%  (%.2f %%) \n" % (attendancePercentage, attendancePercentageWithE) )
            outputFile.write( "Entschuldigt abwesend am: %s \n" % (datesNotPresentWithE) )
         else:
            outputFile.write("Anwesenheit = %.2f %%\n" % (attendancePercentage) )
         outputFile.write( "Unentschuldigt abwesend am: %s \n" % (datesNotPresent) )
      else:
         outputFile.write( "Anwesenheit: 0 \n" )

      qualifyString = ""
      if nonqualified:
         outputFile.write("Leider ist die qualifizierte Teilnahme nicht mehr moeglich, da 80% Anwesenheit nicht mehr erreichbar sind.\n")
         qualifyString = "[non-qualified]"
      outputFile.write( "=%d\n\n" % (not nonqualified) )

      print "%s -- bisher=%d; da=%d; krank=%d, weg=%d;  ->   %.2f (%.2f) %s" % (name.encode('utf-8'), sessionsHad, there, sick, away, attendancePercentage, attendancePercentageWithE, qualifyString) # DEBUG




outputFile.close()
print "\ndone!"
