import datetime
import json
import requests
from pathlib import Path
from math import ceil
from app.model import filemaker_examination_types


class Filemaker:
    def __init__(self, server, user, psw):
        self.server = server
        self.user = user
        self.psw = psw

        # todo, this is sadly needed with the current settings
        self.ssl_verify = False

        self.fm_baseurl = f"https://{self.server}/fmi/data/v1/databases"
        self.session_url = f"{self.fm_baseurl}/molpatho_Leistungserfassung/sessions"

        self._token_ttl = datetime.timedelta(14*1/(24*60)) # in days, around 14 minutes

        self._token = None

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

    def _get(self, url):
        r = requests.get(
                url, 
                verify=self.ssl_verify,
                headers={'Content-Type': 'application/json',
                    "Authorization": f"Bearer {self.token}"}
                    )
        r.raise_for_status()
        return r.json()['response']

    def _post(self, url, data):
        r = requests.get(
                url, 
                data=data,
                verify=self.ssl_verify,
                headers={'Content-Type': 'application/json',
                    "Authorization": f"Bearer {self.token}"}
                    )
        r.raise_for_status()
        return r.json()['response']


    def get_all_records(self, offset, limit=1000):
        ''' bulk gets record in creation order and paginated '''
        url = f'{self.fm_baseurl}/molpatho_Leistungserfassung/layouts/Leistungserfassung/records?_limit={limit}&_offset={offset}'
        return self._get(url)

    def find_records(self):
        url = f'{self.fm_baseurl}/molpatho_Leistungserfassung/layouts/Leistungserfassung/_find'
        data = json.dumps({"query":[{"Zeitstempel":">=10/18/2022"}],
                    "limit":100
                    })
        return self._post(url, data)

    def find_mp_record(self, token, mp_number):
        url = f'{self.fm_baseurl}/molpatho_Leistungserfassung/layouts/Leistungserfassung/_find'
        data = json.dumps({"query":[{"Mol_NR":f"=={mp_number}"}],
                    "limit":10
                    })
        return self._post(url, data)

    def get_new_records(self, day, month, year, examination_types=filemaker_examination_types):
        url = f'{self.fm_baseurl}/molpatho_Leistungserfassung/layouts/Leistungserfassung/_find'

        data = json.dumps({"query":[
            {"Zeitstempel":f">={int(month)}/{(day)}/{(year)}", 
                'Untersuchung':f'="{u}"'}
            for u in examination_types
            ],
            "limit":1000
            })
        return self._post(url,data)
