#!/usr/bin/env python3
#
# Mailman 3 Commander
# A simple menu-based console tool designed to simplify Mailman3 management
#
# Author: Arturo 'Buanzo' Busleiman <buanzo@buanzo.com.ar>
#

from . import __version__
__author__ = 'Buanzo <buanzo@buanzo.com.ar> https://github.com/buanzo'

import sys
import time
import argparse
import configparser
import logging
import shutil
from mailmanclient import Client
from simple_term_menu import TerminalMenu
from buanzobasics.buanzobasics import valueOrDefault
from email import policy
from email.parser import BytesParser

def _T(msgid):
    # Proxy for i18n
    return(msgid)

class Mailman3Commander():
    def __init__(self, configpath):
        self.configpath = configpath
        self.MMI_KEY_VIEW_GLOBAL_CONF = 'alt-g'
        self.MMI_KEY_QUIT = 'alt-q'
        self.MMI_KEY_DELETE_LIST = 'alt-d'
        self.MMI_KEY_MANAGE_LIST = 'm'
        self.MMI_KEY_MODERATION_TASKS = 'p'
        self.MMI_KEY_CONFIG_LIST = 'c'
        self.MMI_STR_SEPARATOR = '------------------------------'
        # self.build_menu() will update this instance reference:
        self.built_menu = None

    def valid_config(self):
        # Reads the config file indicated by configpath argument
        config = configparser.ConfigParser()
        try:
            config.read(self.configpath)
        except Exception as exc:
            logging.error(_T('Exception reading {}: {}').format(self.configpath, exc))
            return(False)

        if 'webservice' not in config:
            logging.error(_T('No webservice section found: {}').format(self.configpath))
            logging.error(_T('Are you sure this is the correct path?'))
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
        api_url = f"{url}/3.1"
        try:
            client = Client(api_url, user, pw)
        except Exception as exc:
            logging.error(_T('Exception accessing REST API URL = {}: {}').format(api_url, exc))
            return(False)
        if 'api_version' in client.system.keys():
            self.mmclient = client
            return(True)
        return(False)

    def main_menu(self):
        """ The main difference between main_menu and main_menu2 is that
        we will support Quick Shortcut Assignment as described here:
        https://github.com/IngoMeyer441/simple-term-menu/issues/8
        This allows us to remove items from the menu, and only keep
        mailing lists there. The removed items will be assigned special
        shortcuts:
        Alt+G - View Global Configuration
        Alt+Q - Quit
        
        Additionally, each menu item (now only consisting of mailing
        lists) will support this shortcuts:
        m/M   - Membership Management
        p/P   - Pending Requests [aka moderation]
        c/C   - List Configuration
        Alt+D - Delete List
        ENTER - Mailing List specific submenu, with items corresponding to
                those described above [list config, requests, membership, etc]
        """
        title = "---[ {} @ Mailman 3 Commander ]----------------\n".format(_T('Main Menu'))
        items = []
        cursor = "> "
        cursor_style = ("fg_blue", "bold")
        menu_style = ("bg_blue", "fg_yellow")
        for lista in self.mmclient.lists:
            items.append(lista.fqdn_listname)
        main_menu = TerminalMenu(menu_entries=items,
                                 title=title,
                                 menu_cursor=cursor,
                                 menu_cursor_style=cursor_style,
                                 menu_highlight_style=menu_style,
                                 show_shortcut_hints=True,
                                 cycle_cursor=True,
                                 clear_screen=True,
                                 accept_keys=("enter",
                                              self.MMI_KEY_VIEW_GLOBAL_CONF,
                                              self.MMI_KEY_QUIT,
                                              self.MMI_KEY_DELETE_LIST,
                                              self.MMI_KEY_MANAGE_LIST,
                                              self.MMI_KEY_MODERATION_TASKS,
                                              self.MMI_KEY_CONFIG_LIST))
        ret = main_menu.show()
        ck = main_menu.chosen_accept_key
        lista = items[ret]
        return((ck,lista))
        

    def build_menu(self, args, items, preview=None, preview_size=0.25):
        # This function creates a menu.
        # Parameters:
        # args: dict with title and optionally cursor, cursor_style, menu_style
        # itemFunc: a function that populates the menu items
        # example call:
        #
        # sel = self.build_menu({'title': 'Numbers from 1 to 10'}, range(10))
        #
        # Returns:
        # (item_number, item_text)
        title = args['title']
        cursor = valueOrDefault(args, 'cursor', "> ")
        cursor_style = valueOrDefault(args, 'cursor_style', ("fg_blue", "bold"))
        menu_style = valueOrDefault(args, 'menu_style', ("bg_blue", "fg_yellow"))
        cycle_cursor = valueOrDefault(args, 'cycle_cursor', True)
        clear_screen = valueOrDefault(args, 'clear_screen', True)
        menu_exit = False
        while not menu_exit:
            self.built_menu = TerminalMenu(menu_entries=items,
                                           title=title,
                                           menu_cursor=cursor,
                                           menu_cursor_style=cursor_style,
                                           menu_highlight_style=menu_style,
                                           cycle_cursor=cycle_cursor,
                                           clear_screen=clear_screen,
                                           preview_command=preview,
                                           preview_size=preview_size)
            ret = self.built_menu.show()
            if ret is None:
                return((None,None))
            else:
                return((ret,items[ret]))

    def get_mm3config_section(self,mainkey):
        items = []
        for key in sorted(self.mmclient.configuration[mainkey]):
            items.append('  {}: {}'.format(key, self.mmclient.configuration[mainkey][key]).replace('\n','\\n'))
        return(items)
        
    def get_mm3config_items(self):
        items = []
        for mainkey in sorted(self.mmclient.configuration):
            items.append(mainkey)
        return(items)

    def view_mm3_config(self):
        args = {}
        args['cycle_cursor'] = False
        args['title'] = """
\033[1;37;44m---[ {} @ Mailman 3 Commander ]----------------\033[0;39;49m\n
{}\n""".format(_T('Global Configuration Browser'),
               _T('Choose a section from the menu, or hit ESC to go back'))
        menu_exit = False
        while not menu_exit:
            v,n = self.build_menu(args, self.get_mm3config_items())
            if v is not None and v >= 0:
                a = self.build_menu(args, self.get_mm3config_section(n))
            elif v is None:
                menu_exit = True

    def membership_management_menu(self, lista):
        args = {}
        args['cycle_cursor'] = False
        args['title'] = """
\033[1;37;44m---[ {} {} @ Mailman 3 Commander ]----------------\033[0;39;49m\n
""".format(lista, _T('Membership'))
        mmlist = self.mmclient.get_list(lista)
        items = [_T('Add Member'), '-------------------------']
        member_addresses = []
        for member in mmlist.members:
            items.append('{} {}'.format(_T('Manage'), member.address))
            member_addresses.append(member.address)
        menu_exit = False
        while not menu_exit:
            v,n = self.build_menu(args, items)
            if v is not None and v == 0: # Top option
                self.add_member_menu(lista)
            elif v is not None and v > 1: # avoid separator
                idx = v - 2
                if idx < len(member_addresses):
                    self.list_member_menu(lista, member_addresses[idx])
            elif v is None:
                menu_exit = True

    def list_configuration_menu(self, lista):
        args = {}
        args['cycle_cursor'] = False
        args['title'] = """
\033[1;37;44m---[ {} {} @ Mailman 3 Commander ]----------------\033[0;39;49m\n
Choose a setting to change.
Be advised: newlines below are filtered to avoid menu issues:
""".format(lista, _T('Settings'))
        mmlist = self.mmclient.get_list(lista)
        items = []
        keys = []
        for key in sorted(mmlist.settings):
            items.append('  {}: {}'.format(key, mmlist.settings[key]))
            keys.append(key)
        menu_exit = False
        while not menu_exit:
            v,n = self.build_menu(args, items)
            if v is not None and v >= 0 and v < len(keys):
                self.list_setting_menu(lista, keys[v])
            elif v is None:
                menu_exit = True

    def add_member_menu(self, lista):
        """Subscribe a new member to the list."""
        mmlist = self.mmclient.get_list(lista)
        email = input(_T('Enter the email address to subscribe: ')).strip()
        if email == '':
            return
        try:
            # Use email for both email and display name and pre-approve
            mmlist.subscribe(email, email, pre_verified=True, pre_confirmed=True, pre_approved=True)
            print(_T('Member {} added to {}').format(email, lista))
        except Exception as exc:
            logging.error(_T('Error subscribing {}: {}').format(email, exc))
        input(_T('Press Enter to continue'))

    def list_member_menu(self, lista, address):
        """Manage an existing member of a list."""
        args = {}
        args['title'] = """\033[1;37;44m---[ {} {} @ Mailman 3 Commander ]----------------\033[0;39;49m\n""".format(address, _T('Member'))
        args['cycle_cursor'] = False
        items = [_T('Remove from list')]
        v,n = self.build_menu(args, items)
        if v is not None and items[v] == _T('Remove from list'):
            confirm = input(_T('Type "yes" to confirm removal of {}: ').format(address))
            if confirm.lower().startswith('y'):
                try:
                    mmlist = self.mmclient.get_list(lista)
                    mmlist.unsubscribe(address)
                    print(_T('{} removed').format(address))
                except Exception as exc:
                    logging.error(_T('Error removing {}: {}').format(address, exc))
                input(_T('Press Enter to continue'))

    def list_setting_menu(self, lista, key):
        """Edit a single list setting."""
        mmlist = self.mmclient.get_list(lista)
        current = mmlist.settings.get(key)
        prompt = _T('New value for {k} (current: {c}): ').format(k=key, c=current)
        newval = input(prompt)
        if newval == '':
            return
        # Attempt to convert to proper type (bool/int/float) when possible
        converted = newval
        if isinstance(current, bool):
            converted = newval.lower() in ['1', 'true', 'yes', 'on']
        else:
            try:
                if isinstance(current, int):
                    converted = int(newval)
                elif isinstance(current, float):
                    converted = float(newval)
            except ValueError:
                converted = newval
        try:
            mmlist.settings[key] = converted
            mmlist.settings.save()
            print(_T('Setting updated'))
        except Exception as exc:
            logging.error(_T('Error updating setting: {}').format(exc))
        input(_T('Press Enter to continue'))

    def delete_list_menu(self, lista):
        """Delete a mailing list after confirmation."""
        args = {}
        args['cycle_cursor'] = False
        args['title'] = """\033[1;37;44m---[ {} {} @ Mailman 3 Commander ]----------------\033[0;39;49m\n{}""".format(lista, _T('Deletion'), _T('Are you sure?'))
        items = [_T('No'), _T('Yes, delete')]
        v,n = self.build_menu(args, items)
        if v is not None and items[v] == _T('Yes, delete'):
            confirm = input(_T('Type the list name ({}) to confirm: ').format(lista))
            if confirm == lista:
                try:
                    mmlist = self.mmclient.get_list(lista)
                    mmlist.delete()
                    print(_T('List {} deleted').format(lista))
                except Exception as exc:
                    logging.error(_T('Error deleting list: {}').format(exc))
                input(_T('Press Enter to continue'))
        
    def get_held_items(self, lista):
        item_f = '{request_id:<5d} - {sender:<{avs1}} - {subject:>{avs2}}|{data}'.format
        mmlist = self.mmclient.get_list(lista)
        retObj = []
        term_cols = shutil.get_terminal_size(fallback=(80, 20)).columns
        avs = max(int((term_cols - 11) / 2), 0)
        avs1 = int(avs * 0.66)
        avs2 = avs - avs1
        for item in mmlist.held:
            rid = item._get('request_id')
            sender = item._get('sender')
            subject = item._get('subject')
            data = '{lista}:HELD:{request_id}'.format(lista=lista,
                                                      request_id=rid)
            retObj.append(item_f(request_id=rid, sender=sender, subject=subject, data=data, avs1=avs1, avs2=avs2))
        return(retObj)

    def preview_held_msg(self, datacomponent):
        # datacomponent as defined/used by simple_term_menu. see self.get_held_items()
        s = datacomponent.split(':')
        # we already know s[1]=="HELD"
        lista = s[0]
        rid = s[2]
        # Get the list
        mmlist = self.mmclient.get_list(lista)
        # From it, get held message by request_id
        msg = mmlist.get_held_message(rid)
        # Extract necessary details
        sender = msg._get('sender')
        subject = msg._get('subject')
        msgid = msg._get('message_id')
        reason = msg._get('reason')
        # MIMEparse msg._get('msg'):
        mp = BytesParser(policy=policy.default).parsebytes(msg._get('msg').encode('utf8'))
        preview_text = mp.get_body(preferencelist=('plain')).get_content()
        pre = """{t_full_subject}: {subject}
{t_msgid}: {msgid}
{t_reason}: {reason}

{preview_text}""".format(t_full_subject=_T('FULL SUBJECT'),
                         t_msgid=_T('MESSAGE ID'),
                         t_reason=_T('REASON'),
                         sender=sender,
                         subject=subject,
                         msgid=msgid,
                         reason=reason,
                         preview_text=preview_text)
        
        return(pre)

    def moderation_menu(self, lista):
        mmlist = self.mmclient.get_list(lista)
        n_items = 0
        try:
            n_items = mmlist.get_held_count()
        except (KeyError, AttributeError) as exc:
            n_items = len(mmlist.held)
        args = {}
        args['title'] = """
\033[1;37;44m---[ {} {} @ Mailman 3 Commander ]----------------\033[0;39;49m\n
{}: {}

{}
""".format(lista,
           _T('Moderation Tasks'),
           _T('Held Messages'),
           n_items,
           _T('You can choose a message below to visualize and act upon.'))
        items = self.get_held_items(lista)
        menu_exit = False
        while not menu_exit:
            v,n = self.build_menu(args, items, preview=self.preview_held_msg, preview_size=0.375)
            if v is None:
                menu_exit = True

    def manage_list_menu(self, lista):
        args = {}
        args['title'] = """
\033[1;37;44m---[ {} {} @ Mailman 3 Commander ]----------------\033[0;39;49m\n
Choose a section from the menu, or hit ESC to go back:
""".format(lista,_T('Management'))
        items = [_T('List Configuration'), _T('Membership Management'), _T('Moderation Tasks'), _T('Delete List')]
        menu_exit = False
        while not menu_exit:
            v,n = self.build_menu(args, items)
            if v is None:
                menu_exit = True
            elif items[v] == _T('List Configuration'):
                self.list_configuration_menu(lista)
            elif items[v] == _T('Membership Management'):
                self.membership_management_menu(lista)
            elif items[v] == _T('Moderation Tasks'):
                self.moderation_menu(lista)
            elif items[v] == _T('Delete List'):
                self.delete_list_menu(lista)

    def main_loop(self):
        # The main loop presents the main menu and handles exiting.
        # https://docs.mailman3.org/projects/mailmanclient/en/latest/src/mailmanclient/docs/using.html
        #
        # General description:
        # Choose a mailing list -> Membership management, Approve/defer/etc messages, list configuration
        # Browser Mailman3 configuration (no changes allowed)
        while True:
            ck,lista = self.main_menu()
            if ck == self.MMI_KEY_QUIT or ck is None:
                sys.exit(0)
            elif ck == self.MMI_KEY_VIEW_GLOBAL_CONF:
                self.view_mm3_config()
            elif ck == self.MMI_KEY_CONFIG_LIST:
                self.list_configuration_menu(lista)
            elif ck == self.MMI_KEY_MANAGE_LIST:
                self.membership_management_menu(lista)
            elif ck == self.MMI_KEY_MODERATION_TASKS:
                self.moderation_menu(lista)
            elif ck == self.MMI_KEY_DELETE_LIST:
                self.delete_list_menu(lista)
            elif ck == 'enter':
                self.manage_list_menu(lista)
            else:
                print('Unknown key "{}" on list item "{}"'.format(ck, lista))
                time.sleep(5)


def run():
    logging.basicConfig(level=logging.INFO)
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
