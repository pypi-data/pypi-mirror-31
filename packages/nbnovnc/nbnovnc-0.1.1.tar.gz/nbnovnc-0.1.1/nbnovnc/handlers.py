import configparser
import os
import socket
import tempfile

from notebook.utils import url_path_join as ujoin

from traitlets import Unicode, Integer
from traitlets.config.configurable import Configurable

from nbserverproxy.handlers import AddSlashHandler, SuperviseAndProxyHandler

class SupervisorHandler(SuperviseAndProxyHandler):
    '''Supervise supervisord.'''

    name = 'supervisord'

    def supervisor_config(self):
        config = configparser.ConfigParser()
        config['supervisord'] = {}
        return config

    def write_conf(self):
        config = self.supervisor_config()
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        config.write(f)
        f.close()
        return f.name

    def get_cmd(self):
        filename = self.write_conf()
        return [ "supervisord", "-c", filename, "--nodaemon" ]

class NBNoVNC(Configurable):
    geometry = Unicode(u"1024x768", help="Desktop geometry.", config=True)
    depth = Integer(24, help="Desktop display depth.", config=True)
    novnc_directory = Unicode(u"/usr/share/novnc", config=True,
        help="Path to noVNC web assets.")
    vnc_command = Unicode(u"xinit -- /usr/bin/Xtightvnc :{display} -geometry {geometry} -depth {depth}", config=True,
        help="Command to start VNC server. Contains string replacement fields.")
    websockify_command = Unicode(u"websockify --web {novnc_directory} --heartbeat {heartbeat} {port} localhost:{vnc_port}", config=True,
        help="websockify command. Contains string replacement fields.")

class NoVNCHandler(SupervisorHandler):
    '''Supervise novnc, websockify, and a VNC server.'''
    def initialize(self, state):
        super().initialize(state)
        self.c = NBNoVNC(config=self.config)
        # This is racy because we don't immediately start the VNC server.
        self.vnc_port = self.random_empty_port()

    def random_empty_port(self):
        '''Allocate a random empty port for use by the VNC server.'''
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    @property
    def display(self):
        return self.vnc_port-5900

    def get_env(self):
        return { 'DISPLAY': ':' + str(self.display) }

    def supervisor_config(self):
        config = super().supervisor_config()
        config['program:vnc'] = {
            'command': self.c.vnc_command.format(
                display=self.display,
                geometry=self.c.geometry,
                depth=self.c.depth
            ),
            'priority': 10,
        }
        config['program:websockify'] = {
            'command': self.c.websockify_command.format(
                novnc_directory=self.c.novnc_directory,
                heartbeat=30,
                port=self.port,
                vnc_port=self.vnc_port
            ),
            'priority': 20,
        }
        return config

    async def get(self, path):
        '''
        When clients visit novnc/, actually get novnc/vnc_auto.html
        or novnc/vnc_lite.html from our proxied service instead.
        '''
        if len(path) == 0:
            for f in ['vnc_auto.html', 'vnc_lite.html']:
                if os.path.exists(os.path.join(self.c.novnc_directory, f)):
                    path = f
                    break
        return await super().get(path)

def setup_handlers(web_app):
    web_app.add_handlers('.*', [
        (ujoin(web_app.settings['base_url'], 'novnc/(.*)'), NoVNCHandler,
            dict(state={})),
        (ujoin(web_app.settings['base_url'], 'novnc'), AddSlashHandler)
    ])

# vim: set et ts=4 sw=4:
