from flask import Flask, request
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from flask_restx import Api, Resource, fields

load_dotenv()

app = Flask(__name__)
api = Api(app, version='1.0', title='Elasticsearch API',
          description='A simple Elasticsearch API with Python and Docker')

# Namespace for operations
ns = api.namespace('elastic', description='Elasticsearch operations')

# Подключение к Elasticsearch
es = Elasticsearch(
    hosts=[f"http://{os.getenv('ELASTIC_HOST')}:{os.getenv('ELASTIC_PORT')}"],
    basic_auth=(os.getenv('ELASTIC_USERNAME'), os.getenv('ELASTIC_PASSWORD'))
)

# Models for Swagger documentation
index_model = api.model('Index', {
    'index_name': fields.String(required=True, description='Name of the index')
})

document_model = api.model('Document', {
    'index_name': fields.String(required=True, description='Name of the index'),
    'document': fields.Raw(required=True, description='Document to be indexed')
})

search_model = api.model('Search', {
    'index_name': fields.String(required=True, description='Name of the index'),
    'query': fields.String(required=True, description='Search query')
})

@ns.route('/')
class Index(Resource):
    def get(self):
        """Check service status"""
        return {"message": "Elasticsearch Python Docker Demo"}

@ns.route('/create_index')
class CreateIndex(Resource):
    @ns.expect(index_model)
    def post(self):
        """Create a new index"""
        data = request.json
        index_name = data.get('index_name')
        
        if not index_name:
            return {"error": "index_name is required"}, 400
        
        try:
            if not es.indices.exists(index=index_name):
                es.indices.create(index=index_name)
                return {"message": f"Index {index_name} created"}, 201
            return {"message": f"Index {index_name} already exists"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@ns.route('/add_document')
class AddDocument(Resource):
    @ns.expect(document_model)
    def post(self):
        """Add document to index"""
        data = request.json
        index_name = data.get('index_name')
        document = data.get('document')
        
        if not index_name or not document:
            return {"error": "index_name and document are required"}, 400
        
        try:
            res = es.index(index=index_name, document=document)
            return {"message": "Document added", "id": res['_id']}, 201
        except Exception as e:
            return {"error": str(e)}, 500

@ns.route('/search')
class Search(Resource):
    @ns.expect(search_model)
    def get(self):
        """Search in index"""
        index_name = request.args.get('index_name')
        query = request.args.get('query')
        
        if not index_name or not query:
            return {"error": "index_name and query are required"}, 400
        
        try:
            res = es.search(
                index=index_name,
                body={
                    "query": {
                        "match": {
                            "content": query
                        }
                    }
                }
            )
            return res['hits']['hits'], 200
        except Exception as e:
            return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)