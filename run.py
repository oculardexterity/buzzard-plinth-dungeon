#! /usr/bin/env python3

import asyncio
import logging
import concurrent.futures
import pprint
import re
import time

from clientManager import ClientManager
from client import Client
from bot import ArseBot, NiceBot

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)



class ConnectionHandler:
    def __init__(self):
        self.clients = ClientManager()
        

    async def manage_bots(self):
        bots = [ArseBot('Arsebot', 15, self.clients),
                NiceBot('NiceBot', 20, self.clients)]

        loop = asyncio.get_event_loop()

        for bot in bots:
            self.clients.add_client(bot.name, bot)
            loop.create_task(bot.bot_loop())



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
        log_msg = "{} tried command '{}' with args [{}]".format(client.name, command, ", ".join(args))
        try:
            getattr(client, "command_" + command)(args, clients=self.clients)
            log_msg += ": ✅" 
            try:
                getattr(self.clients, "info_" + command)(client, args)
            except AttributeError:
                pass
        except AttributeError:
            msg = '"{}" is not a fucking command. (YET!)'.format(command.capitalize())
            client.admin_message(msg, prompt=True)
            log_msg += ": ❌"
        log.info(log_msg)


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
        loop.create_task(self.handler.manage_bots())
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
