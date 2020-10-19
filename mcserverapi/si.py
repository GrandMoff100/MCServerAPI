import json
import os
import subprocess
import atexit
import sys
import psutil
import socket
import multiprocessing
import colorama
import time


class Server:
    def __init__(self, jar_path: str, stdout=None, stderr=None, java_path='java'):
        self.jar = jar_path

        self._java = java_path

        self.process = None
        self._log = 'temp-log.txt'

        self.abs_cwd, self.jar = os.path.split(self.jar)
        if not os.path.isabs(self.abs_cwd):
            self.abs_cwd = os.path.join(os.getcwd(), self.abs_cwd)

        try:
            file = open(os.path.join(self.abs_cwd, self._log), 'r+')
        except FileNotFoundError:
            file = open(os.path.join(self.abs_cwd, self._log), 'w+')
        finally:
            atexit.register(os.remove, os.path.join(self.abs_cwd, self._log))

        self.stdout = file if stdout is None else stdout
        self.sterr = file if stdout is None else stderr
        self.stdin = subprocess.PIPE

    def online(self):
        return True if self.process.returncode is None else False

    def _check_for_conflicting_procs(self):
        if os.path.exists(os.path.join(self.abs_cwd, self._log)):
            os.remove(os.path.join(self.abs_cwd, self._log))
            with open(os.path.join(self.abs_cwd, self._log), 'w') as file:
                pass
        for proc in psutil.process_iter():
            if 'server.jar' in proc.cmdline():
                print(colorama.RED + 'There is another Server Process already running, please terminate that and run this again.')
                time.sleep(5)
                exit()
                

    def start(self, *java_args, **java_flags):
        self._check_for_conflicting_procs()

        if (not os.path.isfile(os.path.join(self.abs_cwd, self.jar))) or (not self.jar.endswith('.jar')):
            raise OSError('{} is not a jar file.'.format(self.jar))

        if 'nogui' in java_args:
            java_args.remove('nogui')
        
        
        # noinspection PyTypeChecker
        self.process = subprocess.Popen(
            ' '.join([self._java, *java_args, *[' '.join(str(k), str(v)) for k,v in java_flags.items()], '-jar', self.jar, 'nogui']),
            cwd=self.abs_cwd,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.sterr,
            shell=True
        )

        sys.stdin = self.process.stdin

        atexit.register(self.process.terminate)

    def _exec_cmd(self, cmd, *params):
        if not self.online:
            raise OSError('Server isn\'t started yet.')
        self.process.stdin.write(bytes(' '.join([cmd, *params]), 'utf-8') + b'\n')
        self.process.stdin.flush()

    def hardstop(self):
        self.process.terminate()

    # Commands
    def run_cmd(self, *args):
        self._exec_cmd(*args)

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
    def properties(self, properties: dict):
        with open(os.path.join(self.abs_cwd, 'server.properties'), 'w') as file:
            properties = ['='.join(item) for item in properties.items()]
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

    @property
    def whitelist(self):
        with open(os.path.join(self.abs_cwd, 'whitelist.json'), 'r') as file:
            whitelist = json.load(file)
        return whitelist

    @property
    def usercache(self):
        with open(os.path.join(self.abs_cwd, 'usercache.json'), 'r') as file:
            usercache = json.load(file)
        return usercache



