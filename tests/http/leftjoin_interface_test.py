# bgp_interface_test.py
# Author: Thomas MINIER - MIT License 2017-2018
import pytest
from sage.http_server.server import run_app
from starlette.testclient import TestClient
from tests.http.utils import post_sparql

perez_queries = [
    ("""
    select * where {
	    ?a <http://example.org/email> ?e.
        OPTIONAL {
            ?a <http://example.org/webpage> ?w
        }
    }
    """, 2, [
        {'?a': 'http://testserver/sparql/bnode#95463b3f9b269ca07945624ede3905e3', '?e': '"ringo@acd.edu"', '?w': '"www.starr.edu"'},
        {'?a': 'http://testserver/sparql/bnode#fae9b9a0d388c5aa026a8b96e2af0c5c', '?e': '"john@acd.edu"'}
    ]
    ),
    ("""
    select * where {
        ?a <http://example.org/name> ?n.
        OPTIONAL {
            ?a <http://example.org/email> ?e
        }.
        OPTIONAL {
            ?a <http://example.org/webpage> ?w
        }	
    }
    """, 4, [
        {'?a': 'http://testserver/sparql/bnode#95463b3f9b269ca07945624ede3905e3', '?n': '"ringo"', '?e': '"ringo@acd.edu"', '?w': '"www.starr.edu"'},
        {'?a': 'http://testserver/sparql/bnode#b55340d9cf8ca5e75683db91f218b5b9', '?n': '"george"', '?w': '"www.george.edu"'},
        {'?a': 'http://testserver/sparql/bnode#e5f48712e5fb52365961aa9bfe58d592', '?n': '"paul"'},
        {'?a': 'http://testserver/sparql/bnode#fae9b9a0d388c5aa026a8b96e2af0c5c', '?n': '"john"', '?e': '"john@acd.edu"'}
    ]),
    ("""
    select * where {
        ?a <http://example.org/name> ?n.
        OPTIONAL {
            ?a <http://example.org/email> ?e.
            OPTIONAL {
                ?a <http://example.org/webpage> ?w
            }
        }
    }

    """, 4, [
        {'?a': 'http://testserver/sparql/bnode#95463b3f9b269ca07945624ede3905e3', '?n': '"ringo"', '?e': '"ringo@acd.edu"', '?w': '"www.starr.edu"'},
        {'?a': 'http://testserver/sparql/bnode#b55340d9cf8ca5e75683db91f218b5b9', '?n': '"george"'},
        {'?a': 'http://testserver/sparql/bnode#e5f48712e5fb52365961aa9bfe58d592', '?n': '"paul"'},
        {'?a': 'http://testserver/sparql/bnode#fae9b9a0d388c5aa026a8b96e2af0c5c', '?n': '"john"', '?e': '"john@acd.edu"'}
    ]),
    ("""
    select * where {
	    ?a <http://example.org/name> ?n.
	    OPTIONAL {
		    ?a <http://example.org/phone> ?p 
	    }.
	    FILTER (?n='paul'^^xsd:string)
    }

    """, 1, [
        {'?a': 'http://testserver/sparql/bnode#e5f48712e5fb52365961aa9bfe58d592', '?n': '"paul"', '?p': '"777-3426"'}
    ])
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
        next_link = None
        while hasNext:
            response = post_sparql(self._client, query, next_link, 'http://localhost:8000/sparql/perez')
            assert response.status_code == 200
            response = response.json()
            nbResults += len(response['bindings'])
            print(response['bindings'])
            hasNext = response['hasNext']
            next_link = response['next']
            nbCalls += 1
        assert nbResults == cardinality
        assert response['bindings'] == oracle
        assert nbCalls >= 1
