#!/usr/bin/env python
import csv
import os
try:
    from lxml import etree
    parse = etree.parse
except ImportError:
    try:
        from xml.etree.cElementTree import ElementTree
    except ImportError:
        from xml.etree.ElementTree import ElementTree
    parse = lambda fn: ElementTree(file=fn)


#Take care of namespace
ns =  "{http://www.talkbank.org/ns/talkbank}"
#Dictionary mapping t-tier values: punctuation and @ values
d = {
    	"p":"." , "q":"?", "e":"!", "trail off": "+...", "interruption": "+/.",
    	"self interruption": "+//", "quotation next line": "+\"/.",
    	"interruption question": "+/?", "singing": "@si", "word play":"@wp",
        "onomatopoeia": "@o", "letter":"@l", "child-invented":"@c",
        "motherese": "@m", "family-specific":"@f", "babbling": "@b",
	"phonology consistent": "@p",}

#file keeping track of position
tfile = "DO_NOT_DELETE.csv"

#for backtracking purposes until I get my logic straight
backTrack = -1
firstTime = 1
notFirst = 0

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

    finished = speaker(iter, filename, errorFile, startLine, firstTime)

    #If there are no more lines left to check
    if finished == 1:
        save("finished", filename)
        efile.close()
        print "Congratulations: You have finished checking this file. WOOOO"
        exit()

#For backtracking purposes. Pretty expensive, but any other way would require quite a bit of code revamping I think
def parsebackwards(ID, errorFile, filename):
    name, ext = os.path.splitext(filename)
    #See if xml file found
    try:
        tree = parse(filename)
    except:
        print "ERROR: File not found. Check and make sure it exists"
        exit()

    iter = tree.getiterator(ns + "u")
    speaker(iter, filename, errorFile, int(ID)-1, backTrack)
	
#Takes care of the speaker tier
def speaker(iter, filename, errorFile, startLine, first): 
    if first == firstTime:
        raw_input("Welcome. Press q to save+quit at any time. Press z to backtrack. Press enter to continue\n--------------------------\n")
    isCompound = True
    for elem in iter:
    	#Each sentence has a speaker, a unique ID, and a mor tier
        speaker = "*" + elem.get("who") +":"
        ID = elem.get("uID")[1:]	#to skip the first "u" for ease of iteration
    	sentence = []
    	mor = []

    	if int(ID)==int(startLine) or first == notFirst:
    		first = notFirst    #Not the first line
		#Checks to see if word. If so, print.
		for child in elem:
		    #is directly under <w>
		    if (child.tag == (ns + "w")):
		    	phrase = child.text 
		        
		        #is fragment
		        if child.get("type") == "fragment":             
		            mor.append("unk|" + phrase)
		            sentence.append(phrase)
		            continue
		        #is shortening
		        if (child.find("%sshortening" % (ns)) != None):
		            if phrase == None:
		                phrase = (child.find("%sshortening" % (ns))).text 
		            else:
		                phrase = phrase + (child.find("%sshortening" % (ns))).text 
		            if child[0].tail != None:
		                phrase = phrase + child[0].tail

		        #is replacement
		        if (child.find("%sreplacement" % (ns)) != None):
			    phrase = (child.find("%sreplacement/%sw" % (ns,ns))).text
			      
	                #is compound
	                if (child.find(".//%smwc/%spos/%sc" % (ns,ns,ns)) != None):
			    if (child[0].tail != None):
			        phrase = phrase + "+" + child[0].tail
			    mor.append(process_mor(child.getiterator(ns + "mor"), isCompound))
		        elif (phrase == "xxx" or phrase == "xx") :
			    mor.append("unk|" + phrase)
		        else:
		            mor.append(process_mor(child.getiterator(ns + "mor"), False))
		        
	                # needs @o, @m, etc at the end
	                if child.get("formType") != None:
		            phrase = phrase + d[child.get("formType")]
		        sentence.append(phrase)
		        
		    #contained under <g>
		    elif (child.tag == (ns + "g")):
		        phrase = (child.find("%sw" % (ns))).text
		        #is shortening
		        if (child.find("%sw/%sshortening" % (ns,ns)) != None):
			    if phrase == None:
		                phrase = (child.find("%sw/%sshortening" % (ns,ns))).text 
		            else:
		                phrase = phrase + (child.find("%sw/%sshortening" % (ns,ns))).text 
		            if child[0].tail != None:
		                phrase = phrase + child[0].tail
		        #is replacement
		        if (child.find("%sw/%sreplacement/%sw" % (ns,ns,ns))) != None:
		    	    phrase = (child.find("%sw/%sreplacement/%sw" % (ns,ns,ns))).text
		    	    
		    	    if (child.find("%sw/%sreplacement/%sw/%swk" % (ns,ns,ns,ns))) != None:
		    	    	phrase = phrase + "+"  + (child.find("%sw/%sreplacement/%sw/%swk" % (ns,ns,ns,ns))).tail
				mor.append(process_mor(child.getiterator(ns + "mor"), isCompound))
				sentence.append(phrase)
				continue
			# needs @o, @m, etc at the end
			if child[0].get("formType") != None:
		            phrase = phrase + d[child.get("formType")]	
		        #has no mor tier
		        if (process_mor(child.getiterator(ns + "mor"), False) == None):
		            if child.find("%sw/%sp" % (ns,ns)) != None:
		                phrase = phrase + "h"
		            mor.append("unk|" + phrase)
		        else:
		            mor.append(process_mor(child.getiterator(ns + "mor"), False))
		        sentence.append(phrase)
		    
		    #paralinguisitic gesture
		    elif(child.tag == (ns + "e")):
		    	if (child.find("%sga" % (ns)) != None):
		            phrase = child.find("%sga" % (ns)).text 
		    	elif (child.find("%shappening" % (ns)) != None):
		            phrase = child.find("%shappening" % (ns)).text 
		        sentence.append("(" + phrase + ")")
		        mor.append("(unk|" + phrase +")")
		        
		    #is punctuation
		    elif (child.tag == (ns + "t")):
			punctuation = child.get("type")
			sentence.append(d[punctuation])
			mor.append(d[punctuation])
			
		    #is a central comma
		    if (child.tag == (ns + "s")):
		    	if child.get("type") == "comma":
		            sentence.append(",")
			    mor.append(",")
		check(ID, speaker, sentence, mor, errorFile, filename)
		elem.clear() 
    return 1

#Takes care of the MOR tier -- returns the proper tag for a word
def process_mor(mor_iter, isCompound):
    for item in mor_iter:
        if (item.get("type") == "mor"):
            if (isCompound == False):
    	        category = item.find("%smw/%spos/%sc" % (ns,ns,ns))
    	        descript = item.findall("%smw/%spos/%ss" % (ns,ns,ns))
    	        stem = item.find("%smw/%sstem" % (ns,ns))
    	        suffix = item.findall("%smw/%smk" % (ns,ns))

    	        #possible clitic portion
    	        c_cat = item.find("%smor-post/%smw/%spos/%sc" % (ns,ns,ns,ns))
    	        c_des = item.findall("%smor-post/%smw/%spos/%ss" % (ns,ns,ns,ns))
    	        c_stem = item.find("%smor-post/%smw/%sstem" % (ns,ns,ns))
    	        c_suff = item.findall("%smor-post/%smw/%smk" % (ns,ns,ns))
    	        result = combine(category, descript, stem, suffix, c_cat, c_des, c_stem, c_suff)

    	    else:
    	    	#if it's a compound
    	        comp_category = item.find("%smwc/%spos/%sc" % (ns,ns,ns))
    	        category = item.findall(".//%smw/%spos/%sc" % (ns,ns,ns))
    	        stem = item.findall(".//%smw/%sstem" % (ns,ns))
                result = combinecmpd(comp_category, category, stem)
        else: pass
        return result

#Combines various fields to create proper mor tag for one word
def combine(category, descript, stem, suffix, c_cat, c_des, c_stem, c_suff):
    mor = category.text
    for s in range(0, len(descript)):
        mor = mor + ":" + descript[s].text
    mor = mor + "|" + stem.text

    for s in range(0, len(suffix)) :
    	if (suffix[s].get("type") == "sfx"):
            mor = mor + "-" + suffix[s].text
        else:
            mor = mor + "&" + suffix[s].text

    if (c_cat != None): #there is a clitic portion
        mor = mor + "~" + c_cat.text
        for s in range(0, len(c_des)):
            mor = mor + ":" + c_des[s].text
        mor = mor + "|" + c_stem.text
        for s in range(0, len(c_suff)) :
            if (c_suff[s].get("type") == "sfx"):
            	mor = mor + "-" + c_suff[s].text
            else:
                mor = mor + "&" + c_suff[s].text
    return mor


#Combines various fields to create proper mor tag for one compound
def combinecmpd(comp_category, category, stem):
     mor = comp_category.text + "|"
     for i in range(0,2):
         mor = mor + "+" +category[i].text + "|" + stem[i].text
     return mor

def check(ID, speaker, sentence, mor, errorFile, filename):
    print "Currently checking sentence " + ID
    print speaker, ' '.join(sentence)
    print speaker, ' '.join(mor) +"\n"
    error = raw_input("Error? Type Y or N, followed by Enter\n")
    if error == "y" or error == "Y":
    	print "-------------------------------------------------------------"
        processError(ID, speaker, sentence, mor, 0, errorFile, filename)
        print "-------------------------------------------------------------"
        print "Sentence completed: Continuing to next phrase\n"
    elif error == "n" or error == "N": print "No error found: Continuing to next phrase\n"
    elif error == "q" or error == "quit":
    	save(ID,filename)
    elif error == "z" or error == "undo":
    	print "\nReturning to previous line:\n***************************\n"
    	if int(ID) < 1:
            print "\nHEY! You're already at the first line of the file!!\n" 
            check(ID, speaker, sentence, mor, errorFile, filename)
        else: parsebackwards(ID, errorFile, filename)
    else:
    	print "\nCommand not recognized:"
        check(ID, speaker, sentence, mor, errorFile, filename)

def processError(ID, speaker, sentence, mor, i, errorFile, filename):
    #To avoid processing punctuation
    length = len(sentence)
    if sentence[length-1] in d.values():
        length -=1
    #Checking word one by one
    utterance = ' '.join(sentence)
    completeMor = ' '.join(mor)
    while i < length:
      if i < 0:
          print "\nHEY! You're already at the first word in the sentence!!\n" 
          print "\nReturning to previous line:\n***************************\n"
    	  if int(ID) < 1:
            print "\nHEY! You're already at the first line of the file!!\n" 
            check(ID, speaker, sentence, mor, errorFile, filename)
          else: parsebackwards(ID, errorFile, filename)
      if sentence[i] != "," or mor[i] != ",":
    	print "Phrase: %s %s " % (speaker, utterance)
        print sentence[i].center(60," ")
        print mor[i].center(60," ")
        error = raw_input("Error in above word? Type Y (Error), C (Error spans two words), or N (No error), followed by Enter\n")
        if error == "y" or error == "Y":
            correction = raw_input("\nEnter Correct Tag and press enter\n")
            notes = raw_input("Enter notes. Press Enter to Continue\n")
            errorFile.writerow([ID, speaker, utterance, completeMor, mor[i], correction, notes])
            i=i+1
	    print "\nError recorded: Continuing to next word\n -------------\n"
        elif error == "n" or error == "N":
            i = i + 1
        elif error == "c" or error == "C":
            print sentence[i].center(30," "), sentence[i+1].center(30," ")
            print mor[i].center(30," "), mor[i+1].center(30," ")
            correction = raw_input("\nEnter Correct Tag and press enter\n")
            notes = raw_input("Enter notes. Press Enter to Continue\n")
            errorFile.writerow([ID, speaker, utterance, completeMor, mor[i]+ " " + mor[i+1], correction, notes])
            i = i + 2
            print "\nCompound error recorded: Continuing to next word\n -------------\n"
        elif error == "z" or error == "Z":
            print "\nReturning to previous word\n*************\n" 
	    if sentence[i-1] == ",": i = i -2
	    else: i = i - 1
	elif error == "q" or error == "quit":
    	    save(ID,filename)
        else:
    	    print "\nCommand not recognized, try again:"
            processError(ID, speaker, sentence, mor, i, errorFile, filename)
            break
      else: i += 1

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
