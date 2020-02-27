#################### Librarys #############################
library(shiny)
library(shinyjs)
#devtools::install_github('wleepang/shiny-directory-input')
library(shinyDirectoryInput)
library(shinyalert)

###################### server function ###################
shinyUI(
  fluidPage(
    #Title
    titlePanel("Welcome to DCC: Dynamic compilation of core gene sets"),

    sidebarLayout(

      sidebarPanel(
        # makes a Radio button with the choices NCBI Taxonomy Id, Scietnific name, inputFile, OmaGroup
        radioButtons(inputId = "inputTyp", label = "Select your input mode",
                     choices = list("NCBI Taxonomy ID" = "ncbiID", "Scientific name" = "speciesName", "File input" = "inputFile", "OMA Group ID" = "OmaId"),
                     selected = "ncbiID"),

        #in this output the input for the species will be created. The input
        #depends on the input of the radio Button and has to be computed in the server.R
        uiOutput("omaSpec"),

        #this output represents the nr of species which are allowed to be missed
        #in a common OmaGroup. This input depends on the number of chosen
        #species and for this reason it has to be computed in the server.R

        uiOutput("nrMissingSpecies"),

        # creates a input whether the update mode or the normal mode should be used
        uiOutput("update"),

        # creates an input to choose which MSA tool should be used
        radioButtons("MSA", label= "MSA tool", choices = c("MAFFT", "MUSCLE"), selected = "MAFFT"),

        #directory input takes the path to HaMStR where the output will be saved
        directoryInput('directory', label = 'Please choose the location you want to save your output', value = '~'),
        # make it possible to disable or anable the action button
        useShinyjs(),
        useShinyalert(),
        # creates the action button to run the calculation
        actionButton("submit", "Run")

      ),

      mainPanel(

        # creates an output where the user can see whether the version of his oma files are up to date or not
        verbatimTextOutput("version"),

        # creates an output for the table where all chosen species can be seen
        DT::dataTableOutput(outputId = "speciesTable"),

        # creates an output table where the user can see which taxons uploaded from a file are available in omaDb
        DT::dataTableOutput(outputId = "checkTax"),

        # creates an output table where the user can see which species are included in the given oma group
        DT::dataTableOutput(outputId = "omaGroupSpeciesTable"),

        # creates an input where the user can select the species he want to collect
        # all species which were selectable are included in the selcted oma group
        uiOutput("speciesSelectionOmaGroup"),

        # creates the error message if there were uploaded taxon ids which aren' available in omadb
        span(textOutput("error"), style="color:red"),

        # creates an user output which shows the number of common oma groups
        verbatimTextOutput("nrOmaGroups"),

        uiOutput("end")

      )
    )
  )
)






#helpages ?funktionsname
