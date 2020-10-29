from mcserverapi import Server, Parser
import mcserverapi.format_codes as codes
import threading
import time

# Define your event triggers.
class MyParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self, ctx):
        print('Server started in {}'.format(ctx[0]))

    def on_ticks_behind(self, ctx):
        self.server.say(codes.RED + 'OVERLOADED')

# Initialize Server Object
server = Server('myserver/server.jar')

# Initialize Custom Event Triggers for server.
parser = MyParser(server, debug=True)

flags = {
    '-Xms': '2G',
    '-Xmx': '7G'
}

server.start(**flags)  # Starts Server Subprocess

threading.Thread(target=parser.watch_for_events).start()  # A blocking while server online loop, watching for events.

while True:
    server.run_cmd('say', codes.BOLD + 'Hello from python')
    time.sleep(10)
