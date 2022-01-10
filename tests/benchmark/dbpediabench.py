from sage.http_server.server import run_app
from starlette.testclient import TestClient
from tests.http.utils import post_sparql
import time



query = """

PREFIX  foaf: <http://xmlns.com/foaf/0.1/>

select * where {
  ?person foaf:name ?Name .
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
        app = run_app('../benchmark/dbpediabench.yaml')
        client = TestClient(app)

        start = time.time()
        nbResults = 0
        nbCalls = 0
        hasNext = True
        next_link = None
        while hasNext:
            response = post_sparql(client, query, next_link, 'http://localhost:8000/sparql/dbpedia')
            response = response.json()
            nbResults += len(response['bindings'])
            # print(response['bindings'])
            hasNext = response['hasNext']
            next_link = response['next']
            nbCalls += 1

        end = time.time()

        print("La requête s'est exécuté en ", end - start, " secondes")

benchmark()