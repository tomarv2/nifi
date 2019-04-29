import yaml


def parse_connections(config_file):
    with open(config_file, 'r') as stream:
        out = yaml.load(stream)
        return (out['required_number_of_connection'])


def parse_sourceId(config_file):
    with open(config_file, 'r') as stream:
        out = yaml.load(stream)
        return (out['sourceId'])


def parse_sourceGroupId(config_file):
    with open(config_file, 'r') as stream:
        out = yaml.load(stream)
        return (out['sourceGroupId'])


def parse_destinationId(config_file):
    with open(config_file, 'r') as stream:
        out = yaml.load(stream)
        return (out['destinationId'])


def parse_destinationGroupId(config_file):
    with open(config_file, 'r') as stream:
        out = yaml.load(stream)
        return (out['destinationGroupId'])


def parse_type(config_file):
    with open(config_file, 'r') as stream:
        out = yaml.load(stream)
        return (out['type'])

#print(parse_destinationGroupId(config_file))



