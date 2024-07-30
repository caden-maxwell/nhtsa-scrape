#!/usr/bin/env bash

cd dist/NHTSA-Scrape

FILENAME=NHTSA-Scrape
if [ -f $FILENAME ]; then
	echo Running $FILENAME...
	./$FILENAME
elif [ -f $FILENAME.exe ]; then
	echo Running $FILENAME.exe...
	./$FILENAME.exe
fi

