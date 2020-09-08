import mcserver as mcs
import time

server = mcs.Server('myserver/server.jar')

server.start()

print('Waiting for event')
for event in server.events:
    print(event)
    print()
    print('Waiting for event')

