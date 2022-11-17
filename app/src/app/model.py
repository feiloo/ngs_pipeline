import datetime

from pydantic import BaseModel

runformat: ['miseq_0', 'only_fastq']


'''
document_types:
    - pipeline_run
    - sequencer_run
    - patient_result
    - study_reference
'''

class BaseDocument(BaseModel):
    data_model_version: str
    document_type: str
    #pipeline_version: str
    #workflow_version: str


class MolYearNumber(BaseModel):
    molnumber: int
    molyear: int

class MiSeqRunOutputRef(BaseModel):
    # the path on the PAT sequencer NAS
    path: str
    samplesheet: str
    fastq: list #[str]
    has_logs: bool

class TrackingFormLine(BaseModel):
    row_number: int
    kit: str
    molnr: str
    concentration: float
    index1: str
    index2: str
    probe: float
    aqua: float

class TrackingForm(BaseModel):
    date: datetime.datetime
    #lines: list[TrackingFormLine]


class Examination(BaseModel):
    ''' medical examination '''
    examinationtype: str # u_type
    ''' one of oncohs, ... '''

class Person(BaseModel):
    name: str
    surname: str

class Patient(Person):
    mp_nr: str
    examinations: list
    birthdate: datetime.datetime
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
