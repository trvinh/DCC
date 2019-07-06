####################### Imports #########################################
import sys
import os
import time




########################### Tests ########################################
#print(type(species))

#for testing:
#speciesList = ["YEAST","HUMAN"]
#speciesSet = set(["YEAST","HUMAN"])
#speciesTaxId = [559292,9606]
#print(type(speciesSet))
#nrMissingSpecies = 0
#path = "/Users/hannahmuelbaier/Desktop/Bachelorarbeit"
#mode = "TRUE"

############################ Functions #####################################

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

def gettingOmaGroups(speciesSet, nr):
    omaGroups = openFileToRead("data/oma-groups.txt")
    commonOmaGroups = []
    speciesDic = {}
    for i in omaGroups:
        row = i.split("\t")

        if len(row) != 1:
            ProteinIds = []
            counter = 0
            for j in range(2, len(row)):
                species = row[j][0:5]
                if species in speciesSet:
                    ProteinIds.append(row[j])
                    counter += 1

            if counter >= (len(speciesSet) - int(nr)):
                commonOmaGroups.append(row[0])
                speciesDic = createSpeciesDic(speciesDic, ProteinIds, row[0])

    return commonOmaGroups, speciesDic

def createSpeciesDic(Dic, ProteinIds, OmaGroup):
    #createSpeciesDic creates a Dic in the following format
    #output: Dic: {<species>: {proteinId : OmaGroup}}
    #input:
    #Dic: old species_dic that will be completed
    #ProteinIds: all protein IDs of one OmaGroup
    #OmaGroup: ID of the group which will be added to the Dic


    for i in ProteinIds:
        species = i[0:5]
        protId = i.replace("\n", "")
        try:
            Dic[species][protId] = OmaGroup
        except KeyError:
            Dic[species] = {}
            Dic[species][protId] = OmaGroup

    #print(Dic)
    return Dic

def gettingSeqeunces(dataset, speciesDic, speciesCode):
    #gettingSeqeunces gets the requiered sequences of one species and creates the speciesSeqeunces
    #input:
    #dataset file of species of the genome_dir
    #speciesDic: Dic for all species as a key : (Protein, OmaGroup ID)
    #speciesCode: OmaCode for the species out of 5 letters
    speciesSequences = {}
    speciesSequences[speciesCode] = {}

    for line in dataset:
        if line[0] == ">":
            ID = line[1:-1]
            try:
                groupNr = speciesDic[speciesCode][ID]
                speciesSequences[speciesCode][ID] = next(dataset)
            except KeyError:
                pass
    return speciesSequences

def createFiles(speciesDic, sequenceDic, speciesNameOneSeq, OmaGroupSet, mode, path):
    """creates the core_ortholog folder and the saves the OmaGroups as multi_fasta files"""
    #input:
    #speciesDic: Dic {<speciesId>: {<proteinID>: <OmaGroup Id>}}
    #seqeunceDic: Dic {<speciesId>: {<proteinID>: <protein sequence>}}
    #speciesNameOneSeq: <speciesCode>@<TaxonomyId>@2

    #update momentan, wenn diese Methode ermöglicht ist, muss ansonsten Gruppe imme gelöscht werden bevor sie befüllt wird

    if mode == "FALSE":

        speciesCode = speciesNameOneSeq.split("@")[0]


        for key in speciesDic[speciesCode]:
            OmaGroup = speciesDic[speciesCode][key]
            if OmaGroup in OmaGroupSet:
                file = openFileToAppend(path + "/core_orthologs/" + OmaGroup + "/" + OmaGroup + ".fa")

            else:
                try:
                    file = openFileToWrite(path + "/core_orthologs/" + OmaGroup + "/" + OmaGroup + ".fa")

                except FileNotFoundError:
                    createFolder(path + "/core_orthologs", OmaGroup)
                    file = openFileToWrite(path + "/core_orthologs/" + OmaGroup + "/" + OmaGroup + ".fa")

            OmaGroupSet.add(OmaGroup)

            header = ">" + OmaGroup + "|" + speciesNameOneSeq + "|" + key + "\n"
            seq = sequenceDic[speciesCode][key]

            file.write(header)
            file.write(seq)
            file.close()

        return(OmaGroupSet)

    else:

        speciesCode = speciesNameOneSeq.split("@")[0]
        for key in speciesDic[speciesCode]:
            OmaGroup = speciesDic[speciesCode][key]
            try:
                oldFile = openFileToRead(path + "/core_orthologs/" + OmaGroup + "/" + OmaGroup + ".fa")
            except FileNotFoundError:
                createFolder(path + "/core_orthologs", OmaGroup)
                newFile = openFileToWrite(path + "/core_orthologs/" + OmaGroup + "/" + OmaGroup + ".fa")
                header = ">" + OmaGroup + "|" + speciesNameOneSeq + "|" + key + "\n"
                seq = sequenceDic[speciesCode][key]

                newFile.write(header)
                newFile.write(seq)
                newFile.close()
                pass

            header = ">" + OmaGroup + "|" + speciesNameOneSeq + "|" + key + "\n"
            check = False
            for line in oldFile:
                if line == header:
                    check = True
                    break
                else:
                    pass
            oldFile.close()

            if check == False:
                file = openFileToAppend(path + "/core_orthologs/" + OmaGroup + "/" + OmaGroup + ".fa")
                seq = sequenceDic[speciesCode][key]
                file.write(header)
                file.write(seq)

                file.close()

def makeOneSeqSpeciesName(code,TaxId):
    #creates the file name for the dataset of the species
    name = code + "@" + str(TaxId) + "@" + "2"
    return name

def createFolder(path, folder_name):
    """creates a folder with the given name at the given path"""
    #input:
    #path: string, path to storing location
    #name: string, name of the new folder
    try:
        os.mkdir(path + "/" + folder_name)
    except FileExistsError:
        return "Folder exists"

def makeTmpFiles(data, name):
    """creates tmp files of the computed OmaGroups and selected species"""
    createFolder(os.getcwd(), "tmp")
    tmp = openFileToWrite("tmp/" + name + ".txt")
    for i in data:
        tmp.write(i + "\n")

    tmp.close()

def main():
    ###################### Input from R #####################################
    start = time.time()
    parameter = sys.argv[1:]
    speciesList = str(parameter[0]).split(",")
    speciesSet = set(speciesList)
    speciesTaxId = str(parameter[1]).split(",")
    for i in range(0, len(speciesTaxId)):
        speciesTaxId[i] = int(speciesTaxId[i])
    nrMissingSpecies = parameter[2]
    path = parameter[3]
    mode = parameter[4]

    ##########################################################################


    commonOmaGroups, speciesDic = gettingOmaGroups(speciesSet, nrMissingSpecies)

    createFolder(path, "core_orthologs")
    createFolder(path, "blast_dir")
    createFolder(path, "genome_dir")
    speciesNames = []
    OmaGroupSet = set()


    for key in speciesDic:
        for i in range(0, len(speciesList)):
            if speciesList[i] == key:
                filename = makeOneSeqSpeciesName(key, speciesTaxId[i])
                break

        speciesDataset = openFileToRead(path + "/genome_dir/" + filename + "/" + filename + ".fa")
        sequenceDic = gettingSeqeunces(speciesDataset, speciesDic, key)
        OmaGroupSet = createFiles(speciesDic, sequenceDic, filename,OmaGroupSet, mode, path)
        speciesNames.append(filename)

    makeTmpFiles(commonOmaGroups, "commonOmaGroups")
    makeTmpFiles(speciesNames, "species")

    print("Finished searching. " + str(len(commonOmaGroups)) + " common OmaGroups were found and saved. Computing MSAs with MAFFT")
    ende = time.time()

    print('{:5.3f}s'.format(ende - start), end='  ')



if __name__ == '__main__':
    main()