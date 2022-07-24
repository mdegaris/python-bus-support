
import re
import os
import json
import sys
import subprocess


SCRIPT_NAME = os.path.basename(__file__)
MAJOR_MINOR_REGEX = re.compile(r'^(\d)\.(\d+)$')


class Args(object):

    CHECK_EXISTS = '--check-exists'
    HAS_MODULES = '--has-modules'

    def __init__(self):
        self.conf_file = None
        self.version = None
        self.arch = None
        self.option1 = None
        self.option2 = None


def exit_print_usage():
    """ Output usage text and exit. """

    print("Usage: {} [conf_file] [version] [arch] [options]".format(SCRIPT_NAME))
    print("Options:")
    print("--check-exists")
    print("--has-modules [module]")
    print("\nE.g {} python.conf 2.7 64 --exists".format(SCRIPT_NAME))

    sys.exit()


def read_conf(conf_filename):
    """ Read a given JSON conf file. """

    if os.path.exists(conf_filename):
        with open(conf_filename) as fp:
            return json.load(fp)


def major_minor_version(v):
    """ Parse a majar.minor version string
        and return the (major,minor) as a tuple. """

    match = MAJOR_MINOR_REGEX.match(v)

    if match:
        major = match.group(1)
        minor = match.group(2)
        return (int(major), int(minor))


def version_compare(subject, target):
    """  """

    if subject and target:
        s_major, s_minor = major_minor_version(subject)
        t_major, t_minor = major_minor_version(target)
        return (s_major == t_major) and (s_minor == t_minor)


def valid_arch(arch):
    return str(arch) in ['32', '64']


def arch_compare(subject, target):
    if subject and target:
        return (int(subject) == int(target))


def get_python_path(conf, version, arch):
    for c in conf:
        if version_compare(version, c['version']):
            if valid_arch(arch) and arch == c['arch']:
                return c['path']


def clean_module_list(modules):

    module_list = [m.strip() for m in modules.split(',')]
    return ','.join(module_list)


def check_exists(conf, version, arch):
    path = get_python_path(conf, version, arch)
    return (path is not None) and os.path.exists(path)


def check_modules(conf, version, arch, modules):
    path = get_python_path(conf, version, arch)

    if path:
        command = "import {m}".format(m=clean_module_list(modules))
        with open(os.devnull, 'w') as devnull:
            process = subprocess.call([path, '-c', command], stderr=devnull)
            return process == 0

    return False


def do_exit(test):
    # print(str(test))
    if test:
        sys.exit(0)
    sys.exit(1)


def process(args):

    conf_json = read_conf(args.conf_file)

    if args.option1 == Args.CHECK_EXISTS:
        do_exit(check_exists(conf_json, args.version, args.arch))

    if args.option1 == Args.HAS_MODULES and args.option2:
        modules = args.option2
        do_exit(check_modules(conf_json, args.version, args.arch, modules))

    do_exit(False)


if __name__ == "__main__":
    if (len(sys.argv)) <= 1:
        exit_print_usage()

    arguments = Args()
    for (i, arg) in enumerate(sys.argv):
        if i == 1:
            arguments.conf_file = arg
        if i == 2:
            arguments.version = arg
        if i == 3:
            arguments.arch = arg
        if i == 4:
            arguments.option1 = arg
        if i == 5:
            arguments.option2 = arg

    process(arguments)
