import subprocess
import threading
import os
import json


class Server:
    def __init__(self, jar_path: str, min_RAM: str = '1G', max_RAM: str = '3G'):
        self.max_RAM = max_RAM
        self.min_RAM = min_RAM
        self.jar = jar_path

        self._server = None
        self.output = []

        self.online = False

        self.abs_cwd, self.jar = os.path.split(self.jar)
        if not os.path.isabs(self.abs_cwd):
            self.abs_cwd = os.path.join(os.getcwd(), self.abs_cwd)

    def _start(self):
        if (not os.path.isfile(os.path.join(self.abs_cwd, self.jar))) or (not self.jar.endswith('.jar')):
            raise OSError('{} is not a jar file.'.format(self.jar))

        self._server = subprocess.Popen(
            ' '.join(['java', f'-Xms{self.min_RAM}', f'-Xmx{self.max_RAM}', '-jar', self.jar, 'nogui']),
            cwd=self.abs_cwd,
            shell=True,
            stdout=open(os.path.join(self.abs_cwd,'temp-log.txt'), 'w'),
            stderr=subprocess.PIPE,
            stdin=open(os.path.join(self.abs_cwd,'terminal-stdin.txt'), 'w')
        )
        self.online = True

    def start(self):
        threading.Thread(target=self._start, name=self.jar).start()

    @property
    def events(self):
        with open(os.path.join(self.abs_cwd, 'temp-log.txt'), 'r') as log:
            events = log.readlines()

        for index in range(len(events)):
            ctx, event = events[index].strip('[').strip(']').split(':')
            time, origin = ctx.split(' ')
            yield {
                'time': time,
                'origin': origin,
                'message': event
            }

    @property
    def is_started(self):
        threads = [thread.name for thread in threading.enumerate()]
        return True if self.jar in threads else False

    def _exec_cmd(self, cmd, *params):
        if not cmd.startswith('/'):
            cmd = '/' + cmd

        if not self.is_started:
            raise OSError('Server isn\'t started yet.')

        stdout, stderr = self._server.communicate(' '.join([cmd, *params]))

        return stdout, stderr

    def killshell(self):
        self._server.kill()

    # Commands
    def execute(self, *args):
        return self._exec_cmd(*args)

    def say(self, message: str):
        return self._exec_cmd('say', message)

    def ban(self, player, reason: str = ''):
        if reason != '':
            return self._exec_cmd('ban', player, reason)
        else:
            return self._exec_cmd('ban', player)

    def unban(self, player):
        return self._exec_cmd('pardon', player)

    def stop(self):
        return self._exec_cmd('stop')

    def op(self, player):
        return self._exec_cmd('op', player)

    def deop(self, player):
        return self._exec_cmd('deop', player)

    def datapack(self, sub, datapack):
        return self._exec_cmd('datapack', sub, datapack)

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





