from zoo_keeper.zoo_keeper_class import ZooKeeper
from zoo_keeper.server_requests import ServerRequests

class Validator(object):
    def __init__(self, zoo_keeper: ZooKeeper):
        self.to_server = ServerRequests()
        self.keeper = zoo_keeper

    def is_zoo_ok(self):
        zoo = self.keeper.zoo_name


