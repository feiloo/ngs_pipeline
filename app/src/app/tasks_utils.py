import time

class Timeout:
    def __init__(self, seconds):
        self.starttime = time.time()
        self.length = seconds

    def reached(self):
        return time.time() > (self.starttime + self.length)

class Schedule:
    def __init__(self, db):
        self.db = db

    def acquire_lock(self):
        app_state = self.db.get('app_state')
        if app_state['sync_running'] == True:
            logger.debug('sync already running')
            raise RuntimeError()
        else:
            logger.debug('sync not running, acquiring sync state')
            app_state['sync_running'] = True
            self.db.save(app_state)

    def release_lock(self):
        app_state = self.db.get('app_state')
        #app_state['sync_running'] = False
        self.db.save(app_state)

    def is_enabled(self):
        default_app_settings = {
            '_id':'app_settings',
            'schedule': '',
            'autorun_pipeline':False
        }

        settings = self.db.get('app_settings')
        return settings['autorun_pipeline'] == True


    def has_work_now(self):
        settings = self.db.get('app_settings')
        return settings['schedule'] == ''
