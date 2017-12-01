import asyncio
import logging
import time

from actor import Actor

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Bot(Actor):
    def __init__(self, bot_name, bot_timeout, client_manager):
        self.timeout = bot_timeout
        self.clients = client_manager
        self.alive = True
        super().__init__(bot_name, "Bot", 0)

    def has_name(self):
        return True

    def get_time(self):
        return time.strftime("%H:%M:%S", time.gmtime())

    async def bot_loop(self):
        while True:
            await asyncio.sleep(self.timeout)
            if self.alive:
                await self.do_task()
            else:
                log.info("Bot-{} cannot do task at {} as is dead."
                            .format(self.name, self.get_time()))

    async def do_task(self):
        raise NotImplementedError


class ArseBot(Bot):
    async def do_task(self):
        t = self.get_time()
        self.clients.broadcast_message(self, "ARSE AT " + t)


class NiceBot(Bot):
    async def do_task(self):
        for name in [client.name for client in self.clients if client.has_name() and client.name != self.name]:
            self.clients.broadcast_message(self, "Hello {}!".format(name))