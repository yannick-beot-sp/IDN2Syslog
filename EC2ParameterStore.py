import boto3
from IStore import IStore

class EC2ParameterStore(IStore):
    def __init__(self, **client_kwargs):
        self.client = boto3.client('ssm', **client_kwargs)
        self.path_delimiter = '/'

    def extract_parameter(self, parameter, strip_path=True):
        key = parameter['Name']
        if strip_path:
            key_parts = key.split(self.path_delimiter)
            key = key_parts[-1]
        value = parameter['Value']
        if parameter['Type'] == 'StringList':
            value = value.split(',')
        return (key, value)

    def set_parameter(self, name, value):
        result = self.client.put_parameter(Name=name, Value=value, Type="String", Overwrite=True)
        return result

    def get_parameter(self, name):
        result = self.client.get_parameter(Name=name, WithDecryption=True)
        p = result['Parameter']
        param = dict([self.extract_parameter(p, strip_path=True)])
        return param[name]
