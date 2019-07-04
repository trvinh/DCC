import sys
import os
import multiprocessing as mp



def makingMSA(id, path):
    output = path + "/core_orthologs/" + id + "/" + id  + ".aln"
    #print(output)

    input = path + "/core_orthologs/" + id +  "/" + id + ".fa"
    #print(input)
    os.system("mafft --quiet --localpair --maxiterate 1000 " + input + " > " + output)




def gettingId(line):
    id = line.replace("\n", "")
    return id

def main():
    ########################## Input ##########################################
    parameter = sys.argv[1:]
    path = parameter[0]
    ###########################################################################
    groupsFile = open("tmp/commonOmaGroups.txt", "r")
    pool = mp.Pool(mp.cpu_count())

    results = [pool.apply(makingMSA, args=(gettingId(line), path)) for line in groupsFile]

    pool.close()
    #print(results)

if __name__ == '__main__':
    main()