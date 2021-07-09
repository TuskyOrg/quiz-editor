import fastapi
from motor.motor_asyncio import AsyncIOMotorClient

from app import database
from app.core import settings
from app.routes import router

# Todo: Getting data from a cdn is whack; we should host it ourselves
# Custom documentation settings: https://github.com/tiangolo/fastapi/issues/2581
app = fastapi.FastAPI(title="Tusky Quiz Service")


app.add_event_handler("startup", database.connect_to_mongo)
app.add_event_handler("shutdown", database.close_mongo_connection)


app.include_router(router)


# Why we care about operation id:
#   Code generation often uses a route's operation id as a function name.
def use_route_names_as_operation_ids(app: fastapi.FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    # https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#openapi-operationid
    for route in app.routes:
        if isinstance(route, fastapi.routing.APIRoute):
            route.operation_id = route.name


use_route_names_as_operation_ids(app)
