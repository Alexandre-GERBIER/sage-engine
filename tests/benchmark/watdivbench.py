from sage.http_server.server import run_app
from starlette.testclient import TestClient
from tests.http.utils import post_sparql
import time



query = """
Select * where {
    ?v0 <http://xmlns.com/foaf/homepage> ?v1.
    OPTIONAL {
        ?v1 <http://schema.org/url> ?v2
    }.
    OPTIONAL {
    ?v1 <http://schema.org/language> ?v3
    }
}

"""

query2 = """
select * where {
    ?v0 <http://xmlns.com/foaf/familyName> ?v1.
    OPTIONAL {
        ?v0 <http://schema.org/nationality> ?v3
    }
}
"""


def benchmark():
        app = run_app('../benchmark/watdivbench.yaml')
        client = TestClient(app)

        start = time.time()
        nbResults = 0
        nbCalls = 0
        hasNext = True
        next_link = None
        while hasNext:
            response = post_sparql(client, query, next_link, 'http://localhost:8000/sparql/watdiv')
            response = response.json()
            nbResults += len(response['bindings'])
            # print(response['bindings'])
            hasNext = response['hasNext']
            next_link = response['next']
            nbCalls += 1

        end = time.time()

        print("La requête s'est exécuté en ", end - start, " secondes")

benchmark()