import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ActorManager:
    def __init__(self):
        self.clients = {}

    def add_client(self, client_writer, client_object):
        self.clients[client_writer] = client_object

    def __call__(self, client):
        return self.clients[client]

    def __iter__(self):
        yield from [self.clients[c] for c in self.clients]

    def __getitem__(self, item):
        return self.__dict__[item]

    def more_than_one(self, include_bots=False):
        return len(self.filter_clients(
            {"name": True}, include_bots=include_bots)) > 1

    def broadcast_message(self, sender, message, exclude=[], prompt=False):
        for client in self:
            if client not in exclude:
                client.send_message(sender.name + ": " + message + "\n", prompt=prompt)

    def broadcast_admin_message(self, message, exclude=[], prompt=False):
        for client in self:
            if client not in exclude:
                client.admin_message(message, prompt=prompt)

    def filter_clients(self, filters, include_bots=False):
        # new implemenation
        # should take a list of tuples or a dict
        assert isinstance(filters, (dict, tuple))
        if isinstance(filters, dict):
            filters = [(k, v) for k, v in filters.items()]
        if not include_bots:
            filters.append(('type', 'Client'))

        print(filters)
        actor_list = []
        for actor in self:
            accept = True
            #print(actor.name)
            for key, value in filters:
                if isinstance(value, bool):
                    if bool(actor.__dict__[key]) != value:
                        accept = False
                        break
                else:
                    #print("COMPARED VALUES:", actor.__dict__[key], value, actor.__dict__[key] == value)
                    if actor.__dict__[key] != value:
                        #print("RESULT: not equal")
                        accept = False
                        break
            #print('accept:', accept)
            if accept:
                actor_list.append(actor)

        return actor_list


    def exists_already(self, filters, include_bots=False):
        return len(self.filter_clients(filters, include_bots=include_bots)) > 0

    def get_client(self, filters, include_bots=False):
        clients = self.filter_clients(filters, include_bots=include_bots)
        print(clients)
        if len(clients) == 1:
            return clients[0]
        else:
            return None

    """
    Broadcast info for commands carried out by others.
    """

    def info_jump(self, client, args):
        msg = "{} jumped{} for some reason."
        msg = msg.format(client.name, " " + " ".join(args))
        self.broadcast_admin_message(msg, exclude=[client], prompt=True)

    def info_die(self, client, args):
        msg = "{} died of death. You can no longer kill them.".format(client.name)
        self.broadcast_admin_message(msg, exclude=[client])