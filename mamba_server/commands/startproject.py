import os


def run(args):
    project_name = args[0]

    os.mkdir(project_name)
    os.mkdir(os.path.join(project_name, 'components'))
    os.mkdir(os.path.join(project_name, 'components', 'drivers'))
    os.mkdir(os.path.join(project_name, 'components', 'gui'))

    print(f"New Mamba project created in: {project_name}")
    print("You can create your first component with:")
    print("    cd %s" % project_name)
    print("    mamba gencomponent example")
