#! /bin/bash 

# (c) Wiltrud Kessler
# 13.07.2015
# This code is distributed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported license 
# http://creativecommons.org/licenses/by-nc-sa/3.0/

# Umlaute entfernen

FILES=$@

echo $FILES

echo hallo

for FILE in $FILES
do
   echo $FILE
   
   cp $FILE $FILE.bak
   
   sed -i "s/ü/ue/g" $FILE
   sed -i "s/ö/oe/g" $FILE
   sed -i "s/ä/ae/g" $FILE
   sed -i "s/ß/ss/g" $FILE

   sed -i "s/Ü/Ue/g" $FILE
   sed -i "s/Ö/Oe/g" $FILE
   sed -i "s/Ä/Ae/g" $FILE

done

echo "Done!"
