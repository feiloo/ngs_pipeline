################################################################################
# Script to sort, filter and assess CLC Genomics Workbench Data - OncoHs Panel
# Version: v1
# Author: Patrick Basitta
################################################################################

# Deleting all variables
rm(list=ls())

# Loading packages
pacman::p_load(optparse, tidyverse, here ,readxl, dplyr,xlsx,
               openxlsx, rentrez)

################################################################################
# General Settings
################################################################################

# Process time
time_start <- Sys.time()

# Handling warnings
options(warn = 1, nwarnings = 10000)

# Setting commands
#command_list = list(
#  make_option(c("-f", "--file"), type="character", default = NULL),
#  make_option(c("-n", "--name"), type="character", default= NULL)
#)
#opt_parser = OptionParser(option_list=command_list)
#opt = parse_args(opt_parser)

# Setting path and getting filename
cwd <- here()
path_to_data <- cwd
filename <- "/22_03_02 OncoHS_test.xlsx"

# Date and time for log file
print(paste("Date:", time_start))

# Show command in log file
print(paste("File:", opt$file))
print("Rscript: OncoHS_v1.R")
print("Process information:")

# Number of excel_sheets and QC
number_all_sheets <- length(excel_sheets(paste(path_to_data,filename,sep="")))

# Names of excel sheets
names_all_sheet <- excel_sheets(paste(path_to_data,filename,sep=""))

################################################################################
# Functions
################################################################################

# Extracting data

# Extracting all "covarge_sheets" from the data

extract_cov_sheets <- function(number_all_sheets) {

  if ((number_all_sheets %% 3) == 0) {
  sheets <- excel_sheets(paste(path_to_data,filename,sep="")) #all sheets???

    if (number_all_sheets == 3) {
    index_cov_sheets <- 1
  } else {
    cov_number_sheets <- number_all_sheets/3
    index_cov_sheets <- c()
    counter_cov <- 1
    for (i in (seq(2, cov_number_sheets))) {
      index_cov_sheets[1] <- 1
      counter_cov <- counter_cov + 3
      index_cov_sheets[i] <- counter_cov
      }
  }
    data_cov_sheets <- lapply(X = sheets[index_cov_sheets], FUN = function(x)
    read_excel(paste(path_to_data,filename,sep=""), sheet = x))
} else {
      stop("Uneven sheet number! Check excel file!")}
}

cov_sheets <- extract_cov_sheets(number_all_sheets = number_all_sheets)

################################################################################

# Extracting all "unfiltered sheets" from the data

extract_unfil_sheets <- function(number_all_sheets) {

if ((number_all_sheets %% 3) == 0) {
  sheets <- excel_sheets(paste(path_to_data,filename,sep="")) #all sheets???

  if (number_all_sheets == 3) {
    index_unfil_sheets <- 2
  } else {
    unfil_number_sheets <- number_all_sheets/3
    index_unfil_sheets <- c()
    counter_unfil <- 2
    for (i in (seq(2,unfil_number_sheets))) {
      index_unfil_sheets[1] <- 2
      counter_unfil <- counter_unfil + 3
      index_unfil_sheets[i] <- counter_unfil
    }
  }
  data_unfil_sheets <- lapply(X = sheets[index_unfil_sheets], FUN = function(x)
    read_excel(paste(path_to_data,filename,sep=""), sheet = x))
} else {
  stop("Uneven sheet number! Check excel file!")}
}

unfil_sheets <- extract_unfil_sheets(number_all_sheets = number_all_sheets)

# Polish chromosome region if incorrect

for (i in seq(1,number_all_sheets/3)) {
  for (j in seq(unfil_sheets[[i]]$Region)) {
    if (str_detect(string = unfil_sheets[[i]]$Region[j], "E") ==TRUE) {
      woE <- gsub(pattern="E.", replacement = "", unfil_sheets[[i]]$Region[j])
      woEP <- gsub(pattern="\\.", replacement = "",   woE)
      unfil_sheets[[i]]$Region[j] <- woEP
    }
  }
}
################################################################################

# Extracting all "filtered sheets" from the data

extract_fil_sheets <- function(number_all_sheets) {

if ((number_all_sheets %% 3) == 0) {
  sheets <- excel_sheets(paste(path_to_data,filename,sep="")) #all sheets???

  if (number_all_sheets == 3) {
    index_fil_sheets <- 3
  } else {
    fil_number_sheets <- number_all_sheets/3
    index_fil_sheets <- c()
    counter_fil <- 3
    for (i in (seq(2,fil_number_sheets))) {
      index_fil_sheets[1] <- 3
      counter_fil <- counter_fil + 3
      index_fil_sheets[i] <- counter_fil
    }
  }
  data_fil_sheets <- lapply(X = sheets[index_fil_sheets], FUN = function(x)
    read_excel(paste(path_to_data,filename,sep=""), sheet = x))
} else {
  stop("Uneven sheet number! Check excel file!")}
}

fil_sheets <- extract_fil_sheets(number_all_sheets = number_all_sheets)

# Polish chromosome region if incorrect

for (i in seq(1,number_all_sheets/3)) {
  for (j in seq(fil_sheets[[i]]$Region)) {
    if (str_detect(string = fil_sheets[[i]]$Region[j], "E") ==TRUE) {
      woE <- gsub(pattern="E.", replacement = "", fil_sheets[[i]]$Region[j])
      woEP <- gsub(pattern="\\.", replacement = "",   woE)
      fil_sheets[[i]]$Region[j] <- woEP
    }
  }
}
################################################################################

# Extract indexes

# Functions to extract the sheet numbers of "coverage-, unfiltered-, and
# filtered-sheets

# Extracting the indexes from the "coverage-sheets"

index_cov_sheets <- function(number_all_sheets) {

  if ((number_all_sheets %% 3) == 0) {
    sheets <- excel_sheets(paste(path_to_data,filename,sep=""))

    if (number_all_sheets == 3) {
      index_cov_sheets <- 1
    } else {
      cov_number_sheets <- number_all_sheets/3
      index_cov_sheets <- c()
      counter_cov <- 1
      for (i in (seq(2, cov_number_sheets))) {
        index_cov_sheets[1] <- 1
        counter_cov <- counter_cov + 3
        index_cov_sheets[i] <- counter_cov
      }
    }
    index_cov_sheets
  } else {
    stop("Uneven sheet number! Check excel file!")}
}

index_coverage_sheets <- index_cov_sheets(number_all_sheets)

################################################################################

# Extracting the indexes from the "unfiltered-sheets"

index_unfil_sheets <- function(number_all_sheets) {

  if ((number_all_sheets %% 3) == 0) {
    sheets <- excel_sheets(paste(path_to_data,filename,sep=""))

    if (number_all_sheets == 3) {
      index_unfil_sheets <- 2
    } else {
      unfil_number_sheets <- number_all_sheets/3
      index_unfil_sheets <- c()
      counter_unfil <- 2
      for (i in (seq(2,unfil_number_sheets))) {
        index_unfil_sheets[1] <- 2
        counter_unfil <- counter_unfil + 3
        index_unfil_sheets[i] <- counter_unfil
      }
    }
    index_unfil_sheets
  } else {
    stop("Uneven sheet number! Check excel file!")}
}

index_unfiltered_sheets <- index_unfil_sheets(number_all_sheets)

################################################################################

# Extracting the indexes from the "filtered-sheets"

index_fil_sheets <- function(number_all_sheets) {

  if ((number_all_sheets %% 3) == 0) {
    sheets <- excel_sheets(paste(path_to_data,filename,sep=""))

    if (number_all_sheets == 3) {
      index_fil_sheets <- 3
    } else {
      fil_number_sheets <- number_all_sheets/3
      index_fil_sheets <- c()
      counter_fil <- 3
      for (i in (seq(2,fil_number_sheets))) {
        index_fil_sheets[1] <- 3
        counter_fil <- counter_fil + 3
        index_fil_sheets[i] <- counter_fil
      }
    }
    index_fil_sheets
  } else {
    stop("Uneven sheet number! Check excel file!")}
}

index_filtered_sheets <- index_fil_sheets(number_all_sheets)

################################################################################

# Rename sheets
rename_sheets <- substr(names_all_sheet, start = 1, stop = 7)

names_all_sheet[index_coverage_sheets] <-
  paste0(rename_sheets[index_coverage_sheets], "c")

names_all_sheet[index_unfiltered_sheets] <-
  paste0(rename_sheets[index_unfiltered_sheets], "u")

names_all_sheet[index_filtered_sheets] <-
  paste0(rename_sheets[index_filtered_sheets], "f")

################################################################################
# Create Workbook DataAnalysisBRCAness
################################################################################
wb <- createWorkbook()
for (i in seq(number_all_sheets)) {
  addWorksheet(wb, sheetName = names_all_sheet[i])
}

################################################################################

# Working on "coverage-sheets"
print("Sorting and filtering coverage sheets")
# Settings

# Style for header
header <-createStyle(wrapText = TRUE, fgFill = "#c0c0c0")

# Style for min coverage
light_red_style <- createStyle(fgFill="#ffcccc")

# Exon_table OncoHS panel
exon_table <- read_excel(paste(cwd,"/exontableOncoHS.xlsx",
                               sep=""))
# Global variables
min_coverage_indexes <- list()
gene_name <- list()
exon_name <- list()
exon_min_coverage <- list()
name_exon_mincov <- list()
length_vector <- max(1,number_all_sheets/3)
output_min_cov <- vector(mode="list", length = length_vector)
colnumber_min_coverage <- which(colnames(cov_sheets[[1]]) == "Min coverage")

# 1. Highlighting coverages below a value of 100
# 2. Adding exon numbers and gene names
# 3. Displaying all genes with corresponding exons possessing coverage values
#    below 100
# 4. Save current workbook

for (i in seq(1,number_all_sheets/3)) {
  min_coverage <- cov_sheets[[i]]$`Min coverage`
  min_coverage_indexes[[i]] <- which(min_coverage < 100)
  Exon <- exon_table$Exon
  cov_sheets[[i]] <- add_column(.data = cov_sheets[[i]], Exon,
             .after = "Median coverage (excluding zero coverage)")
  Gene <- exon_table$Name
  cov_sheets[[i]] <- add_column(.data = cov_sheets[[i]], Gene,
             .after = "Exon")
  gene_name[[i]] <- cov_sheets[[i]]$Name[min_coverage_indexes[[i]]]
  exon_name[[i]] <- cov_sheets[[i]]$`Exon`[min_coverage_indexes[[i]]]
  exon_min_coverage[[i]] <-
    cov_sheets[[i]]$`Min coverage`[min_coverage_indexes[[i]]]
  name_exon_mincov[[i]] <- paste(unlist(gene_name[[i]]), "Ex",
                            unlist(exon_name[[i]]),
                            unlist(exon_min_coverage[[i]]))

  exons_AKT1 <- c()
  exons_BRAF <- c()
  exons_CTNNB1 <- c()
  exons_EGFR <- c()
  exons_ERBB2_HER2 <- c()
  exons_ESR1 <- c()
  exons_FOXL2 <- c()
  exons_GNA11 <- c()
  exons_GNAQ <- c()
  exons_IDH1 <- c()
  exons_IDH2 <- c()
  exons_IL6ST_GP130 <- c()
  exons_KIT <- c()
  exons_KRAS <- c()
  exons_NRAS <- c()
  exons_PDGFRA <- c()
  exons_PIK3CA <- c()
  exons_POLE <- c()
  exons_TERT <- c()
  exons_TP53 <- c()

  min_AKT1 <- 100
  min_BRAF <- 100
  min_CTNNB1 <- 100
  min_EGFR <- 100
  min_ERBB2_HER2 <- 100
  min_ESR1 <- 100
  min_FOXL2 <- 100
  min_GNA11 <- 100
  min_GNAQ <- 100
  min_IDH1 <- 100
  min_IDH2 <- 100
  min_IL6ST_GP130 <- 100
  min_KIT <- 100
  min_KRAS <- 100
  min_NRAS <- 100
  min_PDGFRA <- 100
  min_PIK3CA <- 100
  min_POLE <- 100
  min_TERT <- 100
  min_TP53 <- 100

  count_AKT1 <- 0
  count_BRAF <- 0
  count_CTNNB1 <- 0
  count_EGFR <- 0
  count_ERBB2_HER2 <- 0
  count_ESR1 <- 0
  count_FOXL2 <- 0
  count_GNA11 <- 0
  count_GNAQ <- 0
  count_IDH1 <- 0
  count_IDH2 <- 0
  count_IL6ST_GP130 <- 0
  count_KIT <- 0
  count_KRAS <- 0
  count_NRAS <- 0
  count_PDGFRA <- 0
  count_PIK3CA <- 0
  count_POLE <- 0
  count_TERT <- 0
  count_TP53 <- 0

  for (j in seq(name_exon_mincov[[i]])) {
    splitted <-
      unlist(str_split(string = name_exon_mincov[[i]][j], pattern = " "))

    if ("AKT1" %in% splitted) {
      count_AKT1 <- count_AKT1 + 1
      exons_AKT1 <- append(exons_AKT1, splitted[3])
      min_cov_AKT1 <- as.double(splitted[4])
      if (min_cov_AKT1 < min_AKT1) {
        min_AKT1<- min_cov_AKT1
        num_AKT1 <- paste0("(",min_AKT1 ,")")
      }
    } else if ("BRAF" %in% splitted) {
      count_BRAF <- count_BRAF+ 1
      exons_BRAF <- append(exons_BRAF, splitted[3])
      min_cov_BRAF <- as.double(splitted[4])
      if (min_cov_BRAF <  min_BRAF) {
        min_BRAF <- min_cov_BRAF
        num_BRAF <- paste0("(",min_BRAF ,")")
      }
    } else if ("CTNNB1" %in% splitted) {
      count_CTNNB1 <- count_CTNNB1 + 1
      exons_CTNNB1 <- append(exons_CTNNB1, splitted[3])
      min_cov_CTNNB1 <- as.double(splitted[4])
      if (min_cov_CTNNB1 <  min_CTNNB1) {
        min_CTNNB1 <- min_cov_CTNNB1
        num_CTNNB1 <- paste0("(",min_CTNNB1 ,")")
      }
    } else if ("EGFR" %in% splitted) {
      count_EGFR <- count_EGFR + 1
      exons_EGFR <- append(exons_EGFR, splitted[3])
      min_cov_EGFR <- as.double(splitted[4])
      if (min_cov_EGFR <  min_EGFR) {
        min_EGFR <- min_cov_EGFR
        num_EGFR <- paste0("(",min_EGFR ,")")
      }
    } else if ("ERBB2_HER2" %in% splitted) {
      count_ERBB2_HER2 <- count_ERBB2_HER2 + 1
      exons_ERBB2_HER2 <- append(exons_ERBB2_HER2, splitted[3])
      min_cov_ERBB2_HER2 <- as.double(splitted[4])
      if (min_cov_ERBB2_HER2 <  min_ERBB2_HER2) {
        min_ERBB2_HER2 <- min_cov_ERBB2_HER2
        num_ERBB2_HER2 <- paste0("(",min_ERBB2_HER2 ,")")
      }
    } else if ("ESR1" %in% splitted) {
      count_ESR1 <- count_ESR1 + 1
      exons_ESR1 <- append(exons_ESR1, splitted[3])
      min_cov_ESR1 <- as.double(splitted[4])
      if (min_cov_ESR1 <  min_ESR1) {
        min_ESR1 <- min_cov_ESR1
        num_ESR1 <- paste0("(",min_ESR1 ,")")
      }
    } else if ("FOXL2" %in% splitted) {
      count_FOXL2 <- count_FOXL2 + 1
      exons_FOXL2 <- append(exons_FOXL2, splitted[3])
      min_cov_FOXL2 <- as.double(splitted[4])
      if (min_cov_FOXL2 <  min_FOXL2) {
        min_FOXL2 <- min_cov_FOXL2
        num_FOXL2 <- paste0("(",min_FOXL2 ,")")
      }
    } else if ("GNA11" %in% splitted) {
      count_GNA11 <- count_GNA11 + 1
      exons_GNA11 <- append(exons_GNA11, splitted[3])
      min_cov_GNA11 <- as.double(splitted[4])
      if (min_cov_GNA11 <  min_GNA11) {
        min_GNA11 <- min_cov_GNA11
        num_GNA11 <- paste0("(",min_GNA11 ,")")
      }
    } else if ("GNAQ" %in% splitted) {
      count_GNAQ <- count_GNAQ + 1
      exons_GNAQ <- append(exons_GNAQ, splitted[3])
      min_cov_GNAQ <- as.double(splitted[4])
      if (min_cov_GNAQ <  min_GNAQ) {
        min_GNAQ <- min_cov_GNAQ
        num_GNAQ <- paste0("(",min_GNAQ ,")")
      }
    } else if ("IDH1" %in% splitted) {
      count_IDH1 <- count_IDH1 + 1
      exons_IDH1 <- append(exons_IDH1, splitted[3])
      min_cov_IDH1 <- as.double(splitted[4])
      if (min_cov_IDH1 <  min_IDH1) {
        min_IDH1 <- min_cov_IDH1
        num_IDH1 <- paste0("(",min_IDH1 ,")")
      }
    } else if ("IDH2" %in% splitted) {
      count_IDH2 <- count_IDH2 + 1
      exons_IDH2 <- append(exons_IDH2, splitted[3])
      min_cov_IDH2 <- as.double(splitted[4])
      if (min_cov_IDH2 <  min_IDH2) {
        min_IDH2 <- min_cov_IDH2
        num_IDH2 <- paste0("(",min_IDH2 ,")")
      }
    } else if ("IL6ST_GP130" %in% splitted) {
      count_IL6ST_GP130 <- count_IL6ST_GP130 + 1
      exons_IL6ST_GP130 <- append(exons_IL6ST_GP130, splitted[3])
      min_cov_IL6ST_GP130 <- as.double(splitted[4])
      if (min_cov_IL6ST_GP130 <  min_IL6ST_GP130) {
        min_IL6ST_GP130 <- min_cov_IL6ST_GP130
        num_IL6ST_GP130 <- paste0("(",min_IL6ST_GP130 ,")")
      }
    } else if ("KIT" %in% splitted) {
      count_KIT <- count_KIT + 1
      exons_KIT <- append(exons_KIT, splitted[3])
      min_cov_KIT <- as.double(splitted[4])
      if (min_cov_KIT <  min_KIT) {
        min_KIT <- min_cov_KIT
        num_KIT <- paste0("(",min_KIT ,")")
      }
    } else if ("KRAS" %in% splitted) {
      count_KRAS <- count_KRAS + 1
      exons_KRAS <- append(exons_KRAS, splitted[3])
      min_cov_KRAS <- as.double(splitted[4])
      if (min_cov_KRAS <  min_KRAS) {
        min_KRAS <- min_cov_KRAS
        num_KRAS <- paste0("(",min_KRAS ,")")
      }
    } else if ("NRAS" %in% splitted) {
      count_NRAS <- count_NRAS + 1
      exons_NRAS <- append(exons_NRAS, splitted[3])
      min_cov_NRAS <- as.double(splitted[4])
      if (min_cov_NRAS <  min_NRAS) {
        min_NRAS <- min_cov_NRAS
        num_NRAS <- paste0("(",min_NRAS ,")")
      }
    } else if ("PDGFRA" %in% splitted) {
      count_PDGFRA <- count_PDGFRA + 1
      exons_PDGFRA <- append(exons_PDGFRA, splitted[3])
      min_cov_PDGFRA <- as.double(splitted[4])
      if (min_cov_PDGFRA <  min_PDGFRA) {
        min_PDGFRA <- min_cov_PDGFRA
        num_PDGFRA <- paste0("(",min_PDGFRA ,")")
      }
    } else if ("PIK3CA" %in% splitted) {
      count_PIK3CA <- count_PIK3CA + 1
      exons_PIK3CA <- append(exons_PIK3CA, splitted[3])
      min_cov_PIK3CA <- as.double(splitted[4])
      if (min_cov_PIK3CA <  min_PIK3CA) {
        min_PIK3CA <- min_cov_PIK3CA
        num_PIK3CA <- paste0("(",min_PIK3CA ,")")
      }
    } else if ("POLE" %in% splitted) {
      count_POLE <- count_POLE + 1
      exons_POLE <- append(exons_POLE, splitted[3])
      min_cov_POLE <- as.double(splitted[4])
      if (min_cov_POLE <  min_POLE) {
        min_POLE <- min_cov_POLE
        num_POLE <- paste0("(",min_POLE ,")")
      }
    } else if ("chr5:1.3Mb" %in% splitted) {
      count_TERT <- count_TERT + 1
      exons_TERT <- append(exons_TERT, splitted[3])
      min_cov_TERT <- as.double(splitted[4])
      if (min_cov_TERT <  min_TERT) {
        min_TERT <- min_cov_TERT
        num_TERT <- paste0("(",min_TERT ,")")
      }
    } else if ("TP53" %in% splitted) {
      count_TP53 <- count_TP53 + 1
      exons_TP53 <- append(exons_TP53, splitted[3])
      min_cov_TP53 <- as.double(splitted[4])
      if (min_cov_TP53 <  min_TP53) {
        min_TP53 <- min_cov_TP53
        num_TP53 <- paste0("(",min_TP53 ,")")
      }
    }
  }

  if ("AKT1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_AKT1) > 10) {
        AKT1 <- paste("AKT1", paste0("(",min_AKT1,")"))
        output_min_cov[[i]][1] <- AKT1
    } else {
        AKT1 <- paste("AKT1", "Ex", paste(exons_AKT1, collapse = ","),
                     paste0("(",min_AKT1,")"))
        output_min_cov[[i]][1] <- AKT1
      }
  } else {
      output_min_cov[[i]][1] <-  ""
  }

  if ("BRAF" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_BRAF) > 10) {
        BRAF <- paste("BRAF", paste0("(",min_BRAF,")"))
        output_min_cov[[i]][2] <- BRAF
    } else {
        BRAF <- paste("BRAF", "Ex", paste(exons_BRAF, collapse = ","),
                    paste0("(",min_BRAF,")"))
        output_min_cov[[i]][2] <- BRAF
      }
  } else {
    output_min_cov[[i]][2] <-  ""
  }

  if ("CTNNB1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                  pattern=" "))) {
    if (length(exons_CTNNB1) > 10) {
        CTNNB1 <- paste("CTNNB1", paste0("(",min_CTNNB1,")"))
        output_min_cov[[i]][3] <- CTNNB1
    } else {
        CTNNB1 <- paste("CTNNB1", "Ex", paste(exons_CTNNB1, collapse = ","),
                   paste0("(",min_CTNNB1,")"))
        output_min_cov[[i]][3] <-  CTNNB1
    }
  } else {
    output_min_cov[[i]][3] <-  ""
  }

  if ("EGFR" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_EGFR) > 10) {
        EGFR <- paste("EGFR", paste0("(",min_EGFR,")"))
        output_min_cov[[i]][4] <- EGFR
    } else {
        EGFR <- paste("EGFR", "Ex", paste(exons_EGFR, collapse = ","),
                     paste0("(",min_EGFR,")"))
      output_min_cov[[i]][4] <- EGFR
    }
  } else {
    output_min_cov[[i]][4] <-  ""
  }

  if ("ERBB2_HER2" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_ERBB2_HER2) > 10) {
        ERBB2_HER2 <- paste("ERBB2_HER2", paste0("(",min_ERBB2_HER2,")"))
        output_min_cov[[i]][5] <- ERBB2_HER2
    } else {
        ERBB2_HER2 <- paste("ERBB2_HER2", "Ex", 
                      paste(exons_ERBB2_HER2, collapse = ","),
                      paste0("(",min_ERBB2_HER2,")"))
      output_min_cov[[i]][5] <- ERBB2_HER2
    }
  } else {
    output_min_cov[[i]][5] <-  ""
  }

  if ("ESR1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_ESR1) > 10) {
        ESR1 <- paste("ESR1", paste0("(",min_ESR1,")"))
        output_min_cov[[i]][6] <- ESR1
    } else {
        ESR1 <- paste("ESR1", "Ex", paste(exons_ESR1, collapse = ","),
                     paste0("(",min_ESR1,")"))
      output_min_cov[[i]][6] <- ESR1
    }
  } else {
    output_min_cov[[i]][6] <-  ""
  }

  if ("GNA11" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_GNA11) > 10) {
        GNA11 <- paste("GNA11", paste0("(",min_GNA11,")"))
        output_min_cov[[i]][7] <- GNA11
    } else {
      GNA11 <- paste("GNA11", "Ex", paste(exons_GNA11, collapse = ","),
                     paste0("(",min_GNA11,")"))
      output_min_cov[[i]][7] <- GNA11
    }
  } else {
    output_min_cov[[i]][7] <-  ""
  }

  if ("GNAQ" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_GNAQ) > 10) {
        GNAQ <- paste("GNAQ", paste0("(",min_GNAQ,")"))
      output_min_cov[[i]][8] <- GNAQ
    } else {
      GNAQ <- paste("GNAQ", "Ex", paste(exons_GNAQ, collapse = ","),
                     paste0("(",min_GNAQ,")"))
      output_min_cov[[i]][8] <- GNAQ
    }
  } else {
    output_min_cov[[i]][8] <-  ""
  }
  
  if ("IDH1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_IDH1) > 10) {
        IDH1 <- paste("IDH1", paste0("(",min_IDH1,")"))
        output_min_cov[[i]][9] <- IDH1
    } else {
        IDH1 <- paste("IDH1", "Ex", paste(exons_IDH1, collapse = ","),
                     paste0("(",min_IDH1,")"))
      output_min_cov[[i]][9] <- IDH1
    }
  } else {
    output_min_cov[[i]][9] <-  ""
  }
  
  if ("IDH2" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_IDH2) > 10) {
      IDH2 <- paste("IDH2", paste0("(",min_IDH2,")"))
      output_min_cov[[i]][10] <- IDH2
    } else {
      IDH2 <- paste("IDH1", "Ex", paste(exons_IDH2, collapse = ","),
                    paste0("(",min_IDH2,")"))
      output_min_cov[[i]][10] <- IDH2
    }
  } else {
    output_min_cov[[i]][10] <-  ""
  }
  
  if ("ILST6_GP130" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_ILST6_GP130) > 10) {
      ILST6_GP130 <- paste("ILST6_GP130", paste0("(",min_ILST6_GP130,")"))
      output_min_cov[[i]][11] <- ILST6_GP130
    } else {
      ILST6_GP130 <- paste("ILST6_GP130", "Ex", 
                     paste(exons_ILST6_GP130, collapse = ","),
                     paste0("(",min_ILST6_GP130,")"))
      output_min_cov[[i]][11] <- ILST6_GP130
    }
  } else {
    output_min_cov[[i]][11] <-  ""
  }
  
  if ("KIT" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                          pattern=" "))) {
    if (length(exons_KIT) > 10) {
      KIT <- paste("KIT", paste0("(",min_KIT,")"))
      output_min_cov[[i]][12] <- KIT
    } else {
      KIT <- paste("KIT", "Ex", 
                           paste(exons_KIT, collapse = ","),
                           paste0("(",min_KIT,")"))
      output_min_cov[[i]][12] <- KIT
    }
  } else {
    output_min_cov[[i]][12] <-  ""
  }
  
  if ("KRAS" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                  pattern=" "))) {
    if (length(exons_KRAS) > 10) {
      KRAS <- paste("KRAS", paste0("(",min_KRAS,")"))
      output_min_cov[[i]][13] <- KRAS
    } else {
      KRAS <- paste("KRAS", "Ex", 
                   paste(exons_KRAS, collapse = ","),
                   paste0("(",min_KRAS,")"))
      output_min_cov[[i]][13] <- KRAS
    }
  } else {
    output_min_cov[[i]][13] <-  ""
  }
  
  if ("NRAS" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_NRAS) > 10) {
      NRAS <- paste("NRAS", paste0("(",min_NRAS,")"))
      output_min_cov[[i]][14] <- NRAS
    } else {
      NRAS <- paste("NRAS", "Ex", 
                    paste(exons_NRAS, collapse = ","),
                    paste0("(",min_NRAS,")"))
      output_min_cov[[i]][14] <- NRAS
    }
  } else {
    output_min_cov[[i]][14] <-  ""
  }
  
  if ("PDGFRA" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_PDGFRA) > 10) {
      PDGFRA <- paste("PDGFRA", paste0("(",min_PDGFRA,")"))
      output_min_cov[[i]][15] <- PDGFRA
    } else {
      PDGFRA <- paste("PDGFRA", "Ex", 
                    paste(exons_PDGFRA, collapse = ","),
                    paste0("(",min_PDGFRA,")"))
      output_min_cov[[i]][15] <- PDGFRA
    }
  } else {
    output_min_cov[[i]][15] <-  ""
  }
  
  if ("PIK3CA" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                     pattern=" "))) {
    if (length(exons_PIK3CA) > 10) {
      PIK3CA <- paste("PIK3CA", paste0("(",min_PIK3CA,")"))
      output_min_cov[[i]][16] <- PIK3CA
    } else {
      PIK3CA <- paste("PIK3CA", "Ex", 
                      paste(exons_PIK3CA, collapse = ","),
                      paste0("(",min_PIK3CA,")"))
      output_min_cov[[i]][16] <- PIK3CA
    }
  } else {
    output_min_cov[[i]][16] <-  ""
  }
  
  if ("POLE" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                     pattern=" "))) {
    if (length(exons_POLE) > 10) {
      POLE <- paste("POLE", paste0("(",min_POLE,")"))
      output_min_cov[[i]][17] <- POLE
    } else {
      POLE <- paste("POLE", "Ex", 
                      paste(exons_POLE, collapse = ","),
                      paste0("(",min_POLE,")"))
      output_min_cov[[i]][17] <- POLE
    }
  } else {
    output_min_cov[[i]][17] <-  ""
  }
  
  if ("chr5:1.3Mb" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_TERT) > 10) {
      TERT <- paste("TERT", paste0("(",min_TERT,")"))
      output_min_cov[[i]][18] <- TERT
    } else {
      TERT <- paste("TERT", "Ex", 
                    paste(exons_TERT, collapse = ","),
                    paste0("(",min_TERT,")"))
      output_min_cov[[i]][18] <- TERT
    }
  } else {
    output_min_cov[[i]][18] <-  ""
  }
  
  if ("TP53" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_TP53) > 10) {
      TP53 <- paste("TP53", paste0("(",min_TP53,")"))
      output_min_cov[[i]][19] <- TP53
    } else {
      TP53 <- paste("TP53", "Ex", 
                    paste(exons_TP53, collapse = ","),
                    paste0("(",min_TP53,")"))
      output_min_cov[[i]][19] <- TP53
    }
  } else {
    output_min_cov[[i]][19] <-  ""
  }

  output_min_cov[[i]] <- paste0(unlist(output_min_cov[[i]]), collapse = " ")

  blank <- c("")
  cov_sheets[[i]] <- add_column(.data = cov_sheets[[i]], blank,
                                .after = "Gene")
  minimum_coverage <- c("")

  cov_sheets[[i]] <- add_column(.data = cov_sheets[[i]], minimum_coverage,
                                .after = "blank")
  cov_sheets[[i]]$minimum_coverage[15] <- output_min_cov[[i]]

  writeData(wb = wb, sheet = names_all_sheet[index_coverage_sheets][i],
            x = cov_sheets[[i]], # various = c()?
            startCol = 1, startRow = 1, colNames = TRUE, headerStyle = header)
  addStyle(wb, names_all_sheet[index_coverage_sheets][i],
           cols = colnumber_min_coverage,
           rows =  min_coverage_indexes[[i]]+1,
           style=light_red_style)
}

# Save current workbook
saveWorkbook(wb, "debug_oncoHS.xlsx",
             overwrite = TRUE)

print("Successfull!")

################################################################################

# Working on "unfiltered-sheets"
print("Sorting, filtering and assessing unfiltered sheets")
# Settings

# Getting in-house variant list (PanCancer)
name_of_variant_list <- dir(path = cwd, pattern = "Variantenliste*")
variant_list <-
   read_excel(paste(cwd, "/", name_of_variant_list,
                    sep=""))

# Dict of ENST numbers and corresponding NM numbers
ENST_NM_number_dict <- c("ENST00000555528"="NM_005163",
                         "ENST00000288602" = "NM_004333",
                         "ENST00000349496" = "NM_001904",
                         "ENST00000275493" = "NM_005228",
                         "ENST00000269571" = "NM_004448",
                         "ENST00000206249" = "NM_000125",
                         "ENST00000330315" = "NM_023067",
                         "ENST00000078429" = "NM_002067",
                         "ENST00000286548" = "NM_002072",
                         "ENST00000345146" = "NM_005896",
                         "ENST00000330062" = "NM_002168",
                         "ENST00000381298" = "NM_002184",
                         "ENST00000288135" = "NM_000222",
                         "ENST00000256078" = "NM_033360",#  "NM_004985"
                         "ENST00000369535" = "NM_002524",
                         "ENST00000257290" = "NM_006206",
                         "ENST00000263967" = "NM_006218",
                         "ENST00000320574" = "NM_006231",
                         "ENST00000310581" = "NM_198253",
                         "ENST00000269305" = "NM_000546")

# Global variables
sorted_unfil_sheets <- list()
merged_sorted_unfil_sheets <- list()
ENST_msu_sheets <- list()
ENST_msu_sheets_converted <- list()
NM_numbers_msu <- vector(mode = "list", length = max(1,number_all_sheets/3))
mut_msu_sheets <- list()

clinVar_summary_lst <- list()
mut_msu_sheets_Clinvar_check <- list()
mut_msu_sheets_Clinvar_check_p <- list()
mut_msu_sheets_Clinvar_check_p_name <- list()
mut_msu_sheets_Clinvar_check_n <- list()
mut_msu_sheets_Clinvar_check_n_egfr <- list()
mut_msu_sheets_Clinvar_check_n_egfr_GNA11 <- list()
mut_msu_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA <- list()

NM_mut_msu <- list()
msu_ENST <- list()
clinvar_variation_name <- list()
length_global_loop <- number_all_sheets/3
result_clinvar_msu <- vector(mode = "list", length = length_global_loop)

#  1. Sorting "Reference allel", "QUAL" and "Frequency"
#     !!!sort function!!! not the same as in excel
#  2. Merging in-house variant list; new column at the end of the table
#  3. Getting ENST numbers without .xx (e.g. ENST00000357654.xx)
#  4. Getting corresponding NM_numbers (e.g. "ENST00000357654"="NM_007294")
#  5. Getting mutations (e.g. c.123A>T)
#  6. Getting NM with mutations (e.g. NM_007294:c.123A>T)
#  7. Adding NM with mutations to the data
#     New column after "Coding region change in longest transcript"
#  8. Getting indexes of variants with frequencies above 10,5,1
#  9. Adding ClinVar information to the end of the column
# 10. Getting indexes of variants defined as P, P/LP, US, unklar, B/LB, B
# 11. Setting style of variants defined as P, P/LP, US, unklar, B/LB, B
# 12. Save current workbook

for (i in seq(1,number_all_sheets/3)) {

  # sorting unfiltered sheets
  sorted_unfil_sheets[[i]] <- unfil_sheets[[i]]  %>%
      filter(str_detect(`Reference allele`, "No")) %>%
      arrange(desc(Frequency)) %>% arrange(desc(QUAL))

  # merge in-house variant list to unfil sheets
  merged_sorted_unfil_sheets[[i]] <- sorted_unfil_sheets[[i]] %>%
      left_join(variant_list, by = "name dbsnp_v138")

  # Getting ENST numbers without .xx and handling TERT-Promoter mutations
  ENST_msu_sheets[[i]] <-
    merged_sorted_unfil_sheets[[i]]$`Coding region change in longest transcript`
  index_tert <- which(is.na(ENST_msu_sheets[[i]]))
  ENST_msu_sheets[[i]][index_tert] <-  
    merged_sorted_unfil_sheets[[i]]$`Coding region change`[index_tert]
  ENST_msu_sheets_converted[[i]] <- gsub("\\:.*","",ENST_msu_sheets[[i]])
  
  # Getting corresponding NM_numbers
  index <- 0
  for (j in unlist(ENST_msu_sheets_converted[[i]])) {
    index <- index + 1
    if (is.na(ENST_msu_sheets_converted[[i]][index])) {
      NM_numbers_msu[[i]][index] <- "Na"
    }
    else {
      NM_numbers_msu[[i]][index] <- ENST_NM_number_dict[[j]][1]
    }
  }
  
  # Getting mutations
  mut_msu_sheets[[i]] <- gsub(".*\\:",":",ENST_msu_sheets[[i]])
  
  # Getting mutations for Clinvar check
  mut_msu_sheets_Clinvar_check[[i]] <- gsub(".*\\:", "",ENST_msu_sheets[[i]])
  
  # Getting mutations for Clinvar check_p
  mut_msu_sheets_Clinvar_check_p[[i]] <- 
  merged_sorted_unfil_sheets[[i]]$`Amino acid change in longest transcript`
  mut_msu_sheets_Clinvar_check_p_name[[i]] <- gsub(".*\\:", 
                              "",mut_msu_sheets_Clinvar_check_p[[i]])
  
  # Getting gene names for Clinvar check_n
  mut_msu_sheets_Clinvar_check_n[[i]] <- 
    merged_sorted_unfil_sheets[[i]]$Homo_sapiens_ensembl_v74_Genes
  mut_msu_sheets_Clinvar_check_n_egfr[[i]] <-  gsub("EGFR, EGFR-AS1", 
                                    "EGFR",mut_msu_sheets_Clinvar_check_n[[i]])
  mut_msu_sheets_Clinvar_check_n_egfr_GNA11[[i]] <-  
    gsub("GNA11, AC005262.3", "GNA11",mut_msu_sheets_Clinvar_check_n_egfr[[i]])
  mut_msu_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA[[i]] <-  
    gsub("FIP1L1, PDGFRA", "PDGFRA",
         mut_msu_sheets_Clinvar_check_n_egfr_GNA11[[i]])
  
  # NM with mutations
  NM_mut_msu[[i]] <- paste(NM_numbers_msu[[i]],mut_msu_sheets[[i]], sep = "")

  #ENST_number
  `Coding region change in longest transcript (NM)` <- NM_mut_msu[[i]]
  msu_ENST[[i]] <- add_column(merged_sorted_unfil_sheets[[i]],
                   `Coding region change in longest transcript (NM)`,
                   .after = "Coding region change in longest transcript")

  # Underling the last variant with a frequency above 10,5,1
  underline <- createStyle(border = "bottom", borderColour = "#0f0f0f",
                           borderStyle = "thin")
  
  # Getting indexes of variants with frequencies above 10,5,1
  
  last_index_above_10_msu <- c()
  
  if (is_empty(which(msu_ENST[[i]]$Frequency > 10 & 
                     msu_ENST[[i]]$QUAL == 200)+1) == FALSE) {
    
    last_index_above_10_msu <- max(which(msu_ENST[[i]]$Frequency > 10 &
                                           msu_ENST[[i]]$QUAL == 200))+1
    
    addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
             cols = c(1, seq(colnames(msu_ENST[[i]]))+1),
             rows =  last_index_above_10_msu,
             style= underline, gridExpand = TRUE, stack = TRUE)
  }
  
  last_index_above_5_msu <- last_index_above_10_msu
  
  if (is_empty(which(msu_ENST[[i]]$Frequency > 5 &
                     msu_ENST[[i]]$QUAL == 200)+1) == FALSE) {
    
    last_index_above_5_msu <- max(which(msu_ENST[[i]]$Frequency > 5 &
                                          msu_ENST[[i]]$QUAL == 200))+1
    
    addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
             cols = c(1, seq(colnames(msu_ENST[[i]]))+1),
             rows =  last_index_above_5_msu,
             style= underline, gridExpand = TRUE, stack = TRUE)
  }
  
  last_index_above_1_msu <- last_index_above_5_msu
  
  if (is_empty(which(msu_ENST[[i]]$Frequency < 5 &
                     msu_ENST[[i]]$Frequency > 1 &
                     msu_ENST[[i]]$QUAL == 200)+1) == FALSE) {
    
    last_index_above_1_msu <- max(which(msu_ENST[[i]]$Frequency < 5 &
                                          msu_ENST[[i]]$Frequency > 1 &
                                          msu_ENST[[i]]$QUAL == 200))+1
    
    addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
             cols = c(1, seq(colnames(msu_ENST[[i]]))+1),
             rows =  last_index_above_1_msu,
             style= underline, gridExpand = TRUE, stack = TRUE)
  }
  
  # Adding new column with default values "NA"
  msu_ENST[[i]]["ClinVar"] <- NA
  
  # Adding ClinVar information to the end of the column
  for (k in seq_along(NM_mut_msu[[i]][seq(last_index_above_1_msu-1)])) {

    ClinVar_search <-entrez_search(db="ClinVar", term=NM_mut_msu[[i]][k])
    #ClinVar_search <-entrez_search(db="ClinVar", term="NM_198253:c.-111delC")
    
    clinVar_summary_lst <- list()
    lst_clinvar_msu <- list()
    output_Clinvar_msu <- c()
    
    if (ClinVar_search$count >= 1) {
    
        for (l in seq(ClinVar_search$count)) {

          clinVar_summary <- entrez_summary(db="ClinVar",
                                          id = ClinVar_search$ids[l])
      
          clinvar_variation_set <- clinVar_summary$variation_set
          clinvar_variation_name <- clinvar_variation_set$variation_name
      
          clinVar_summary_lst <- append(clinVar_summary_lst, 
                                        clinvar_variation_name)
          
          clinicalsignificane <- clinVar_summary$clinical_significance
          description <- clinicalsignificane$description
          lst_clinvar_msu <- append(lst_clinvar_msu, description)
        }
     
       clinVar_summary_index <- which(str_detect(string=clinVar_summary_lst, 
                                 pattern=mut_msu_sheets_Clinvar_check[[i]][k]) &
                          #             str_detect(string=clinVar_summary_lst, 
                          #pattern=NM_numbers_msu[[i]][k]) |
                  #mut_msu_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA[[i]][k] %in% 
                  # clinVar_summary_lst |
              #grepl(mut_msu_sheets_Clinvar_check_n[[i]][k],clinVar_summary_lst)
                                       str_detect(string=clinVar_summary_lst,
            pattern=mut_msu_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA[[i]][k]) |
                                       str_detect(string=clinVar_summary_lst, 
                          pattern=mut_msu_sheets_Clinvar_check_p_name[[i]][k]))
      
       output_Clinvar_msu <- lst_clinvar_msu[clinVar_summary_index]
       
    } else {
      lst_clinvar_msu <- c()
      lst_clinvar_msu <- append(lst_clinvar_msu, 
                                "not provided, PLEASE CHECK YOURSELF!")
      output_Clinvar_msu <- lst_clinvar_msu
      
    }
  
    result_clinvar_msu[[i]][k] <- output_Clinvar_msu
    
  }
    
  msu_ENST[[i]]$`ClinVar`[seq(last_index_above_1_msu-1)] <-
    result_clinvar_msu[[i]]

    # Getting indexes of variants defined as P, P/LP, VUS, unklar, B/LB, B and
  # Conflicting interpretations of pathogenicity (CI)
  index_pathogenic_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Pathogenic")

  index_LP_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Likely pathogenic")

  index_PLP_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Pathogenic/Likely pathogenic")

  index_VUS_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Uncertain significance")

  index_unklar_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="unklar")

  index_begnin_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Benign")

  index_BLB_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Benign/Likely benign")

  index_LB_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Likely benign")

  index_CI_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Conflicting interpretations of pathogenicity")

  index_np_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="not provided")

  # Setting style of variants defined as P, P/LP, VUS, unklar, B/LB, B and
  # Conflicting interpretations of pathogenicity (CI)

  colour_pathogenic_msu <- createStyle(textDecoration = "bold")

  colour_LP_msu <- createStyle(textDecoration = "bold")

  colour_PLP_msu <- createStyle(textDecoration = "bold")

  colour_VUS_msu <- createStyle(textDecoration = "bold")

  colour_unklar_msu <- createStyle(textDecoration = "bold")

  colour_CI_msu <- createStyle(textDecoration = "bold")

  colour_np_msu <- createStyle(textDecoration = "bold")

  colour_benign_msu <- createStyle(fontColour = "#797980")

  colour_BLB_msu <- createStyle(fontColour = "#797980")

  colour_LB_msu <- createStyle(fontColour = "#797980")

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_pathogenic_msu+1,
           style= colour_pathogenic_msu, gridExpand = TRUE, stack = TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_LP_msu+1,
           style= colour_LP_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_PLP_msu+1,
           style= colour_PLP_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_VUS_msu+1,
           style= colour_VUS_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_unklar_msu+1,
           style= colour_unklar_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_begnin_msu+1,
           style= colour_benign_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_BLB_msu+1,
           style= colour_BLB_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_LB_msu+1,
           style= colour_LB_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_CI_msu+1,
           style= colour_CI_msu, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_np_msu+1,
           style= colour_np_msu, gridExpand = TRUE, stack=TRUE)

  writeData(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
            x = msu_ENST[[i]], # vorher msu_ENST[[i]]
            startCol = 1, startRow = 1, colNames = TRUE, headerStyle = header)
}

# Save current workbook
saveWorkbook(wb, "debug_oncoHS.xlsx",
             overwrite = TRUE)

print("Successfull!")

################################################################################

# Working on "filtered-sheets"
print("Sorting, filtering and assessing filtered sheets")
# Settings

# Global variables
sorted_fil_sheets <- list()
merged_sorted_fil_sheets <- list()
ENST_msf_sheets <- list()
ENST_msf_sheets_converted <- list()
NM_numbers_msf <- vector(mode = "list", length = max(1,number_all_sheets/3))
mut_msf_sheets <- list()

clinVar_summary_lst <- list()
mut_msf_sheets_Clinvar_check <- list()
mut_msf_sheets_Clinvar_check_p <- list()
mut_msf_sheets_Clinvar_check_p_name <- list()
mut_msf_sheets_Clinvar_check_n <- list()
mut_msf_sheets_Clinvar_check_n_egfr <- list()
mut_msf_sheets_Clinvar_check_n_egfr_GNA11 <- list()
mut_msf_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA <- list()

NM_mut_msf <- list()
msf_ENST <- list()
length_global_loop <- number_all_sheets/3
result_clinvar_msf <- vector(mode = "list", length = length_global_loop)
output_Clinvar <- c()

# 1. Sorting "Reference allel", "QUAL" and "Frequency"
#    !!!sort function!!! not the same as in excel
# 2. Merging in-house variant list; new column at the end of the table
# 3. Getting ENST numbers without .xx (e.g. ENST00000357654.xx)
# 4. Getting corresponding NM_numbers (e.g. "ENST00000357654"="NM_007294")
# 5. Getting mutations (e.g. c.123A>T)
# 6. Getting NM with mutations (e.g. NM_007294:c.123A>T)
# 7. Adding NM with mutations to the data
#    New column after "Coding region change in longest transcript"
#  8. Getting indexes of variants with frequencies above 10,5,1
#  9. Adding ClinVar information to the end of the column
# 10. Getting indexes of variants defined as P, P/LP, US, unklar, B/LB, B
# 11. Setting style of variants defined as P, P/LP, US, unklar, B/LB, B
# 12. Save current workbook

for (i in seq(1,number_all_sheets/3)) {
  # sorting filtered sheets
  sorted_fil_sheets[[i]] <-  fil_sheets[[i]] %>%
  arrange(desc(Frequency))

  # merge in-house variant list to unfil sheets
  merged_sorted_fil_sheets[[i]] <- sorted_fil_sheets[[i]] %>%
    left_join(variant_list, by = "name dbsnp_v138")

  # Getting ENST numbers without .xx and handling TERT-Promoter mutations
  ENST_msf_sheets[[i]] <-
    merged_sorted_fil_sheets[[i]]$`Coding region change in longest transcript`
  index_tert_msf <- which(is.na(ENST_msf_sheets[[i]]))
  ENST_msf_sheets[[i]][index_tert_msf] <-  
    merged_sorted_fil_sheets[[i]]$`Coding region change`[index_tert_msf]
  ENST_msf_sheets_converted[[i]] <- gsub("\\:.*","",ENST_msf_sheets[[i]])
  
  # Getting corresponding NM_numbers
  index <- 0
  for (j in unlist(ENST_msf_sheets_converted[[i]])) {
    index <- index + 1
    NM_numbers_msf[[i]][index] <- ENST_NM_number_dict[[j]][1]
  }

  # Getting mutations
  mut_msf_sheets[[i]] <- gsub(".*\\:",":",ENST_msf_sheets[[i]])
  
  # Getting mutations for Clinvar check
  mut_msf_sheets_Clinvar_check[[i]] <- gsub(".*\\:", "",ENST_msf_sheets[[i]])
  
  # Getting mutations for Clinvar check_p
  mut_msf_sheets_Clinvar_check_p[[i]] <- 
    merged_sorted_fil_sheets[[i]]$`Amino acid change in longest transcript`
  mut_msf_sheets_Clinvar_check_p_name[[i]] <- gsub(".*\\:", 
                                    "",mut_msf_sheets_Clinvar_check_p[[i]])
  
  # Getting gene names for Clinvar check_n
  mut_msf_sheets_Clinvar_check_n[[i]] <- 
    merged_sorted_fil_sheets[[i]]$Homo_sapiens_ensembl_v74_Genes
  mut_msf_sheets_Clinvar_check_n_egfr[[i]] <-  gsub("EGFR, EGFR-AS1", 
                                    "EGFR",mut_msf_sheets_Clinvar_check_n[[i]])
  mut_msf_sheets_Clinvar_check_n_egfr_GNA11[[i]] <-  
    gsub("GNA11, AC005262.3", "GNA11",mut_msf_sheets_Clinvar_check_n_egfr[[i]])
  mut_msf_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA[[i]] <-  
    gsub("FIP1L1, PDGFRA", "PDGFRA",
         mut_msf_sheets_Clinvar_check_n_egfr_GNA11[[i]])

  # NM with mutations
  NM_mut_msf[[i]] <- paste(NM_numbers_msf[[i]],mut_msf_sheets[[i]], sep = "")

  #ENST_number
  `Coding region change in longest transcript NM` <- NM_mut_msf[[i]]
  msf_ENST[[i]] <- add_column(merged_sorted_fil_sheets[[i]],
                   `Coding region change in longest transcript NM`,
                   .after = "Coding region change in longest transcript")

  # Getting indexes of variants with frequencies above 10,5,1

  if (is_empty(which(msf_ENST[[i]]$Frequency > 10)+1) == FALSE) {

    last_index_above_10 <- max(which(msf_ENST[[i]]$Frequency > 10))+1

    addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
             cols = c(1,seq(colnames(msf_ENST[[i]]))+1),
             rows =  last_index_above_10,
             style= underline, gridExpand = TRUE, stack = TRUE)
  }

  if (is_empty(which(msf_ENST[[i]]$Frequency > 5 &
                      msf_ENST[[i]]$Frequency < 10)+1) == FALSE) {

    last_index_above_5 <- max(which(msf_ENST[[i]]$Frequency > 5 &
                                        msf_ENST[[i]]$Frequency < 10))+1

    addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
             cols = c(1,seq(colnames(msf_ENST[[i]]))+1),
             rows =  last_index_above_5,
             style= underline, gridExpand = TRUE, stack = TRUE)
  }

  if (is_empty(which(msf_ENST[[i]]$Frequency < 5 &
                    msf_ENST[[i]]$Frequency > 1)+1) == FALSE) {

    last_index_above_1 <- max(which(msf_ENST[[i]]$Frequency < 5 &
                                        msf_ENST[[i]]$Frequency > 1))+1

    addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
             cols = c(1,seq(colnames(msf_ENST[[i]]))+1),
             rows =  last_index_above_1,
             style= underline, gridExpand = TRUE, stack = TRUE)
  }

  # Adding new column with default values "NA"
  msf_ENST[[i]]["ClinVar"] <- NA

  for (k in seq_along(NM_mut_msf[[i]])) {

    ClinVar_search <-entrez_search(db="ClinVar", term=NM_mut_msf[[i]][k])
    
    clinVar_summary_lst <- list()
    lst_clinvar <- list()
    output_Clinvar <- c()
    
    if (ClinVar_search$count >= 1) {
      
      for (l in seq(ClinVar_search$count)) {
        
        clinVar_summary <- entrez_summary(db="ClinVar",
                                          id = ClinVar_search$ids[l])
        
        clinvar_variation_set <- clinVar_summary$variation_set
        clinvar_variation_name <- clinvar_variation_set$variation_name
        
        clinVar_summary_lst <- append(clinVar_summary_lst, 
                                      clinvar_variation_name)
        
        clinicalsignificane <- clinVar_summary$clinical_significance
        description <- clinicalsignificane$description
        lst_clinvar <- append(lst_clinvar, description)
      }
      
      clinVar_summary_index <- which(str_detect(string=clinVar_summary_lst, 
                                pattern=mut_msf_sheets_Clinvar_check[[i]][k]) &
                                       #             str_detect(string=clinVar_summary_lst, 
                                       #pattern=NM_numbers_msu[[i]][k]) |
                                       #mut_msu_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA[[i]][k] %in% 
                                       # clinVar_summary_lst |
                                       #grepl(mut_msu_sheets_Clinvar_check_n[[i]][k],clinVar_summary_lst)
                            str_detect(string=clinVar_summary_lst,
            pattern=mut_msf_sheets_Clinvar_check_n_egfr_GNA11_PDGFRA[[i]][k]) |
                                       str_detect(string=clinVar_summary_lst, 
                        pattern=mut_msf_sheets_Clinvar_check_p_name[[i]][k]))
      
      output_Clinvar <- lst_clinvar[clinVar_summary_index]
      
    } else {
      lst_clinvar <- c()
      lst_clinvar <- append(lst_clinvar, 
                                "not provided, PLEASE CHECK YOURSELF!")
      output_Clinvar <- lst_clinvar
      
    }
    
    result_clinvar_msf[[i]][k] <- output_Clinvar
    
  }

  msf_ENST[[i]]$`ClinVar` <- result_clinvar_msf[[i]]

  # Getting indexes of variants defined as P, P/LP, US, unklar, B/LB, B and
  # Conflicting interpretations of pathogenicity (CI)

  index_pathogenic <-
  which(msf_ENST[[i]]$`ClinVar`=="Pathogenic")

  index_LP <-
    which(msf_ENST[[i]]$`ClinVar`=="Likely pathogenic")

  index_PLP <-
  which(msf_ENST[[i]]$`ClinVar`=="Pathogenic/Likely pathogenic")

  index_VUS <-
  which(msf_ENST[[i]]$`ClinVar`=="Uncertain significance")

  index_unklar <-
  which(msf_ENST[[i]]$`ClinVar`=="unklar")

  index_begnin <-
  which(msf_ENST[[i]]$`ClinVar`=="Benign")

  index_BLB <-
  which(msf_ENST[[i]]$`ClinVar`=="Benign/Likely benign")

  index_LB <-
    which(msf_ENST[[i]]$`ClinVar`=="Likely benign")

  index_CI <-
    which(msf_ENST[[i]]$`ClinVar`=="Conflicting interpretations of pathogenicity")

  index_np <-
    which(msf_ENST[[i]]$`ClinVar`=="not provided")

  # Setting style of variants defined as P, P/LP, US, unklar, B/LB, B and
  # Conflicting interpretations of pathogenicity (CI)

  colour_pathogenic <- createStyle(textDecoration = "bold")

  colour_LP <- createStyle(textDecoration = "bold")

  colour_PLP <- createStyle(textDecoration = "bold")

  colour_VUS <- createStyle(textDecoration = "bold")

  colour_unklar <- createStyle(textDecoration = "bold")

  colour_CI <- createStyle(textDecoration = "bold")

  colour_np <- createStyle(textDecoration = "bold")

  colour_benign <- createStyle(fontColour = "#797980")

  colour_BLB <- createStyle(fontColour = "#797980")

  colour_LB <- createStyle(fontColour = "#797980")

  # Adding style to the excel table
  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_pathogenic+1,
           style= colour_pathogenic, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_LP+1,
           style= colour_LP, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_PLP+1,
           style= colour_PLP, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_VUS+1,
           style= colour_VUS, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_unklar+1,
           style= colour_unklar, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_begnin+1,
           style= colour_benign, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_BLB+1,
           style= colour_BLB, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_LB+1,
           style= colour_LB, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_CI+1,
           style= colour_CI, gridExpand = TRUE, stack=TRUE)

  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows =  index_np+1,
           style= colour_np, gridExpand = TRUE, stack=TRUE)

  writeData(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
            x = msf_ENST[[i]],
            startCol = 1, startRow = 1, colNames = TRUE, headerStyle = header)
}

# Save current workbook
saveWorkbook(wb, "debug_oncoHS.xlsx",
             overwrite = TRUE)

print("Successfull!")

# Highlighting rows in unfiltered-sheet not present in filtered-sheet
for (i in seq(1,number_all_sheets/3)) {

  indexes_fil_compare <- which(msf_ENST[[i]]$Frequency > 1 &
                                 msf_ENST[[i]]$QUAL == 200)

  indexes_unfil_compare <- which(msu_ENST[[i]]$Frequency > 1 &
                                   msu_ENST[[i]]$QUAL == 200)

  not_abundant <- which(msu_ENST[[i]]$Frequency[indexes_unfil_compare]
                        %in% msf_ENST[[i]]$Frequency[indexes_fil_compare] == FALSE)+1

  colour_not_abundant <- createStyle(fgFill = "#ffffcc")

  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  not_abundant,
           style= colour_not_abundant, gridExpand = TRUE, stack = TRUE)

  writeData(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
            x = msu_ENST[[i]],
            startCol = 1, startRow = 1, colNames = TRUE, headerStyle = header)

}

# Save workbook
saveWorkbook(wb, "debug_oncoHS.xlsx",
             overwrite = TRUE)

# Display runtime
end_time <- Sys.time()
process_time_difference <- round(end_time-time_start, 2)
process_time <- format(process_time_difference)
print(paste("Process time:", process_time))





