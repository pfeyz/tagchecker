#Contains the phrase object

#Dictionary mapping t-tier values: punctuation and @ values
d = {
		"p":"." , "q":"?", "e":"!", "trail off": "+...", "interruption": "+/.",
		"self interruption": "+//", "quotation next line": "+\"/.",
		"interruption question": "+/?", "singing": "@si", "word play":"@wp",
		"onomatopoeia": "@o", "letter":"@l", "child-invented":"@c",
		"motherese": "@m", "family-specific":"@f", "babbling": "@b",
		"phonology consistent": "@p",}

#Take care of namespace
ns =  "{http://www.talkbank.org/ns/talkbank}"

class Phrase(object):
	def __init__(self, ID=None, speaker=None, utterance=[], mor=[]):
		self.ID = ID
		self.speaker = speaker
		self.utterance = utterance
		self.mor = mor
		
	def printSentence(self):
		print "Currently checking sentence " + str(self.ID)
		print self.speaker, ' '.join(self.utterance)
		print self.speaker, ' '.join(self.mor) +"\n"
	
	def printWord(self, i):
		print "Phrase: %s %s " % (self.speaker, ' '.join(self.utterance))
		print self.utterance[i].center(60," ")
		print self.mor[i].center(60," ")
	
	def printCompound(self,i):
		print self.utterance[i].center(30," "), self.utterance[i+1].center(30," ")
		print self.mor[i].center(30," "), self.mor[i+1].center(30," ")
		
	def getLengthofUtterance(self):
	   length = len(self.utterance)
	   if self.utterance[length-1] in d.values():
		   length -=1
	   return length
	
	def completeMor(self):
		return ' '.join(self.mor)
		
	def completeSentence(self):
		return ' '.join(self.utterance)
		
		
#populates phrase list
def populate(iter):
	isCompound = True
	listofphrases = []
	for elem in iter:
		#Each sentence has a speaker, a unique ID, and a mor tier
		ID = int(elem.get("uID")[1:])	#to skip the first "u" for ease of iteration
		speaker = "*" + elem.get("who") +":"
		mor = []
		utterance = []
		#Checks to see if word. If so, print.
		for child in elem:
			#is directly under <w>
			if (child.tag == (ns + "w")):
				phrase = child.text 
				#is fragment
				if child.get("type") == "fragment":				
					mor.append("unk|" + phrase)
					utterance.append(phrase)
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
				utterance.append(phrase)
				
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
					mor.append(process_mor(child.getiterator(ns + "mor"), False))
					utterance.append(phrase)
					continue
				
				# needs @o, @m, etc at the end
				if child[0].get("formType") != None:
					phrase = phrase + d[child[0].get("formType")]	
				#has no mor tier
				if (process_mor(child.getiterator(ns + "mor"), False) == None):
					if child.find("%sw/%sp" % (ns,ns)) != None:
						phrase = phrase + "h"
						mor.append("unk|" + phrase)
				else:
					mor.append(process_mor(child.getiterator(ns + "mor"), False))
				utterance.append(phrase)
				
			
			#paralinguisitic gesture
			elif(child.tag == (ns + "e")):
				if (child.find("%sga" % (ns)) != None):
					phrase = child.find("%sga" % (ns)).text 
				elif (child.find("%shappening" % (ns)) != None):
					phrase = child.find("%shappening" % (ns)).text 
				utterance.append("(" + phrase + ")")
				mor.append("(unk|" + phrase +")")
				
			#is punctuation
			elif (child.tag == (ns + "t")):
				punctuation = child.get("type")
				utterance.append(d[punctuation])
				mor.append(d[punctuation])
			
			#is a central comma
			if (child.tag == (ns + "s")):
				if child.get("type") == "comma":
					utterance.append(",")
					mor.append(",")

		#sets for backtracking purposes
		listofphrases.append(Phrase(ID, speaker, utterance, mor))
		elem.clear() 	
	return listofphrases

#Takes care of the MOR tier -- returns the proper tag for a word
def process_mor(mor_iter, isCompound):
	for item in mor_iter:
		if (item.get("type") == "mor"):
			if (isCompound == False):
				category = item.find("%smw/%spos/%sc" % (ns,ns,ns))
				descript = item.findall("%smw/%spos/%ss" % (ns,ns,ns))
				stem = item.find("%smw/%sstem" % (ns,ns))
				suffix = item.findall("%smw/%smk" % (ns,ns))
				prefix = item.find("%smw/%smpfx" % (ns,ns))
				
				#possible clitic portion
				c_cat = item.find("%smor-post/%smw/%spos/%sc" % (ns,ns,ns,ns))
				c_des = item.findall("%smor-post/%smw/%spos/%ss" % (ns,ns,ns,ns))
				c_stem = item.find("%smor-post/%smw/%sstem" % (ns,ns,ns))
				c_suff = item.findall("%smor-post/%smw/%smk" % (ns,ns,ns))
				result = combine(category, descript, stem, suffix, c_cat, c_des, c_stem, c_suff, prefix)

			else:
				#if it's a compound
				comp_category = item.find("%smwc/%spos/%sc" % (ns,ns,ns))
				category = item.findall(".//%smw/%spos/%sc" % (ns,ns,ns))
				stem = item.findall(".//%smw/%sstem" % (ns,ns))
				result = combinecmpd(comp_category, category, stem)
		else: pass
		return result

#Combines various fields to create proper mor tag for one word
def combine(category, descript, stem, suffix, c_cat, c_des, c_stem, c_suff, prefix):
	if prefix != None:
		mor = prefix.text + "#" + category.text
	else:
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
