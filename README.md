# MCServerAPI
MCServerAPI is a python framework for running and creating events triggered by minecraft events in the server-console.

## Example

```py
from mcserverapi import Server, Parser
    

server = Server('<jar location>') # Can either relative or absolute

class MyParser(Parser):
  def on_player_message(self, ctx):
    player, message = ctx
    server.run_cmd('say', player, 'has said', message)
  
  def on_ready(self, ctx):
    print('Server took', ctx[0], 'to start.')

parser = MyParser(server)

java_flags = {
  '-Xmx': '3G',
  '-Xms': '1G'
}

server.start(**java_flags)

parser.watch_for_events() # This is a blocking call. If you don't want it to block it, run it in a thread like so... threading.Thread(target=parser.watch_for_events).start()
```


# Changelog
- 1.3.1:
You can now pass arguments and flags to .start() like so... 
> (Note that init has been modified so you have to include any flags or arguments besides -jar and nogui)
```py
server.start('<arg1>', '<arg2>',**{'-Xmx':'3g', '-Xms':'1g'})
```
