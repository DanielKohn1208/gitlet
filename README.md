# Gitlet
This program attempts to mimic several of the features implemented by git. This project was completed using the python programming language and was inspired by the project in the course cs 61B taught at UC Berkeley. This version is done in python and while similar to the version project presented in the class, *IT DOES BEHAVE SLIGHTLY DIFFERENTLY*

## Commands

### init 
```
python gitlet.py init
```
Initializes the git repository
### add
```
python gitlet.py add [filename]
```
Add's the given file to the staging area. 

### rm
```
python gitlet.py rm [filename]
```
If the file is in the staging area, remove it from the staging area. If the file isn't in the staging area, but is in the previous commit, the file is removed from the filesystem and all future commits

### commit
```
python gitlet.py commit [message]
```
Add's all of the staged changes and remove's file's flagged to be removed to the commit tree with the provided message

### log
```
python gitlet.py log
```
Display's information about all of the commit's from the current commit on the current branch to the initial commit

### status
```
python gitlet.py status
```
Print's out information about the current status of the gitlet repository

### branch
```
python gitlet.py branch [branchname]
```
Create's a new branch with the given name

### checkout
```
python gitlet.py checkout [branchname]
```
Switches the current branch to the given branchname
```
python gitlet.py checkout -- [filename]
```
Checks out the given file to the most recent commit
```
python gitlet.py checkout [commitId] -- [filename]
```
Checks out the given file at the given commitId

### reset
```
python gitlet.py reset
```
Resets all files to the last commit

### merge
```
python gitlet.py merge [branchname]
```
Merges all files from the branchname into the current branch

### branch-rm
```
python gitlet.py branch-rm [branchname]
```
Deletes the specified branchname

