import shelve
from IStore import IStore

class ShelveStore(IStore):
    
    def __init__(self, db_path = './cache/shelf'):
        self.shelve = shelve.open(db_path, writeback=True)


    def set_parameter(self, name, value):
        self.shelve[name] = value

    def get_parameter(self, name)-> str:
        return self.shelve[name]

    def __del__(self):
        # body of destructor
        self.shelve.close()