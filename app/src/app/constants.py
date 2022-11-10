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
