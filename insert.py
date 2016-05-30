import argparse
import json

from aws import *
from neo4j.v1 import GraphDatabase, basic_auth

def insert_item(resource, session):
    def not_exist(resource, session):
        print("{} not supported".format(resource['type']))

    action = {
        'aws_instance': insert_aws_instance,
        'aws_subnet': insert_aws_subnet,
        'aws_vpc': insert_aws_vpc
        }

    return action.get(resource['type'], not_exist)(resource, session)

def main():
    parser = argparse.ArgumentParser(description="""
        Insert a Terraform state file into neo4j
    """)
    parser.add_argument('-d','--db', required=True, help="Neo4j host")
    parser.add_argument('-u','--username', required=True, help="Neo4j user")
    parser.add_argument('-p','--password', required=True, help="Neo4j password")
    parser.add_argument('state_file', help="Terraform state file")
    args = parser.parse_args()

    print args
    with open(args.state_file, 'r') as f:
        state = json.load(f)

    driver = GraphDatabase.driver("bolt://{}".format(args.db),
        auth=basic_auth(args.username, args.password))
    session = driver.session()

    # Reduce all the modules and resouces to a single array of objects
    resources = reduce( lambda a,b: a+b,
                map(lambda m: m['resources'].values(),
                    state['modules']))

    # Run actions for resources and capture hooks
    hooks = set()
    for resource in resources:
        hooks.add(insert_item(resource, session))

    # Run hooks
    for hook in hooks:
        if hook:
            hook(session)

if __name__ == '__main__':
    main()
