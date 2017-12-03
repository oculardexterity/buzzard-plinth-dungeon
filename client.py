import logging

from actor import Actor


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Client(Actor):
    def __init__(self, output_writer, client_manager=[]):
        self.writer = output_writer
        self.peername = output_writer.get_extra_info('peername')
        
        super().__init__("", 'Client', 0, client_manager=client_manager)

   
    
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

    def command_jump(self, args):
        self.admin_message("You jumped{}! (Not sure why.)".format(" " + " ".join(args)), prompt=True)

    def command_die(self, args):
        self.alive = False
        self.admin_message("You died", prompt=True)

    def command_autorevive(self, args):
        if self.alive:
            self.admin_message("Not sure what death you plan to revive yourself from...")
        else:
            self.alive = True
            self.admin_message("By the miracles of science you're brought back to life")

    def command_kill(self, args):
        try:
            name = args[0].lower().capitalize()
            person_to_die = self.clients.get_client({"name": name, "location": self.location}, include_bots=True)
            
            if person_to_die == self:
                msg = "You can't kill yourself."

            elif person_to_die.alive:
                msg = "You killed {}. That's mean.".format(person_to_die.name)
                person_to_die.get_killed_by(self.name)
            else:
                msg = "{} is already dead.".format(person_to_die.name)
        except Exception as e:
            print(e)
            msg = "There's no such person as {} in this dungeon.".format(name)
        self.admin_message(msg)

    def command_resuscitate(self, args):
        try:
            name = args[0].lower().capitalize()

            subject = self.clients.get_client({"name": name, "location": self.location}, include_bots=True)
            if subject.alive:
                msg = "{} is alive already".format(subject.name)
            else:
                msg = "You've brought {} back to life. What a blessing.".format(subject.name)
                subject.get_resuscitated_by(self.name)
        except Exception as e:
            print(e)
            msg = "There's no such person as {} in the dungeon.".format(name)
        self.admin_message(msg)

    def command_describe(self, args):
        assert args[0] == "here"

        self.send_message(self.others_in_room_message())
