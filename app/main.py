import fastapi
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app import database
from app.routes import router

# Todo: Getting data from a cdn is whack; we should host it ourselves
# Custom documentation settings: https://github.com/tiangolo/fastapi/issues/2581
app = fastapi.FastAPI(title="Tusky Quiz Service")


app.add_event_handler("startup", database.connect_to_mongo)
app.add_event_handler("shutdown", database.close_mongo_connection)

origins = [
    "http://tusky.org",
    "http://localhost:5000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    # The logic here is simple; most of this function is error handling

    route_names = set()
    route_count = 0

    for route in app.routes:
        if isinstance(route, fastapi.routing.APIRoute):
            route.operation_id = route.name  # This line is the actual logic

            route_names.add(route.name)
            route_count += 1
            if len(route_names) != route_count:
                raise ValueError(
                    f"Each api endpoint must have a unique name. "
                    f"{route.name} is used as the name of multiple endpoints. "
                    f"Change the endpoint's name to fix this error."
                )


use_route_names_as_operation_ids(app)
