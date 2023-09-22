from requests import get
import json
from os import getenv

BEARER_TOK = getenv("BEARER_TOK")

DELIMS = ["==", "~=", '>=', '<=', ">", "<"]
INVALID_START = ['#', '--']

py_services = [
    "la-pipeline",
    "la-heartbeat",
    "la-insight",
    "la-cooccurrence",
    "la-tag-service",
    "la-datacollector",
    "la-theme",
    "la-summarisation",
    "la-api",
    "la-file-source",
    "la-progress",
    "la-smart-uploads",
    "la-queue-stats",
    "la-dep-store",
    "la-event",
    "la-logger",
    "la-data-discovery",
    "la-trackers",
    "la-automation",
    "la-automation-api"
]

py_libs = [
    "la-common-tools",
    "la-common-date",
    "la-common-amqp",
    "la-common-redis",
    "la-common-mongo",
    "la-common-grpc",
    "la-common-pipeline",
    "la-common-mysql",
    "la-common-schemas",
    "la-common-flask",
]

node_srv = [
    "page-parser",
    "cache_service",
    "update_service",
    "resource_service",
    "flag_api",
    "auth-service",
    "la-data-upload",
    "admin-api",
    "heat_map_service"
]

node_libs = [
    "rabbitmq_message_library",
    "admin_models"
]

deprecated = [
    "la-tag-libs",
    "ri_key_value_store",
    'rrti_cache',
    'ri-key-value-store',
    'ri_grpc',
    'ri_storage_utilities',
    'ri_service_property_settings'
    'ri_stat_importance'
    'ri_amqp',
    'ri_nosql',
    'redis_cache_library'
]
def get_latest(repo):
    resp = get(
            f"https://api.bitbucket.org/2.0/repositories/relativeinsight/{repo}/src/master/VERSION",
            headers={"Authorization": BEARER_TOK}
        )
    if resp.status_code == 200:
        return resp.content.decode('ascii')
    else:
    
        resp = get(
        f"https://api.bitbucket.org/2.0/repositories/relativeinsight/{repo}/src/master/version.py",
        headers={"Authorization": BEARER_TOK}
        )
    return resp.content.decode('ascii').split('=')[1]


def scan_py(scan_type):
    deps = {}
    for srv in py_services if scan_type == 'services' else py_libs:
        resp = get(
            f"https://api.bitbucket.org/2.0/repositories/relativeinsight/{srv}/src/master/requirements.txt",
            headers={"Authorization": BEARER_TOK}
        )
        service_requirements = resp.content.decode('ascii').splitlines()
        reqs = []
        for req in service_requirements:
            if req and not any([req.startswith(s) for s in INVALID_START]):
                for delimiter in DELIMS:
                    req = "DELIM".join(req.split(delimiter))

                result = req.split('DELIM')
                dep = result[0].split()[0]
                dep = result[0].split('[')[0]                
                version = result[1].split()[0] if len(result) > 1 else 'latest'

                reqs.append(dict(dependency=dep, version=version))
        deps.update({srv: {'deps': reqs, 'latest': get_latest(srv)}})
    return deps

def scan_node(scan_type):
    deps = {}
    for srv in node_srv if scan_type == 'services' else node_libs:
        resp = get(
            f"https://api.bitbucket.org/2.0/repositories/relativeinsight/{srv}/src/master/package.json",
            headers={"Authorization": BEARER_TOK}
        )
        package = json.loads(
            resp.content.decode('ascii')
        )
        service_requirements = package.get('dependencies')
        node_version=package.get('version')

        reqs = []
        for k, v in service_requirements.items():
            reqs.append(dict(dependency=k, version=v.lstrip('^')))

        deps.update({srv: {'deps': reqs, 'latest': node_version}})
    return deps
