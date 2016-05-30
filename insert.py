import json

from neo4j.v1 import GraphDatabase, basic_auth
from aws import *

state_file = 'xx'
with open(state_file, 'r') as f:
    state = json.load(f)

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
    driver = GraphDatabase.driver("bolt://xxx", auth=basic_auth("xxx", "xxx"))
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
