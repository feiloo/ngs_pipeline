from app.model import document_types


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
    def __init__(self, *args, *kwargs):
        pass

    def link_to_sequencer_run(self, sequencer_run):
        pass
