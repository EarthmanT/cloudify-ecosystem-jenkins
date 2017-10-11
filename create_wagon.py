#!/usr/bin/env python

import os
import ast
import sys
import tempfile
import virtualenv
import pip
pip.main(['install', '-U', 'pip'])
pip.main(['install', 'wagon==0.3.2'])
from wagon import wagon


if __name__ == '__main__':

    # Create and initialize a virtual environment.
    venv_create_args = os.environ.get('venv_create_args')
    _home_dir = venv_create_args.get('home_dir')
    if not _home_dir:
        _home_dir = tempfile.mkdtemp()
        venv_create_args['home_dir'] = _home_dir
    virtualenv.create_environment(**venv_create_args)
    init_file = os.path.join(_home_dir, 'bin', 'activate_this.py')
    execfile(init_file, dict(__file__=init_file))

    # Arguments for creating the wagon.
    wagon_source = os.environ.get('wagon_source')
    wagon_create_args = os.environ.get('wagon_create_args')
    _archive_destination_dir = wagon_create_args.get('archive_destination_dir')
    if _archive_destination_dir is None:
        _archive_destination_dir = tempfile.gettempdir()
    if not os.path.exists(_archive_destination_dir):
        os.mkdir(_archive_destination_dir)
    wagon_create_args['archive_destination_dir'] = _archive_destination_dir

    if not isinstance(wagon_source, basestring):
        print "The wagon source %s is not valid" % str(wagon_source)
        sys.exit(os.EX_USAGE)

    if isinstance(wagon_create_args, basestring):
        try:
            wagon_create_args = ast.literal_eval(wagon_create_args)
        except SyntaxError:
            print "The wagon_create_args structure %s is not valid." % str(wagon_create_args)
            sys.exit(os.EX_USAGE)

    w = wagon.Wagon(source=wagon_source)

    try:
        build_wagon_output = w.create(**wagon_create_args)
        print build_wagon_output
    except KeyError as e:
        print "Failed to create wagon because: %s." % str(e)
        sys.exit(os.EX_CANTCREAT)

    if not build_wagon_output:
        raise Exception('Wagon output: {0}'.format(build_wagon_output))

    sys.exit(os.EX_OK)

