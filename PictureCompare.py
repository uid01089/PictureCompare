from __future__ import annotations
from typing import Tuple
import ks.FileUtil as FileUtil
import ks.PictureUtil as PictureUtil
from ks.Stream import Stream
import re
import os



#CHECK_DIR = ".*?Mein Fotostream"
ROOT_DIR = 'c:/Users/msk/SynologyDrive/17_Pictures'
CHECK_DIR = 'd:/00_Bilder'
FILE_PATTERN = '.*?\.orf$'

class Pic :
    def __init__(self, path) -> None:
        self.path = path
        self.hash = FileUtil.getHash(path)

    def getHash(self) -> str:
        return self.hash
    
    def getPath(self):
        return  self.path

    def isSimilar(self, other : Pic) -> bool:
        
        return self.getHash() == other.getHash()


class PictureCompare :
    def __init__(self, rootDir, checkDir, filePattern) -> None:
        self.rootDir = rootDir
        self.checkDir = checkDir
        self.filePattern = filePattern

    def readInFiles(self) -> PictureCompare:
        allPictures = FileUtil.getPaths(self.rootDir, self.filePattern)
        pathsToCheck  = set(FileUtil.getPaths(self.checkDir, self.filePattern))

        self.checkPictures = Stream(pathsToCheck) \
        .mapP(Pic) \
        .collectToList()

        self.refPictures = Stream(allPictures) \
        .filter(lambda path:not path in pathsToCheck) \
        .mapP(Pic) \
        .collectToList() 

        print (f"All pictures: {len(allPictures)}")
        print (f"Pictures to be checked: {len(self.checkPictures)}")
        print (f"Pictures as references: {len(self.refPictures)}")

        return self       

    def _comparePicture(self, pic: Pic) -> list: 
        equalPics = Stream(self.refPictures) \
            .filter(pic.isSimilar) \
            .collectToList()
        equalPics.insert(0, pic)
        return equalPics
    
    def compare(self) -> PictureCompare:
        
        equalPics = Stream(self.checkPictures) \
            .mapP(self._comparePicture) \
            .filter(lambda x : len(x) > 1) \
            .collectToList()

        for picList in equalPics:
            print ('----------------------')
            fileToRename = picList.pop(0)
            print (f"{fileToRename.getPath().__str__()} -> {fileToRename.getPath().__str__()}.double" )
            os.rename(fileToRename.getPath().__str__(), fileToRename.getPath().__str__()+".double")
            for pic in picList:
                print (pic.getPath().__str__())


        
        return self       


def main(): 

    PictureCompare(ROOT_DIR, CHECK_DIR, FILE_PATTERN) \
    .readInFiles() \
    .compare()

    
    #Stream(meinFotoStream).foreach(lambda path: print(path.__str__()))

    #Stream(allPictures).foreachP(lambda path: PictureUtil.getExif(path))

    print("end")
    exit


if __name__ == '__main__':
    main()
