#! /bin/bash

# Script to automatically execute updates.
# Update Script need to be bash scripts and need to be located in $SCRIPTFOLDER.
# A script is executed if there is no log file for this script in $LOGFOLER.

# @author Wiltrud Kessler, 2017, MINT-Kolleg Stuttgart


BASEFOLDER="/home/mintadmin/Poolsetup"
SCRIPTFOLDER="$BASEFOLDER/updates"
LOGFOLDER="$BASEFOLDER/logs"


echo "Running MINT updates for '$HOSTNAME' on $SCRIPTFOLDER ..."

# Set path correctly (it may not have been set when cron runs)
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Get all files in the script folder and execute each one.
for file in $SCRIPTFOLDER/*.sh
do
   if [[ -f $file ]]; then # remove the folder itself/* (happens if the folder is empty)

      # Get the name of the file (without path)
      FILENAME="${file##*/}"

      # Get the path of the corresponding log file in the log folder.
      # The log file will have the name of the script as first part and the name
      # of the computer it was executed on as the second part.
      # We get the name of a computer from the environment variable $HOSTNAME
      # which should be set on every linux.
      SEP="_"
      LOGNAME="$LOGFOLDER/$FILENAME$SEP$HOSTNAME.log"

      # Check if there is a log file.
      # If yes, this file has already been processed, so we skip it.
      # If no, execute this file and write the result to a log in the log folder
      if [[ ! -f "$LOGNAME" ]] ; then

         # Check if we can create the log file, if not fall back to local log file
         touch $LOGNAME
         if [[ ! -f "$LOGNAME" ]] ; then
           LOGNAME=$FILENAME$SEP$HOSTNAME.log
           echo "I was not able to create the log file!! Logging to $LOGNAME instead"
         fi

         # Execute the script file with bash, redirect outputs to log file.
         # The -x executes the script in verbose mode, meaning every command
         # is logged before execution.
         echo "-- process $file (logging to $LOGNAME)"
         DATE=`date +"%b %d %H:%M:%S"`
         echo "=== Processing start: $DATE" > "$LOGNAME"
         bash -x "$file" &>> "$LOGNAME"
         if [ $? -eq 1 ]
         then
            echo "=== Processing ended with Error!!!!"  >> "$LOGNAME"
         fi
         DATE=`date +"%b %d %H:%M:%S"`
         echo "=== Processing end: $DATE" >> "$LOGNAME"
      fi

   fi
done

echo "... done running MINT updates!"
