import requests
import json

COUCHDB_DEFAULT_PORT=5984

class Document(dict):
    pass

class Auth:
    pass

class NoAuth(Auth):
    pass

class BasicAuth(Auth):
    def __init__(self, user, psw):
        self.user = user
        self.psw = psw

class Database:
    def __init__(self, dbname, url, auth):
        self.dbname = dbname
        self.url = url

        self.auth = auth

        if isinstance(self.auth, NoAuth):
            self._request_auth = None
        elif isinstance(self.auth, BasicAuth):
            self._request_auth = (self.auth.user, self.auth.psw)
        else:
            #self._request_auth = None
            raise NotImplementedError


    def get_doc(self, docid):
        response = requests.get(
                f"{self.url}/{self.dbname}/{docid}", 
                auth=self._request_auth)
        return response.json()

    def put_doc(self, doc):
        docid = doc['_id']
        response = requests.put(
                f"{self.url}/{self.dbname}/{docid}", 
                data=json.dumps(doc),
                auth=self._request_auth)
        return response.json()

    def find(self, query):
        response = requests.post(
                f"{self.url}/{self.dbname}/_find", 
                headers={'Content-Type':'application/json'},
                data=json.dumps(query),
                auth=self._request_auth)
        return response.json()



class Server:
    def __init__(self, host, *args, auth, port=COUCHDB_DEFAULT_PORT):
        self.host = host
        self.port = port

        self.auth = auth

        if isinstance(self.auth, NoAuth):
            self._request_auth = None
        elif isinstance(self.auth, BasicAuth):
            self._request_auth = (self.auth.user, self.auth.psw)
        else:
            #self._request_auth = None
            raise NotImplementedError

    def _get_url(self):
        return f"http://{self.host}:{self.port}"

    def get_db(self, dbname):
        return Database(dbname, self._get_url(), self.auth)

    def create_db(self, dbname):
        response = requests.put(
                f"{self.url}/{self.dbname}",
                auth=self._request_auth)

        return Database


