from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import os


def engine_from_config(database: str = "politeness") -> Engine:
    """
    Create a SQLAlchemy Engine based on the credentials located in the `.my.cnf`
    file.

    Parameters
    ----------
    database: default="politeness"
        The name of the database to connect to.

    Returns
    -------
    A SQLAlchemy engine connected to the specified database.
    """
    parser = ConfigParser()
    parser.read(os.path.expanduser("~/.my.cnf"))
    config = parser["client"]

    engine = create_engine(
        "mysql+pymysql://{username}:{password}@localhost/{database}".format(
            username=config["user"], password=config["password"], database=database
        )
    )
    return engine
