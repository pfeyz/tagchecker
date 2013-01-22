
README

To get to the right location (the right Dropbox folder):
cd <folder name> --> change directory to folder 
ls --> list whatever is in folder

Once you're in the tagchecker folder, you can run the program with the following command:

python tagchecker.py "Valian/01b.xml" "errors/Valian_01b_errors.csv" -s MOT,CHI

where the final three arguments are the file you want to check, the file you
want to save to, and (optionaly) a comma seperated list of speakers you want to
limit corrections to. If the last file already exists, the program will append
the errors to the end of it. If it doesn't exist, it will create the file.

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


