####################### Imports #########################################
import sys
import os

###################### Input from R #####################################

parameter = sys.argv[1:]
speciesList = str(parameter[0]).split(",")
speciesSet = set(speciesList)
speciesTaxId = str(parameter[1]).split(",")
for i in range(0,len(speciesTaxId)):
    speciesTaxId[i] = int(speciesTaxId[i])
omaGroupId = parameter[2]
path = parameter[3]
mode = parameter[4]


#print(speciesList, speciesTaxId, omaGroupId, path, mode)

####################### for testing ######################################

#speciesList = ['DESA1', 'DESM0']
#speciesSet = set(speciesList)
#speciesTaxId = [490899, 765177]
#omaGroupId = int("1")
#path = "/Users/hannahmuelbaier/Desktop/Bachelorarbeit"
#mode = "FALSE"

#print(speciesList, speciesTaxId, omaGroupId, path, mode)


######################### Functions #####################################

def openFileToRead(location):
    #opens a file in mode read
    file = open(location, "r")
    return file

def openFileToWrite(location):
    # opens a file in mode write
    file = open(location, "w")
    return file

def openFileToAppend(location):
    #opens a file in mode read
    file = open(location, "a+")
    return file

def gettingOmaGroupProteins():
    fileGroups = openFileToRead("/Users/hannahmuelbaier/Desktop/Bachelorarbeit/oma-groups.txt")
    allGroups = fileGroups.readlines()
    fileGroups.close()

    groupLine = allGroups[int(omaGroupId) + 2].split("\t")
    proteinIds = groupLine[2:]

    return(proteinIds)

def createFolder(path, folder_name):
    """creates a folder with the given name at the given path"""
    #input:
    #path: string, path to storing location
    #name: string, name of the new folder
    try:
        os.mkdir(path + "/" + folder_name)
    except FileExistsError:
        return "Folder exists"

def getSpeciesDic():
    speciesDic = {}
    for i in range(0, len(speciesList)):
        speciesDic[speciesList[i]] = speciesTaxId[i]

    return(speciesDic)

def makeOneSeqId(speciesDic, species):
    header = species + "@" + str(speciesDic[species]) + "@" + "2"
    return(header)

def createHeader(protId, speciesHeader):
    header = str(omaGroupId) + "|" + speciesHeader + "|" + protId[0:10]
    return(header)

def gettingSequences(speciesCode, protId, SeqDic, speciesDic):

    fileName = makeOneSeqId(speciesDic, speciesCode)
    fileSpecies = openFileToRead(path + "/genome_dir/" + fileName + "/" + fileName + ".fa")
    dataset = fileSpecies.readlines()
    fileSpecies.close()
    lineNr = int(protId[6:11])
    #header = dataset[lineNr * 2 - 2]
    header = createHeader(protId, fileName)
    seq = dataset[lineNr * 2 - 1]

    SeqDic[header] = seq

    return SeqDic

def createFiles(Dic):
    newFile = openFileToWrite(path + "/core_orthologs/" + str(omaGroupId) + "/" + str(omaGroupId) + ".fa")
    for key in Dic:
        newFile.write(">" + key + "\n")
        newFile.write(Dic[key])

def main():
    speciesDic = getSpeciesDic()
    proteinIds = gettingOmaGroupProteins()
    SequenceDic = {}

    createFolder(path, "core_orthologs")

    for i in proteinIds:
        speciesCode = i[0:5]
        if speciesCode in speciesSet:
            SequenceDic = gettingSequences(speciesCode, i, SequenceDic, speciesDic)

    createFiles(SequenceDic)

    return ("Oma Group " + omaGroupId + "has been saved in your core_orthologs folder")




if __name__ == '__main__':
    main()
