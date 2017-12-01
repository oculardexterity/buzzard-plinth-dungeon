import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Actor:
    def __init__(self, actor_name, actor_type, actor_location):
        self.name = actor_name
        self.type = actor_type
        self.location = actor_location
        self.alive = True

    def __getitem__(self, item):
        if item in self.__dict__:
            return item

    def has_name(self):
        return self.name != ""

    # Generic versions of action methods
    # to be implemented for Client and Bot classes
    # Uses 'pass' so we don't have to worry about
    # being accidentally called on a bot

    def send_message(self, message, prompt=False):
        """
        Base function overwritten by Client.
        So let's just log it shall we.
        """
        message = message.replace("\n", "")
        log_message = "Message received by {}-{}: '{}'"
        log.info(log_message.format(self.type, self.name, message))

    # Not actually used.
    def broadcast_message(self, message):
        pass

    def admin_message(self, message, prompt=False):
        log_message = "DUNGEON ADMIN message sent to {}-{}: '{}'"
        log.info(log_message.format(self.type, self.name, message))


    def get_killed_by(self, killer):
        msg = "You were killed by {}! (The bastard)".format(killer)
        self.admin_message(msg)
        self.alive = False
