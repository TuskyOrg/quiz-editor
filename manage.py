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
    from app.database import init_db

    init_db()


@click.command()
def dropdb():
    from app.database import drop_db

    drop_db()


@click.command()
def resetdb():
    from app.database import drop_db, init_db

    init_db()
    drop_db()


@click.command()
@click.option("--production/--debug", default=False)
@click.option("--warning/--no-warning", default=True)
def runserver(production, warning):
    import uvicorn

    reload = False if production else True
    if warning:
        click.echo(
            "manage.py is currently not a production ready implementation. \n"
            "The app runs in debug mode unless otherwise specified using the `--production` option."
        )
    uvicorn.run("app:app", reload=reload)


@click.command()
def test():
    import pytest
    from app.database import init_db, drop_db
    drop_db()
    init_db()
    pytest.main()


cli.add_command(runserver)
cli.add_command(initdb)
cli.add_command(dropdb)
cli.add_command(resetdb)
cli.add_command(test)


if __name__ == "__main__":
    cli()
