from pyparsing import Word, nums, alphas, alphanums, one_of

fastq_name = Word(nums, exact=4)+'-'+Word(nums,exact=2)+'_S'+Word(nums, min=1,max=2)+"_L001_R"+one_of(list('12'))+"_001.fastq.gz"
    
teststr = '1111-11_S11_L001_R1_001.fastq.gz'

def parse_fastq_name(name):
    return fastq_name.parse_string(teststr)

tokens = parse_fastq_name(teststr)
molnumber = tokens[0]
    # parses the fastq filename



teststr = '220101_M01011_0111_000000000-A11A1'
miseq_name = Word(nums, exact=6)+'_M'+Word(nums, exact=5)+'_'+Word(nums, exact=4)+"_"+Word(nums, exact=9)+'-'+Word(alphanums, exact=5)

def parse_miseq_run_name(name):
    return miseq_name.parse_string(name)

parse_miseq_run_name(teststr)

# the default naming scheme is
# YYMMDD_<InstrumentNumber>_<Run Number>_<FlowCellBarcode>
# see illumina: miseq-system-guide-15027617-06-1.pdf
# page 44 Appendix B output Files and Folders
def parse_run_output_name(name):
    try:
        datestr, instrument_number, run_number, flow_cell_barcode = name.split('_')

        date = datetime.strptime('%y%m%d')
        d = {
            "date":date,
            "instrument_number": instrument_number,
            "run_number": run_number,
            "flow_cell_barcode": flow_cell_barcode
            }

    except:
        raise RuntimeError('incorrect miseq run root folder name')

    return d

