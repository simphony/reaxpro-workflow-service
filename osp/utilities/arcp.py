"""OSP-utilities for arcp-iris"""

from urllib.parse import quote, urlencode

from arcp import arcp_name, arcp_random, is_arcp_uri
from arcp.parse import ARCPParseResult, parse_arcp

from osp.core.cuds import Cuds


def check_arcp(cuds: Cuds) -> bool:
    """Check whether the iri of a Cuds is an arcp-uri"""
    return is_arcp_uri(cuds.iri)


def wrap_arcp(cuds: Cuds) -> ARCPParseResult:
    """Parse the iri of a Cuds according to the arcp-rules"""
    return parse_arcp(cuds.iri)


def make_remote(*args, **kwargs) -> str:
    """Make a named arcp-iri"""
    return arcp_name(*args, **kwargs)


def make_local(*args, **kwargs) -> str:
    """Make a randomized arcp-iri"""
    return arcp_random(*args, **kwargs)


def make_arcp(*args, query: dict = None, dtype: str = "local", **kwargs) -> str:
    """Make a arcp-iri, named or randomized."""
    if query:
        for key, value in query.items():
            query[key] = [quote(".".join(item)) for item in value]
        query = urlencode(query, doseq=True)
    if dtype == "local":
        func = make_local
    elif dtype == "remote":
        func = make_remote
    else:
        raise ValueError(
            f"Unknown conversion-type {dtype}. Must be 'local' or 'remote'."
        )
    return func(*args, **kwargs, query=query)
