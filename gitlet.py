# Entry point for application
import os
import sys
import uuid

from repo import Blob, Branches, Commit, Stage


args = sys.argv[1:]

# Commands


def init():
    if os.path.exists(".gitlet"):
        print("ERROR: A gitlet directory already exists here")
        return
    os.makedirs(".gitlet/blobs")
    os.makedirs(".gitlet/stage")
    os.makedirs(".gitlet/commits")
    os.makedirs(".gitlet/data")
    file = open('.gitlet/rm_on_commit', 'w')
    file.close()
    newCommitId = uuid.uuid4().hex
    Branches.updateCurrentBranch("master")
    Branches.updateCurrentCommitId(newCommitId)
    commit = Commit()
    commit.createNew(newCommitId, '', 'Initial Commit', {})
    commit.writeCommit()
    print("gitlet repository has been initialized")


def add(filename):
    Stage.addToStagingArea(filename)
    print("the file has been added")


def commit(message):
    commit = Commit()
    commit.addCommit(uuid.uuid4().hex, message)
    commit.writeCommit()
    Stage.clearStagingArea()


def log():
    id = Branches.getCurrentCommitId()
    commit = Commit()
    commit.getFromId(id)
    while commit is not False:
        print('===')
        print(f'commit  {commit.id}')
        # NEED STUFF FOR MERGE
        if commit.merge:
            print(f'Merge: {commit.parent[0]} {commit.parent[1]}')
        print(f'Date: {commit.time}')
        print(commit.message)
        if not commit.merge:
            commit = commit.getParent()
        else:
            commit = commit.getParent()[0]
        print()


def branch(branchName):
    if branchName == "head":
        print("a branch with this name is not allowed")
        return
    if os.path.exists(os.path.join('.gitlet/data', branchName)):
        print('a branch with that name already exists')
        return

    currentCommitId = Branches.getCurrentCommitId()
    Branches.updateCurrentBranch(branchName)
    Branches.updateCurrentCommitId(currentCommitId)
    print("branch has been added")


def rmBranch(branchname):
    if branchname == "head":
        print("a branch with that name does not exist")
    elif Branches.getCurrentBranch() == branchname:
        print("cannot remove the current branch")
    elif not os.path.exists(os.path.join('.gitlet/data', branchname)):
        print('a branch with that name does not exist')
    else:
        os.remove(os.path.join('.gitlet/data', branchname))
        print("the branch has been removed")


def rm(filename):
    if not os.path.exists(filename):
        print("the file does not exist")
        return

    if os.path.exists(os.path.join('.gitlet/stage/', filename)):
        Stage.removeFromStagingArea(filename)
        print('the file has been removed from the staging area')
        return

    currentCommit = Commit()
    currentCommit.getFromId(Branches.getCurrentCommitId())
    if filename not in currentCommit.fileMaps.keys():
        print("You have no reason to rm this file")
        return

    Stage.addNotInclude(filename)
    os.remove(filename)
    print("the file has been removed")


def status():
    print('=== Branches ===')
    currentBranch = Branches.getCurrentBranch()
    for branch in Branches.getAllBranches():
        if branch == currentBranch:
            print(f"*{currentBranch}")
        else:
            print(branch)
    print()

    print('=== Staged Files ===')
    for file in Stage.getStagedFiles():
        print(file)
    print()

    print('=== Removed Files ===')
    for file in Stage.getNotInclude():
        print(file)
    print()

    currentCommitId = Branches.getCurrentCommitId()
    currentCommit = Commit()
    currentCommit.getFromId(currentCommitId)

    print('=== Modifictations Not Staged for Commit ===')
    for file in currentCommit.fileMaps:
        if not os.path.exists(file):
            print(f"{file} (deleted)")
        else:
            blobContent = Blob.getContent(currentCommit.fileMaps[file])
            f = open(file, 'r')
            content = f.readlines()
            f.close()
            if content != blobContent:
                print(f'{file} (modified)')
    print()

    untrackedFiles = currentCommit.getUntrackedFiles()
    print('=== Untracked Files ===')
    for file in untrackedFiles:
        print(file)
    print()


def checkoutFile(filename):
    print("trying to checkout")
    currentCommitId = Branches.getCurrentCommitId()
    currentCommit = Commit()
    # adding some try/catch stuff here in the future
    currentCommit.getFromId(currentCommitId)
    Blob.writeFileFromBlob(currentCommit.fileMaps[filename], filename)
    print("checkout is complete")


def checkoutFileByCommitId(filename, commitId):
    commit = Commit()
    commit.getFromId(commitId)
    print("the commit file maps are")
    print(commit.fileMaps)
    Blob.writeFileFromBlob(commit.fileMaps[filename], filename)
    print('checkout is complete')


def checkoutBranch(branchName):
    if branchName == "head" or not os.path.exists(
            os.path.join('.gitlet/data', branchName)):
        print('the branch does not exist')
        exit()
    # old commit
    oldId = Branches.getCurrentCommitId()
    oldCommit = Commit()
    oldCommit.getFromId(oldId)
    oldFileMaps = oldCommit.fileMaps

    Branches.updateCurrentBranch(branchName)
    commitId = Branches.getCurrentCommitId()
    commit = Commit()
    commit.getFromId(commitId)
    fileMaps = commit.fileMaps

    for file in fileMaps:
        Blob.writeFileFromBlob(fileMaps[file], file)

    for file in oldFileMaps:
        if file not in fileMaps:
            os.remove(file)

    print('checked out the branch')


def reset(commitId):
    currentCommitId = Branches.getCurrentCommitId()
    currentCommit = Commit()
    currentCommit.getFromId(currentCommitId)
    currentFileMaps = currentCommit.fileMaps

    resetCommit = Commit()
    resetCommit.getFromId(commitId)
    resetFileMaps = resetCommit.fileMaps

    for file in resetFileMaps:
        Blob.writeFileFromBlob(resetFileMaps[file], file)

    for file in currentFileMaps:
        if file not in resetFileMaps:
            os.remove(file)

    Branches.updateCurrentCommitId(commitId)


def merge(branchName):
    # Failure Cases
    if len(Stage.getStagedFiles()) > 0 or len(Stage.getNotInclude()) > 0:
        print("You have uncommited changes")
        return

    currentBranchName = Branches.getCurrentBranch()
    if currentBranchName == branchName:
        print("Cannot merge a branch with itself")
        return

    if branchName not in Branches.getAllBranches():
        print("Branch name not in branches")
        return

    # get current Commit
    currentCommitId = Branches.getCurrentCommitId()
    currentCommit = Commit()
    currentCommit.getFromId(currentCommitId)

    givenCommitId = Branches.getCommidIdByBranch(branchName)
    givenCommit = Commit()
    givenCommit.getFromId(givenCommitId)

    splitPointId = Branches.getSplitPoint(currentCommit, givenCommit)

    print('split point id is', splitPointId)
    print('given id is ', givenCommitId)
    print('current point id is' , currentCommitId)

    if splitPointId == givenCommitId:
        print("Given branch is an ancestor of the current branch")
        exit()

    elif splitPointId == currentCommitId:
        Branches.updateCurrentCommitId(givenCommitId)
        checkoutBranch(currentBranchName)
        print('Current Branch fast-forwarded')
        exit()

    splitPoint = Commit()
    splitPoint.getFromId(splitPointId)

    newCommit = Commit(merge=True)

    newFiles = {}
    merges = []
    untracked = currentCommit.getUntrackedFiles()

    # go through currentCommit
    for file in currentCommit.fileMaps:
        # in other branch
        currentFileContent = Blob.getContent(currentCommit.fileMaps[file])
        if file in givenCommit.fileMaps:
            givenFileContent = Blob.getContent(givenCommit.fileMaps[file])
            if currentFileContent == givenFileContent:
                newFiles[file] = currentCommit.fileMaps[file]

            else:
                if file in splitPoint.fileMaps:
                    splitPointFileContent = Blob.getContent(
                        splitPoint.fileMaps[file])
                    if splitPointFileContent == currentFileContent:
                        newFiles[file] = givenCommit.fileMaps[file]
                    elif splitPointFileContent == givenFileContent:
                        newFiles[file] = currentCommit.fileMaps[file]
                    else:
                        mergeString = Blob.makeMergeString(
                            currentFileContent, givenFileContent)
                        merges.append({"file": file, "content": mergeString})
                else:
                    mergeString = Blob.makeMergeString(
                        currentFileContent, givenFileContent)
                    merges.append({"file": file, "content": mergeString})

            givenCommit.fileMaps.pop(file)
        else:
            if file not in splitPoint.fileMaps or Blob.getContent(
                    splitPoint.fileMaps[file]) != currentFileContent:
                newFiles[file] = currentCommit.fileMaps[file]

    # at this point all files left in given are not in current commit but may
    # be untracked
    for file in givenCommit.fileMaps:
        givenFileContent = Blob.getContent(givenCommit.fileMaps[file])
        if file in untracked:
            f = open(file)
            untrackedContent = f.readlines()
            f.close()
            if untrackedContent != givenFileContent:
                print("There is an untracked file in the way; delete it or add it first")
                exit()
        if file not in splitPoint.fileMaps or Blob.getContent(
                splitPoint.fileMaps[file]) != currentFileContent:
            newFiles[file] = givenCommit.fileMaps[file]

    # go through remainingCommit
    newCommitId = uuid.uuid4().hex
    newCommit.createNew(newCommitId,
                        [currentCommitId,
                         givenCommitId],
                        f'Merged {branchName} into {currentBranchName}',
                        newFiles,
                        merge=True
                        )
    newCommit.writeCommit()
    Branches.updateCurrentCommitId(newCommitId)
    for file in newFiles:
        Blob.writeFileFromBlob(newFiles[file], file)
    for merge in merges:
        file = open(merge['file'], 'w')
        file.write(merge['content'])
        file.close()
        Stage.addToStagingArea(merge['file'])
        print(f"Merge conflict exists in: {merge['file']}")
    print('Merge complete')


if len(args) == 0:
    print('no command provided')
    exit()

if args[0] == "init":
    init()
    exit()

if not os.path.exists(".gitlet"):
    print("Error: A gitlet directory does not exists, create one with 'gitlet init'")

elif args[0] == "add":
    try:
        filename = args[1]
    except BaseException:
        print("add requires an argument")
        exit()
    add(filename)

elif args[0] == "rm":
    try:
        filename = args[1]
    except BaseException:
        print("rm takes an argument")
        exit()
    rm(filename)

elif args[0] == "commit":
    try:
        message = args[1]
    except BaseException:
        message = ''
    commit(message)

elif args[0] == "log":
    log()

elif args[0] == "branch":
    try:
        newBranchName = args[1]
    except BaseException:
        print("branch requires an argument")
        exit()
    branch(newBranchName)

elif args[0] == "status":
    status()
elif args[0] == "checkout":
    if len(args) == 4:
        commitId = args[1]
        fileName = args[3]
        checkoutFileByCommitId(fileName, commitId)
    elif len(args) >= 1:
        if args[1] == "--":
            try:
                filename = args[2]
            except BaseException:
                print('checkout does not recognize the provided arguments')
                exit()
            checkoutFile(filename)
        else:
            try:
                branchName = args[1]
            except BaseException:
                print('checkout does not recognize the provided arguments')
                exit()
            checkoutBranch(branchName)
    else:
        print("checkout does not recognize the provided arguments")
elif args[0] == "reset":
    try:
        commitId = args[1]
    except BaseException:
        print("reset takes an argument")
        exit()
    reset(commitId)
elif args[0] == "merge":
    try:
        mergeBranch = args[1]
    except BaseException:
        print("merge takes an argument")
        exit()
    merge(mergeBranch)
elif args[0] == "branch-rm":
    try:
        branch = args[1]
    except BaseException:
        print("branch takes an argument")
        exit()
    rmBranch(branch)
else:
    print("This is not one of the recognized arguments")
