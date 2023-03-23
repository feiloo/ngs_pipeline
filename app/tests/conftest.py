import pytest

from app.constants import testconfig

@pytest.fixture(scope='session')
def config():
    return testconfig

''' sythetic example record
'''
fm_record = {'fieldData': {
        'lf_Untersuchung_ID': 49999, 
        'Zeitstempel': '12/24/2020', 
        'Mol_NR': 4000, 
        'FISH_ NR': '', 
        'Kürzel': 'E ', 
        'Nummer': 18000, 
        'Jahr': 2020, 
        'Block_NR': 'XX X0.0.0X', 
        'Untersuchung': 'BRAF Ex11', 
        'Befunder': 'X', 
        'Ergebnis': '', 
        'Zeitstempel_ Ergebnis': '', 
        'ADR1::DBCKOMFORT': '', 
        'Vorname': '',
        'Name': '',
        'GBD': '12/24/2020',
        'Abrechnungsziffer': '',
        'Bemerkung': '',
        'Erledigt_Abrechnung': 'nein',
        'Barcode': 'E 00.00000',
        'global_lokal::next Mol Nr': 4021,
        'global_lokal::Untersuchung': 'XXXX',
        'global_lokal::next FISH Nr': 0,
        'DBCARZTORG': '',
        'DBCARZTKOP': '', 
        'Kürzel_JK_MT': '',
        'Kürzel_Erfassung': 'XX',
        'global_lokal::gl_Kuerzel_Erfasser': 'XX',
        'global_lokal::gl_Befunder': '',
        'global_lokal::gl_Jahr': '20',
        'Barcode_automatisch': 'E 1111111',
        'Geschlecht': 'M',
        'Leerschnitte': 3,
        'TZAnteil': 80,
        'Markierer': 'XX',
        'Diagnose': '',
        'Primarius_Metastase': '',
        'Lokalisation': '',
        'ICD10': '',
        'ICD03': ''
        },
    'portalData': {},
    'recordId': '40000',
    'modId': '9'
    }

@pytest.fixture()
def filemaker_testdata():
    return fm_record

class FilemakerMock:
    def __init__(self, *args, **kwargs):
        pass

    def get_all_records(self, offset, limit=1000):
        print(f'offset: {offset}')
        if offset > 50000:
            raise RuntimeError('offset in filemaker mock reached all documents')
        return {'data': [fm_record]}

@pytest.fixture()
def fm_mock():
    return FilemakerMock()
