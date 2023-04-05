from datetime import datetime
from pyparsing import Word, nums, alphas, alphanums, one_of, Combine, Opt, Literal

#fastq_name_example = '1111-11_S11_L001_R1_001.fastq.gz'
fastq_name = (
        Combine(Word(nums, exact=4) + '-' 
            + Word(nums, exact=2))('sample_name') + Opt(Literal('-wdh')) + '_'
        + Word('S', nums, min=2,max=3)('sample_number') + '_'
        + Word('L', nums, exact=4)('lane_number') + '_'
        + Combine('R' + one_of(list('12')))('read')
        + "_001.fastq.gz"
        )
    

#see illumina fastq naming convention
# https://support.illumina.com/help/BaseSpace_OLH_009008/Content/Source/Informatics/BS/NamingConvention_FASTQ-files-swBS.htm
def parse_fastq_name(name):
    return fastq_name.parse_string(name).as_dict()

#miseq_name_example = '220101_M01011_0111_000000000-A11A1'
miseq_name = (
    Word(nums, exact=6)('date') + '_'
    + Word('M', nums, exact=6)('device') + '_'
    + Word(nums, exact=4)('run_number') + "_"
    + Combine(Word(nums, exact=9) + '-'
        + Word(alphanums, exact=5))('flowcell_barcode')
    )

# the default naming scheme is
# YYMMDD_<InstrumentNumber>_<Run Number>_<FlowCellBarcode>
# see illumina: miseq-system-guide-15027617-06-1.pdf
# page 44 Appendix B output Files and Folders
def parse_miseq_run_name(name):
    return miseq_name.parse_string(name).as_dict()


def parse_date(datestr):
    return datetime.strptime(datestr, '%m/%d/%Y')
