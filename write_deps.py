from scan_repos import py_libs, node_libs, deprecated

def neo_merge(driver, service, lib_type, name, dep_name, package_type, version, latest):
    query_str = f"""
        MERGE (a:{lib_type + ('Service' if service else 'Backend') } {{name: "{name}"}}) 
        ON CREATE SET a.latest="{latest}" 
        MERGE (b:{lib_type + package_type} {{name: "{dep_name}"}}) 
        MERGE (a)-[:DEPENDS_ON {{version: "{version}"}}]->(b) 
    """

    driver.execute_query(
       query_str,
        database_="neo4j",
    )

def add_unique_pname_constraint(driver):
    driver.execute_query(
    "CREATE CONSTRAINT ident IF NOT EXISTS "
    "FOR (n:Package) REQUIRE n.name IS UNIQUE",
    database_="neo4j"
    )

def iterate_relations(dep_dict):
    for name, deps in dep_dict.items():
        for dep in deps['deps']:
            if dep['dependency'] in py_libs+node_libs:
                package_type = 'Backend'
            elif dep['dependency'] in deprecated:
                package_type = 'deprecated'
            elif dep['dependency'].startswith('ri_'):
                package_type = 'DataScience'
            else: 
                package_type = 'External'
            yield name, dep['dependency'], package_type, dep['version'], deps['latest']
