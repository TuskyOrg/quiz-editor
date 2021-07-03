import os

import click

HERE = os.path.dirname(__file__)
CODEGEN_DIR = os.path.join(HERE, "codegen")
OPENAPI_FILE = os.path.join(CODEGEN_DIR, "openapi.json")
PROTO_FILE = os.path.join(CODEGEN_DIR, "users.proto")
JS_DIR = os.path.join(CODEGEN_DIR, "js")
PYTHON_DIR = os.path.join(CODEGEN_DIR, "python")


@click.group()
def cli():
    pass


@click.command()
def initdb():
    set_env()
    from app.database import init_db, SessionLocal

    with SessionLocal() as db:
        init_db(db)


@click.command()
def dropdb():
    set_env()
    from app.database import drop_db, SessionLocal

    with SessionLocal() as db:
        drop_db(db)


@click.command()
def resetdb():
    set_env()
    from app.database import drop_db, init_db, SessionLocal

    with SessionLocal() as db:
        drop_db(db)
        init_db(db)


def set_env():
    import dotenv

    dotenv.load_dotenv("dev.env")
    # os.environ.pop("POSTGRES_SERVER")
    # os.environ.setdefault("POSTGRES_SERVER", "localhost")


@click.command()
@click.option("--production/--debug", default=False)
@click.option("--warning/--no-warning", default=True)
def runserver(production, warning):
    import uvicorn

    reload = False if production else True
    if warning:
        click.echo(
            "manage.py is currently not a production ready implementation. "
            "A Docker image will be later provided to run the server.\n"
            "The app runs in debug mode unless otherwise specified using the `--production` option."
        )
    uvicorn.run("server:app", reload=reload)


cli.add_command(runserver)
cli.add_command(initdb)
cli.add_command(dropdb)
cli.add_command(resetdb)


if __name__ == "__main__":
    cli()
