################################################################################
# Script to sort, filter and assess CLC Genomics Workbench Data - BRACness Panel
# Version: v3
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
command_list = list(
  make_option(c("-f", "--file"), type="character", default = NULL),
  make_option(c("-n", "--name"), type="character", default= NULL)
)
opt_parser = OptionParser(option_list=command_list)
opt = parse_args(opt_parser)

# Setting path and getting filename
cwd <- here()
path_to_data <- cwd
filename <- paste("/", opt$file, sep="")

# Date and time for log file
print(paste("Date:", time_start))

# Show command in log file
print(paste("File:", opt$file))
print("Rscript: BRCAness_v3.R")
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
rename_sheets <- substr(names_all_sheet, start = 1, stop = 8)

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

# Exon_table BRCAness panel
exon_table <- read_excel(paste(cwd,"/exontable.xlsx",
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

  exons_HDAC2 <- c()
  exons_ATM <- c()
  exons_BRCA2 <- c()
  exons_PALB2 <- c()
  exons_FANCA <- c()
  exons_CDK12 <- c()
  exons_BRCA1 <- c()
  exons_CHEK2 <- c()
  
  min_HDAC2 <- 100
  min_ATM <- 100
  min_BRCA2 <- 100
  min_PALB2 <- 100
  min_FANCA <- 100
  min_CDK12 <- 100
  min_BRCA1 <- 100
  min_CHEK2 <- 100
  
  count_HDAC2 <- 0
  count_ATM <- 0
  count_BRCA2 <- 0
  count_PALB2 <- 0
  count_FANCA <- 0
  count_CDK12 <- 0
  count_BRCA1 <- 0
  count_CHEK2 <- 0
  
  for (j in seq(name_exon_mincov[[i]])) {
    splitted <- 
      unlist(str_split(string = name_exon_mincov[[i]][j], pattern = " "))
    
    if ("HDAC2" %in% splitted) {
      count_HDAC2 <- count_HDAC2 + 1
      exons_HDAC2 <- append(exons_HDAC2, splitted[3])
      min_cov_HDAC2 <- as.double(splitted[4])
      if (min_cov_HDAC2 < min_HDAC2) {
        min_HDAC2 <- min_cov_HDAC2
        num_HDAC2 <- paste0("(",min_HDAC2 ,")")
      }
    } else if ("ATM" %in% splitted) {
      count_ATM <- count_ATM + 1
      exons_ATM <- append(exons_ATM, splitted[3])
      min_cov_ATM <- as.double(splitted[4])
      if (min_cov_ATM <  min_ATM) {
        min_ATM <- min_cov_ATM
        num_ATM <- paste0("(",min_ATM ,")")
      }
    } else if ("BRCA2" %in% splitted) {
      count_BRCA2 <- count_BRCA2 + 1
      exons_BRCA2 <- append(exons_BRCA2, splitted[3])
      min_cov_BRCA2 <- as.double(splitted[4])
      if (min_cov_BRCA2 <  min_BRCA2) {
        min_BRCA2 <- min_cov_BRCA2
        num_BRCA2 <- paste0("(",min_BRCA2 ,")")
      }
    } else if ("PALB2" %in% splitted) {
      count_PALB2 <- count_PALB2 + 1
      exons_PALB2 <- append(exons_PALB2, splitted[3])
      min_cov_PALB2 <- as.double(splitted[4])
      if (min_cov_PALB2 <  min_PALB2) {
        min_PALB2 <- min_cov_PALB2
        num_PALB2 <- paste0("(",min_PALB2 ,")")
      }
    } else if ("FANCA" %in% splitted) {
      count_FANCA <- count_FANCA + 1
      exons_FANCA <- append(exons_FANCA, splitted[3])
      min_cov_FANCA <- as.double(splitted[4])
      if (min_cov_FANCA <  min_FANCA) {
        min_FANCA <- min_cov_FANCA
        num_FANCA <- paste0("(",min_FANCA ,")")
      }
    } else if ("CDK12" %in% splitted) {
      count_CDK12 <- count_CDK12 + 1
      exons_CDK12 <- append(exons_CDK12, splitted[3])
      min_cov_CDK12 <- as.double(splitted[4])
      if (min_cov_CDK12 <  min_CDK12) {
        min_CDK12 <- min_cov_CDK12
        num_CDK12 <- paste0("(",min_CDK12 ,")")
      }
    } else if ("BRCA1" %in% splitted) {
      count_BRCA1 <- count_BRCA1 + 1
      exons_BRCA1 <- append(exons_BRCA1, splitted[3])
      min_cov_BRCA1 <- as.double(splitted[4])
      if (min_cov_BRCA1 <  min_BRCA1) {
        min_BRCA1 <- min_cov_BRCA1
        num_BRCA1 <- paste0("(",min_BRCA1 ,")")
      }
    } else if ("CHEK2" %in% splitted) {
      count_CHEK2 <- count_CHEK2 + 1
      exons_CHEK2 <- append(exons_CHEK2, splitted[3])
      min_cov_CHEK2 <- as.double(splitted[4])
      if (min_cov_CHEK2 <  min_CHEK2) {
        min_CHEK2 <- min_cov_CHEK2
        num_CHEK2 <- paste0("(",min_CHEK2 ,")")
      }
    }
  }
 
  if ("HDAC2" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                    pattern=" "))) {
    if (length(exons_HDAC2) > 10) {
        HDAC2 <- paste("HDAC2", paste0("(",min_HDAC2,")"))
        output_min_cov[[i]][1] <-  HDAC2
    } else {
        HDAC2 <- paste("HDAC2", "Ex", paste(exons_HDAC2, collapse = ","), 
                     paste0("(",min_HDAC2,")"))
        output_min_cov[[i]][1] <-  HDAC2
      }
  } else {
      output_min_cov[[i]][1] <-  ""
  }
  
  if ("ATM" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                    pattern=" "))) {
    if (length(exons_ATM) > 10) {
        ATM <- paste("ATM", paste0("(",min_ATM,")"))
        output_min_cov[[i]][2] <-  ATM
    } else {
        ATM <- paste("ATM", "Ex", paste(exons_ATM, collapse = ","), 
                    paste0("(",min_ATM,")"))
        output_min_cov[[i]][2] <-  ATM
      }
  } else {
    output_min_cov[[i]][2] <-  ""
  }
  
  if ("BRCA2" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                  pattern=" "))) {
    if (length(exons_BRCA2) > 10) {
      BRCA2 <- paste("BRCA2", paste0("(",min_BRCA2,")"))
      output_min_cov[[i]][3] <-  BRCA2
    } else {
      BRCA2 <- paste("BRCA2", "Ex", paste(exons_BRCA2, collapse = ","), 
                   paste0("(",min_BRCA2,")"))
      output_min_cov[[i]][3] <-  BRCA2
    }
  } else {
    output_min_cov[[i]][3] <-  ""
  }
  
  if ("PALB2" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                    pattern=" "))) {
    if (length(exons_PALB2) > 10) {
      PALB2 <- paste("PALB2", paste0("(",min_PALB2,")"))
      output_min_cov[[i]][4] <-  PALB2
    } else {
      PALB2 <- paste("PALB2", "Ex", paste(exons_PALB2, collapse = ","), 
                     paste0("(",min_PALB2,")"))
      output_min_cov[[i]][4] <-  PALB2
    }
  } else {
    output_min_cov[[i]][4] <-  ""
  }
  
  if ("FANCA" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                    pattern=" "))) {
    if (length(exons_FANCA) > 10) {
      FANCA <- paste("FANCA", paste0("(",min_FANCA,")"))
      output_min_cov[[i]][5] <-  FANCA
    } else {
      FANCA <- paste("FANCA", "Ex", paste(exons_FANCA, collapse = ","), 
                     paste0("(",min_FANCA,")"))
      output_min_cov[[i]][5] <-  FANCA
    }
  } else {
    output_min_cov[[i]][5] <-  ""
  }
  
  if ("CDK12" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                    pattern=" "))) {
    if (length(exons_CDK12) > 10) {
      CDK12 <- paste("CDK12", paste0("(",min_CDK12,")"))
      output_min_cov[[i]][6] <-  CDK12
    } else {
      CDK12 <- paste("CDK12", "Ex", paste(exons_CDK12, collapse = ","), 
                     paste0("(",min_CDK12,")"))
      output_min_cov[[i]][6] <-  CDK12
    }
  } else {
    output_min_cov[[i]][6] <-  ""
  }
  
  if ("BRCA1" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                    pattern=" "))) {
    if (length(exons_BRCA1) > 10) {
      BRCA1 <- paste("BRCA1", paste0("(",min_BRCA1,")"))
      output_min_cov[[i]][7] <-  BRCA1
    } else {
      BRCA1 <- paste("BRCA1", "Ex", paste(exons_BRCA1, collapse = ","), 
                     paste0("(",min_BRCA1,")"))
      output_min_cov[[i]][7] <-  BRCA1
    }
  } else {
    output_min_cov[[i]][7] <-  ""
  }
  
  if ("CHEK2" %in% unlist(str_split(string=name_exon_mincov[[i]], 
                                    pattern=" "))) {
    if (length(exons_CHEK2) > 10) {
      CHEK2 <- paste("CHEK2", paste0("(",min_CHEK2,")"))
      output_min_cov[[i]][8] <-  CHEK2
    } else {
      CHEK2 <- paste("CHEK2", "Ex", paste(exons_CHEK2, collapse = ","), 
                     paste0("(",min_CHEK2,")"))
      output_min_cov[[i]][8] <-  CHEK2
    }
  } else {
    output_min_cov[[i]][8] <-  ""
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
saveWorkbook(wb, paste(cwd,"/output/", "output_", opt$name, "_", 
                       opt$file, sep=""),
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

# Import BRCAness Panel Referenztranskripte
reftranscript <- 
  read_excel(paste(cwd,"/Brcaness Panel Referenztranskripte.xlsx",sep=""))

# Dict of ENST numbers and corresponding NM numbers
ENST_NM_number_dict <- c("ENST00000357654"="NM_007294",
                         "ENST00000519065" = "NM_001527",
                         "ENST00000544455" = "NM_000059",
                         "ENST00000278616" = "NM_000051",
                         "ENST00000328354" = "NM_007194",
                         "ENST00000261584" = "NM_024675",
                         "ENST00000389301" = "NM_000135",
                         "ENST00000447079" = "NM_016507")

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
      NM_numbers_msu[[i]][index] <- ENST_NM_number_dict[[j]][1]
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

  # Getting indexes of variants with frequencies above 10,5,1
  last_index_above_10_msu <- max(which(msu_ENST[[i]]$Frequency > 10 & 
                                         msu_ENST[[i]]$QUAL == 200))+1
  
  last_index_above_5_msu <- max(which(msu_ENST[[i]]$Frequency > 5 & 
                                        msu_ENST[[i]]$QUAL == 200))+1
  
  last_index_above_1_msu <- max(which(msu_ENST[[i]]$Frequency < 5 & 
                                        msu_ENST[[i]]$Frequency > 1 & 
                                        msu_ENST[[i]]$QUAL == 200))+1
  
  # Underling the last variant with a frequency above 10,5,1
  underline <- createStyle(border = "bottom", borderColour = "#0f0f0f",
                           borderStyle = "thin")
  
  addStyle(wb = wb, sheet = names_all_sheet[index_unfiltered_sheets][i],
           cols = c(1, seq(colnames(msu_ENST[[i]]))+1),
           rows =  c(last_index_above_10_msu,
                     last_index_above_5_msu, last_index_above_1_msu),
           style= underline, gridExpand = TRUE, stack = TRUE)
  
  # Adding new column with default values "NA"
  msu_ENST[[i]]["ClinVar"] <- NA
  
  # Adding ClinVar information to the end of the column
  for (k in seq_along(NM_mut_msu[[i]][seq(last_index_above_1_msu-1)])) {
    
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
saveWorkbook(wb, paste(cwd,"/output/", "output_", opt$name, "_", 
                       opt$file, sep=""),
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
saveWorkbook(wb, paste(cwd,"/output/", "output_", opt$name, "_", 
                       opt$file, sep=""),
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
saveWorkbook(wb, paste(cwd,"/output/", "output_", opt$name, "_", 
                       opt$file, sep=""),
             overwrite = TRUE)

# Display runtime
end_time <- Sys.time()
process_time_difference <- round(end_time-time_start, 2)
process_time <- format(process_time_difference)
print(paste("Process time:", process_time))
            




