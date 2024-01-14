import filecmp
import os
import shutil

class Blob:
    def writeBlob(id, file):
        shutil.copy(
            os.path.join(
                '.gitlet/stage',
                file),
            os.path.join(
                '.gitlet/blobs',
                id))

    def writeFileFromBlob(blobId, file):
        if os.path.dirname(file) != '':
            os.makedirs(os.path.dirname(file), exist_ok=True)
        shutil.copy(os.path.join('.gitlet/blobs', blobId), file)

    def makeMergeString(current, given):
        s = "<<<<<<< HEAD"
        s += "\n"
        s += '\n'.join(current)
        s += "========"
        s += '\n'
        s += '\n'.join(given)
        s += ">>>>>>>>"
        return s

    def compare(blob1, blob2):
        return filecmp.cmp(os.path.join('.gitlet/blobs', blob1),
                           os.path.join('.gitlet/blobs', blob2), shallow=False)

    def getContent(blob):
        file = open(os.path.join('.gitlet/blobs', blob))
        contents = file.readlines()
        file.close()
        return contents



