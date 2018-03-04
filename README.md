# README #

This README documents the steps required to get the cellular automaton up and running. It is written in Python 3.4 and is best run by calling cellular.py from the command line.

### What is this repository for? ###

This repository contains the four co-dependent scripts for running the cellular automaton simulating cryoconite migrating over a sloped ice surface.

The four requisite files that must be saved int he working directory are: cellular_class.py, cellular.py, cell_view.py, ca.py. There should also be an empty folder created in the working directory named 'tmp_image'.


### To run the model ###

Open windows command prompt and, if necessary, change the working directory to the appropriate path using the 'cd' command. 
First, open the file 'cellular_class.py'. At the bottom of the script, in the class definition 'Ex1', values for the number of ticks, total coverage, speed of migration and grid dimensions can be defined. Update according to user preference. Save and close cellular.py.

Run the script in the command line by typing:

>> python cellular_class.py

Plots will appear and update in a detached window and a PNG file of each image will be saved to the tmp_image folder in the working directory.  


### Contribution guidelines ###

Some difficulty in running this code in the Spyder2 editor has been experienced, which are not encountered from the command line. We therefore suggest using the command line as the default environment for running this code.
We are keen for other users to develop or use this code independently or in collaboration, and would appreciate citation of our paper (Arctic, Antarctic and Alpine Research, currently under review).

### Who do I talk to? ###

These codes were developed by Joseph Cook and Angus Taggart at the University of Sheffield, UK. Contact joe.cook@sheffield.ac.uk. 

## DISCLAIMER ##

We provide free and open access to this software on the understanding that it requires validation and further rigorous testing - the authors assume no responsibility for downstream usage and, while we welcome collaboration, we are not obliged to provide training or support for users. We hope that this code and data will be useful and encourage collaboration, but we provide it WITHOUT WARRANTY or even the implied warranty of merchantability or fitness for any particular purpose.
