from 

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
