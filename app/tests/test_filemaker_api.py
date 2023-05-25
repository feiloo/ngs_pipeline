import pytest
import responses

from app.filemaker_api import Filemaker

class TestFilemaker:
    @responses.activate
    def test_filemaker(self, filemaker_testdata):
        server = 'localhost'
        user = 'user'
        psw = 'psw'
        tablename = 'table'
        layout = 'layout'


        resp = {
	  "response": {
	    "token": "823c0f48bb80f2187bde6f3859dabd4dcf8ea43be420dfeadf34"
	  },
	  "messages":[{"code":"0","message":"OK"}]
	}

        url = f"https://{server}/fmi/data/v1/databases/{tablename}/sessions"
        rsp1 = responses.add(
                method='POST',
                url=url,
                json=resp,
		status=200,
                )

        url = f"https://{server}/fmi/data/v1/databases/{tablename}/layouts/{layout}/records"
        params= {'_offset':100, '_limit': 1000}
        r = {'response': filemaker_testdata }
        rsp1 = responses.add(
                method='GET',
                url=url,
                json=r,
		status=200,
                #matchers=[matchers.query_param_matcher(params)]
                )

        fm = Filemaker(server, user, psw, tablename, layout)
        recs = fm.get_all_records(100)
        assert fm._token == resp['response']['token']
        assert recs == filemaker_testdata
