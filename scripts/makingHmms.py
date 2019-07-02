import sys
import os
import multiprocessing as mp

parameter = sys.argv[1:]
path = parameter[0]

#path = "/Users/hannahmuelbaier/Desktop/Bachelorarbeit"





def makingHmm(id, path):
    try:
        os.mkdir(path + "/core_orthologs/" + id + "/hmm_dir")
    except FileExistsError:
        pass

    output = path + "/core_orthologs/" + id + "/hmm_dir/" + id + ".hmm"
    #print(output)

    input = path + "/core_orthologs/" + id + "/" + id + ".aln"
    #print(input)
    os.system("hmmbuild -o " + path + "/tmp/hmmbuild.txt --amino " + output + " " + input)

def gettingId(line):
    id = line.replace("\n", "")
    return id

def main():
    groupsFile = open(path + "/tmp/commonOmaGroups.txt", "r")
    pool = mp.Pool(mp.cpu_count())

    results = [pool.apply(makingHmm, args=(gettingId(line), path)) for line in groupsFile]

    pool.close()
    #print(results)


if __name__ == '__main__':
    main()