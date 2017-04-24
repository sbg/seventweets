from seventweets.client import Client


# class Singleton(type):
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


class Global:
    """
    Class for simulating global object g
    """

    def get_client(self, server_name=None, server_address=None):
        """
        Get instance of class Client
        :param server_name: Server with whom Client instance communicates
        :param server_address: Server with whom Client instance communicates
        :return: Client instance
        """
        if server_name:
            for name, address in self.registry.servers.items():
                if name == server_name:
                    return Client(address)
            return None
        elif server_address:
            return Client(server_address)

g = Global()
