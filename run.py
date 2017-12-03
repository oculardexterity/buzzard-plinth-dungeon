#! /usr/bin/env python3

import asyncio
import logging
import concurrent.futures
import pprint
import re


from actorManager import ActorManager
from client import Client
from bot import ArseBot, NiceBot

from geog1 import Geography


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


class ConnectionHandler:
    def __init__(self):
        self.clients = ActorManager()


    async def manage_bots(self):
        bots = [ArseBot('Arsebot', 15, 1, self.clients),
                NiceBot('Nicebot', 20, 2, self.clients)]

        loop = asyncio.get_event_loop()

        for bot in bots:
            self.clients.add_client(bot.name, bot)
            loop.create_task(bot.bot_loop())



    async def __call__(self, reader, writer):

        self.clients.add_client(writer, Client(writer, client_manager=self.clients))
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

                            exclude = self.clients.filter_clients({"alive": False}) + [client]
                            self.clients.broadcast_to_room(client, message, exclude=exclude)
                
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
        log_msg = "{} tried command '{}' with args [{}]"
        log_msg.format(client.name, command, ", ".join(args))
        print("COMMAND: ", command, "| ARGS: ", args)

        # Try to get method
        try:
            method_to_call = getattr(client, "command_" + command)
        except AttributeError:
            print('NO METHOD TO CALL')
            msg = '"{}" is not a fucking command. (YET!)'
            msg = msg.format(command.capitalize())
            client.admin_message(msg, prompt=True)

        # Try to call method
        try:
            method_to_call(args)

            log_msg += ": ✅"
        except Exception:
            print('CANNOT CALL WITH THESE ARGS')
            msg = 'You cannot "{}" so-called "{}"... fool.'
            msg = msg.format(command, " ".join(args))
            client.admin_message(msg)

            log_msg += ": ❌"

        # Try to find broadcast information method
        try:
            getattr(self.clients, "info_" + command)(client, args)
        except AttributeError:
            pass

        # Finally log information.
        log.info(log_msg)


    def handle_client_naming(self, client, message):
        if self.clients.exists_already({"name": message}, include_bots=True):
            print("client {} already exists".format(message))
            client.admin_message('That name is already taken. Try again.', prompt=True)
        else:    
            client.set_name_and_greet(message)
            msg = "{} has entered the dungeon complex! (Have fun.)".format(client.name)
            self.clients.broadcast_admin_message(msg, exclude=[client], prompt=True)
            if self.clients.more_than_one(include_bots=True):
                c_names = [client.name for client in self.clients]
                msg = "People currently in these dungeons are: " + ", ".join(c_names)
                client.admin_message(msg, prompt=True)
            else:
                msg = "You are all alone in these dungeons at the moment. (HAHAHA)"
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
