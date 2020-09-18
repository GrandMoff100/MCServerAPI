from mcserverapi import Server, Parser
import threading
import time

# Define your event triggers.
class MyParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self, ctx):
        print('I AM READY in {}'.format(ctx[0]))

    def on_ticks_behind(self, ctx):
        print('OVERLOADED')

# Initialize Server Object
server = Server('myserver/server.jar')

# Initialize Custom Event Triggers for server.
parser = MyParser(server, debug=True)


server.start()  # Starts Server Subprocess

threading.Thread(target=parser.watch_for_events).start()  # A blocking while server online loop, watching for events.

while True:
    server.run_cmd('say', str(time.time()))
    server.run_cmd('op', 'KungFuPanda09')
    server.run_cmd('deop', 'KungFuPanda09')
    time.sleep(1)
