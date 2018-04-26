#! /bin/bash 

# (c) Wiltrud Kessler
# 13.10.2014
# This code is distributed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported license 
# http://creativecommons.org/licenses/by-nc-sa/3.0/

# Create handouts from LaTeX slides


if [[ $# -lt 1 ]] ; then
   echo "Usage: createHandout.sh <path to LaTeX file>"
   exit 1
fi

BASEFILE=$1
LOGFILE="log.txt"
CLEAN=false
SUFFIX="_h"

if [[ $# -gt 1 ]] ; then
   CLEAN=true
fi


# Check if LaTeX file exists
if [[ ! -f "$BASEFILE" ]] ; then
   echo "File $BASEFILE not found!"
   exit 1
fi

 # File name: Strip from start longest match of [*/]
FILENAME="${BASEFILE##*/}"

# Folder: Strip from end shortest match of [/ plus at least one non-/ char]
FOLDER="${BASEFILE%/[^/]*}"

# File prefix: Strip from end shortest match of [dot plus at least one non-dot char]
FILEPREFIX="${FILENAME%.[^.]*}"
HANDOUTPREFIX=$FILEPREFIX$SUFFIX

# File extension: Strip from start longest match of [at least one non-dot char plus dot]
EXTENSION="${FILENAME##[^.]*.}"


# Check if this is a LaTeX file (by extension)
if [[ $EXTENSION != "tex" ]] ; then
   echo "This is not a LaTeX file: $EXTENSION"
   exit 1
fi

# Go to the folder (otherwise includes don't work)
# If we are already in the correct folder, the regex extracts the filename as the foldername
if [[ $FOLDER != $FILENAME ]] ; then
   cd $FOLDER
fi


# Add option 'handout' to first line
# TODO only works when no other beamer options are given
# We know the source file exists
echo "Do sed."
sed "s/{beamer}/[handout]{beamer}/" $FILENAME  > $HANDOUTPREFIX.tex

# TODO check if this worked
if [[ ! -f $HANDOUTPREFIX.tex ]] ; then
   echo "File not found! 2"
   exit 1
fi

# Run LaTeX
echo "Do LaTeX first run (see $LOGFILE)."
pdflatex $HANDOUTPREFIX.tex > $LOGFILE

if [[ ! -f $HANDOUTPREFIX.pdf ]] ; then
   echo "File not found! 3"
   exit 1
fi

# Re-run LaTeX to get slide numbers right
# Don't need to check output, if it worked once, it works again
echo "Do LaTeX second run (see $LOGFILE)."
pdflatex $HANDOUTPREFIX.tex >> $LOGFILE


# Delete all temporary files
# This includes the created tex-file
echo "Delete tmp files (all besides pdf)"
rm $HANDOUTPREFIX.aux
rm $HANDOUTPREFIX.log
rm $HANDOUTPREFIX.nav
rm $HANDOUTPREFIX.out
rm $HANDOUTPREFIX.snm
rm $HANDOUTPREFIX.toc
rm $HANDOUTPREFIX.vrb
rm $HANDOUTPREFIX.tex # might want to keep this

if [[ "$CLEAN" = "true" ]]; then
   echo "Cleanup normal tmp files as well"
   rm $FILEPREFIX.aux
   rm $FILEPREFIX.log
   rm $FILEPREFIX.nav
   rm $FILEPREFIX.out
   rm $FILEPREFIX.snm
   rm $FILEPREFIX.toc
   rm $FILEPREFIX.vrb
fi


echo "Done!"
