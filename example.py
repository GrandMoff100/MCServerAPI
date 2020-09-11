from mcserver import Server, Parser
import time

server = Server('myserver/server.jar')

server.run()

sec = 1
min = 60 * sec
hour = 60 * min
day = 24 * hour
year = 365 * day

time.sleep(2 * day)