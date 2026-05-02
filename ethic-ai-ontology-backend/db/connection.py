import os
from typing import Any, Dict, Iterable, List, Optional

from neo4j import Driver, GraphDatabase, Session

_driver: Optional[Driver] = None


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def get_driver() -> Driver:
    """
    Lazily create and return a reusable Neo4j driver.

    Environment variables:
    - NEO4J_URI (default: bolt://localhost:7687)
    - NEO4J_USER or NEO4J_USERNAME (default: neo4j)
    - NEO4J_PASSWORD (required unless auth is disabled on your Neo4j)
    """
    global _driver
    if _driver is not None:
        return _driver

    uri = _get_env("NEO4J_URI", "bolt://localhost:7687")
    user = _get_env("NEO4J_USER") or _get_env("NEO4J_USERNAME") or "neo4j"
    password = _get_env("NEO4J_PASSWORD", "")

    _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver


def get_session(database: Optional[str] = None) -> Session:
    """
    Create a new session from the shared driver.

    Optional env var: NEO4J_DATABASE (used when database arg is None).
    """
    driver = get_driver()
    db = database or _get_env("NEO4J_DATABASE")
    if db:
        return driver.session(database=db)
    return driver.session()


def run_query(cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Helper for read-style queries that returns list[dict].
    """
    with get_session() as session:
        result = session.run(cypher, params or {})
        return [record.data() for record in result]


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None