import strawberry

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:

    @strawberry.field
    def hello(self) -> str:
        return "Hello World"
    
    @strawberry.field
    def user(self) -> str:
        return "user"


schema = strawberry.Schema(Query)

graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

# uvicorn main:app --reload