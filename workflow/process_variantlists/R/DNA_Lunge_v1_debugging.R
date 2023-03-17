################################################################################
# Script to sort, filter and assess CLC Genomics Workbench Data - DNALunge Panel
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
#cwd <- here()
#path_to_data <- cwd
#filename <- paste("/", opt$file, sep="")

# Setting path and getting filename
cwd <- here()
path_to_data <- cwd
filename <- "/22_03_25_DNA_Lunge_test.xlsx"

# Date and time for log file
print(paste("Date:", time_start))

# Show command in log file
print(paste("File:", opt$file))
print("Rscript: DNA_Lunge_v1.R")
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
exon_table <- read_excel(paste(cwd,"/exontableDNALunge.xlsx",
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

  exons_ALK <- c()
  exons_BRAF <- c()
  exons_CTNNB1 <- c()
  exons_EGFR <- c()
  exons_ERBB2_HER2 <- c()
  exons_FGFR1 <- c()
  exons_FGFR2 <- c()
  exons_FGFR3 <- c()
  exons_FGFR4 <- c()
  exons_HRAS <- c()
  exons_IDH1 <- c()
  exons_IDH2 <- c()
  exons_KEAP1 <- c()
  exons_KRAS <- c()
  exons_MAP2K1_MEK1 <- c()
  exons_MET <- c()
  exons_NRAS <- c()
  exons_NTRK1 <- c()
  exons_NTRK2 <- c()
  exons_NTRK3 <- c()
  exons_PIK3CA <- c()
  exons_PTEN <- c()
  exons_RET <- c()
  exons_ROS1 <- c()
  exons_STK11 <- c()
  exons_TP53 <- c()

  min_ALK <- 100
  min_BRAF <- 100
  min_CTNNB1 <- 100
  min_EGFR <- 100
  min_ERBB2_HER2 <- 100
  min_FGFR1 <- 100
  min_FGFR2 <- 100
  min_FGFR3 <- 100
  min_FGFR4 <- 100
  min_HRAS <- 100
  min_IDH1 <- 100
  min_IDH2 <- 100
  min_KEAP1 <- 100
  min_KRAS <- 100
  min_MAP2K1_MEK1 <- 100
  min_MET <- 100
  min_NRAS <- 100
  min_NTRK1 <- 100
  min_NTRK2 <- 100
  min_NTRK3 <- 100
  min_PIK3CA <- 100
  min_PTEN <- 100
  min_RET <- 100
  min_ROS1 <- 100
  min_STK11 <- 100
  min_TP53 <- 100

  count_ALK <- 0
  count_BRAF <- 0
  count_CTNNB1 <- 0
  count_EGFR <- 0
  count_ERBB2_HER2 <- 0
  count_FGFR1 <- 0
  count_FGFR2 <- 0
  count_FGFR3 <- 0
  count_FGFR4 <- 0
  count_HRAS <- 0
  count_IDH1 <- 0
  count_IDH2 <- 0
  count_KEAP1 <- 0
  count_KRAS <- 0
  count_MAP2K1_MEK1 <- 0
  count_MET <- 0
  count_NRAS <- 0
  count_NTRK1 <- 0
  count_NTRK2 <- 0
  count_NTRK3 <- 0
  count_PIK3CA <- 0
  count_PTEN <- 0
  count_RET <- 0
  count_ROS1 <- 0
  count_STK11 <- 0
  count_TP53 <- 0

  for (j in seq(name_exon_mincov[[i]])) {
    splitted <-
      unlist(str_split(string = name_exon_mincov[[i]][j], pattern = " "))

    if ("ALK" %in% splitted) {
      count_ALK <- count_ALK + 1
      exons_ALK <- append(exons_ALK, splitted[3])
      min_cov_ALK <- as.double(splitted[4])
      if (min_cov_ALK < min_ALK) {
        min_ALK <- min_cov_ALK
        num_ALK <- paste0("(",min_ALK ,")")
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
    } else if ("FGFR1" %in% splitted) {
      count_FGFR1 <- count_FGFR1 + 1
      exons_FGFR1 <- append(exons_FGFR1, splitted[3])
      min_cov_FGFR1 <- as.double(splitted[4])
      if (min_cov_FGFR1 <  min_FGFR1) {
        min_FGFR1 <- min_cov_FGFR1
        num_FGFR1 <- paste0("(",min_FGFR1 ,")")
      }
    } else if ("FGFR2" %in% splitted) {
      count_FGFR2 <- count_FGFR2 + 1
      exons_FGFR2 <- append(exons_FGFR2, splitted[3])
      min_cov_FGFR2 <- as.double(splitted[4])
      if (min_cov_FGFR2 <  min_FGFR2) {
        min_FGFR2 <- min_cov_FGFR2
        num_FGFR2<- paste0("(",min_FGFR2 ,")")
      }
    } else if ("FGFR3" %in% splitted) {
      count_FGFR3 <- count_FGFR3 + 1
      exons_FGFR3 <- append(exons_FGFR3, splitted[3])
      min_cov_FGFR3 <- as.double(splitted[4])
      if (min_cov_FGFR3 <  min_FGFR3) {
        min_FGFR3 <- min_cov_FGFR3
        num_FGFR3 <- paste0("(",min_FGFR3 ,")")
      }
    } else if ("FGFR4" %in% splitted) {
      count_FGFR4 <- count_FGFR4 + 1
      exons_FGFR4 <- append(exons_FGFR4, splitted[3])
      min_cov_FGFR4 <- as.double(splitted[4])
      if (min_cov_FGFR4 <  min_FGFR4) {
        min_FGFR4 <- min_cov_FGFR4
        num_FGFR4 <- paste0("(",min_FGFR4 ,")")
      }
    } else if ("HRAS" %in% splitted) {
      count_HRAS <- count_HRAS + 1
      exons_HRAS <- append(exons_HRAS, splitted[3])
      min_cov_HRAS <- as.double(splitted[4])
      if (min_cov_HRAS <  min_HRAS) {
        min_HRAS <- min_cov_HRAS
        num_HRAS <- paste0("(",min_HRAS ,")")
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
    } else if ("KEAP1" %in% splitted) {
      count_KEAP1 <- count_KEAP1 + 1
      exons_KEAP1 <- append(exons_KEAP1, splitted[3])
      min_cov_KEAP1 <- as.double(splitted[4])
      if (min_cov_KEAP1 <  min_KEAP1) {
        min_KEAP1 <- min_cov_KEAP1
        num_KEAP1 <- paste0("(",min_KEAP1 ,")")
      }
    } else if ("KRAS" %in% splitted) {
      count_KRAS <- count_KRAS + 1
      exons_KRAS <- append(exons_KRAS, splitted[3])
      min_cov_KRAS <- as.double(splitted[4])
      if (min_cov_KRAS <  min_KRAS) {
        min_KRAS <- min_cov_KRAS
        num_KRAS <- paste0("(",min_KRAS ,")")
      }
    } else if ("MAP2K1" %in% splitted) {
      count_MAP2K1_MEK1 <- count_MAP2K1_MEK1 + 1
      exons_MAP2K1_MEK1 <- append(exons_MAP2K1_MEK1, splitted[3])
      min_cov_MAP2K1_MEK1 <- as.double(splitted[4])
      if (min_cov_MAP2K1_MEK1 <  min_MAP2K1_MEK1) {
        min_MAP2K1_MEK1 <- min_cov_MAP2K1_MEK1
        num_MAP2K1_MEK1 <- paste0("(",min_MAP2K1_MEK1 ,")")
      }
    } else if ("MET" %in% splitted) {
      count_MET <- count_MET + 1
      exons_MET <- append(exons_MET, splitted[3])
      min_cov_MET <- as.double(splitted[4])
      if (min_cov_MET <  min_MET) {
        min_MET <- min_cov_MET
        num_MET <- paste0("(",min_MET ,")")
      }
    } else if ("NRAS" %in% splitted) {
      count_NRAS <- count_NRAS + 1
      exons_NRAS <- append(exons_NRAS, splitted[3])
      min_cov_NRAS <- as.double(splitted[4])
      if (min_cov_NRAS <  min_NRAS) {
        min_NRAS <- min_cov_NRAS
        num_NRAS <- paste0("(",min_NRAS ,")")
      }
    } else if ("NTRK1" %in% splitted) {
      count_NTRK1 <- count_NTRK1 + 1
      exons_NTRK1 <- append(exons_NTRK1, splitted[3])
      min_cov_NTRK1 <- as.double(splitted[4])
      if (min_cov_NTRK1 <  min_NTRK1) {
        min_NTRK1 <- min_cov_NTRK1
        num_NTRK1 <- paste0("(",min_NTRK1 ,")")
      }
    } else if ("NTRK2" %in% splitted) {
      count_NTRK2 <- count_NTRK2 + 1
      exons_NTRK2 <- append(exons_NTRK2, splitted[3])
      min_cov_NTRK2 <- as.double(splitted[4])
      if (min_cov_NTRK2 <  min_NTRK2) {
        min_NTRK2 <- min_cov_NTRK2
        num_NTRK2 <- paste0("(",min_NTRK2 ,")")
      }
    } else if ("NTRK3" %in% splitted) {
      count_NTRK3 <- count_NTRK3 + 1
      exons_NTRK3 <- append(exons_NTRK3, splitted[3])
      min_cov_NTRK3 <- as.double(splitted[4])
      if (min_cov_NTRK3 <  min_NTRK3) {
        min_NTRK3 <- min_cov_NTRK3
        num_NTRK3 <- paste0("(",min_NTRK3 ,")")
      }
    } else if ("PIK3CA" %in% splitted) {
      count_PIK3CA <- count_PIK3CA + 1
      exons_PIK3CA <- append(exons_PIK3CA, splitted[3])
      min_cov_PIK3CA <- as.double(splitted[4])
      if (min_cov_PIK3CA <  min_PIK3CA) {
        min_PIK3CA <- min_cov_PIK3CA
        num_PIK3CA <- paste0("(",min_PIK3CA ,")")
      }
    } else if ("PTEN" %in% splitted) {
      count_PTEN <- count_PTEN + 1
      exons_PTEN <- append(exons_PTEN, splitted[3])
      min_cov_PTEN <- as.double(splitted[4])
      if (min_cov_PTEN <  min_PTEN) {
        min_PTEN <- min_cov_PTEN
        num_PTEN <- paste0("(",min_PTEN ,")")
      }
    } else if ("RET" %in% splitted) {
      count_RET <- count_RET + 1
      exons_RET <- append(exons_RET, splitted[3])
      min_cov_RET <- as.double(splitted[4])
      if (min_cov_RET <  min_RET) {
        min_RET <- min_cov_RET
        num_RET <- paste0("(",min_RET ,")")
      }
    } else if ("ROS1" %in% splitted) {
      count_ROS1 <- count_ROS1 + 1
      exons_ROS1 <- append(exons_ROS1, splitted[3])
      min_cov_ROS1 <- as.double(splitted[4])
      if (min_cov_ROS1 <  min_ROS1) {
        min_ROS1 <- min_cov_ROS1
        num_ROS1 <- paste0("(",min_ROS1 ,")")
      }
    } else if ("STK11" %in% splitted) {
      count_STK11 <- count_STK11 + 1
      exons_STK11 <- append(exons_STK11, splitted[3])
      min_cov_STK11 <- as.double(splitted[4])
      if (min_cov_STK11 <  min_STK11) {
        min_STK11 <- min_cov_STK11
        num_STK11 <- paste0("(",min_STK11 ,")")
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

  if ("ALK" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_ALK) > 10) {
        ALK <- paste("ALK", paste0("(minimum coverage: ",min_ALK,")"))
        output_min_cov[[i]][1] <- ALK
    } else {
        ALK <- paste("ALK", "Ex", paste(exons_ALK, collapse = ","),
                     paste0("(minimum coverage: ",min_ALK,")"))
        output_min_cov[[i]][1] <- ALK
      }
  } else {
      output_min_cov[[i]][1] <-  ""
  }

  if ("BRAF" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_BRAF) > 10) {
        BRAF <- paste("BRAF", paste0("(minimum coverage: ",min_BRAF,")"))
        output_min_cov[[i]][2] <- BRAF
    } else {
        BRAF <- paste("BRAF", "Ex", paste(exons_BRAF, collapse = ","),
                    paste0("(minimum coverage: ",min_BRAF,")"))
        output_min_cov[[i]][2] <- BRAF
      }
  } else {
    output_min_cov[[i]][2] <-  ""
  }

  if ("CTNNB1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                  pattern=" "))) {
    if (length(exons_CTNNB1) > 10) {
        CTNNB1 <- paste("CTNNB1", paste0("(minimum coverage: ",min_CTNNB1,")"))
        output_min_cov[[i]][3] <- CTNNB1
    } else {
        CTNNB1 <- paste("CTNNB1", "Ex", paste(exons_CTNNB1, collapse = ","),
                   paste0("(minimum coverage: ",min_CTNNB1,")"))
        output_min_cov[[i]][3] <-  CTNNB1
      }
  } else {
    output_min_cov[[i]][3] <-  ""
  }

  if ("EGFR" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_EGFR) > 10) {
        EGFR <- paste("EGFR", paste0("(minimum coverage: ",min_EGFR,")"))
        output_min_cov[[i]][4] <- EGFR
    } else {
        EGFR <- paste("EGFR", "Ex", paste(exons_EGFR, collapse = ","),
                     paste0("(minimum coverage: ",min_EGFR,")"))
      output_min_cov[[i]][4] <- EGFR
      }
  } else {
    output_min_cov[[i]][4] <-  ""
  }

  if ("ERBB2_HER2" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_ERBB2_HER2) > 10) {
        ERBB2_HER2 <- paste("ERBB2_HER2", paste0("(minimum coverage: ",
                                                 min_ERBB2_HER2,")"))
        output_min_cov[[i]][5] <- ERBB2_HER2
    } else {
        ERBB2_HER2 <- paste("ERBB2_HER2", "Ex", 
                      paste(exons_ERBB2_HER2, collapse = ","),
                      paste0("(minimum coverage: ",min_ERBB2_HER2,")"))
      output_min_cov[[i]][5] <- ERBB2_HER2
      }
  } else {
    output_min_cov[[i]][5] <-  ""
  }

  if ("FGFR1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_FGFR1) > 10) {
        FGFR1 <- paste("FGFR1", paste0("(minimum coverage: ",min_FGFR1,")"))
        output_min_cov[[i]][6] <- FGFR1
    } else {
        FGFR1 <- paste("FGFR1", "Ex", paste(exons_FGFR1, collapse = ","),
                     paste0("(minimum coverage: ",min_FGFR1,")"))
      output_min_cov[[i]][6] <- FGFR1
      }
  } else {
    output_min_cov[[i]][6] <-  ""
  }

  if ("FGFR2" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_FGFR2) > 10) {
        FGFR2 <- paste("FGFR2", paste0("(minimum coverage: ",min_FGFR2,")"))
        output_min_cov[[i]][7] <- FGFR2
    } else {
        FGFR2 <- paste("FGFR2", "Ex", paste(exons_FGFR2, collapse = ","),
                     paste0("(minimum coverage: ",min_FGFR2,")"))
      output_min_cov[[i]][7] <- FGFR2
      }
  } else {
    output_min_cov[[i]][7] <-  ""
  }

  if ("FGFR3" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_FGFR3) > 10) {
        FGFR3 <- paste("FGFR3", paste0("(minimum coverage: ",min_FGFR3,")"))
        output_min_cov[[i]][8] <- FGFR3
    } else {
        FGFR3 <- paste("FGFR3", "Ex", paste(exons_FGFR3, collapse = ","),
                     paste0("(minimum coverage: ",min_FGFR3,")"))
      output_min_cov[[i]][8] <- FGFR3
      }
  } else {
    output_min_cov[[i]][8] <-  ""
  }
  
  if ("FGFR4" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_FGFR4) > 10) {
      FGFR4 <- paste("FGFR4", paste0("(minimum coverage: ",min_FGFR4,")"))
      output_min_cov[[i]][9] <- FGFR4
    } else {
      FGFR4 <- paste("FGFR4", "Ex", paste(exons_FGFR4, collapse = ","),
                     paste0("(minimum coverage: ",min_FGFR4,")"))
      output_min_cov[[i]][9] <- FGFR4
      }
  } else {
    output_min_cov[[i]][9] <-  ""
  }
  
  if ("HRAS" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_HRAS) > 10) {
      HRAS <- paste("HRAS", paste0("(minimum coverage: ",min_HRAS,")"))
      output_min_cov[[i]][10] <- HRAS
    } else {
      HRAS <- paste("HRAS", "Ex", paste(exons_HRAS, collapse = ","),
                     paste0("(minimum coverage: ",min_HRAS,")"))
      output_min_cov[[i]][10] <- HRAS
      }
  } else {
    output_min_cov[[i]][10] <-  ""
  }
  
  if ("IDH1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_IDH1) > 10) {
        IDH1 <- paste("IDH1", paste0("(minimum coverage: ",min_IDH1,")"))
        output_min_cov[[i]][11] <- IDH1
    } else {
        IDH1 <- paste("IDH1", "Ex", paste(exons_IDH1, collapse = ","),
                     paste0("(minimum coverage: ",min_IDH1,")"))
      output_min_cov[[i]][11] <- IDH1
      }
  } else {
    output_min_cov[[i]][11] <-  ""
  }
  
  if ("IDH2" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_IDH2) > 10) {
      IDH2 <- paste("IDH2", paste0("(minimum coverage: ",min_IDH2,")"))
      output_min_cov[[i]][12] <- IDH2
    } else {
      IDH2 <- paste("IDH1", "Ex", paste(exons_IDH2, collapse = ","),
                    paste0("(minimum coverage: ",min_IDH2,")"))
      output_min_cov[[i]][12] <- IDH2
      }
  } else {
    output_min_cov[[i]][12] <-  ""
  }
  
  if ("KEAP1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_KEAP1) > 10) {
      KEAP1 <- paste("KEAP1", paste0("(minimum coverage: ",min_KEAP1,")"))
      output_min_cov[[i]][13] <- KEAP1
    } else {
      KEAP1 <- paste("KEAP1", "Ex", 
                     paste(exons_KEAP1, collapse = ","),
                     paste0("(minimum coverage: ",KEAP1,")"))
      output_min_cov[[i]][13] <- KEAP1
      }
  } else {
    output_min_cov[[i]][13] <-  ""
  }
  
  if ("KRAS" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                  pattern=" "))) {
    if (length(exons_KRAS) > 10) {
      KRAS <- paste("KRAS", paste0("(minimum coverage: ",min_KRAS,")"))
      output_min_cov[[i]][14] <- KRAS
    } else {
      KRAS <- paste("KRAS", "Ex", 
                   paste(exons_KRAS, collapse = ","),
                   paste0("(minimum coverage: ",min_KRAS,")"))
      output_min_cov[[i]][14] <- KRAS
      }
  } else {
    output_min_cov[[i]][14] <-  ""
  }
  
  if ("MAP2K1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_MAP2K1_MEK1) > 10) {
      MAP2K1_MEK1 <- paste("MAP2K1_MEK1", paste0("(minimum coverage: ",
                                                 min_MAP2K1_MEK1,")"))
      output_min_cov[[i]][15] <- MAP2K1_MEK1
    } else {
      MAP2K1_MEK1 <- paste("MAP2K1_MEK1", "Ex", 
                    paste(exons_MAP2K1_MEK1, collapse = ","),
                    paste0("(minimum coverage: ",min_MAP2K1_MEK1,")"))
      output_min_cov[[i]][15] <- MAP2K1_MEK1
      }
  } else {
    output_min_cov[[i]][15] <-  ""
  }
  
  if ("MET" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                     pattern=" "))) {
    if (length(exons_MET) > 10) {
       MET <- paste("MET", paste0("(minimum coverage: ",min_MET,")"))
      output_min_cov[[i]][16] <- MET
    } else {
      MET <- paste("MET", "Ex", 
                           paste(exons_MET, collapse = ","),
                           paste0("(minimum coverage: ",min_MET,")"))
      output_min_cov[[i]][16] <- MET
      }
  } else {
    output_min_cov[[i]][16] <-  ""
  }
  
  if ("NRAS" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_NRAS) > 10) {
      NRAS <- paste("NRAS", paste0("(minimum coverage: ",min_NRAS,")"))
      output_min_cov[[i]][17] <- NRAS
    } else {
      NRAS <- paste("NRAS", "Ex", 
                    paste(exons_NRAS, collapse = ","),
                    paste0("(minimum coverage: ",min_NRAS,")"))
      output_min_cov[[i]][17] <- NRAS
      }
  } else {
    output_min_cov[[i]][17] <-  ""
  }
  
  if ("NTRK1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_NTRK1) > 10) {
      NTRK1 <- paste("NTRK1", paste0("(minimum coverage: ",min_NTRK1,")"))
      output_min_cov[[i]][18] <- NTRK1
    } else {
      NTRK1 <- paste("NTRK1", "Ex", 
                    paste(exons_NTRK1, collapse = ","),
                    paste0("(minimum coverage: ",min_NTRK1,")"))
      output_min_cov[[i]][18] <- NTRK1
      }
  } else {
    output_min_cov[[i]][18] <-  ""
  }
  
  if ("NTRK2" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_NTRK2) > 10) {
      NTRK2 <- paste("NTRK2", paste0("(minimum coverage: ",min_NTRK2,")"))
      output_min_cov[[i]][19] <- NTRK2
    } else {
      NTRK2 <- paste("NTRK2", "Ex", 
                     paste(exons_NTRK2, collapse = ","),
                     paste0("(minimum coverage: ",min_NTRK2,")"))
      output_min_cov[[i]][19] <- NTRK2
      }
  } else {
    output_min_cov[[i]][19] <-  ""
  }
  
  if ("NTRK3" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_NTRK3) > 10) {
      NTRK3 <- paste("NTRK3", paste0("(minimum coverage: ",min_NTRK3,")"))
      output_min_cov[[i]][20] <- NTRK3
    } else {
      NTRK3 <- paste("NTRK3", "Ex", 
                     paste(exons_NTRK3, collapse = ","),
                     paste0("(minimum coverage: ",min_NTRK3,")"))
      output_min_cov[[i]][20] <- NTRK3
      }
  } else {
    output_min_cov[[i]][20] <-  ""
  }
  
  if ("NTRK4" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                    pattern=" "))) {
    if (length(exons_NTRK4) > 10) {
      NTRK4 <- paste("NTRK4", paste0("(minimum coverage: ",min_NTRK4,")"))
      output_min_cov[[i]][21] <- NTRK4
    } else {
      NTRK4 <- paste("NTRK4", "Ex", 
                     paste(exons_NTRK4, collapse = ","),
                     paste0("(minimum coverage: ",min_NTRK4,")"))
      output_min_cov[[i]][21] <- NTRK4
    }
  } else {
    output_min_cov[[i]][21] <-  ""
  }
  
  if ("PIK3CA" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                     pattern=" "))) {
    if (length(exons_PIK3CA) > 10) {
      PIK3CA <- paste("PIK3CA", paste0("(minimum coverage: ",min_PIK3CA,")"))
      output_min_cov[[i]][22] <- PIK3CA
    } else {
      PIK3CA <- paste("PIK3CA", "Ex", 
                      paste(exons_PIK3CA, collapse = ","),
                      paste0("(minimum coverage: ",min_PIK3CA,")"))
      output_min_cov[[i]][22] <- PIK3CA
    }
  } else {
    output_min_cov[[i]][22] <-  ""
  }
  
  if ("PTEN" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                     pattern=" "))) {
    if (length(exons_PTEN) > 10) {
      PTEN <- paste("PTEN", paste0("(minimum coverage: ",min_PTEN,")"))
      output_min_cov[[i]][23] <- PTEN
    } else {
      PTEN <- paste("PTEN", "Ex", 
                      paste(exons_PTEN, collapse = ","),
                      paste0("(minimum coverage: ",min_PTEN,")"))
      output_min_cov[[i]][23] <- PTEN
    }
  } else {
    output_min_cov[[i]][23] <-  ""
  }
  
  if ("RET" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_RET) > 10) {
      RET <- paste("RET", paste0("(minimum coverage: ",min_RET,")"))
      output_min_cov[[i]][24] <- RET
    } else {
      RET <- paste("RET", "Ex", 
                    paste(exons_RET, collapse = ","),
                    paste0("(minimum coverage: ",min_RET,")"))
      output_min_cov[[i]][24] <- RET
      }
  } else {
    output_min_cov[[i]][24] <-  ""
  }
  
  if ("ROS1" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                  pattern=" "))) {
    if (length(exons_ROS1) > 10) {
      ROS1 <- paste("ROS1", paste0("(minimum coverage: ",min_ROS1,")"))
      output_min_cov[[i]][25] <- ROS1
    } else {
      ROS1 <- paste("ROS1", "Ex", 
                   paste(exons_ROS1, collapse = ","),
                   paste0("(minimum coverage: ",min_ROS1,")"))
      output_min_cov[[i]][25] <- ROS1
      }
  } else {
    output_min_cov[[i]][25] <-  ""
  }
  
  if ("STK11" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_STK11) > 10) {
      STK11 <- paste("STK11", paste0("(minimum coverage: ",min_STK11,")"))
      output_min_cov[[i]][26] <- STK11
    } else {
      STK11 <- paste("STK11", "Ex", 
                    paste(exons_STK11, collapse = ","),
                    paste0("(minimum coverage: ",min_STK11,")"))
      output_min_cov[[i]][26] <- STK11
      }
  } else {
    output_min_cov[[i]][26] <-  ""
  }
  
  if ("TP53" %in% unlist(str_split(string=name_exon_mincov[[i]],
                                   pattern=" "))) {
    if (length(exons_TP53) > 10) {
      TP53 <- paste("TP53", paste0("(minimum coverage: ",min_TP53,")"))
      output_min_cov[[i]][27] <- TP53
    } else {
      TP53 <- paste("TP53", "Ex", 
                    paste(exons_TP53, collapse = ","),
                    paste0("(minimum coverage: ",min_TP53,")"))
      output_min_cov[[i]][27] <- TP53
      }
  } else {
    output_min_cov[[i]][27] <-  ""
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
saveWorkbook(wb, "debug_Lunge.xlsx",
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
ENST_NM_number_dict <- c("ENST00000389048"="NM_004304",
                         "ENST00000288602" = "NM_004333",
                         "ENST00000349496" = "NM_001904",
                         "ENST00000275493" = "NM_005228",
                         "ENST00000269571" = "NM_004448",
                         "ENST00000447712" = "NM_023110",
                         "ENST00000358487" = "NM_000141",
                         "ENST00000457416" = "NM_022970",
                         "ENST00000440486" = "NM_000142",
                         "ENST00000292408" = "NM_213647",
                         "ENST00000311189" = "NM_005343",
                         "ENST00000345146" = "NM_005896",
                         "ENST00000330062" = "NM_002168",
                         "ENST00000171111" = "NM_203500",
                         "ENST00000256078" = "NM_033360",
                         "ENST00000307102" = "NM_002755",
                         "ENST00000397752" = "NM_001127500",
                         "ENST00000369535" = "NM_002524",
                         "ENST00000524377" = "NM_002529",
                         "ENST00000277120" = "NM_006180",
                         "ENST00000360948" = "NM_001012338",
                         "ENST00000263967" = "NM_006218",
                         "ENST00000371953" = "NM_000314",
                         "ENST00000355710" = "NM_020975",
                         "ENST00000368508" = "NM_002944",
                         "ENST00000326873" = "NM_000455",
                         "ENST00000269305" = "NM_000546")

valid_ENST <- c("ENST00000389048", "ENST00000288602", "ENST00000349496",
                "ENST00000275493", "ENST00000269571", "ENST00000447712",
                "ENST00000358487", "ENST00000457416", "ENST00000440486",
                "ENST00000292408", "ENST00000311189", "ENST00000345146",
                "ENST00000330062", "ENST00000171111", "ENST00000256078", 
                "ENST00000307102", "ENST00000397752", "ENST00000369535", 
                "ENST00000524377", "ENST00000277120", "ENST00000360948", 
                "ENST00000263967", "ENST00000371953", "ENST00000355710", 
                "ENST00000368508", "ENST00000326873", "ENST00000269305") 

# Global variables
sorted_unfil_sheets <- list()
merged_sorted_unfil_sheets <- list()
ENST_msu_sheets <- list()
ENST_msu_sheets_converted <- list()
NM_numbers_msu <- vector(mode = "list", length = max(1,number_all_sheets/3))
mut_msu_sheets <- list()
NM_mut_msu <- list()
msu_ENST <- list()
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

  # Getting ENST numbers without .xx
  ENST_msu_sheets[[i]] <-
    merged_sorted_unfil_sheets[[i]]$`Coding region change in longest transcript`
  ENST_msu_sheets_converted[[i]] <- gsub("\\:.*","",ENST_msu_sheets[[i]])
  
  # Getting corresponding NM_numbers
  index <- 0
  for (j in unlist(ENST_msu_sheets_converted[[i]])) {
    index <- index + 1
    if (ENST_msu_sheets_converted[[i]][index] %in% valid_ENST) {
        if (is.na(ENST_msu_sheets_converted[[i]][index])) {
          NM_numbers_msu[[i]][index] <- "NA"
        }
        else {
          NM_numbers_msu[[i]][index] <- ENST_NM_number_dict[[j]][1]
        }
    }
    else {
      NM_numbers_msu[[i]][index] <- "NA"
    }
  }

  # Getting mutations
  mut_msu_sheets[[i]] <- gsub(".*\\:",":",ENST_msu_sheets[[i]])

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
  index_clinvar_info <- 0
  for (k in seq_along(NM_mut_msu[[i]][seq(last_index_above_1_msu-1)])) {
    
    index_clinvar_info <- index_clinvar_info + 1
    
    if (!is.na(ENST_msu_sheets[[i]][index_clinvar_info])) {
      
        ClinVar_search <-entrez_search(db="ClinVar", term=NM_mut_msu[[i]][k])

        for (l in seq(ClinVar_search$count)) {

          if (ClinVar_search$count >= 1) {

            lst_clinvar_msu <- c()
            output_Clinvar_msu <- c()
            clinVar_summary <- entrez_summary(db="ClinVar",
                                              id = ClinVar_search$ids[l])
            clingicalsignificane <- clinVar_summary$clinical_significance
            description <- clingicalsignificane$description
            lst_clinvar_msu <- append(lst_clinvar_msu, description)
            output_Clinvar_msu <- paste(lst_clinvar_msu, collapse = ",")
          } else {
            lst_clinvar_msu <- c()
            output_Clinvar_msu <- c()
            lst_clinvar_msu <- append(lst_clinvar_msu, "not provided")
            output_Clinvar_msu <- paste(lst_clinvar_msu, collapse = ",")
          }
        }
        result_clinvar_msu[[i]][k] <- output_Clinvar_msu
    } else {
      lst_clinvar_msu <- c()
      output_Clinvar_msu <- c()
      lst_clinvar_msu <- append(lst_clinvar_msu, "not provided")
      output_Clinvar_msu <- paste(lst_clinvar_msu, collapse = ",")
      result_clinvar_msu[[i]][k] <- output_Clinvar_msu
    }
  }

  msu_ENST[[i]]$`ClinVar`[seq(last_index_above_1_msu-1)] <-
    result_clinvar_msu[[i]]

    # Getting indexes of variants defined as P, P/LP, VUS, unklar, B/LB, B and
  # Conflicting interpretations of pathogenicity (CI)
  index_pathogenic_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Pathogenic")
  
  index_pathogenic_drugresponse_other_msu <-
    which(msu_ENST[[i]]$`ClinVar`=="Pathogenic; drug response; other")
  
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
  
  colour_pathogenic_drugresponse_other_msu <- createStyle(textDecoration = "bold")

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
           rows =  index_pathogenic_drugresponse_other_msu+1,
           style= colour_pathogenic_drugresponse_other_msu, gridExpand = TRUE, 
           stack = TRUE)
  
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

  # Highlight ID SNPs
  
  index_ID_SNP_msu <- which(str_detect(string = msu_ENST[[i]]$`Wertung`, 
                                       pattern = "ID SNP*") == TRUE)
  
  colour_ID_SNP_msu <- createStyle(fontColour = "#a2e63c")
  
  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = seq(colnames(msu_ENST[[i]])),
           rows =  index_ID_SNP_msu+1,
           style= colour_ID_SNP_msu, gridExpand = TRUE, stack=TRUE)
  
   writeData(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
            x = msu_ENST[[i]], 
            startCol = 1, startRow = 1, colNames = TRUE, headerStyle = header)
}

# Save current workbook
saveWorkbook(wb, "debug_Lunge.xlsx",
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

  # Getting ENST numbers without .xx
  ENST_msf_sheets[[i]] <-
    merged_sorted_fil_sheets[[i]]$`Coding region change in longest transcript`
  ENST_msf_sheets_converted[[i]] <- gsub("\\:.*","",ENST_msf_sheets[[i]])

  # Getting corresponding NM_numbers
  index <- 0
  for (j in unlist(ENST_msf_sheets_converted[[i]])) {
    index <- index + 1
    NM_numbers_msf[[i]][index] <- ENST_NM_number_dict[[j]][1]
  }

  # Getting mutations
  mut_msf_sheets[[i]] <- gsub(".*\\:",":",ENST_msf_sheets[[i]])

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

    for (l in seq(ClinVar_search$count)) {

      if (ClinVar_search$count >= 1) {

        lst_clinvar <- c()
        output_Clinvar <- c()
        clinVar_summary <- entrez_summary(db="ClinVar", id = ClinVar_search$ids[l])
        clingicalsignificane <- clinVar_summary$clinical_significance
        description <- clingicalsignificane$description
        lst_clinvar <- append(lst_clinvar, description)
        output_Clinvar <- paste(lst_clinvar, collapse = ",")
      } else {
        lst_clinvar <- c()
        output_Clinvar <- c()
        lst_clinvar <- append(lst_clinvar, "not provided")
        output_Clinvar <- paste(lst_clinvar, collapse = ",")
      }
    }
    result_clinvar_msf[[i]][k] <- output_Clinvar

  }

  msf_ENST[[i]]$`ClinVar` <- result_clinvar_msf[[i]]

  # Getting indexes of variants defined as P, P/LP, US, unklar, B/LB, B and
  # Conflicting interpretations of pathogenicity (CI)

  index_pathogenic <-
  which(msf_ENST[[i]]$`ClinVar`=="Pathogenic")
  
  index_pathogenic_drugresponse_other <-
    which(msf_ENST[[i]]$`ClinVar`=="Pathogenic; drug response; other")
  
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
  
  colour_pathogenic_drugresponse_other <- createStyle(textDecoration = "bold")

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
           rows =  index_pathogenic_drugresponse_other+1,
           style= colour_pathogenic_drugresponse_other, gridExpand = TRUE, 
           stack=TRUE)
  
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

  # Highlight ID SNPs
  
  index_ID_SNP <- which(str_detect(string = msf_ENST[[i]]$`Wertung`, 
                                       pattern = "ID*") == TRUE)
  
  colour_ID_SNP <- createStyle(fontColour = "#7d8079")
  
  addStyle(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
           cols = seq(colnames(msf_ENST[[i]])),
           rows = index_ID_SNP+1,
           style= colour_ID_SNP, gridExpand = TRUE, stack=TRUE)
  
  writeData(wb = wb, sheet = names_all_sheet[index_filtered_sheets][i],
            x = msf_ENST[[i]],
            startCol = 1, startRow = 1, colNames = TRUE, headerStyle = header)

}

# Save current workbook
saveWorkbook(wb, "debug_Lunge.xlsx",
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

# Save current workbook
saveWorkbook(wb, "debug_Lunge.xlsx",
             overwrite = TRUE)


# Display runtime
end_time <- Sys.time()
process_time_difference <- round(end_time-time_start, 2)
process_time <- format(process_time_difference)
print(paste("Process time:", process_time))





