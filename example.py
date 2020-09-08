import mcserver as mcs

server = mcs.Server('myserver/server.jar')

server.start()

while server.online:
    for event in server.new_events:
        print(repr(event))

server.killserver()
