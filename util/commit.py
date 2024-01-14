from datetime import datetime
import os
import uuid

from util.branches import Branches 
from util.stage import Stage
from util.blob import Blob


class Commit:
    def __init__(self, merge=False):
        self.merge = merge

    def getFromId(self, id, minimal=False):
        if os.path.exists(f'.gitlet/commits/{id}'):
            fp = f'.gitlet/commits/{id}'
            self.merge = False
        else:
            fp = f'.gitlet/commits/merge-{id}'
            self.merge = True
        file = open(fp, 'r')
        parentData = file.readline().strip('\n')
        if not self.merge:
            self.parent = parentData
        else:
            self.parent = parentData.split(' ')
        if not minimal:
            self.message = file.readline().strip('\n')
            self.time = file.readline().strip('\n')
            fileMaps = {}
            while True:
                dir = file.readline()
                if not dir:
                    break
                blob = file.readline()
                dir = dir.strip('\n')
                blob = blob.strip('\n')
                fileMaps[dir] = blob
            self.fileMaps = fileMaps
        file.close()
        self.id = id

    def createNew(self, id, parent, message, files, merge=False):
        self.id = id
        self.parent = parent
        self.message = message
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.merge = merge
        self.fileMaps = {}

    def addCommit(self, id, message):
        self.id = id
        self.message = message
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.parent = Branches.getCurrentCommitId()
        parentCommit = self.getParent()
        fileMaps = parentCommit.fileMaps
        newFiles = Stage.getStagedFiles()
        for file in newFiles:
            blobId = uuid.uuid4().hex
            Blob.writeBlob(blobId, file)
            fileMaps[file] = blobId
        filesToRemove = Stage.getNotInclude()
        for file in filesToRemove:
            fileMaps.pop(file)
        self.fileMaps = fileMaps

    def writeCommit(self):
        if self.merge == False:
            fp = f'.gitlet/commits/{self.id}'
        else:
            fp = f'.gitlet/commits/merge-{self.id}'
        file = open(fp, 'w')

        if self.merge == False:
            file.write(self.parent)
            file.write('\n')
        else:
            file.write(f'{self.parent[0]} {self.parent[1]}')
            file.write('\n')

        file.write(self.message)
        file.write('\n')
        file.write(self.time)
        for dir in self.fileMaps:
            file.write('\n')
            file.write(dir)
            file.write('\n')
            file.write(self.fileMaps[dir])
        file.close()
        Branches.updateCurrentCommitId(self.id)

    def getParent(self, minimal=False):
        if self.parent == "":
            return False

        if self.merge == True:
            par1 = Commit()
            par1.getFromId(self.parent[0], minimal)
            par2 = Commit()
            par2.getFromId(self.parent[1], minimal)
            parent = [par1, par2]
        else:
            parent = Commit()
            parent.getFromId(self.parent, minimal)
        return parent

    def getAncestorsWithDistance(self, distance=1):
        def mergeDictionaries(d1, d2):
            for ele in d2:
                if ele not in d1:
                    d1[ele] = d2[ele]
                elif d1[ele] > d2[ele]:
                    d1[ele] = d2[ele]
            return d1

        parent = self.getParent(minimal=True)
        if parent == False:
            return {self.id: distance}
        elif not isinstance(parent, list):
            return mergeDictionaries(
                parent.getAncestorsWithDistance(distance + 1), {self.id: distance})
        else:
            return mergeDictionaries(
                mergeDictionaries(parent[0].getAncestorsWithDistance(distance + 1),
                                  {self.id: distance}),
                parent[1].getAncestorsWithDistance(distance + 1)),

    def getAncestors(self):
        parent = self.getParent(minimal=True)
        if parent == False:
            return {self.id}
        if not isinstance(parent, list):
            ancestors = parent.getAncestors()
            ancestors.add(self.id)
            return ancestors
        else:
            ancestors = parent[0].getAncestors()
            ancestors.update(parent[1].getAncestors())
            ancestors.add(self.id)
            return ancestors

    def getUntrackedFiles(self):
        untracked = []
        for path, subdirs, files in os.walk('.'):
            for name in files:
                file = os.path.join(path, name)[2:]
                if file[:8] != '.gitlet/' and file not in self.fileMaps:
                    untracked.append(file)
        return untracked
