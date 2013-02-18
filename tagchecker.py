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

#Dictionary mapping shortcuts to possible tags
possibletags = {
	#be (cop)
	"c3":"v:cop|be&3S", "cp":"v:cop|be&PRES", 
	"iv1":"pro:sub|I~v:cop|be&1S","yvp":"pro:sub|you~v:cop|be&PRES",
	"pec3":"pro:exist|there~v:cop|be&3S", "wc":"adv:wh|where~v:cop|be&3S",
	"whc":"pro:wh|who~v:cop|be&3S", "ic":"pro|it~v:cop|be&3S",
	"hc":"pro:sub|he~v:cop|be&3S",
	#be (aux)
	"wa":"adv:wh|where~aux|be&3S", "a3":"aux|be&3S", "ap":"aux|be&PRES",
	"wha":"pro:wh|who~aux|be&3S", "ya":"pro|you~aux|be&PRES", "ia":"pro|it~aux|be&3S",
	"ha":"pro:sub|he~aux|be&3S",
	#prepositions
	"pu":"prep|up", "po": "prep|out", "pi":"prep|in", "pov": "prep|over",
	"pis":"prep|inside", "pl":"prep|like", "pb":"prep|back", "pos":"prep|outside",
	"pa":"prep|at",
	#adv:loc
	"ali":"adv:loc|in", "alo":"adv:loc|out",  "alu":"adv:loc|up",
	"alov":"adv:loc|over", "alis": "adv:loc|inside", "alos": "adv:loc|outside",
	"alt":"adv:loc|top",
	#other common 
	"n":"n|mommy", "pe":"pro:exist|there", "d":"det|that", "i":"inf|to",
	"pd":"pro:dem|that", "pd2":"pro:dem|this", "a":"adj|right", "l":"v|like",	
	"ct":"co|there",
	#compounds
	"ct":"n|+n|tape+n|recorder", "cp":"n|+n|chicken+n|pox", "cw":"n|+n|water+n|boat",
}
   

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
    print "Total lines to check:", len(listofphrases)
    finished = check(listofphrases, int(startLine), errorFile, filename)

    #If there are no more lines left to check
    if finished == True:
        print "Congratulations: You have finished checking this file. WOOOO"
        efile.close()
        clearfinished(filename)
        save("finished", filename)        
    
def check(listofphrases, lineNumber, errorFile, filename):
    while lineNumber < len(listofphrases):
        current = listofphrases[lineNumber]
        current.printSentence()
        error = raw_input("Error? Type Y or N, followed by Enter\n")
        if error == "y":
            print "-------------------------------------------------------------"
            processError(listofphrases, current, 0, errorFile, filename)
            print "-------------------------------------------------------------"
            print "Sentence completed: Continuing to next phrase\n"
        elif error == "n":
            print "No error found: Continuing to next phrase\n"
            check(listofphrases, lineNumber+1, errorFile, filename)
        elif error == "q":
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
        if lineNumber >= len(listofphrases):
            return True
        
    
def processError(listofphrases, tiers, i, errorFile, filename):
    length = tiers.getLengthofUtterance()
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
            if error == "y":
                correction = inputval()
                notes = raw_input("Enter notes. Enter z to re-enter correction. Enter n to avoid writing anything to file. Press Enter to Continue\n")
                if notes == "z":
                    correction = inputval()
                    notes = raw_input("Enter notes. Enter n to avoid writing anything to file. Press Enter to Continue\n")
                if notes != "n":
                    errorFile.writerow([tiers.ID, tiers.speaker, tiers.completeSentence(), tiers.completeMor(), tiers.mor[i], correction, notes])
                    print "\nError recorded: Continuing to next word\n -------------\n"
                i +=1
            elif error == "n":
                i +=1
            elif error == "c":
                tiers.printCompound(i)
                correction = inputval()
                notes = raw_input("Enter notes. Enter z to re-enter correction. Enter n to avoid writing anything to file.Press Enter to Continue\n")
                if notes == "z":
                    correction = inputval()
                    notes = raw_input("Enter notes. Enter n to avoid writing anything to file. Press Enter to Continue\n")
                if notes != "n":
                    errorFile.writerow([tiers.ID, tiers.speaker, tiers.completeSentence(), tiers.completeMor(), tiers.mor[i]+ " " + tiers.mor[i+1], correction, notes])
                    print "\nCompound error recorded: Continuing to next word\n -------------\n"
                i=i+2
            elif error == "z":
                print "\nReturning to previous word\n*************\n" 
                if tiers.utterance[i-1] == ",": i = i -2
                else: i = i - 1
            elif error == "q":
                save(tiers.ID,filename)
            else:
                print "\nCommand not recognized, try again:"
                processError(listofphrases, tiers, i, errorFile, filename)
                break
        else: i +=1

def inputval():
    correction = raw_input("\nEnter Correct Tag and press enter.\n")
    if correction in possibletags:
        correction = possibletags[correction]
        print "YOU ENTERED:", correction
    return correction
        
def save(ID, filename):
    print "\nLine saved as line %s. Exiting." % (ID)
    t = open(tfile, "a")
    trackingfile = csv.writer(t, delimiter=",")
    trackingfile.writerow([filename, ID])
    t.close()
    quit()

#when a file is finished, go to the tracking file and delete all the previous 
#for that file to prevent the tracking file from cluttering too much
def clearfinished(filename):
    r = open(tfile, "rb")
    trackingfile = csv.reader(r, delimiter=",")
    toWrite = []
    for entry in trackingfile:
        if entry[0] != filename or entry[1] == "finished":
            toWrite.append([entry[0], entry[1]])
    r.close()
    os.remove(tfile)
    t = open(tfile, "a")
    newtrackingfile = csv.writer(t, delimiter=",")
    for item in toWrite:
        newtrackingfile.writerow(item)
    t.close()
    
if __name__ == "__main__":
    from sys import argv
    parseFile(argv[1], argv[2])
