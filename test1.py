#! /usr/bin/env python3

import asyncio
import logging
import concurrent.futures
import pprint

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


class Client:
    def __init__(self, writer):
        print('client init called')
        self.writer = writer
        self.peername = writer.get_extra_info('peername')
        self.name = ""

    def has_name(self):
        return self.name != ""

    def set_name(self, name):
        self.name = name.replace("\n", "").replace("\r", "")
        print(repr(self.name))

    def send_message(self, message, prompt=True):
        self.writer.write(str.encode(message))
        if prompt:
            self.write_prompt()

    def broadcast_message(self, sender, message):
        self.send_message(sender.name + ": " + message + "\n")

    def write_prompt(self):
        self.writer.write(str.encode("> "))


class ConnectionHandler:
    def __init__(self):
        self.clients = {}

    async def __call__(self, reader, writer):
        self.clients[writer] = Client(writer)
        log.info('Accepted connection from {}'.format(self.clients[writer]))
        print(self.clients)

        print(type(self.clients))
        for client in self.clients:
            print(self.clients[client])

        if not self.clients[writer].has_name():
            self.clients[writer].send_message("HI THERE. WHAT IS YOUR NAME? ", prompt=False)

        while True:
            try:
                _bytes = await reader.readline()
                if _bytes:
                    if not self.clients[writer].has_name():
                        self.clients[writer].set_name(_bytes.decode()) 
                        self.clients[writer].send_message('Hello {}!\n'.format(self.clients[writer].name))
                    else:
                        self.send_broadcast_message(_bytes.decode(), writer)
                else:
                    log.info('Connection from {} closed by peer'.format(
                        self.clients[writer].peername))
                    break
            except concurrent.futures.TimeoutError:
                log.info('Connection from {} closed by timeout'.format(
                    self.clients[writer].peername))
                break
        writer.close()
        del self.clients[writer]

    def send_broadcast_message(self, msg, sender):
        """
        :type msg: bytes
        """
        for c in self.clients:
            client = self.clients[c]
            client.broadcast_message(self.clients[sender], msg)


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
