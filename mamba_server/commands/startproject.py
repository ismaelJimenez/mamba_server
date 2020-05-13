import os

from mamba_server.commands import MambaCommand


class Command(MambaCommand):
    @staticmethod
    def syntax():
        return "<project_name>"

    @staticmethod
    def short_desc():
        return "Create new project"

    @staticmethod
    def run(args, opts, mamba_dir):
        project_name = args[0]

        os.mkdir(project_name)
        with open(os.path.join(project_name, 'mamba.cfg'), 'w') as fp:
            pass
        os.mkdir(os.path.join(project_name, 'components'))
        with open(os.path.join(project_name, 'components', '__init__.py'),
                  'w') as fp:
            pass
        os.mkdir(os.path.join(project_name, 'components', 'drivers'))
        os.mkdir(os.path.join(project_name, 'components', 'gui'))

        print("New Mamba project created in: {}".format(project_name))
        print("You can create your first component with:")
        print("    cd %s" % project_name)
        print("    mamba gencomponent example")
