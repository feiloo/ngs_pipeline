from typing import Optional, Literal, List
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import json

runformat: ['miseq_0', 'only_fastq']

DATA_MODEL_VERSION = '0.0.1'

# based on the ordercodes of "NGS_Panel_Abdeckung_MolPath.docx"
panel_types = [
        'unset', 
        'NGS DNA Lungenpanel', 
        'NGS oncoHS', 
        'NGS BRCAness', 
        'NGS RNA Sarkom', 
        'NGS RNA Fusion Lunge', 
        'NGS PanCancer'
        ]
PanelType = Literal[
        'unset', 
        'NGS DNA Lungenpanel', 
        'NGS oncoHS', 
        'NGS BRCAness', 
        'NGS RNA Sarkom', 
        'NGS RNA Fusion Lunge', 
        'NGS PanCancer'
        ]

primerMixes = {
        'C1': {
            'panel type': 'unknown',
            'primers': [],
            }
        }


class BaseDocument(BaseModel):
    id: Optional[str]
    rev: Optional[str]
    data_model_version: str = DATA_MODEL_VERSION
    document_type: str

    def to_dict(self):
        # convert to serializable dict
        d = json.loads(self.json())
        d.pop('id')
        d.pop('rev')
        if self.id is not None:
            d['_id'] = self.id
        if self.rev is not None:
            d['_rev'] = self.rev
        return d

    def from_dict(self, d):
        if '_id' in d:
            d['id'] = d.pop('_id')
        if '_rev' in d:
            d['rev'] = d.pop('_rev')
        m = type(self)(**d)
        return m

class PipelineLogs(BaseModel):
    stdout: str
    stderr: str

class PipelineRun(BaseDocument):
    document_type: str = 'pipeline_run'
    created_time: datetime
    input_samples: List[Path]
    workflow: str
    sequencer_run: Path
    status: str
    logs: PipelineLogs

class SequencerRun(BaseDocument):
    document_type: str = 'sequencer_run'
    original_path: Path
    name_dirty: bool
    parsed: dict
    indexed_time: datetime
    state: str = 'unfinished'
    # a targeted sequencer run, is always related to a single type of diagnostic panel
    # this is needed to later choose the right workflow
    panel_type: PanelType

class MolYearNumber(BaseModel):
    molnumber: int
    molyear: int

class Examination(BaseModel):
    ''' medical examination '''
    examinationtype: str

class Person(BaseModel):
    name: str
    surname: str

class Patient(Person):
    mp_nr: str
    examinations: list
    birthdate: datetime
    gender: str

class Pathologist(Person):
    name: str
    short_name: str


#we need to create different taxonomical concepts for "workflow"
# patho_workflow is the generalization of a ngs_panel 
# that also includes manual steps like library preparation
# this will be modeled by the according manual descriptions
# versioned and available
# in human readable form like html, pdf, word

# sequence_analysis_workflow is the workflow that specifically
# uses code in wdl format to automatically analyse mutations

# model for a pathology examination

# steps can be repeated, if for example samples are contaminated

# step started and finished are usefull, because multiple steps 
# could run concurrently
'''
database_stub = [
        {
        "_id": "1",
        "case_ref": {
            "molnr":2132, 
            "year":2022, 
            "examinationtype":"oncohs",
            },
        "workflow": {
            "patho_workflow_uri": "uri",
            "steps": [
                {   "step_id": "patho_workflow_step_pipetting",
                    "step_data": {
                        "kit":"rna 340",
                        "original_concentration (ng/ul)":116.0, 
                        "diluted aqua (ul)":3.71, 
                        "index1":"IL-N728",
                        "index2":"IL-S502",
                        },
                    "step_started": "date",
                    "step_finished": "date",
                },
                {
                    "step_id": "patho_workflow_step_validate_pipetting"
                    "step_started": "date",
                    "step_finished": "date",
                },
                {   "step_id": "patho_workflow_step_pipetting_repeat",
                    "step_data": {
                        "original_concentration (ng/ul)":116.0, 
                        "diluted aqua (ul)":3.71, 
                        "repitition": 1,
                        },
                    "step_started": "date",
                    "step_finished": "date",
                },
                {   "step_id": "sequence_analysis",
                    "step_data": "..."
                    "step_started": "date",
                    "step_finished": "date",
                }
                ]
            }
        }]
'''
