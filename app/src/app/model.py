from typing import Optional, Literal, List
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from uuid import UUID
import json

''' contains classes for the data model and for domain actors '''

DATA_MODEL_VERSION = '0.0.1'
ACTOR_MODEL_VERSION = DATA_MODEL_VERSION

# first the data model

# based on the ordercodes of "NGS_Panel_Abdeckung_MolPath.docx"
panel_types = [
        'invalid', 
        'NGS DNA Lungenpanel', 
        'NGS oncoHS', 
        'NGS BRCAness', 
        'NGS RNA Sarkom', 
        'NGS RNA Fusion Lunge', 
        'NGS PanCancer'
        ]

PanelType = Literal[
        'invalid', 
        'NGS DNA Lungenpanel', 
        'NGS oncoHS', 
        'NGS BRCAness', 
        'NGS RNA Sarkom', 
        'NGS RNA Fusion Lunge', 
        'NGS PanCancer'
        ]

# examination identifiers used in filemaker
filemaker_examination_types = [
        'DNA Lungenpanel Qiagen - kein nNGM Fall',
        'DNA Panel ONCOHS',
        'DNA PANEL ONCOHS (Mamma)', # basically calls ONCOHS,
        'DNA PANEL ONCOHS (Melanom)',# basically calls ONCOHS
        'DNA PANEL ONCOHS (Colon)',# basically calls ONCOHS
        'DNA PANEL ONCOHS (GIST)',# basically calls ONCOHS
        'DNA PANEL 522', # research panel
        'DNA PANEL Multimodel PanCancer DNA',
        'DNA PANEL Multimodel PanCancer RNA',
        'NNGM Lunge Qiagen',
        'RNA Fusion Lunge',
        'RNA Sarkompanel',
        'BRCANess Qiagen'
        ]


class BaseDocument(BaseModel):
    id: str 
    rev: Optional[str] = None
    data_model_version: str = DATA_MODEL_VERSION
    document_type: str
    dirty: bool = True
    ignore_dirty: bool = False

    class Config:
        validate_assignment = True
        frozen = True


class PipelineLogs(BaseModel):
    stdout: str
    stderr: str


class PipelineRun(BaseDocument):
    document_type: str = 'pipeline_run'
    created_time: datetime
    input_samples: List[Path]
    workflow: str
    panel_type: str
    status: Literal['created', 'paused', 'running', 'error', 'aborted', 'successful']
    logs: PipelineLogs


class SequencerRun(BaseDocument):
    document_type: str = 'sequencer_run'
    original_path: Path
    name_dirty: bool
    parsed: dict
    indexed_time: datetime
    state: str = 'unfinished'
    outputs: List[Path]


class SampleBlock(BaseDocument):
    patient_ref: int

class SampleCuts(BaseDocument):
    block_ref: int

class SampleExtraction(BaseDocument):
    sample_cut_ref: int
    molnr: str

class SequencerInputSample(BaseDocument):
    document_type: str = 'sequencer_input_sample'
    kit: str
    molnr: str # references sample-extraction
    concentration: float
    index1: str
    index2: str
    sample_volume: float
    sample_water: float
    final: bool = False
    repetition: bool = False


class MolYearNumber(BaseModel):
    molnumber: int
    molyear: int


class Examination(BaseDocument):
    ''' medical examination/case '''
    document_type: str = 'examination'
    examinationtype: str
    #examination_requester: Union[Literal['internal'], str]
    started_date: datetime
    sequencer_runs: List[str]
    pipeline_runs: List[str]
    filemaker_record: Optional[dict] = None
    last_sync_time: Optional[datetime] = None
    result: Optional[str] = None
    patient: Optional[str] = None

    
class Person(BaseDocument):
    names: dict[str,str]

class Patient(Person):
    document_type: str = 'patient'
    #mp_nr: str
    examinations: List[str]
    birthdate: Optional[datetime]
    gender: str

class Pathologist(Person):
    short_name: str

class Clinician(Person):
    short_name: str

class Result(BaseModel):
    description: str

document_class_map = {
        'sequencer_run': SequencerRun, 
        'pipeline_run': PipelineRun, 
        'examination': Examination, 
        'patient': Patient
        }


# below are the domain actors
# atm just unused stubs

class Pipeline:
    def __init__(self, db, config, backend):
        self.db = db
        self.config = config
        self.filemaker = filemaker

    def checkpoint(self):
        pass

    def run(self):
        pass

class Workflow:
    pass

class Sequencer:
    def scan_output_files(self):
        pass

class Examination:
    def __init__(self, *args, **kwargs):
        pass

    def link_to_sequencer_run(self, sequencer_run):
        pass
