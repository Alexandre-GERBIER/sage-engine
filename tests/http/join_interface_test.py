# bgp_interface_test.py
# Author: Thomas MINIER - MIT License 2017-2018
import pytest
from sage.http_server.server import run_app
from starlette.testclient import TestClient
from tests.http.utils import post_sparql

perez_queries = [
    ("""
    select * where {
	    ?a <http://example.org/name> ?n.
            ?a <http://example.org/webpage> ?w
    }
    """, 2, [
        {'?a': 'http://testserver/sparql/bnode#95463b3f9b269ca07945624ede3905e3', '?n': '"ringo"',  '?w': '"www.starr.edu"'},
        {'?a': 'http://testserver/sparql/bnode#b55340d9cf8ca5e75683db91f218b5b9', '?n': '"george"',  '?w': '"www.george.edu"'}
    ]
    ),
]


class TestLeftJoinInterface(object):
    @classmethod
    def setup_class(self):
        self._app = run_app('tests/data/optional/perez.yaml')
        self._client = TestClient(self._app)

    @classmethod
    def teardown_class(self):
        pass

    @pytest.mark.parametrize("query,cardinality,oracle", perez_queries)
    def test_leftjoin_interface(self, query, cardinality, oracle):
        nbResults = 0
        nbCalls = 0
        hasNext = True
        results = []
        next_link = None
        while hasNext:
            response = post_sparql(self._client, query, next_link, 'http://localhost:8000/sparql/perez')
            assert response.status_code == 200
            response = response.json()
            nbResults += len(response['bindings'])
            results.extend(response['bindings'])
            hasNext = response['hasNext']
            next_link = response['next']
            nbCalls += 1
        assert nbResults == cardinality
        assert results == oracle
        assert nbCalls >= 1