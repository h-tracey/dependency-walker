from requests import get, post
import json
def get_pypi_package_info(package_name, version=None):
    req_url = f"https://pypi.org/pypi/{package_name}/{version}/json" if version else \
              f"https://pypi.org/pypi/{package_name}/json"    
    resp = get(req_url)
    if resp.status_code != 200:
        return 'no matching version found in pypi'
    content = resp.json()
    version = content['info'].get("version")

    return version

def get_npm_package_info(package_name, version=None):
    req_url = f"https://registry.npmjs.org/{package_name}/{version}" if version else \
              f"https://registry.npmjs.org/{package_name}"    
    resp = get(req_url)
    if resp.status_code != 200:
        return 'no matching version found in npm'
    content = resp.json()
    version = content.get("version", content.get('dist-tags', {}).get('latest'))

    return version

def check_osv_vulns(name: str, package_version, ecosystem):
    url = "https://api.osv.dev/v1/query"
    query = {
        "version": package_version,
        "package": {"name": name.lower(), "ecosystem": ecosystem}
    }
    resp  = post(url, json=query)
    content = resp.json()
    if resp.status_code != 200:
        raise
    all_vulns = []
    for vuln in content.get('vulns', []):
        osv_id = vuln.get('id')
        severity = vuln.get('database_specific', {}).get('severity')
        summary = vuln.get('summary')
        all_vulns.append((osv_id, severity, summary))
    return all_vulns

def update_external_packages(driver):
    records, _, _ = driver.execute_query(
        "match (n) where n:PyExternal or n:JSExternal return DISTINCT n"
    )
    print(len(records))
    for i, record in enumerate(records):
        print(i)
        package = record['n']['name']
        label,  = record['n'].labels
        package_repo = 'PyPI' if label == 'PyExternal' else 'npm'
        if package_repo == 'PyPI':
            latest = get_pypi_package_info(package)
        else:
            latest = get_npm_package_info(package)

        query = f"""
            match (n {{name: "{package}"}}) 
            where n:{label} 
            set n.latest = "{latest}"
        
        """
        driver.execute_query(query, database_="neo4j")

        vulns = check_osv_vulns(package, latest, package_repo)
        if any(vulns):
            #only the latest - not ideal
            id, sev, summ = vulns[0]
            vuln_query = f"""
                match (n:{label} {{name: "{package}", latest: "{latest}"}})
                set n.vulnerability_id = "{id}", n.summary = "{summ}", n.severity = "{sev}"
            """
            driver.execute_query(vuln_query, database_="neo4j")
        
def update_package_version(driver):
    records, _, _ = driver.execute_query(
        "match () - [r] - (n)  where n:PyExternal or n:JSExternal return DISTINCT n, r.version"
    )
    print(len(records))
    for i, record in enumerate(records):
        print(i)
        package = record['n']['name']
        label,  = record['n'].labels
        version = record['r.version']
        package_repo = 'PyPI' if label == 'PyExternal' else 'npm'

        vulns = check_osv_vulns(package, version, package_repo)
        if any(vulns):
            #only the latest - not ideal
            id, sev, summ = vulns[0]
            vuln_query = f"""
                match (n:{label} {{name: "{package}"}}) - [r:DEPENDS_ON {{version: "{version}"}}] - () 
                set r.vulnerability_id = "{id}", r.summary = "{summ}", r.severity = "{sev}"
            """
            driver.execute_query(vuln_query, database_="neo4j")


