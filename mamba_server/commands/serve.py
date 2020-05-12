import os
from mamba_server.commands import MambaCommand

from mamba_server.context_composer import execute


class Command(MambaCommand):
    @staticmethod
    def short_desc():
        return "Start mamba server"

    @staticmethod
    def run(args):
        execute(os.path.join('launch', 'default_tk.launch.json'))
