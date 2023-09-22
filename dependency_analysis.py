import csv

def generate_sbom(driver):
    query = """
        match(n)
        where n:PyExternal or n:JSExternal
        return distinct  n.name
    """
    records, _, _ = driver.execute_query(
        query
    )
    with open('sbom.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['name'])

        for item in records:
            writer.writerow([item['n.name']])

def generate_drift_analysis_internal(driver):
    query = """
        match (n1)- [r]->(n)
        where (n:PyBackend or n:JSBackend) and r.version <> n.latest
        return n1.name, r.version, n.name, n.latest
        order by n1.name
    """
    records, _, _ = driver.execute_query(
        query
    )
    with open('internal_drift.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['name', 'version', 'dependency_name', 'dependency_latest'])

        for item in records:
            writer.writerow([item['n1.name'], item['r.version'],  item['n.name'], item['n.latest']])

def generate_drift_analysis_external(driver):
    query = """
        match (n1)- [r]->(n)
        where (n:PyExternal or n:JSExternal) and r.version <> n.latest
        return n1.name, r.version, n.name, n.latest
        order by n1.name
    """
    records, _, _ = driver.execute_query(
        query
    )

    with open('external_drift.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['name', 'version', 'dependency_name', 'dependency_latest'])

        for item in records:
            writer.writerow([item['n1.name'], item['r.version'], item['n.name'], item['n.latest']])


def generate_py_vulnerability(driver):
    query = """
        match (n1) - [r]-> (n2)
        where r.vulnerability_id is not null
        return n1.name, r.version, r.vulnerability_id, r.severity, r.summary,  n2.name, n2.latest
        order by n2.name
    """
    records, _, _ = driver.execute_query(
        query
    )
    

    with open('py_vulns.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['name', 'version', 'vulnerabilities', 'dependency_name', 'dependency_latest'])

        for item in records:
            writer.writerow(
                [
                    item['n1.name'],
                    item['r.version'],
                    item['r.vulnerability_id'],
                    item['r.severity'],
                    item['r.summary'],
                    item['n2.name'],
                    item['n2.latest']
                ]
            )
