#! /usr/bin/env python3

import asyncio
import logging
import concurrent.futures
import pprint
import re

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


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

    def filter_clients(self, filt):
        if isinstance(filt, tuple):
            key, value = filt
            return [client for client in self\
                    if client[key] == value]
        if isinstance(filt, str):
            return [client for client in self\
                    if bool(client[filt])]
        raise TypeError("Requires a tuple or a string as input.")

    def exists_already(self, filt):
        return len(self.filter_clients(filt)) > 0

    def get_client(self, filt):
        clients = self.filter_clients(filt)
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

class Client:
    def __init__(self, writer):
        self.writer = writer
        self.peername = writer.get_extra_info('peername')
        self.name = ""
        self.location = 0
        self.alive = True

        # Send message asking for name:

    def __getitem__(self, item):
        return self.__dict__[item]

    def ask_name(self):
        self.admin_message("Welcome. Please type your name: ", prompt=False)

    def has_name(self):
        return self.name != ""

    def set_name(self, name):

        self.name = name.replace("\n", "").replace("\r", "").lower().capitalize()
        log.info("Client with peername: {} set name to '{}'".format(self.peername, self.name))
    
    def set_name_and_greet(self, name):
        self.set_name(name)
        self.admin_message('Hello {}!\n'.format(self.name), prompt=False)

    def send_message(self, message, prompt=True):
        self.writer.write(str.encode(message))
        if prompt:
            self.write_prompt()

    def broadcast_message(self, sender, message):
        self.send_message(sender.name + ": " + message + "\n")

    def write_prompt(self):
        self.writer.write(str.encode("\n"))

    def admin_message(self, message, prompt=True):
        message = "DUNGEON ADMIN: {}".format(message)
        self.send_message(message, prompt=prompt)

    """
    Hereafter are actual dispatchable commands.
    """

    def command_jump(self, args, clients=[]):
        self.admin_message("You jumped{}! (Not sure why.)".format(" " + " ".join(args)), prompt=True)

    def command_die(self, args, clients=[]):
        self.alive = False
        self.admin_message("You died", prompt=True)

    def command_autorevive(self, args, clients=[]):
        if self.alive:
            self.admin_message("Not sure what death you plan to revive yourself from...")
        else:
            self.alive = True
            self.admin_message("By the miracles of science you're brought back to life")

    def command_kill(self, args, clients=None):
        try:
            name = args[0].lower().capitalize()
            person_to_die = clients.get_client(("name", name))
            if person_to_die.alive:
                msg = "You killed {}. That's mean.".format(person_to_die.name)
                person_to_die.get_killed_by(self.name)
            else:
                msg = "{} is already dead.".format(person_to_die.name)
        except Exception:
            msg = "There's no such person as {} in the dungeon.".format(name)
        self.admin_message(msg)

    def get_killed_by(self, killer):
        msg = "You were killed by {}! (The bastard)".format(killer)
        self.admin_message(msg)
        self.alive = False




class ConnectionHandler:
    def __init__(self):
        self.clients = ClientManager()

    async def __call__(self, reader, writer):
        self.clients.add_client(writer, Client(writer))

        client = self.clients(writer)
        client.ask_name()

        log.info('Accepted connection from {}'.format(client.peername))
       

        while True:
            try:
                _bytes = await reader.readline()
                if _bytes:
                    
                    
                    try:
                        test_message = repr(_bytes.decode().replace("\r", "").replace("\n", "").strip())
                        test_message = re.sub(r'\\\w{3}\[\w{1}', "", test_message).replace("'", "")
                        if not test_message:
                            continue
                    except Exception as e:
                        print(e)
                    
                    message = _bytes.decode().replace("\r", "").replace("\n", "")
                                      
                    # Sets the client name and does log in: called once
                    if not client.has_name():
                        self.handle_client_naming(client, message)

                    # Dispatch commands, admin messages or broadcast message.
                    elif not client.alive and message != '!autorevive':
                        client.admin_message("No can do. Because you're dead.")
                    else:
                        if message.startswith("!"):
                            self.handle_command(client, message)
                        elif message.startswith("@"):
                            self.clients.broadcast_admin_message(message.replace('@', ''))
                        elif message != "" or message != " ":

                            log.info("Client '{}' sent message: '{}'".format(client.name, message))

                            exclude = self.clients.filter_clients(("alive", False)) + [client]
                            self.clients.broadcast_message(client, message, exclude=exclude)
                
                else:
                    log.info('Connection from {} closed by peer'.format(
                        client.peername))
                    break
            except concurrent.futures.TimeoutError:
                log.info('Connection from {} closed by timeout'.format(
                    client.peername))
                break
        writer.close()
        del self.clients[writer]

    def handle_command(self, client, message):

        message_as_list = message.replace("!", "").lower().split()
        command, args = message_as_list[0], message_as_list[1:]
        log.info("{} tried command '{}' with args [{}]".format(client.name, command, " ,".join(args)))
        try:
            getattr(client, "command_" + command)(args, clients=self.clients)
            try:
                getattr(self.clients, "info_" + command)(client, args)
            except AttributeError:
                pass
        except AttributeError:
            msg = '"{}" is not a fucking command. (YET!)'.format(command.capitalize())
            client.admin_message(msg, prompt=True)



    def handle_client_naming(self, client, message):
        if self.clients.exists_already(("name", message)):
            print("client {} already exists".format(message))
            client.admin_message('That name is already taken. Try again.', prompt=True)
        else:    
            client.set_name_and_greet(message)
            msg = "{} has joined the conversation".format(client.name)
            self.clients.broadcast_admin_message(msg, exclude=[client], prompt=True)
            if self.clients.more_than_one():
                c_names = [client.name for client in self.clients]
                msg = "People currently in the dungeon are: " + ", ".join(c_names)
                client.admin_message(msg, prompt=True)
            else:
                msg = "You are all alone in the dungeon at the moment. (HAHAHA)"
                client.admin_message(msg, prompt=True)


class ChatServer:
    def __init__(self, host, port, handler):
        """
        :type handler: ConnectionHandler
        """
        self.host = host
        self.port = int(port)
        self.handler = handler

    def start(self):
        loop = asyncio.get_event_loop()
        server_coroutine = asyncio.start_server(
            self.handler, host=self.host, port=self.port, loop=loop)
        server = loop.run_until_complete(server_coroutine)
        log.info('Listening established on {0}'.format(
            server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            log.info("Aborted by the user")
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()


def main():
    ChatServer(host='', port=51234, handler=ConnectionHandler()).start()


if __name__ == '__main__':
    main()
