import datetime
import json
import os
import subprocess
import time

from .parser import Parser


class Server:
    def __init__(self, jar_path: str, min_RAM: str = '1G', max_RAM: str = '3G', parser=None, update_wait: int = 3):
        if parser is None:
            parser = Parser()

        self.update_wait = update_wait
        self.parser = parser
        self.max_RAM = max_RAM
        self.min_RAM = min_RAM
        self.jar = jar_path

        self._server = None
        self._old_events = 0

        self.online = False

        self.abs_cwd, self.jar = os.path.split(self.jar)
        if not os.path.isabs(self.abs_cwd):
            self.abs_cwd = os.path.join(os.getcwd(), self.abs_cwd)

    def run(self):
        if (not os.path.isfile(os.path.join(self.abs_cwd, self.jar))) or (not self.jar.endswith('.jar')):
            raise OSError('{} is not a jar file.'.format(self.jar))

        self._server = subprocess.Popen(
            ' '.join(['java', f'-Xms{self.min_RAM}', f'-Xmx{self.max_RAM}', '-jar', self.jar, 'nogui']),
            cwd=self.abs_cwd,
            shell=True,
            stdout=open(os.path.join(self.abs_cwd, 'temp-log.txt'), 'w'),
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        self.online = True

        while self.online:
            self.parser.process_events(self.new_events)
            time.sleep(self.update_wait)

    @property
    def new_events(self):
        with open(os.path.join(self.abs_cwd, 'temp-log.txt'), 'r') as log:
            events = log.readlines()
        if len(events) > self._old_events:
            new_events = events[self._old_events:]
            print(len(new_events), self._old_events, len(events))
            self._old_events += len(events) - self._old_events
            return new_events
        else:
            return []

    def _exec_cmd(self, cmd, *params):
        if not self.online:
            raise OSError('Server isn\'t started yet.')

        stdout, stderr = self._server.communicate(' '.join([cmd, *params]))

        return stdout, stderr

    def killserver(self):
        self._server.kill()

    # Commands
    def run_cmd(self, *args):
        return self._exec_cmd(*args)

    def op(self):
        pass

    # Server Folder Analysis
    @property
    def properties(self):
        with open(os.path.join(self.abs_cwd, 'server.properties'), 'r') as file:
            lines = file.readlines()
        properties = {}
        for line in lines:
            if not line.startswith('#'):
                k, v = line.split('=')
                properties[k] = v
        return properties

    @properties.setter
    def properties(self, value: dict):
        with open(os.path.join(self.abs_cwd, 'server.properties'), 'w') as file:
            properties = ['='.join(item) for item in value.items()]
            file.writelines(properties)

    @property
    def banned_ips(self):
        with open(os.path.join(self.abs_cwd, 'banned-ips.json'), 'r') as file:
            banned_ips = json.load(file)
        return banned_ips

    @property
    def banned_players(self):
        with open(os.path.join(self.abs_cwd, 'banned-players.json'), 'r') as file:
            banned_players = json.load(file)
        return banned_players

    @property
    def ops(self):
        with open(os.path.join(self.abs_cwd, 'ops.json'), 'r') as file:
            ops = json.load(file)
        return ops
