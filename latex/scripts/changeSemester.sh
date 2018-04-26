#! /bin/bash 

# (c) Wiltrud Kessler
# 13.07.2015
# This code is distributed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported license 
# http://creativecommons.org/licenses/by-nc-sa/3.0/

# Change semester for LaTeX slides

NEWSEMESTER=$1
shift
FILES=$@

# \\\\ becomes one \ in the end!!
PATTERN="s|\date{\(.*\)\\\\\\\\[^}]*}|\date{\1\\\\\\\\ ${NEWSEMESTER}}|"


for FILE in ${FILES[@]}
do

   # Check if LaTeX file exists
   if [ ! -f "$FILE" ] ; then
      echo "File $FILE not found!"
   else
   
      # If so, apply sed to exchange the date
      echo "File: $FILE"
      sed -i "$PATTERN" $FILE
   fi

done
echo "Done!"
