
README

List of shortcuts

#be (cop)
	"c3":"v:cop|be&3S", "cp":"v:cop|be&PRES", 
	"iv1":"pro:sub|I~v:cop|be&1S","yvp":"pro:sub|you~v:cop|be&PRES",
	"pec3":"pro:exist|there~v:cop|be&3S", "wc":"adv:wh|where~v:cop|be&3S",
	"whc":"pro:wh|who~v:cop|be&3S",
#be (aux)
	"wa":"adv:wh|where~aux|be&3S", "a3":"aux|be&3S", "ap":"aux|be&PRES",
	"wha":"pro:wh|who~aux|be&3S", "ya":"pro|you~aux|be&PRES",
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


To get to the right location (the right Dropbox folder):
cd <folder name> --> change directory to folder 
ls --> list whatever is in folder

Once you're in the tagchecker folder, you can run the program with the following command:

python tagchecker-new.py "Valian/01b.xml" "errors/Valian_01b_errors.csv"

where the final two arguments are the file you want to check and the file you want to save to, respectively. If 
the last file already exists, the program will append the errors to the end of it. If it doesn't exist, it will 
create the file.

--------

DO_NOT_DELETE is a shared file that keeps track of the position we're at within each file we're checking. You can go
in to manually edit it if you want to start at a particular line or want to backtrack a little. Just be careful
to not change any lines by accident since it is a shared file.

--

Other useful commands

Ctrl-Z will terminate the program without saving anything. This comes in handy when you mess up immediately following a save.

---
Valian folder contains all the xml files.

--- 

errors can be where we keep track of all the error files (as to not clutter up the tagchecker folder itself).

--


