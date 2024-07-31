#!/usr/bin/env bash

cd dist/NHTSA-Scrape

FILENAME=NHTSA-Scrape
if [ -f $FILENAME.exe ]; then
	echo Running $FILENAME.exe...
	./$FILENAME.exe
elif [ -f $FILENAME ]; then
	echo Running $FILENAME...
	./$FILENAME
fi

