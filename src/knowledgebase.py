#===============================================================================
#
#  Flatmap viewer and annotation tool
#
#  Copyright (c) 2019  David Brooks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#===============================================================================
#
# A simple knowledge base...
#
#===============================================================================

from contextlib import ContextDecorator

#===============================================================================

import pyparsing

import rdflib

import rdflib_sqlalchemy as sqlalchemy
sqlalchemy.registerplugins()

from rdflib.plugins.sparql.results.jsonresults import JSONResultSerializer

#===============================================================================

from namespaces import SCICRUNCH_NS

#===============================================================================

class KnowledgeBase(rdflib.Graph, ContextDecorator):
    def __init__(self, kb_path):
        SPARC = rdflib.URIRef('SPARC')
        store = rdflib.plugin.get('SQLAlchemy', rdflib.store.Store)(identifier=SPARC)
        super().__init__(store, identifier=SPARC)
        self.namespace_manager = SCICRUNCH_NS
        database = rdflib.Literal('sqlite:///{}'.format(kb_path))
        self.open(database)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def query(self, sparql, **kwds):
        results = {}
        try:
            query_results = super().query(sparql, **kwds)
            json_results = JSONResultSerializer(query_results)
            if json_results.result.type == 'ASK':
                results['head'] = {}
                results['boolean'] = json_results.result.askAnswer
            else:                       # SELECT
                results['head'] = { 'vars': json_results.result.vars }
                results['results'] = { 'bindings': [
                    json_results._bindingToJSON(x) for x in json_results.result.bindings
                ]}
        except pyparsing.ParseException as error:
            results = { 'error': str(error) }
        except:
            pass
        return results

#===============================================================================