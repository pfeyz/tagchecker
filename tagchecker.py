#!/usr/bin/env python
import csv
import os
from phrase import *

try:
	from lxml import etree
	parse = etree.parse
except ImportError:
	try:
		from xml.etree.cElementTree import ElementTree
	except ImportError:
		from xml.etree.ElementTree import ElementTree
	parse = lambda fn: ElementTree(file=fn)

#file keeping track of position
tfile = "DO_NOT_DELETE.csv"

#filename should be an xml file, errors should be a csv file
def parseFile(filename, errors):
	name, ext = os.path.splitext(filename)
	name2, ext2 = os.path.splitext(errors)

	#Check to make sure file types are correct
	if ext != ".xml" or ext2 != ".csv":
		print "Error: First file must be .xml and second must be .csv"
		exit()

	#See if xml file found
	try:
		tree = parse(filename)
	except:
		print "ERROR: File not found. Check and make sure it exists"
		exit()
		
	iter = tree.getiterator(ns + "u")
	efile = open(errors, "a")
	errorFile = csv.writer(efile, delimiter=",")

	#if new error file, set up template
	if os.stat(errors)[6]==0:
		errorFile.writerow(["Line", "Speaker", "Utterance", "Tags",
					"Incorrect Tag", "Correct Tag", "Notes"])
	#Tracking file
	try:
		track = open(tfile, "r")
	except IOError:
		print "Error: DO_NOT_DELETE.csv not found"
		exit()

	#Find the line to start (if there was a previous save). Otherwise the start line is zero.
	#Enables us to keep track of multiple files at once
	trackingfile = csv.reader(track, delimiter=",")
	startLine = 0
	for row in trackingfile:
		if row and row[0] == filename:
			startLine = row[1]
			if startLine == "finished":
				print "This file has already been completely checked. "
				exit()
	track.close()
	
	raw_input("Welcome. Press q to save+quit at any time. Press z to backtrack. Press enter to continue\n--------------------------\n")
	listofphrases = populate(iter)
	finished = check(listofphrases, int(startLine), filename, errorFile)

	#If there are no more lines left to check
	if finished == 1:
		save("finished", filename)
		efile.close()
		print "Congratulations: You have finished checking this file. WOOOO"
		exit()
		
	
def check(listofphrases, lineNumber, errorFile, filename):
	while lineNumber <= len(listofphrases):
		current = listofphrases[lineNumber]
		current.printSentence()
		error = raw_input("Error? Type Y or N, followed by Enter\n")
		if error == "y" or error == "Y":
			print "-------------------------------------------------------------"
			processError(listofphrases, current, 0, errorFile, filename)
			print "-------------------------------------------------------------"
			print "Sentence completed: Continuing to next phrase\n"
		elif error == "n" or error == "N":
			print "No error found: Continuing to next phrase\n"
			check(listofphrases, lineNumber+1, errorFile, filename)
		elif error == "q" or error == "quit":
			save(current.ID,filename)
		elif error == "z":
			print "\nReturning to previous line:\n***************************\n"
			if current.ID == 0 :
				print "\nHEY! You're already at the first line of the file!!\n" 
				check(listofphrases, lineNumber, errorFile, filename)
			else: check(listofphrases, lineNumber-1, errorFile, filename)
		else:
			print "\nCommand not recognized:"
			check(listofphrases, lineNumber, errorFile, filename)
		lineNumber += 1
	return 1
	
def processError(listofphrases, tiers, i, errorFile, filename):
	length = tiers.getLengthofUtterance()
	print length
	#Checking word one by one
	#if requested index is before first of sentence, bring to previous sentence
	while i < length:
		if i < 0:
			print "\nHEY! You're already at the first word in the sentence!!\n" 
			print "\nReturning to previous line:\n***************************\n"
			if tiers.ID < 1:
				print "\nHEY! You're already at the first line of the file!!\n" 
				check(listofphrases, tiers.ID, errorFile, filename)
			else: check(listofphrases, tiers.ID-1, errorFile, filename)
			
	  #otherwise check word by word
		if tiers.utterance[i] != "," or tiers.mor[i] != ",":
			tiers.printWord(i)
			error = raw_input("Error in above word? Type Y (Error), C (Error spans two words), or N (No error), followed by Enter\n")
			if error == "y" or error == "Y":
				correction = raw_input("\nEnter Correct Tag and press enter\n")
				notes = raw_input("Enter notes. Press Enter to Continue\n")
				errorFile.writerow([tiers.ID, tiers.speaker, tiers.completeSentence(), tiers.completeMor(), tiers.mor[i], correction, notes])
				i+=1
				print "\nError recorded: Continuing to next word\n -------------\n"
			elif error == "n" or error == "N":
				i +=1
			elif error == "c" or error == "C":
				tiers.printCompound(i)
				correction = raw_input("\nEnter Correct Tag and press enter\n")
				notes = raw_input("Enter notes. Press Enter to Continue\n")
				errorFile.writerow([tiers.ID, tiers.speaker, tiers.completeSentence(), tiers.completeMor(), tiers.mor[i]+ " " + tiers.mor[i+1], correction, notes])
				i = i + 2
				print "\nCompound error recorded: Continuing to next word\n -------------\n"
			elif error == "z" or error == "Z":
				print "\nReturning to previous word\n*************\n" 
				if tiers.utterance[i-1] == ",": i = i -2
				else: i = i - 1
			elif error == "q" or error == "quit":
				save(tiers.ID,filename)
			else:
				print "\nCommand not recognized, try again:"
				processError(listofphrases, tiers, i, errorFile, filename)
				break
		else: i +=1
		
def save(ID, filename):
	print "\nLine saved as line %s. Exiting." % (ID)
	t = open(tfile, "a")
	trackingfile = csv.writer(t, delimiter=",")
	trackingfile.writerow([filename, ID])
	t.close()
	quit()

if __name__ == "__main__":
	from sys import argv
	parseFile(argv[1], argv[2])
