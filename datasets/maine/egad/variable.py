import geopandas as gdp
from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                           VOID, XMLNS, XSD
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal

import math
import os
import json
import pickle
import numpy as np
from tqdm import tqdm
import random
import re
import requests
from re import sub
import shapely

from datetime import datetime



NAME_SPACE = "http://w3id.org/sawgraph/v1/"

_PREFIX = {
    "me_egad": Namespace(f"{NAME_SPACE}me-egad#"),
    "me_egad_data": Namespace(f"{NAME_SPACE}me-egad-data#"),
    "us_sdwis": Namespace(f"{NAME_SPACE}us-sdwis#"),
    "coso": Namespace(f"http://w3id.org/coso/v1/contaminoso#"),
    "comptox": Namespace("http://w3id.org/comptox/v1/"),
    "geo": Namespace("http://www.opengis.net/ont/geosparql#"),
    "sf": Namespace("http://www.opengis.net/ont/sf#"),
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "owl": OWL,
    "time": TIME,
    "ssn": SSN,
    "sosa": SOSA,
    "qudt": Namespace("http://qudt.org/schema/qudt/"),
    "unit": Namespace("http://qudt.org/vocab/unit/"),
    "prov": PROV,
    "skos": SKOS,
    "gcx": Namespace(f'http://geoconnex.us/'),
    "dcterms": DCTERMS

}

def camel_case(s):
  s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
  return ''.join([s[0].lower(), s[1:]])

