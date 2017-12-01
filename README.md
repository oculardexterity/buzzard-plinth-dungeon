# Buzzard-Plinth-Dungeon*

A pointless project I'm working on to learn about asynchronous Python.

At the moment it's a dungeon-cum-chatroom, where you can arbitrarily kill people.
Connect via command-line telnet connection.

## Running

You need __Python 3.6__ installed.
There aren't any requirements to install with pip at the moment.

Just run:
	
	$ python3 run.py

Then fire up telnet in another Terminal window:

	$ telnet 127.0.0.1 51234

(or whatever IP address it is)

	$ telnet 127.0.0.1 51234
	Trying 127.0.0.1...
	Connected to localhost.
	Escape character is '^]'.
	DUNGEON ADMIN: Welcome. Please type your name:

Then type your name and press Enter to log in.

	DUNGEON ADMIN: Hello John!
	DUNGEON ADMIN: You are all alone in the dungeon at the moment. (HAHAHA)

Then get all your mates to connect, as a chatroom with optional killing is a bit pointless otherwise.

## Some commands

Once connected, you will be asked to enter your name.

Then, just type to chat, as if this were a normal chatroom.

Commands are preceded by an exclamation mark(!) — because RiscOS executables used ! in the same way — e.g. :

	!jump

	DUNGEON ADMIN: You jumped ! (Not sure why.)

Some commands support arguments. Read the source code.

	!jump really fucking high in the sky

	DUNGEON ADMIN: You jumped really fucking high in the sky! (Not sure why.)

## Future developments...

### Proper development stuff
- rename a whole bunch of classes to be more sane

### Random features
- multiple rooms
- objects
- more stuff to do
- bots
- buzzards and plinths

 *  The buzzard-plinth business is because I made an earlier version of this in JavaScript with only one person and the optional task of putting a buzzard on a plinth in the shortest space of time. (The trick was to move the plinth to the buzzard.)