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
        return self.__dict__[item]

    def has_name(self):
        return self.name != ""

    # Generic versions of action methods
    # to be implemented for Client and Bot classes

    # Uses 'pass' so we don't have to worry about being accidentally called on a bot

    def send_message(self, message, prompt=False):
        """
        Base function overwritten by Client.
        So let's just log it shall we.
        """
        log_message = "Message sent to {}: '{}'".format(self.name, message)
        log.info(log_message)

    # Not actually used.
    def broadcast_message(self, message):
        pass

    def admin_message(self, message):
        pass



    def get_killed_by(self, killer):
        msg = "You were killed by {}! (The bastard)".format(killer)
        self.admin_message(msg)
        self.alive = False





class Client(Actor):
    def __init__(self, output_writer):
        self.writer = output_writer
        self.peername = output_writer.get_extra_info('peername')
        
        super().__init__("", 'Client', 0)

   
    
    # Methods for acquiring name and greeting on login.
    def ask_name(self):
        self.admin_message("Welcome. Please type your name: ", prompt=False)

    def set_name(self, name):
        """
        Removes bizarre capitalisation. Logs name change.
        Called by self.set_name_and_greet().
        """
        self.name = name.lower().capitalize()
        log.info("Client with peername: {} set name to '{}'".format(self.peername, self.name))
    
    def set_name_and_greet(self, name):
        self.set_name(name)
        self.admin_message('Hello {}!\n'.format(self.name), prompt=False)

    
    # Generic message functions
    def send_message(self, message, prompt=True):
        """
        Generic function for writing to the client.
        """
        self.writer.write(str.encode(message))
        if prompt: self.write_prompt()

    '''
    NOT USED ANYWHERE: clientManager.broadcast_message() is
    implemented with generic Actor.send_message()
    

    def broadcast_message(self, sender, message):
        """
        Client method for writing broadcast message.
        Sender argument is an instance of Actor.
        """
        self.send_message(sender.name + ": " + message + "\n")
    '''

    def write_prompt(self):
        """
        For if we want to add some kind of sigil to the next line.
        Difficult to predict, so just went with new line.
        """
        self.writer.write(str.encode("\n"))

    def admin_message(self, message, prompt=True):
        """
        Sends client a message from the Dungeon Admin.
        """
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
            person_to_die = clients.get_client(("name", name), bots=True)
            print(person_to_die)
            if person_to_die.alive:
                msg = "You killed {}. That's mean.".format(person_to_die.name)
                person_to_die.get_killed_by(self.name)
            else:
                msg = "{} is already dead.".format(person_to_die.name)
        except Exception as e:
            print(e)
            msg = "There's no such person as {} in the dungeon.".format(name)
        self.admin_message(msg)

