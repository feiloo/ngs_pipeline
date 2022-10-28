import pycouchdb

assert 'couchdb_user' in config
assert 'couchdb_psw' in config


server = pycouchdb.Server(f"http://{config['couchdb_user']}:config['couchdb_psw']@localhost:8001")
db1 = server.database('db1')
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
