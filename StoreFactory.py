import os
from IStore import IStore
from EC2ParameterStore import EC2ParameterStore
from ShelveStore import ShelveStore


class StoreFactory(object):
    """ Factory for IStore """

    def get_store(self) -> IStore:
        class_name = os.getenv("CACHE_PROVIDER") or "ShelveStore"
        if (class_name == "ShelveStore"):
            cache_path = os.getenv("CACHE_PATH") or "./cache/db"
            return self.create_store(class_name, db_path=cache_path)
        else:
            return self.create_store("EC2ParameterStore",
                                  aws_access_key_id=os.getenv(
                                      'AWS_ACCESS_KEY'),
                                  aws_secret_access_key=os.getenv(
                                      'AWS_SECRET_KEY'),
                                  region_name=os.getenv('AWS_REGION'))

    def create_store(self, class_name, **my_args):
        module = __import__(class_name)
        class_ = getattr(module, class_name)
        instance = class_(**my_args)
        return instance
