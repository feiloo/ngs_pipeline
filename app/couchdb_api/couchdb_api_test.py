from couchdb_api import *

config_path = '/etc/ngs_pipeline_config.json'
with open(config_path, 'r') as f:
    config = json.loads(f.read())

assert 'couchdb_user' in config
assert 'couchdb_psw' in config

# test
auth = BasicAuth(config['couchdb_user'], config['couchdb_psw'])
s = Server('localhost', port=8001, auth=auth)
print(auth.psw)
db = s.get_db('ngs_app')

doca = db.get_doc('1')
docb = {'_id':'2','text':'world'}

query = '''
{
   "selector": {
      "data": {
         "fieldData": {
            "Zeitstempel": {
               "$eq": "10/24/2022"
            }
         }
      }
   }
}
'''

view = '''
function (doc) {
  if(doc.data.fieldData.Zeitstempel == '10/24/2022') {
        emit(doc);
    }
}
'''

'''
for rec in records['response']['data']:
    add_to_couch
'''

found = db.find(json.loads(query))
print(found)
