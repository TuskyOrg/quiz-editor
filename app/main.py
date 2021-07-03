import logging

import fastapi
import sqlalchemy.exc

from app import crud
from app.database import init_db, SessionLocal
from app.routes import router

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# Todo: Getting data from a cdn is whack; we should host it ourselves
# Custom documentation settings: https://github.com/tiangolo/fastapi/issues/2581
app = fastapi.FastAPI(title="Tusky Quiz Service")
app.include_router(router)


@app.on_event("startup")
async def ensure_database():
    logging.debug("Application startup")
    db = SessionLocal()
    try:
        try:
            crud.quiz.get(db, id=0)
        except sqlalchemy.exc.ProgrammingError:
            logging.info("Initializing database tables")
            init_db(db)
            logging.info("Database tables initialized")
    finally:
        db.close()


def use_route_names_as_operation_ids(app: fastapi.FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, fastapi.routing.APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)