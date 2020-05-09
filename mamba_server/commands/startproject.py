import os

from mamba_server.commands import MambaCommand


class Command(MambaCommand):
    def syntax(self):
        return "<project_name>"

    def short_desc(self):
        return "Create new project"

    def run(self, args):
        project_name = args[0]

        os.mkdir(project_name)
        os.mkdir(os.path.join(project_name, 'components'))
        os.mkdir(os.path.join(project_name, 'components', 'drivers'))
        os.mkdir(os.path.join(project_name, 'components', 'gui'))

        print("New Mamba project created in: {}".format(project_name))
        print("You can create your first component with:")
        print("    cd %s" % project_name)
        print("    mamba gencomponent example")
