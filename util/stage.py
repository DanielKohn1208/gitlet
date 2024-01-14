import os
import shutil

class Stage:
    def clearStagingArea():
        shutil.rmtree('.gitlet/stage')
        os.makedirs('.gitlet/stage')
        file = open('.gitlet/rm_on_commit', 'w')
        file.close()

    def addToStagingArea(file):
        dir = '/'.join(file.split('/')[:-1])
        if dir != "":
            os.makedirs(os.path.join('.gitlet/stage', dir), exist_ok=True)
        shutil.copy(file, os.path.join('.gitlet/stage', file))

    def removeFromStagingArea(file):
        os.remove(os.path.join('.gitlet/stage', file))

    def getStagedFiles():
        stagedFiles = []
        for path, subdirs, files in os.walk(".gitlet/stage"):
            for name in files:
                stagedFile = os.path.join(path, name)[14:]
                stagedFiles.append(stagedFile)
        return stagedFiles

    def addNotInclude(filename):
        file = open('.gitlet/rm_on_commit', 'a')
        file.write(f'{filename}\n')
        file.close()

    def getNotInclude():
        notCommitedFiles = []
        file = open('.gitlet/rm_on_commit', 'r')
        notCommitedFile = file.readline().strip('\n')
        while True:
            if not notCommitedFile:
                break
            elif notCommitedFile != "":
                notCommitedFiles.append(notCommitedFile)
            notCommitedFile = file.readline().strip('\n')
        file.close()
        return notCommitedFiles


