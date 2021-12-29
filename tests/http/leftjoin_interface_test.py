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
    """, 2),
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
    """, 4),
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

    """, 4),
    ("""
    select * where {
	    ?a <http://example.org/name> ?n.
	    OPTIONAL {
		    ?a <http://example.org/phone> ?p 
	    }.
	    FILTER (?n='paul'^^xsd:string)
    }

    """, 1)
]


class TestUnionInterface(object):
    @classmethod
    def setup_class(self):
        self._app = run_app('tests/data/optional/perez.yaml')
        self._client = TestClient(self._app)

    @classmethod
    def teardown_class(self):
        pass

    @pytest.mark.parametrize("query,cardinality", perez_queries)
    def test_leftjoin_interface(self, query, cardinality):
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
        assert nbCalls >= 1
