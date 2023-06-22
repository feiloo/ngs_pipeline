import datetime
import json
import requests
from pathlib import Path
from math import ceil
from app.model import filemaker_examination_types


class Filemaker:
    def __init__(self, server, user, psw, table_name=None, layout=None):
        self.server = server
        self.user = user
        self.psw = psw

        # todo, this is sadly needed with the current settings
        self.ssl_verify = False

        self.fm_baseurl = f"https://{self.server}/fmi/data/v1/databases"

        # use fixed table name and layout for simplicity
        if table_name is None:
            self.table_name = 'molpatho_Leistungserfassung'
        else:
            self.table_name = table_name

        if layout is None:
            self.layout = 'Leistungserfassung'
        else:
            self.layout=layout

        self.session_url = f"{self.fm_baseurl}/{self.table_name}/sessions"

        self._token_ttl = datetime.timedelta(14*1/(24*60)) # in days, around 14 minutes

        self._token = None

    @staticmethod
    def from_config(config):
        fm = Filemaker(
                config['filemaker_server'], 
                config['filemaker_user'], 
                config['filemaker_psw'])
        return fm

    def _get_new_token(self):
        r = requests.post(
                self.session_url, 
                auth=(self.user,self.psw), 
                verify=self.ssl_verify,
                headers={'Content-Type': 'application/json'})

        r.raise_for_status()
        self._token_timestamp = datetime.datetime.now()
        return r.json()['response']['token']

    @property
    def token(self):
        ''' gets a filemaker auth token, and caches it for 14 minutes
        filemaker tokens expire after 15 minutes
        '''
        if self._token is None:
            self._token = self._get_new_token()
        elif datetime.datetime.now() > self._token_timestamp + self._token_ttl:
            self._token = self._get_new_token()

        return self._token


    def logout(self):
        ''' explicitely logout of a session, instead of letting it expire after 15 minutes '''
        if self._token is not None:
            url = f'{self.session_url}/sessions/{self._token}'
            r = requests.delete(
                    url,
                    verify=self.ssl_verify
                    )
            r.raise_for_status()
            self._token = None
                

    def __enter__(self):
        ''' automatically logs in when self.token is accessed '''
        pass

    def __exit__(self):
        self.logout()

    def _get(self, url) -> dict:
        r = requests.get(
                url, 
                verify=self.ssl_verify,
                headers={'Content-Type': 'application/json',
                    "Authorization": f"Bearer {self.token}"}
                    )
        r.raise_for_status()
        return r.json()['response']

    def _post(self, url, data) -> dict:
        r = requests.get(
                url, 
                data=data,
                verify=self.ssl_verify,
                headers={'Content-Type': 'application/json',
                    "Authorization": f"Bearer {self.token}"}
                    )
        r.raise_for_status()
        return r.json()['response']

    def get_highest_recordid(self):
        raise NotImplemented()
        url = f'{self.fm_baseurl}/{self.table_name}/layouts/{self.layout}/_find'


    def get_all_records(self, offset, limit=1000) -> dict:
        ''' bulk gets record in creation order and paginated 
        note that filemaker records are sorted by their recordid, but 
        not all recordids are consecutive, so record 406 might follow record 400
        '''
        if offset <=0:
            raise RuntimeError("invalid record offset, offsets start with 1")
        if limit <= 0:
            raise RuntimeError("invalid record limit, limits must be at least >= 1")
        url = f'{self.fm_baseurl}/{self.table_name}/layouts/{self.layout}/records?_limit={limit}&_offset={offset}'
        return self._get(url)

    def find_records(self, layout=None):
        raise NotImplemented()
        if layout is None:
            layout='Leistungserfassung'
        url = f'{self.fm_baseurl}/{self.table_name}/layouts/{self.layout}/_find'
        data = json.dumps({"query":[{"Zeitstempel":">=10/18/2022"}],
                    "limit":100
                    })
        return self._post(url, data)

    def find_mp_record(self, token, mp_number,limit=10):
        raise NotImplemented()
        url = f'{self.fm_baseurl}/{self.table_name}/layouts/{self.layout}/_find'
        data = json.dumps({"query":[{"Mol_NR":f"=={mp_number}"}],
                    "limit":limit
                    })
        return self._post(url, data)

    def get_new_records_by_date(self, day, month, year, examination_types=filemaker_examination_types, limit=1000):
        raise NotImplemented()
        url = f'{self.fm_baseurl}/{self.table_name}/layouts/{self.layout}/_find'

        data = json.dumps({"query":[
            {"Zeitstempel":f">={int(month)}/{(day)}/{(year)}", 
                'Untersuchung':f'="{u}"'}
            for u in examination_types
            ],
            "limit":limit
            })
        return self._post(url,data)
