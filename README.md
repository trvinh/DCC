# DCC
DCC: dynamic compilation of core gene sets

1: Download the OMA files from https://omabrowser.org/oma/current/
Required files:

OMA groups in Text format
Protein sequences in Fasta format
Species information Text format

2: run /scripts/createDic.py

3: Download and install the following libraries:

Python:

os
sys
json
time
multiprocessing
coreapi

R:
shiny
shinyjs
shinyalert
data.table
shinyDirectoryInput
