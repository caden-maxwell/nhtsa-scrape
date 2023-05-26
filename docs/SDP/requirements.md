# [Software Development Plan](README.md)

## Requirements Specification

### Purpose

The purpose of this document is to outline general requirements
for the software being developed, and will be used to
ensure that the software meets the needs of the client.

### Scope

This software will be used to fetch data and images from the NASS/CDS 
database, which is made accesible through the NHTSA. The software will 
present the data in a GUI application, in such a way as to facilitate 
research and allow the user to investigate numerous cases at once. The 
user may compare this information with their own, which may be useful 
for consulting firms hired to investigate an accident. The 
user will be able to easily filter out cases that are not of interest, 
and save both data and images to their local machine for further research. 
A CSV file will be created at the user's request, containing the data 
for all cases that are currently of interest. This CSV file will be 
formatted in such a way as to be easily imported into a spreadsheet 
program, such as Microsoft Excel. The user will also be able to make 
separate research profiles, allowing them to return to their current 
research at a later time. Multiple profiles can be saved, allowing the 
user to easily switch between different cases of interest. The software 
will be written in Python utilizing the PyQt6 framework, and will be 
available as a standalone executable for Windows, Mac, and Linux. The 
raw source code will also be available for download, allowing the user 
to run the software on any platform that supports Python, PyQt6, and 
any other dependencies that are listed in the [installation instructions](../installation.md).

### Definitions, Acronyms, and Abbreviations

* CSV: Comma Separated Values
* GUI: Graphical User Interface
* NASS/CDS: National Automotive Sampling System / Crashworthiness Data System
* NHTSA: National Highway Traffic Safety Administration

### References

* [NASS/CDS](https://www.nhtsa.gov/crash-data-systems/national-automotive-sampling-system)
* [Python](https://www.python.org/)
* [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)