import asyncio
import logging
import random
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
        message = "This is your {} arse: ARSE!"
        self.clients.broadcast_message(self, message.format(t))


class NiceBot(Bot):
    async def do_task(self):
        print('NiceBot Running')
        MESSAGES = ["My oh my, {}! You're looking lovely today!",
                    "{} is truly marvellous.",
                    "{}! I don't know when I've met a wittier fellow!",
                    "There's no one more charming than {}!",
                    "It's a brighter day for having {} in this dungeon!"]

        c_names = [client.name for client in self.clients if client != self]
        message = random.choice(MESSAGES).format(random.choice(c_names))
        self.clients.broadcast_message(self, message, exclude=[self])
