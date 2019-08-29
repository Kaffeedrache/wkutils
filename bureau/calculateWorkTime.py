#!/usr/bin/env python
# encoding: utf-8

# (c) Wiltrud Kessler, 26.9.11

"""
Berechnung der Arbeitszeit SOLL und IST.
"""


printWeek = True
printMonth = True



WEEK_WORKTIME = 40 # work hours in a normal week
WEEK_WORKDAYS = 5 # work days in a normal week


from datetime import datetime
from datetime import time
from datetime import timedelta
import re
import sys


def getHours (timedeltaValue):
   """
   Converts the given timedelta into hours and returns a formatted String
   (decimal representation of hours, e.g., 2,5 h = 2h 30s).
   """
   return "%.2f" % (timedeltaValue.total_seconds()/3600)



def getMonthName (filename):
   """
   Extracts the name of the month from the given filename/path
   (assumes /path/to/file/name_year-month.txt).
   """
   #
   m = re.search('-([0-9]+).txt', filename)
   if m != None:
      return m.group(1)
   else:
      return "current"


def getYear (filename):
   """
   Extracts the name of the year from the given filename/path
   (assumes /path/to/file/name_year-month.txt).
   """
   m = re.search('_([0-9]+)-', filename)
   if m != None:
      return m.group(1)
   else:
      return filename


def printDay (date, spentTime, dailyWorkTime):
   """
   Printout a day.
   """
   message = ""
   minimumSpentTime = dailyWorkTime*0.5
   if spentTime < timedelta(hours=minimumSpentTime):
      message = "        !!less than %.2fh!!" % (minimumSpentTime)
   print "%s spent time: \t%s%s" % (date, spentTime, message)


def printTotal (spentTime, expectedTime, workdays = 0):
   """
   Printout a total.
   """
   overTime = spentTime - expectedTime
   print "Total spent time:\t%s\t (should be %s => %s)" % (getHours(spentTime), getHours(expectedTime), getHours(overTime))
   if workdays > 0:
      print "Work days: %d" % (workdays)



# End of week, print week summary
def printWeekSummary (weekTimes, ghostWeekTime, spentTimeWeek, dailyWorkTime, workdaysPerWeek):

   print ">>> week ---"
   print "This week work time: "

   # Print the times for each day
   for day in sorted(weekTimes):
      spentTimeDay = weekTimes.get(day)
      printDay(day, spentTimeDay, dailyWorkTime)

   # Print the time spent on ghost days (if there is any)
   if (ghostWeekTime > timedelta()):
      printDay("ghost days", ghostWeekTime, 0)

   # Error: typo in day causes one day to count twice
   if len(weekTimes) > workdaysPerWeek:
      print "!!!!! ERROR !!!!! this week has %d days: %s " % (len(weekTimes), str(weekTimes.keys()))

   expectedTimeWeek = timedelta(seconds=len(weekTimes) * dailyWorkTime * 3600)
   printTotal(spentTimeWeek, expectedTimeWeek)
   print "--- week <<<"



# End of month, print month summary
def printMonthSummary (monthTimes, ghostMonthTime, dailyWorkTime, month, year, spentTimeMonth, expectedTimeMonth):
   print "=== month " + month + " " + year + " ==="
   print "This month work time: "
   for day in sorted(monthTimes):
      spentTimeDay = monthTimes.get(day)
      printDay("    " +day, spentTimeDay, dailyWorkTime)

   if (ghostMonthTime > timedelta()):
      printDay("ghost days", ghostMonthTime, 0)

   printTotal(spentTimeMonth, expectedTimeMonth, len(monthTimes))
   print "=== /month ==="



# Analyze a timefile for a month
def analyzeMonth(timefile, printWeek, printMonth):

   if printWeek or printMonth:
      print "@~~ Analyze file: %s" % (timefile)

   percent = 1 # a normal position is 100%
   workdaysPerWeek = 5 # a normal week has 5 days
   workhoursPerWeek = 40 # a normal week has 40 hours
   dailyWorkTime = workhoursPerWeek / workdaysPerWeek # a normal day is 8 hours
   carryon = timedelta() # a normal carry-on from previous months is zero

   weekTimes = {}
   ghostWeekTime = timedelta()
   monthTimes = {}
   ghostMonthTime = timedelta()

   month = getMonthName(timefile)
   year = getYear(timefile)

   # Read in the timefile
   for line in open(timefile):
      line = line.strip()

    #   print line

      # Empty line = End of week
      if line == "":

         # If there are no week times saved, skip
         # (happens at end of file or with spurious new lines)
         if not weekTimes and (ghostWeekTime == timedelta()):
            continue

         # Calculate spent time and
         # copy week time to month time
         spentTimeWeek = timedelta()
         for day in sorted(weekTimes):
            spentTimeDay = weekTimes.get(day)
            spentTimeWeek += spentTimeDay
            monthTimes[day] = spentTimeDay
         ghostMonthTime += ghostWeekTime
         spentTimeWeek += ghostWeekTime

         # End of week, print week summary
         if printWeek:
            printWeekSummary(weekTimes, ghostWeekTime, spentTimeWeek, dailyWorkTime, workdaysPerWeek)

         # Reset week time
         weekTimes = {}
         ghostWeekTime = timedelta()
         continue

      # Position/percentage
      # Line format:
      #   CONF: <part>/<part>/...
      if line.startswith("CONF:"):
         parts = line[5:].split("/")
         for part in parts:
            if part[-1] == '%':
               percent = float(part[:-1])/float(100)
            elif part[-1] == 'h':
               workhoursPerWeek = float(part[:-1])
            elif part[-1] == 'd':
               workdaysPerWeek = int(part[:-1])
            else:
               print "Error in CONF line, did not recognize part: " + part
         dailyWorkTime = percent * (workhoursPerWeek) / workdaysPerWeek
         if printWeek or printMonth:
            print "Work %d percent of %.2f hours per week, daily work time is %.2f on %d work days" % (percent*100, workhoursPerWeek, dailyWorkTime, workdaysPerWeek)
         continue

      # Position/percentage
      # Line format:
      #   $<percentage number [int]>
      if line.startswith("%"):
         percent = float(line[1:])/float(100)
         dailyWorkTime = percent * (workhoursPerWeek) / workdaysPerWeek
         if printWeek or printMonth:
            print "Work " + str(percent*100) + "%, daily work time is: " + str(dailyWorkTime) + " (" + str(workdaysPerWeek) + " work days)"
         continue

      # Number of work days in a week
      # Line format:
      #   ~<number of days [int]>
      if line.startswith("*"):
         workdaysPerWeek = int(line[1:])
         dailyWorkTime = percent * (workhoursPerWeek) / workdaysPerWeek
         if printWeek or printMonth:
            print "Work " + str(percent*100) + "%, daily work time is: " + str(dailyWorkTime) + " (" + str(workdaysPerWeek) + " work days)"
         continue

      # Carry-on from previous months
      # Negative or positive (overtime)
      # Line format:
      #   =<time in hours>
      if line.startswith("="):
         carryon = carryon + timedelta(hours=float(line[1:]))
         if printWeek or printMonth:
            print "Carry-on from previous months: " + getHours(carryon)
         continue

      # Comments
      # Line format:
      #  #<anything>
      elif line.startswith("#"):
         # If line starts with # ignore
         continue


      # Time-entry
      # Line format:
      #     day ; start time ; end time ; comment
      parts = line.split(";")
      daystring = parts[0].strip()
      start = parts[1].strip()
      end = parts[2].strip()

      # Re-format date
      # (put date in front of weekday name to be able to sort,
      # if necessary add a zero to the day)
      dayparts = daystring.split(" ")
      addzero = ""
      if len(dayparts[1].split(".")[0]) < 2:
         addzero = "0"
      day = addzero + dayparts[1] + " " + dayparts[0][0:2]

      # Calculate spent time
      # (end - start)
      FMT = '%H:%M'
      endTime = datetime.strptime(end, FMT)
      startTime = datetime.strptime(start, FMT)
      spentTime = endTime - startTime

      # Error: start time is before end time
      # -> Ignore this entry
      if spentTime < timedelta(0):
         print "!!!!! ERROR !!!!! spent time is negative on day " + daystring + "(" + start + " to " + end + ")"
         continue;

      # If spentTime, start and end are all 0, this is a holiday
      zerotime = time(0)
      if spentTime == timedelta(0) and endTime.time() == zerotime and startTime.time() == zerotime:
         spentTime = timedelta(hours = int(dailyWorkTime), minutes = int((dailyWorkTime-int(dailyWorkTime))*60))
         if printWeek or printMonth:
            print "Holidaz on %s, count as %s" % (day, spentTime)

      if daystring.startswith("."):
         ghostWeekTime += spentTime

      else:

         # Otherwise add this time to the time spent on day
         savedTime = weekTimes.get(day)
         if savedTime != None:
            # Not first entry for that day
            # Add times
            weekTimes[day] = savedTime + spentTime
         else:
            # First entry for that day
            # Make entry with time.
            weekTimes[day] = spentTime


   # We went through everything.
   # If there is still a week that we haven't processed,
   # do the same as we did before
   # (happens at end of file if there is no new line).
   if weekTimes or (ghostWeekTime > timedelta()):
      spentTimeWeek = timedelta()
      for day in sorted(weekTimes):
         spentTimeDay = weekTimes.get(day)
         spentTimeWeek += spentTimeDay
         monthTimes[day] = spentTimeDay
      ghostMonthTime += ghostWeekTime
      spentTimeWeek += ghostWeekTime
      if printWeek:
         printWeekSummary(weekTimes, ghostWeekTime, spentTimeWeek, dailyWorkTime, workdaysPerWeek)


   # Calculate mont time stuff
   workdays = len(monthTimes)
   spentTimeMonth = ghostMonthTime
   for day in sorted(monthTimes):
      spentTimeMonth += monthTimes.get(day)
   expectedTimeMonth = timedelta(seconds=workdays * dailyWorkTime * 3600)
   overtimeMonth = spentTimeMonth - expectedTimeMonth

   # End of file, print month summary
   if printMonth:
      printMonthSummary(monthTimes, ghostMonthTime, dailyWorkTime, month, year, spentTimeMonth, expectedTimeMonth)

   return spentTimeMonth, expectedTimeMonth, overtimeMonth, month, year, "%d" %(percent*100), carryon


# MAIN

timefiles = []

if len(sys.argv) > 1: # 0 is program name
   for i in range(1,len(sys.argv)):
      print(sys.argv[i])
      timefiles.append(sys.argv[i])

print("Analyze files: ", timefiles)


overtimeTotal = timedelta()
spentTotal = timedelta()
expectedTotal = timedelta()
carryon = timedelta()
for timefile in timefiles:
   spentTimeMonth, expectedTimeMonth, overtimeMonth, month, year, percent, carryon = analyzeMonth(timefile, printWeek, printMonth)
   overtimeTotal += overtimeMonth + carryon
   spentTotal += spentTimeMonth
   expectedTotal += expectedTimeMonth

   if printMonth:
      print "Overall spent time: " + getHours(spentTotal)
      print "Overall expected time: " + getHours(expectedTotal)
      if carryon > timedelta(0):
         print "Explicit carry-on from previous months: " + getHours(carryon)
      print "Overall difference between spent and expected: " + getHours(overtimeTotal)
   print year  + ";\t" + month + ";\t"+ percent + ";\t" + getHours(spentTimeMonth) + ";\t" + getHours(expectedTimeMonth) + ";\t" + getHours(overtimeMonth)+ ";\t" + getHours(overtimeTotal) + ";"

   if printMonth:
      print ""
