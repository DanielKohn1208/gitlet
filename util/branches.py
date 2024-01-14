import os
import sys

class Branches:
    def updateCurrentBranch(newBranchName):
        file = open(f'.gitlet/data/head', 'w')
        file.write(newBranchName)
        file.close()

    def getCurrentBranch():
        file = open(f'.gitlet/data/head', 'r')
        currentBranch = file.readline().strip('\n')
        file.close()
        return currentBranch

    def updateCurrentCommitId(newCommitId):
        branchName = Branches.getCurrentBranch()
        file = open(os.path.join('.gitlet/data', branchName), 'w')
        file.write(newCommitId)
        file.close()

    def getCurrentCommitId():
        branchName = Branches.getCurrentBranch()
        file = open(os.path.join('.gitlet/data', branchName), 'r')
        commitId = file.readline()
        file.close()
        return commitId

    def getCommidIdByBranch(branchName):
        file = open(os.path.join('.gitlet/data', branchName), 'r')
        commitId = file.readline()
        file.close()
        return commitId

    def getAllBranches():
        branches = os.listdir('.gitlet/data')
        branches.remove('head')
        return branches

    def getSplitPoint(current, given):
        ancestorsWithDistance = current.getAncestorsWithDistance()
        givenAncestors = given.getAncestors()
        lowestDistance = sys.maxsize
        splitPoint = None

        for anc in givenAncestors:
            if anc in ancestorsWithDistance and lowestDistance > ancestorsWithDistance[anc]:
                lowestDistance = ancestorsWithDistance[anc]
                splitPoint = anc
        return splitPoint


