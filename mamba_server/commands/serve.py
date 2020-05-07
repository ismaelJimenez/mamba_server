from mamba_server.commands import MambaCommand

from mamba_server.main_window import execute


class Command(MambaCommand):
    def short_desc(self):
        return "Start mamba server"

    def run(self, args):
        execute()
