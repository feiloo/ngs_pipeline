sample_size_targets = {
    'brcaness_mass': 60., # nanogram
    'brcaness_volume': 16.75, # microliter maximum
    'DNA_mass': 40., # nanogram
    'DNA_volume': 16.75, # microliter maximum
    'RNA_mass': 150., # nanogram
    'RNA_volume': 5., # microliter maximum
}


READS = [231, 151]
ADAPTER = 'CTGTCTCTTATACACATCT'


# fake example todo
untersuchung_kit_map = {
        "oncohs": "DNA 999"
        }

schema = [
     'lf_Untersuchung_ID',
     'Zeitstempel',
     'Mol_NR',
     'FISH_ NR',
     'Kürzel',
     'Nummer',
     'Jahr',
     'Block_NR',
     'Untersuchung',
     'Befunder',
     'Ergebnis',
     'Zeitstempel_ Ergebnis',
     'ADR1::DBCKOMFORT',
     'Vorname',
     'Name',
     'GBD',
     'Abrechnungsziffer',
     'Bemerkung',
     'Erledigt_Abrechnung',
     'Barcode',
     'global_lokal::next Mol Nr',
     'global_lokal::Untersuchung',
     'global_lokal::next FISH Nr',
     'DBCARZTORG',
     'DBCARZTKOP',
     'Kürzel_JK_MT',
     'Kürzel_Erfassung',
     'global_lokal::gl_Kuerzel_Erfasser',
     'global_lokal::gl_Befunder',
     'global_lokal::gl_Jahr',
     'Barcode_automatisch',
     'Geschlecht',
     'Leerschnitte',
     'TZAnteil',
     'Markierer',
     'Diagnose',
     'Primarius_Metastase',
     'Lokalisation',
     'ICD10',
     'ICD03']



filemaker_examination_types_workflow_mapping = {
        'DNA Lungenpanel Qiagen - kein nNGM Fall':'NGS_dna_loung',
        'DNA Panel ONCOHS': 'NGS oncoHS',
        'DNA PANEL ONCOHS (Mamma)': 'NGS_oncohs', # basically calls ONCOHS,
        'DNA PANEL ONCOHS (Melanom)': 'NGS_oncohs',# basically calls ONCOHS
        'DNA PANEL ONCOHS (Colon)': 'NGS_oncohs',# basically calls ONCOHS
        'DNA PANEL ONCOHS (GIST)': 'NGS_oncohs',# basically calls ONCOHS
        'DNA PANEL 522': None, # research panel
        'DNA PANEL Multimodel PanCancer DNA': None,
        'DNA PANEL Multimodel PanCancer RNA': None,
        'NNGM Lunge Qiagen': 'NGS_dna_loung',
        'RNA Fusion Lunge': 'NGS_rna_fusion_loung',
        'RNA Sarkompanel': None,
        }


workflow_paths_wdl = {
    'NGS_dna_lungenpanel': '/data/ngs_pipeline/workflow/wdl/test.wdl',
    'NGS_oncohs' : '/data/ngs_pipeline/workflow/wdl/test.wdl',
    'NGS_brcaness': '/data/ngs_pipeline/workflow/wdl/test.wdl',
    'NGS_rna_sarkom': '/data/ngs_pipeline/workflow/wdl/test.wdl',
    'NGS_rna_fusion_Lunge': '/data/ngs_pipeline/workflow/wdl/test.wdl',
    'NGS_pancancer': '/data/ngs_pipeline/workflow/wdl/test.wdl',
    'NGS_dna_loung': '/data/ngs_pipeline/workflow/wdl/test.wdl',
    }

workflow_paths_nextflow = {
    'NGS_dna_loung': '/opt/cio/variantinterpretation'
    }

workflow_paths_clc = {}

workflow_impls = {
    'clc': workflow_paths_clc,
    'nextflow': workflow_paths_nextflow,
    'wdl': workflow_paths_wdl,
    'noop': 'noop',
    }
