import datetime
import os
import sys
import threading
import atexit
import time
from typing import Union, Optional, List
from mcserverapi.si import Server

"""
[17:12:16] [Server thread/INFO]: <KungFuPanda09> hello
[17:12:20] [Server thread/INFO]: KungFuPanda09 left the game
[17:12:29] [Server thread/WARN]: Can't keep up! Is the server overloaded? Running 11693ms or 233 ticks behind
[17:12:20] [Server thread/INFO]: KungFuPanda09 left the game
"""


class Event:
    def __init__(self, parser, raw_event: str):
        self._parser = parser
        self._set_context(raw_event)
        self.event_type = None
        self.ctx = []
        self._clean_raw_message(self._raw_message)

    def _clean_raw_message(self, raw_message):
        comps = raw_message.split(' ')
        head = comps[0]

        if head.startswith('<') and head.endswith('>'):
            self.ctx.append(head.replace('<', '').replace('>', ''))
            self.ctx.append(' '.join(comps[1:]))
            self.event_type = 'player_message'
        elif "Can't keep up!" in raw_message:
            self.ctx.append(int(comps[9]))
            self.event_type = 'ticks_behind'
        elif "left the game" in raw_message:
            self.ctx.append(head)
            self.event_type = 'player_leave'
        elif "joined the game" in raw_message:
            self.ctx.append(head)
            self.event_type = 'player_join'
        elif "Done" in raw_message:

            self.event_type = 'ready'
        elif "Preparing spawn area:" in raw_message:
            self.ctx.append(int(comps[-1].replace('%', '')))
            self.event_type = 'spawn_prep'
        elif 'Environment:' in raw_message:
            env = {}
            for comp in comps:
                comp = comp.replace(',', '').replace("'", '')
                if '=' in comp:
                    k, v = comp.split('=')
                    env[k] = v
            self.ctx.append(env)
            self.event_type = 'start'
        elif 'Failed to start the minecraft server' in raw_message:
            self.event_type = 'failed_start'


    def _set_context(self, raw):
        raw = raw.replace(': ', '@@@', 1)
        info, self._raw_message = raw.split('@@@')
        info = info.replace('] [', ']@@@[', 1)
        time, thread_type = info\
            .replace('[', '')\
            .replace(']', '')\
            .split('@@@')

        self.at_time = self._convert_time(time)
        self.thread_type = thread_type
    
    def _convert_time(self, time_string):
        hour, minute, second = [int(num) for num in time_string.split(':')]
        _now = datetime.datetime.now()
        return datetime.datetime(_now.year, _now.month, _now.day, hour, minute, second)


class Parser:
    def __init__(self, server: Server, cycle_length: int = 1):
        self._si = server
        self._cycle_length = cycle_length
        self._event_cache = {}
        self._error_cache = []

    def watch_for_events(self):
        while self._si.online:
            new_stream = open(os.path.join(self._si.abs_cwd, self._si._log), 'r+')
            self.process_events(*new_stream.readlines())
            new_stream.close()
            time.sleep(self._cycle_length)

    def player_uuid(self, player):
        usercache = self._si.usercache
        return {name: uuid for name, uuid in zip([cache['name'] for cache in usercache], [cache['uuid'] for cache in usercache])}[player]

    def process_events(self, *events):
        for raw_event in events:
            raw_event = raw_event.replace('\n', '', 1)
            try:
                if raw_event not in self._event_cache:
                    sys.stdout.write(raw_event)
                    self._event_cache[raw_event] = Event(self, raw_event)
                    sys.stdout.write(' -> ' + str(self._event_cache[raw_event].event_type) + '\n')
                    event = self._event_cache[raw_event]
                    if event.event_type is None:
                        threading.Thread(target=self.on_unrecognized_event, args=[raw_event]).start()
                    else:
                        threading.Thread(target=self.__dict__['on_' + event.event_type], args=[event.ctx]).start()

            except Exception as err:
                if raw_event not in self._error_cache:
                    self.on_parsing_error(err, raw_event)
                    self._error_cache.append(raw_event)

    def on_ready(self, ctx):
        pass

    def on_spawn_prep(self, ctx):
        pass

    def on_player_join(self, ctx):
        pass

    def on_player_connect(self, ctx):
        pass

    def on_player_leave(self, ctx):
        pass

    def on_player_disconnect(self, ctx):
        pass

    def on_player_death(self, ctx):
        pass

    def on_ticks_behind(self, ctx):
        pass

    def on_player_message(self, ctx):
        pass

    def on_crash(self, ctx):
        pass

    def on_start(self, ctx):
        pass

    def on_failed_start(self, ctx):
        pass

    def on_default_gametype_init(self, ctx):
        pass

    def on_preparing_level(self, ctx):
        pass

    def on_start_region(self, ctx):
        pass

    def on_loading_recipes(self, ctx):
        pass

    def on_loading_achievements(self, ctx):
        pass

    def on_start_minecraft_version(self, ctx):
        pass

    def on_properties_load(self, ctx):
        pass

    def on_parsing_error(self, err, raw_event):
        sys.stderr.write(': '.join([str(err.__class__.__name__), *err.args, raw_event]))
        sys.exit()

    def on_unrecognized_event(self, raw_event):
        pass
