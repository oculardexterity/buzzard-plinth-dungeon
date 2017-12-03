import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from geog1 import Geography

class Actor:
    def __init__(self, actor_name, actor_type, actor_location, client_manager):
        self.name = actor_name
        self.type = actor_type
        self.location = actor_location
        self.alive = True
        self.clients = client_manager
        self.orientation = "n"

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

    def get_resuscitated_by(self, resuscitator):
        msg = "You were resuscitated by {}! (Back to the dungeon!)".format(resuscitator)
        self.admin_message(msg)
        self.alive = True

    # Generic actor commands.
    def command_mylocation(self, args):
        my_location = Geography.location_desc(self.location)
        msg = 'You are currently in "{}"'.format(my_location)
        self.admin_message(msg)

    def command_compass(self, args):
        self.admin_message(self._compass())

    def _compass(self):
        orient = Geography.direction_name(self.orientation)
        return "You are facing {}".format(orient)

    def command_turn(self, args):
        assert len(args) == 1
        assert args[0] in ["left", "right"]
        self._turn(args[0])

    def _turn(self, turn):
        try:
            self.orientation = Geography.resolve_direction(self.orientation, turn)
            self.admin_message(self._compass())
        except Exception as e:
            print(e)

    def command_move(self, args):
        if args[0] ==   "forward":
            self._move_forward()

    def _move_forward(self):
        destination = Geography.get_direction(self.location, self.orientation)
        success, message = destination.move_into()
        if success:
            self.location = destination.ident
            self.admin_message(message)
            self.admin_message(self.others_in_room_message())
            msg = "{} entered this dungeon.".format(self.name)
            self.clients.broadcast_admin_to_room(self.location, msg, exclude=[self])
        else:
            self.admin_message(message)

    def others_in_room_message(self):
        others = self.clients.filter_clients({'location': self.location}, include_bots=True)
        print([c.name for c in others])
        if len(others) > 1:
            msg = "Currently in this dungeon are: {}"
            msg = msg.format(", ".join([c.name for c in others]))
        else:
            msg = "This dungeon is empty apart from you."
        return msg
