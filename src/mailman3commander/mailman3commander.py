#!/usr/bin/env python3
#
# Mailman 3 Commander
# A simple menu-based console tool designed to simplify Mailman3 management
#
# Author: Arturo 'Buanzo' Busleiman <buanzo@buanzo.com.ar>
#

__version__ = '0.1.0'
__author__ = 'Buanzo <buanzo@buanzo.com.ar> https://github.com/buanzo'

import sys
import time
import tqdm
import argparse
import configparser
from mailmanclient import Client
from simple_term_menu import TerminalMenu
from pprint import pprint
from buanzobasics.buanzobasics import printerr, pprinterr


class Mailman3Commander():
    def __init__(self, configpath):
        self.configpath = configpath
        self.MMI_STR_VIEW_GLOBAL_CONF = 'View Global Mailman3 Configuration'
        self.MMI_STR_QUIT = 'End Mailman 3 Commander'
        self.MMI_STR_SEPARATOR = '------------------------------'

    def valid_config(self):
        # Reads the config file indicated by configpath argument
        config = configparser.ConfigParser()
        try:
            config.read(self.configpath)
        except Exception as exc:
            printerr('Exception reading {}'.format(self.configpath))
            printerr(exc)
            return(False)

        if 'webservice' not in config:
            printerr('No webservice section found: {}'.format(self.configpath))
            printerr('Are you sure this is the correct path?')
            return(False)

        # Get parameters for Mailman3 REST API URL:
        https = config['webservice'].getboolean('use_https')
        host = config['webservice']['hostname']
        port = config['webservice'].getint('port')
        user = config['webservice']['admin_user']
        pw = config['webservice']['admin_pass']
        s = 'http'
        if https:
            s = 'https'
        # Now build the URL:
        url = '{schema}://{host}:{port}'.format(schema=s, host=host, port=port)

        # And test it using the credentials:
        try:
            client = Client('http://localhost:8001/3.1', user, pw)
        except Exception as exc:
            printerr('Exception accesing REST API URL = {}'.format(url))
            printerr(exc)
            return(False)
        if 'api_version' in client.system.keys():
            self.mmclient = client
            return(True)
        return(False)

    def main_menu(self):
        title = "---[ Main Menu @ Mailman 3 Commander ]----------------\n"
        items = []
        cursor = "> "
        cursor_style = ("fg_blue", "bold")
        menu_style = ("bg_blue", "fg_yellow")
        for lista in self.mmclient.lists:
            items.append('Manage {}'.format(lista.fqdn_listname))
        items.append(self.MMI_STR_SEPARATOR)
        items.append(self.MMI_STR_VIEW_GLOBAL_CONF)
        items.append(self.MMI_STR_QUIT)

        main_menu = TerminalMenu(menu_entries=items,
                                 title=title,
                                 menu_cursor=cursor,
                                 menu_cursor_style=cursor_style,
                                 menu_highlight_style=menu_style,
                                 cycle_cursor=True,
                                 clear_screen=True)
        ret = main_menu.show()
        if ret is None:
            return(None)
        return(items[ret])

    def view_mm3_config(self):
        title = "---[ MM3 Configuration Browser @ Mailman 3 Commander ]----------------\n"
        cursor = "> "
        cursor_style = ("fg_blue", "bold")
        menu_style = ("bg_blue", "fg_yellow")
        menu_exit = False
        items = []
        for mainkey in sorted(self.mmclient.configuration):
            items.append('- [ {} ]'.format(mainkey))
            # print('- [ {} ]'.format(mainkey))
            for key in sorted(self.mmclient.configuration[mainkey]):
                items.append('  {}: {}'.format(key, self.mmclient.configuration[mainkey][key]).replace('\n','\\n'))
                # print('  {}: {}'.format(key,self.mmclient.configuration[mainkey][key]))
        while not menu_exit:
            main_menu = TerminalMenu(menu_entries=items,
                                     title=title,
                                     menu_cursor=cursor,
                                     menu_cursor_style=cursor_style,
                                     menu_highlight_style=menu_style,
                                     cycle_cursor=False,
                                     clear_screen=True)
            ret = main_menu.show()
            if ret is None:
                menu_exit = True

    def main_loop(self):
        # The main loop presents the main menu and handles exiting.
        # https://docs.mailman3.org/projects/mailmanclient/en/latest/src/mailmanclient/docs/using.html
        #
        # General description:
        # Choose a mailing list -> Membership management, Approve/defer/etc messages, list configuration
        # Browser Mailman3 configuration (no changes allowed)
        main_menu_exit = False
        while not main_menu_exit:
            msel = self.main_menu()
            if msel == self.MMI_STR_QUIT or msel is None:
                sys.exit(0)
            elif msel == self.MMI_STR_VIEW_GLOBAL_CONF:
                self.view_mm3_config()
            elif msel.startswith('Manage '):
                print('will {}'.format(msel))
                time.sleep(5)
            else:
                print('Unknown option')
                time.sleep(5)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version',
                        action='version',
                        version='Mailman3 Commander v{} by {}'.format(__version__, __author__))
    parser.add_argument('--config', '-c',
                        default='/etc/mailman3/mailman.cfg',
                        help='Path to mailman.cfg - Defaults to /etc/mailman3/mailman.cfg',
                        required=False,
                        dest='configpath')
    args = parser.parse_args()
    m3c = Mailman3Commander(configpath=args.configpath)
    if not m3c.valid_config():
        print('Mailman3 configuration not found or invalid: {}'.format(args.configpath))
        sys.exit(1)
    m3c.main_loop()


if __name__ == '__main__':
    run()