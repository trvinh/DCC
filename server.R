################# Librarys #####################

library(data.table)
library(DT)

######## setup shiny server ###############

shinyServer <- function(input, output, session) {


  readOmaSpec <- reactive({
    #loads the oma-species file from OmaDb and creates an data.frame
    # location has to be changed!
    taxTable <- fread("data/oma-species.txt",
                      header = FALSE,
                      skip = 2,
                      sep = "\t")
    colnames(taxTable) <- c("OMAcode", "TaxonID", "ScientificName", "GenomeSource", "Version/Release")
    head(taxTable)
    return(taxTable)
  })

  readOmaGroup <- reactive({
    #loads the transformed oma-groups-tmp.txt file as an data.frame, returns the table
    groupTable <- fread("data/oma-groups-tmp.txt")
    return(groupTable)
  })

  findOmaCode <- function(outputSpecies, speciesTable){
    # returns the OmaCode of the species chosen from the user
    if (input$inputTyp == "ncbiID") {
      omaCode <- (speciesTable$OMAcode[speciesTable$TaxonID %in% outputSpecies])
    }else if (input$inputTyp == "speciesName") {
      omaCode <- (speciesTable[speciesTable$ScientificName %in% outputSpecies,]$OMAcode)
    }else{
      omaCode <- (speciesTable[speciesTable$TaxonID %in% outputSpecies]$OMAcode)
    }
    return(omaCode)
  }

  findTaxId <- function(outputSpecies, speciesTable){
    #returns the taxonomy Ids from the species choosen from the user
    if (input$inputTyp == "ncbiID") {
      omaCode <- (speciesTable$TaxonID[speciesTable$TaxonID %in% outputSpecies])
    }else if (input$inputTyp == "speciesName"){
      omaCode <- (speciesTable[speciesTable$ScientificName %in% outputSpecies,]$TaxonID)
    }else{
      omaCode <- (speciesTable$TaxonID[speciesTable$TaxonID %in% outputSpecies])
    }
    return(omaCode)
  }

  output$omaSpec <- renderUI({
    # creates the User input addicted to the input option the user selected
    # creates select inputs for the options protein search and taxonoy or scientic name input
    # creates a headler to upload files for the file input
    omaSpecTable <- readOmaSpec()
    omaGroupTable <- readOmaGroup()
    #print(input$inputTyp)
    if (input$inputTyp == "ncbiID") {
      selectInput(
        inputId = "species",
        label = "Select up to 10 species",
        multiple = TRUE,
        choices = omaSpecTable$TaxonID
      )
    } else if (input$inputTyp == "speciesName") {
      selectInput(
        inputId = "species",
        label = "Select up to 10 species",
        multiple = TRUE,
        choices = omaSpecTable$ScientificName
      )} else if (input$inputTyp == "inputFile"){
        fileInput("taxFile", "Choose File")
      } else if (input$inputTyp == "OmaId"){
        #print("test")
        x = readOmaGroup()
        numericInput(
          inputId = "omaGroupId",
          value = NULL,
          label = "Select a Oma Group Id between 1 and 866647",
          min = 1,
          max = nrow(x),
          step = 1
        )
      }

  })

  makeWarningWindow <- reactive({
    DF <- getFileTable()
    notAvailableTaxons <- DF$TaxonID[is.na(DF$ScientificName)]
    if (length(notAvailableTaxons) > 0){
      shinyalert(title = "warning", text = paste("The following TaxonIds aren't available in Oma. Do you want to continue without them?", notAvailableTaxons), type = "warning", showConfirmButton = TRUE, showCancelButton = TRUE)
    }
  })

  getFileTable <- reactive({
    inFile <- input$taxFile

    speciesTable <- readOmaSpec()
    if (is.null(inFile)){
      DF <- NULL
      return(DF)
    }else if (input$inputTyp == "inputFile"){
      taxaInFile <- read.table(inFile$datapath, header = FALSE)
      colnames(taxaInFile) <- "TaxonID"
      DF <- merge(
        taxaInFile, speciesTable[,c("TaxonID", "ScientificName")],
        by = "TaxonID",
        all.x = TRUE
      )
      return(DF)}

    })

  createFileOutput <- reactive({
    # checks if the taxonomy ids of the file input is available in oma
    # returns a error if there is a not available taxon id
    # run button will than be disabled <- has to be changed, should ignore nr which aren't in oma
      DF <- getFileTable()
      notAvailableTaxons <- DF$TaxonID[is.na(DF$ScientificName)]
      DF$ScientificName[is.na(DF$ScientificName)] <- "not available yet"
      if (length(notAvailableTaxons) > 0){
        #output$error <- renderText(paste(notAvailableTaxons, "Those Taxon Ids are not available in OmaDB."))
        #disable("submit")
        makeWarningWindow()
      }

      return(DF)


  })

  createOmaIdOutput <- reactive({
    # creates a output table if the user chooses to only input an oma group
    # all species which are included in this choosen oma group will be available in this produced table
    # afterwards the user can choose which species should be collected
    tableGroup <- readOmaGroup()
    speciesTable <- readOmaSpec()

    if (is.null(input$omaGroupId)){
      return(NULL)
    }
    else{
      #print(tableGroup)
      speciesList <- strsplit(tableGroup$V2[tableGroup$V1 == input$omaGroupId], ",")
      #print(speciesList)
      specCode <- data.frame(OMAcode = speciesList[[1]])

      head(specCode)
      DF <- merge(
        specCode, speciesTable[,c("TaxonID", "ScientificName", "OMAcode")],
        by = "OMAcode",
        all.x = TRUE
      )



    }
    return(DF)
  })

  output$version <-  renderPrint({
    # this function starts a python program which returns the current version of the used oma files
    # the script returns if the version we use is up to date
    y <- cat(system(paste("python scripts/getVersion.py"), intern = TRUE))

  })


  reloadDirectory <- observeEvent(
    # creates a directory input where the user can select where the data should be saved
    ignoreNULL = TRUE,
    eventExpr = {
      input$directory
    },
    handlerExpr = {
      if (input$directory > 0) {
        # condition prevents handler execution on initial app launch

        # launch the directory selection dialog with initial path read from the widget
        path = choose.dir(default = readDirectoryInput(session, 'directory'))

        # update the widget value
        updateDirectoryInput(session, 'directory', value = path)
      }
    }
  )

  output$update <- renderUI({
      if (input$inputTyp != "OmaId"){
          checkboxInput("update", label = "update Mode")
      }

  })

  output$nrMissingSpecies <- renderUI({
    # a user input will be created which is addicted to the number of choosen species
    # this choosen number stands for the number of species which can be missed in an oma group
    if (input$inputTyp != "OmaId"){
      if (input$inputTyp != "inputFile"){
        selectInput(inputId = "nrMissingSpecies",
                                 label = "How many species can be missed in an OmaGroup",
                                 choices = seq(0,(length(input$species)-1))
                     )
      } else if (input$inputTyp == "inputFile"){
        inFile <- input$taxFile
        if (is.null(inFile)){
          taxaInFile <- 1
          selectInput(inputId = "nrMissingSpecies",
                      label = "How many species can be missed in an OmaGroup",
                      choices = 0
          )
        }else{
          taxaInFile <- read.table(inFile$datapath, header = FALSE)
          selectInput(inputId = "nrMissingSpecies",
                      label = "How many species can be missed in an OmaGroup",
                      choices = seq(0,(nrow(taxaInFile)-1))
          )

        }
        }
    }
  })

  createTableOutput <- reactive({
    # created a table which represends the species choosen from the user in mode ScientificName or TaxnonID
    speciesTable <- readOmaSpec()
    DF <- NULL
    if (input$inputTyp == "ncbiID"){
      if (is.null(input$species) == TRUE){
        DF <- data.table(
          TaxonmyIDs = "Nothing selected",
          ScientificNames = "Nothing selected")
      } else {
        if (sum(speciesTable$TaxonID %in% input$species) > 0) {
          DF <- data.table(
            TaxonomyIDs = input$species,
            ScientificNames = unlist(speciesTable$ScientificName[speciesTable$TaxonID %in% input$species])
          )
        }
      }
    }
    else if (input$inputTyp == "speciesName"){
      if (is.null(input$species) == TRUE){
        DF <- data.table(
        TaxonmyIDs = "Nothing selected",
        ScientificNames = "Nothing selected")
      }
      else{
        if (sum(speciesTable$ScientificName %in% input$species) > 0) {
        DF <- data.table(
          TaxonomyIDs = speciesTable$TaxonID[speciesTable$ScientificName %in% input$species],
          ScientificNames = unlist(input$species)
        )}
      }
    }
    else{
      DF <- NULL
    }
    return(DF)
  })

  output$speciesTable <- DT::renderDataTable({
    # creates the species table output seen by the user
    speciesTable <- createTableOutput()
  })

  output$checkTax <- DT::renderDataTable({
    # creates the shiny output of the table with the species from the file input
    fileTable <- createFileOutput()
  })

  output$omaGroupSpeciesTable <- DT::renderDataTable({
    # creates the shiny output of the table which includes the species from the OmaGroup the user selected
    if (input$inputTyp == "OmaId"){
      speciesTable <- createOmaIdOutput()
    }

  })

  output$speciesSelectionOmaGroup <- renderUI({
    # creates a user input, where the user can choose the species which are included in the choosen OmaGroup
    if (input$inputTyp == "OmaId"){
      speciesTable <- createOmaIdOutput()
      selectInput(
        inputId = "GroupSpecies",
        label = "Select up to 10 species",
        multiple = TRUE,
        choices = speciesTable$TaxonID,
        selected = speciesTable$TaxonID[1]

      )
    }
  })

  getDatasets <- function(inputOmaCode, inputTaxId, path){
    # this function runs the python script which collects the datasets of the chossen species
    fileGettingDataset <- "python scripts/gettingDataset.py"
    system(paste(fileGettingDataset, inputOmaCode,inputTaxId, path))
    return(0)

  }

  getCommonOmaGroups <- function(inputOmaCode, inputTaxId, path){
    # this function runs the phyton script which collects the common Oma Groups of the choosen species
    fileGettingOmaGroups <- "python scripts/gettingOmaGroups.py"
    y <- cat(system(paste(fileGettingOmaGroups, inputOmaCode, inputTaxId, input$nrMissingSpecies, path, input$update), inter = TRUE))
    return(y)
  }

  getOmaGroup <- function(inputOmaCode, inputTaxId, path){
    fileGettingOmaGroup <- "python scripts/gettingOmaGroup.py"
    y <- cat(system(paste(fileGettingOmaGroup, inputOmaCode, inputTaxId, input$omaGroupId, path)))
  }

  disableButton <- observeEvent(input$shinyalert,{
    if (length(input$shinyalert) > 0){
      if (input$shinyalert == FALSE){
        disable("submit")
      }
    }
  })

  startPythonScript <- observeEvent(input$submit, {
    # runs the calculation of the dataset collection, the collection of common oma groups and the MSAs, hMMS, Blastdbs...
    disable("submit")
    #print(input$MSA)

    progress <- shiny::Progress$new()
    progress$set(message = "Computing data", value = 0)
    on.exit(progress$close())

    updateProgress <- function(value = NULL, detail = NULL) {
      if (is.null(value)) {
        value <- progress$getValue()
        value <- value + (progress$getMax() - value) / 5
      }
      progress$set(value = value, detail = detail)
    }

    if (input$inputTyp == "inputFile"){
      inFile <- input$taxFile
      taxa <- fread(inFile$datapath, header = FALSE)
      speciesInput <- taxa$V1
    } else if (input$inputTyp == "OmaId"){
      speciesInput <- input$GroupSpecies
    } else{
      speciesInput <- input$species
    }

    taxTable <- readOmaSpec()
    OmaCodes <- findOmaCode(speciesInput, taxTable)
    taxIds <-  findTaxId(speciesInput, taxTable)
    inputOmaCode <- gsub(" ", "", toString(OmaCodes))
    inputTaxId <- gsub(" ", "", toString(taxIds))
    path <- readDirectoryInput(session, 'directory')

    getDatasets(inputOmaCode, inputTaxId, path)

    updateProgress(detail = "Dataset collection is finished. Start to compile commonOmaGroups")

    if (input$inputTyp == "OmaId"){
      #print("OmaId")
      y <- getOmaGroup(inputOmaCode, inputTaxId, path)
    } else{
      y <-  getCommonOmaGroups(inputOmaCode, inputTaxId, path)
    }


    if (input$MSA == "MAFFT"){
      fileMSA <- "python scripts/makingMsaMafft.py"
    }
    else{
      fileMSA <- "python scripts/makingMsaMuscle.py"
    }
    updateProgress(detail = y)
    system(paste(fileMSA, path), intern = TRUE)

    fileHmm <- "python scripts/makingHmms.py"
    updateProgress(detail = "Computing hMMs with HMMER")
    system(paste(fileHmm, path), intern = TRUE)

    fileBlastDb <- "python scripts/makingBlastdb.py"
    updateProgress(detail = "Computing Blastdbs")
    system(paste(fileBlastDb, path), inter = TRUE)

    output$end <- renderText(paste("The calculation is finished. Your output is saved under: ", path, y))

  })
}
