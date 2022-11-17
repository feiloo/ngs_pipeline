from app.constants import *

# see miseq-sample-sheet-quick-ref-guide-15028392-j.pdf for more info
sample_sheet_defaults = {
        'Workflow':'GenerateFASTQ',
        'Application': 'FASTQ Only',
        'Instrument Type': 'MiSeq',
        'Assay': 'Nextera XT',
        'Index Adapters': 'Nextera XT v2 Index Kit B',
        'Chemistry': 'Amplicon',
        'Reads': READS,
        'CustomRead1PrimerMix': 'C1',
        'ReverseComplement': 0,
        'Adapter': ADAPTER
        }

def generate_samplesheet(tracking_sheet):
    sample_sheet_values = sample_sheet_defaults
    date = tracking_sheet['date']
    sample_sheet_values['date'] = date
    sample_sheet_values['experiment_name'] = date.strftime('%d%m%Y')
    
    data = tracking_sheet['tracking']
    samples = [f"{d['molnr']},,,{d['index1']},todo,{d['index2']},todo,," for d in data]
    sample_sheet_values['samples'] = samples

    csv = render_template('samplesheet_template.csv', **sample_sheet_values)
    return csv


def read_samplesheet(path):
    # this is run on the output sample sheets, not the input
    lines = []
    with open(path, 'r') as f:
        lines = f.readlines()

    s_lines = list(map(lambda x: x.strip(), lines))
    data_offset = s_lines.index('[Data]')
    # data_offset + 1 because there is a header line
    data = lines[data_offset+1:]

    # rough sanity check
    # todo: better parsing of the samplesheets
    if data_offset < 20:
        raise RuntimeError("unexpected samplesheet format")
    if len(data) == 0:
        raise RuntimeError("unexpected samplesheet, data segment not detected")

    expected_data_header = 'Sample_ID,Description,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Sample_Plate,Sample_Well'
    if lines[data_offset+1].strip() != expected_data_header:
        raise RuntimeError('unexpected samplesheet data header, cant parse')

    mp_numbers = []

    for line in data:
        cells = line.split(',')
        sample_id, description, i7_index_id, i5_index_id = cells[0:4]
        index2, sample_project, sample_plate, sample_well = cells[4:8]

        mp_numbers.append(sample_id)

    return mp_numbers
