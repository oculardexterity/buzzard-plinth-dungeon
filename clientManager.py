import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ClientManager:
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

    def more_than_one(self):
        return len(self.filter_clients('name')) > 1

    def broadcast_message(self, sender, message, exclude=[], prompt=False):
        for client in self:
            if client not in exclude:
                client.send_message(sender.name + ": " + message + "\n", prompt=prompt)

    def broadcast_admin_message(self, message, exclude=[], prompt=False):
        for client in self:
            if client not in exclude:
                client.admin_message(message, prompt=prompt)

    def filter_clients(self, filt, bots=False):
        if isinstance(filt, tuple):
            key, value = filt

            clients_list = []
            for client in self:
                print(key, value)
                print(client.type, client['name'], client[key] == value)
                if client.type == "Bot" and bots and client[key] == value:
                    print('got bot')
                    clients_list.append(client)
                elif client[key] == value:
                    clients_list.append(client)
            return clients_list
        

        if isinstance(filt, str):
            return [client for client in self\
                    if (client.type == "Bot" and bots) or bool(client[filt])]
        raise TypeError("Requires a tuple or a string as input.")

    def exists_already(self, filt, bots=False):
        return len(self.filter_clients(filt, bots=bots)) > 0

    def get_client(self, filt, bots=False):
        clients = self.filter_clients(filt, bots=bots)
        print(clients)
        if len(clients) == 1:
            return clients[0]
        else:
            return None

    """
    Return info for commands carried out by others
    """
    def info_jump(self, client, args):
        msg = "{} jumped{} for some reason.".format(client.name, " " + " ".join(args))
        self.broadcast_admin_message(msg, exclude=[client], prompt=True)

    def info_die(self, client, args):
        msg = "{} died of death. You can no longer kill them.".format(client.name)
        self.broadcast_admin_message(msg, exclude=[client])