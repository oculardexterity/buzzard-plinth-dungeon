import asyncio
import logging
import time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Bot:
    def __init__(self, name, timeout, clients):
        self.name = name
        self.timeout = timeout
        self.clients = clients
        self.type = "Bot"
        self.alive = True

    def __getitem__(self, item):
        if item in self.__dict__:
            return item

    def has_name(self):
        return True

    def send_message(self, message, prompt=False):
        pass

    def admin_message(self, message, prompt=False):
        pass

    async def bot_loop(self):
        while True:
            await asyncio.sleep(self.timeout)
            await self.do_task()

    async def do_task(self):
        raise NotImplementedError

    def get_killed_by(self, killer):
        #msg = "You were killed by {}! (The bastard)".format(killer)
        #self.admin_message(msg)
        self.alive = False
        print("bot is dead")

class ArseBot(Bot):
    async def do_task(self):
        t = time.strftime("%H:%M:%S", time.gmtime())
        self.clients.broadcast_message(self, "ARSE AT " + t)

class NiceBot(Bot):
    async def do_task(self):
        t = time.strftime("%H:%M:%S", time.gmtime())
        
        for name in [client.name for client in self.clients if client.has_name() and client.name != self.name]:
            self.clients.broadcast_message(self, "Hello {}!".format(name))