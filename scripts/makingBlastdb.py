import sys
import os
import multiprocessing as mp



def makingMSA(species, path):
    output = path + "/blast_dir/" + species + "/" + species
    #print(output)

    input = path + "/genome_dir/" + species +  "/" + species + ".fa"
    #print(input)
    os.system("makeblastdb  -dbtype prot -in " + input + " -out " + output)

    os.chdir(path + "/blast_dir/" + species)
    os.system("ln -s ../../genome_dir/" + species + "/" + species + ".fa .")


def gettingId(line):
    id = line.replace("\n", "")
    return id



def main():
    ########################### Input ###################################
    parameter = sys.argv[1:]
    path = parameter[0]

    #####################################################################



    speciesFile = open("tmp/species.txt", "r")
    pool = mp.Pool(mp.cpu_count())

    results = [pool.apply(makingMSA, args=(gettingId(line), path)) for line in speciesFile]

    pool.close()
    #print(results)

if __name__ == '__main__':
    main()