import datetime
import requests
import json
import io
from typing import Union, IO, List, Optional

class Player:
    cache = {}

    def __init__(self, player=None, uuid=None):
        if player and uuid:
            pass
        elif uuid:
            player = self.get_player(uuid)
        elif player:
            uuid = self.get_uuid(player)
        else:
            raise ValueError('class Player needs either a player username or uuid to initialize.')
        self.player = player
        self.uuid = uuid

    def get_player(self, uuid):
        if uuid in self.cache.values():
            return {v:k for k,v in self.cache.items()}[uuid]
        api = 'https://api.mojang.com/user/profiles/%s/names' % uuid
        try:
            response = requests.get(api).json()
            if 'error' in response and 'errorMessage' in response:
                ResponseError = type(response['error'], tuple([Exception]), {})
                raise ResponseError(response['errorMessage'])
            self.cache[response[-1]['name']] = uuid
            return response[-1]['name']
        except json.decoder.JSONDecodeError:
            raise ValueError('No players exist with uuid, {}, according to Mojang.'.format(uuid))

    def get_uuid(self, player):
        if player in self.cache:
            return self.cache[player]

        api = 'https://api.mojang.com/users/profiles/minecraft/%s' % player
        try:
            response = requests.get(api).json()
            if 'error' in response and 'errorMessage' in response:
                ResponseError = type(response['error'], tuple([Exception]), {})
                raise ResponseError(response['errorMessage'])
            self.cache[player] = response['id']
            return response['id']
        except json.decoder.JSONDecodeError:
            raise ValueError('Player {} Doesn\'t exist, according to Mojang.'.format(player))

    def __repr__(self):
        return '<Player {}:{}>'.format(self.player, self.uuid)


class Event():
    def __init__(self, raw_event: str):
        self.raw = raw_event
        if self.raw.startswith('['):
            info = self.raw.replace('\n', '').split(': ')[0]
            message = self.raw.replace('\n', '').split(': ')[1:]
            self.message = ': '.join(message).replace('[', ' ').replace(']', '')
            time, self.process = info.replace('[', '').replace(']', '').split(' ')[0], ' '.join(info.replace('[', '').replace(']', '').split(' ')[1:])
            now = datetime.datetime.now()
            self.time = datetime.datetime(now.year, now.month, now.day, *[int(num) for num in time.split(':')])
        else:
            raise ValueError('Not a recognized event,', self.raw)

        self.type = self._event_type()

    def _event_type(self) -> Union[str, None]:
        msg_comps = self.message.split(' ')
        try:
            Player(msg_comps[0])  # Check if valid player from Mojang.
            if msg_comps[1] == 'left':
                return 'player_leave'
            elif msg_comps[1] == 'joined':
                return 'player_join'
            elif ' '.join(msg_comps[1:3]) == 'lost connection':
                return 'player_disconnect'
            elif msg_comps[1].startswith('/'):
                return 'player_connect'
        except ValueError:
            print(' '.join(msg_comps[0:3]), 'Preparing spawn area')
            if ' '.join(msg_comps[0:3]) == 'Preparing spawn area':
                return 'spawn_prep'
            if msg_comps[0] == 'Done':
                return 'ready'
            if ' '.join(msg_comps[0:3]) == 'Can\'t keep up!':
                return 'ticks_behind'
            if ' '.join(msg_comps[0:6]) == 'Considering it to be crashed,':
                return 'crash'
            if msg_comps[0].startswith('<') and msg_comps[0].endswith('>'):
                try:
                    Player(msg_comps[0].replace('<', '').replace('>', ''))
                    return 'player_msg'
                except ValueError:
                    return str(None)

    @property
    def ctx(self):
        return [self.time, self._parse_message(self.message)]

    def _parse_message(self, message: str):
        pass


class Parser(io.TextIOBase):
    def __init__(self):
        self._events = []
        self._writable = True
        self._readable = True

    def fileno(self) -> int:
        return 1

    def readable(self) -> bool:
        return self._readable

    def read(self, __size: Optional[int] = ...) -> str:
        return '\n'.join(self._events)

    def readlines(self, __hint: int = ...) -> List[str]:
        return self._events[:__hint]

    def readline(self, __size: int = ...) -> str:
        return self._events[__size]

    def write(self, __s: str) -> int:
        self.events = __s.split('\n')
        return len(self.events)

    def writelines(self, __lines: List[str]) -> None:
        self.events = __lines

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, events: list):
        print(events, sep='\n')
        print()
        # self.process_events(events)
        self._events = events

    def process_events(self, events):
        for raw_event in events:
            try:
                event = Event(raw_event)
                for attr in self.__dict__:
                    if attr == 'on_' + event.type:
                        self.__dict__[attr](*event.ctx)

            except Exception as err:
                self.on_parsing_error(err, raw_event)

    def on_ready(self, time, startup_time):
        print('ready')

    def on_spawn_prep(self, completion_percent: float):
        print('prep')

    def on_player_join(self, time, player):
        print('join')

    def on_player_connect(self, time, player):
        print('connect')

    def on_player_leave(self, time, player):
        print('leave')

    def on_player_disconnect(self, time, player):
        print('disconnect')

    def on_ticks_behind(self, time, ticks):
        print('behind')

    def on_command(self, time, command):
        print('command')

    def on_player_message(self, time, player, message):
        print('message')

    def on_crash(self):
        print('crashed')

    def on_parsing_error(self, err, raw_event):
        print(err.__class__.__name__, err, raw_event)