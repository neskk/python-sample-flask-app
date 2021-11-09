#!/usr/bin/python
# -*- coding: utf-8 -*-

import configargparse
import os
import sys


class Config:
    """ Singleton class that parses and holds all the configuration arguments """
    __args = None

    @staticmethod
    def get_args():
        """ Static access method """
        if Config.__args == None:
            Config()
        return Config.__args

    def __init__(self):
        """ Parse config/cli arguments and setup workspace """
        if Config.__args != None:
            raise Exception("This class is a singleton!")
        else:
            Config.__args = get_args()
            self.__setup_workspace()

    def __setup_workspace(self):
        if not os.path.exists(self.__args.log_path):
            # Create directory for log files.
            os.mkdir(self.__args.log_path)

        if not os.path.exists(self.__args.download_path):
            # Create directory for downloaded files.
            os.mkdir(self.__args.download_path)


def get_args():
    default_config = []
    app_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..'))
    config_file = os.path.normpath(
        os.path.join(app_path, 'config/config.ini'))

    if '-cf' not in sys.argv and '--config' not in sys.argv:
        default_config = [config_file]
    parser = configargparse.ArgParser(default_config_files=default_config)

    parser.add_argument('-cf', '--config',
                        is_config_file=True, help='Set configuration file.')
    parser.add_argument('-v', '--verbose',
                        help='Run in the verbose mode.',
                        action='store_true')
    parser.add_argument('--log-path',
                        help='Directory where log files are saved.',
                        default='logs')
    parser.add_argument('--download-path',
                        help='Directory where download files are saved.',
                        default='downloads')

    group = parser.add_argument_group('Database')
    group.add_argument('--db-name',
                       env_var='MYSQL_DATABASE',
                       help='Name of the database to be used.',
                       required=True)
    group.add_argument('--db-user',
                       env_var='MYSQL_USER',
                       help='Username for the database.',
                       required=True)
    group.add_argument('--db-pass',
                       env_var='MYSQL_PASSWORD',
                       help='Password for the database.',
                       required=True)
    group.add_argument('--db-host',
                       env_var='MYSQL_HOST',
                       help='IP or hostname for the database.',
                       default='127.0.0.1')
    group.add_argument('--db-port',
                       env_var='MYSQL_PORT',
                       help='Port for the database.',
                       type=int, default=3306)

    group = parser.add_argument_group('Worker')
    group.add_argument('-mc', '--max-concurrency',
                       help=('Maximum concurrent worker threads. '
                             'Default: 100.'),
                       default=100,
                       type=int)
    group.add_argument('-ni', '--notice-interval',
                       help=('Print manager statistics every X seconds. '
                             'Default: 60.'),
                       default=60,
                       type=int)
    group.add_argument('-p', '--protocol',
                       help=('Specify the protocol we are using. ' +
                             'Default: socks.'),
                       default='socks',
                       choices=('http', 'socks', 'all'))
    args = parser.parse_args()

    if args.verbose:
        parser.print_values()

    return args
