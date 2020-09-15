from mcserverapi import Server, Parser
import psutil

# Define your event triggers.
class MyParser(Parser):
    def on_ready(self, ctx):
        print('I AM READY')

# Initialize Server Object
server = Server('myserver/server.jar')

# Initialize Custom Event Triggers for server.
parser = MyParser(server)


server.start()  # Starts Server Subprocess

parser.watch_for_events()  # A blocking while server online loop, watching for events.
