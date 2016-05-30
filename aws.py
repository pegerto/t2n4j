import pprint
from string import Template

def create_plug_relation(session):
    session.run(r"MATCH (i:Instance),(s:Subnet) WHERE i.subnet_id = s.id CREATE (i)-[r:PLUG]->(s)")


def create_subnet_network_relation(session):
    session.run(r"MATCH (n:Network),(s:Subnet) WHERE n.id = s.vpc_id CREATE (s)-[r:SUBNET]->(n)")


def insert_aws_subnet(resource, session):
    attr = resource['primary']['attributes']
    t = Template(r"CREATE (i:Subnet {name: '$name', id: '$id', vpc_id: '$vpc_id', az:'$az'})")
    session.run(t.substitute (
                    name=attr['tags.Name'],
                    id=attr['id'],
                    vpc_id=attr['vpc_id'],
                    az=attr['availability_zone']))
    return create_plug_relation


def insert_aws_instance(resource, session):
    attr = resource['primary']['attributes']
    t = Template(r"""CREATE (i:Instance {name: '$name', id: '$id',
                     subnet_id: '$subnet_id'})
                  """)
    session.run(t.substitute (
                    name=attr['tags.Name'],
                    id=attr['id'],
                    subnet_id=attr['subnet_id']))
    return None


def insert_aws_vpc(resource, session):
    attr = resource['primary']['attributes']
    t = Template(r"CREATE (n:Network {name: '$name', id: '$id'})")
    session.run(t.substitute (
                    name=attr['tags.Name'],
                    id=attr['id']))
    return create_subnet_network_relation
