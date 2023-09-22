from os import getenv
from neo4j import GraphDatabase
from scan_repos import scan_py, scan_node
from write_deps import (
    iterate_relations,
    add_unique_pname_constraint,
    neo_merge
)
from dependency_analysis import (
    generate_py_vulnerability,
    generate_drift_analysis_external,
    generate_drift_analysis_internal,
    generate_sbom

)

from external_package_check import update_external_packages, update_package_version


URI = getenv('URI')
AUTH = (getenv('AUTH_USER'), getenv('AUTH_PASSWORD'))

def write_initial():
    with GraphDatabase.driver(uri=URI, auth=AUTH) as driver:
        add_unique_pname_constraint(driver)
        print('python lib')
        for relation in iterate_relations(scan_py('libs')):
            neo_merge(driver, False, 'Py', *relation)
        print('python srv')
        for relation in iterate_relations(scan_py('services')):
            neo_merge(driver, True, 'Py', *relation)
        print('node lib')
        for relation in iterate_relations(scan_node('lib')):
            neo_merge(driver, False, 'JS', *relation)
        print('node srv')
        for relation in iterate_relations(scan_node('services')):
            neo_merge(driver, True, 'JS', *relation)

def populate_external():
    with GraphDatabase.driver(uri=URI, auth=AUTH) as driver:
        print("package lookup")
        update_external_packages(driver)
        print("version lookup")
        update_package_version(driver)

def graph_analysis():
    with GraphDatabase.driver(uri=URI, auth=AUTH) as driver:
        print('getting output')
        generate_py_vulnerability(driver)
        generate_drift_analysis_external(driver)
        generate_drift_analysis_internal(driver)
        generate_sbom(driver)

if __name__ == '__main__':
    write_initial()
    populate_external()
    graph_analysis()