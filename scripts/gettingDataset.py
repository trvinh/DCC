
########################## Imports ##################################
import sys
from Bio import SeqIO
import os
from pyfaidx import Fasta
import time
import json


########################### Testing ###################################
#path = "/Users/hannahmuelbaier/Desktop/Bachelorarbeit"
#speciesCode = ["DESA1","STAMF"]
#speciesTaxId = ["490899","399550"]


######################### Functions ################################


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

def makeOneSeqSpeciesName(code,TaxId):
    # creates the file name for the dataset of the species
    name = code + "@" + TaxId + "@" + "2"
    return name

def createFolder(path, folder_name):
    try:
        os.mkdir(path + "/" + folder_name)
    except FileExistsError:
        return "Folder exists"

# def makeTmpFile(species, path):
#     createFolder(path, "tmp")
#     try:
#         tmp = openFileToAppend(path + "/tmp/species.txt")
#     except FileNotFoundError:
#         tmp = openFileToWrite(path + "/tmp/species.txt")
#
#     tmp.write(species + "\n")

def getDataset(speciesCode, speciesTaxId, path):
    start = time.time()
    print(speciesCode)
    print(speciesTaxId)
    allProteins = SeqIO.parse("data/oma-seqs.fa", "fasta")
    for j in range(0, len(speciesCode)):

        name = makeOneSeqSpeciesName(speciesCode[j], speciesTaxId[j])
        #print(name)

        createFolder(path, "genome_dir")
        #makeTmpFile(name)

        try:
            os.mkdir(path + "/genome_dir/" + name)
        except FileExistsError:
            print("File exists already for species " + speciesCode[j])
            return("FileExistsError")

        newFile = openFileToWrite(path + "/genome_dir/" + name + "/" + name + ".fa")

        #print(speciesCode[j])
        getSequence(allProteins, speciesCode[j], newFile, name)
        newFile.close()
    allProteins.close()
    ende = time.time()
    print('{:5.3f}s'.format(ende-start), end='  ')


def getSequence(allProteins, speciesCode, newFile, name):
    check = False
    for record in allProteins:
        codeAllProteins = record.id[0:5]
        if codeAllProteins == speciesCode:
            check = True
            newFile.write(">" + str(record.id) + "\n")
            newFile.write(str(record.seq) + "\n")
        elif check == True:
            newFile.close()
            print("saved " + name)
            break


def getDataset2(speciesCode, speciesTaxId, path):
    createFolder(path, "genome_dir")
    start = time.time()
    name = makeOneSeqSpeciesName(speciesCode, speciesTaxId)
    try:
        os.mkdir(path + "/genome_dir/" + name)
    except FileExistsError:
        print("File exists already for species " + speciesCode)
        return("FileExistsError")

    #print("faidx --regex \"" + speciesCode + "\" /Users/hannahmuelbaier/Desktop/Bachelorarbeit/oma-seqs.fa " + "> " + path + "/genome_dir/" + name + "/" + name + ".fa")
    os.system("faidx --regex \"" + speciesCode + "\" /Users/hannahmuelbaier/Desktop/Bachelorarbeit/oma-seqs.fa " + ">" + path + "/genome_dir/" + name + "/" + name + ".fa")

    ende = time.time()
    print('{:5.3f}s'.format(ende - start), end='  ')

def getDataset3(speciesCode, speciesTaxId, path):
    createFolder(path, "genome_dir")
    start = time.time()

    toDo = []

    with open("data/oma-seqs-dic.fa") as f:
        sequence_dic = json.load(f)

    for i in range(0,len(speciesCode)):
        #print(len(speciesCode))
        name = makeOneSeqSpeciesName(speciesCode[i], speciesTaxId[i])
        #print(name)

        try:
            os.mkdir(path + "/genome_dir/" + name)
            toDo.append(i)
        except FileExistsError:
            print("File exists already for species " + speciesCode[i])


    if toDo != []:
        allProteins = openFileToRead("data/oma-seqs.fa")
        allProteinsLines = allProteins.readlines()
        allProteins.close()

    for j in range(0,len(toDo)):
        name = makeOneSeqSpeciesName(speciesCode[toDo[j]], speciesTaxId[toDo[j]])
        newFile = openFileToWrite(path + "/genome_dir/" + name + "/" + name + ".fa")
        startLine = sequence_dic[speciesCode[toDo[j]]][0]
        #print(startLine)
        endLine = sequence_dic[speciesCode[toDo[j]]][1]


        #print(allProteinsLines[startLine])
        #print(type(sequence_dic))


        for z in range(startLine, endLine + 1):
            if allProteinsLines[z] == allProteinsLines[startLine]:
                newLine = allProteinsLines[z].replace(" ", "")
                newFile.write(newLine)
            elif allProteinsLines[z][0] != ">":
                newLine = allProteinsLines[z].replace("\n", "")
                newLine = newLine.replace(" ", "")
                newFile.write(newLine)
            else:
                newLine = allProteinsLines[z].replace(" ", "")
                newFile.write("\n" + newLine)

        newFile.close()

    ende = time.time()
    print('{:5.3f}s'.format(ende - start), end='  ')


def main():
    ########################### Input from R ############################

    parameter = sys.argv[1:]

    speciesCode = str(parameter[0]).split(",")
    speciesTaxId = str(parameter[1]).split(",")
    path = parameter[2]

    ########################## Function call ##############################
    getDataset3(speciesCode, speciesTaxId, path)
    #getDataset(speciesCode,speciesTaxId,path)


if __name__ == '__main__':
    main()

############################# Notes ###############################
# Doppelte Funktionen in den scripten: openFile Funktionen, createFolder
# Pfade müssen noch ersetzt werden
# testen!

