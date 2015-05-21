#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from time import sleep
import curses, os

MENU = "menu"
COMMAND = "command"
FORM = "form"
EXITMENU = "exitmenu"

class Minitel(object):

  SERVTELEMATIQUE = "Envoyer sur le serveur telematique de Numa"
  HISTORY_MESSAGE = '''Le DevFloor est situe dans un quartier central et anime en plein coeur\n de Paris. Nous fournissons aux residents tout le necessaire pour travailler\n et recevoir leurs partenaires et clients dans les meilleures conditions.'''

  def __init__(self):
    super(Minitel, self).__init__()

    # message
    self.leavemessage_dict = {}

    # result message
    self.result_message = ''

    self.menu_leave_message = {
      'title': "Laisser un message",
      'type': MENU,
      'subtitle': "Tapez le chiffre + Entree",
      'options': [
        { 'title': "Nom", 'type': FORM },
        { 'title': "Email", 'type': FORM },
        { 'title': "Message", 'type': FORM},
        { 'title': Minitel.SERVTELEMATIQUE, 'type': FORM },
      ]
    }
    self.menu_history = {
      'title': "L'histoire du DevFloor",
      'type': MENU,
      'subtitle': Minitel.HISTORY_MESSAGE,
      'options': []
    }
    self.menu_root = {
      'title': "Livre d'Or de l apero DevFloor",
      'type': MENU,
      'subtitle': "Tapez le chiffre + Entree",
      'options':[
        self.menu_leave_message,
        self.menu_history,
      ]
    }

  def run(self):

    # init curses

    # initializes a new window for capturing key presse
    self.screen = curses.initscr()

    # Disables automatic echoing of key presses (prevents program from input\
    # each key twice)
    curses.noecho()

    # Disables line buffering (runs each key as it is pressed rather than
    #  waiting for the return key to pressed)
    curses.cbreak()

    # Lets you use colors when highlighting selected menu option
    curses.start_color()

    # Capture input from keypad
    self.screen.keypad(1)

    # run menu
    self.processmenu(self.menu_root)

    # Important!
    # This closes out the menu system and returns you to the bash prompt.
    curses.endwin()
    os.system('clear')

  def post_slack_message(self, text, username='Minitel'):
    requests.post(
      url="https://slack.com/api/chat.postMessage",
      params = {
        "token":"xoxp-3673911929-3918993035-5010858377-0403b1",
      },
      data = {
        "username":username,
        "icon_url":"http://mazaheri.s3.amazonaws.com/minitel.png",
        "channel":"C050AQ1AB", # Minitel channel
        "text":text,
      },
    )

  def leavemessage(self, field):

    # send message
    if field == Minitel.SERVTELEMATIQUE:

      # result message
      self.result_message = ' > Message teletransmit avec succes'

      # write to file
      with open("livredor.txt", "a") as f:
        for field in ['Nom', 'Email', 'Message']:
          f.write('{field} : {userinput}\n'.format(
            field=field,
            userinput=self.leavemessage_dict.get(field) or '[Pas de {0}]'.format(field),
          ))
        f.write('==============\n')

      # send Slack message
      if field == 'Message':
        self.post_slack_message(
          text=self.leavemessage_dict.get('Message') or '[Pas de message]',
          username='{0} via Minitel'.format(self.leavemessage_dict.get('Nom') or 'Anonyme'),
        )

    # get field value
    else:
      self.screen.addstr(8,2, "Entrez votre {0}: ".format(field))
      self.screen.refresh()
      curses.echo()
      userinput = self.screen.getstr(9, 2).strip()
      curses.noecho()

      # keep data in leavemessage_dict
      self.leavemessage_dict[field] = userinput

  def runmenu(self, menu, parent):
    '''
    This function displays the appropriate menu and returns the option selected.
    '''

    # work out what text to display as the last menu option
    if parent is None:
      lastoption = "Exit"
      #curses.beep()
    else:
      lastoption = "Revenir au menu %s " % parent['title']

    optioncount = len(menu['options']) # how many options in this menu

    # pos is the zero-based index of the hightlighted menu option. Every time
    # runmenu is called, position returns to 0, when runmenu ends the position
    # is returned and tells the program what opt$
    pos=0
    # used to prevent the screen being redrawn every time
    oldpos=None
    # control for while loop, let's you scroll through options until return key
    # is pressed then returns pos to program
    x = None

    # Loop until return key is pressed
    while x !=ord('\n'):
      if pos != oldpos:
        oldpos = pos
        self.screen.border(0)
        self.screen.addstr(2,2, menu['title'], curses.A_STANDOUT)
        self.screen.addstr(4,2, menu['subtitle'], curses.A_BOLD)
        self.screen.addstr(6,2, self.result_message, curses.A_BOLD)
        self.result_message = '' # reset message

        # Display all the menu items, showing the 'pos' item highlighted
        firstmenuline = 9
        for index in range(optioncount):
          textstyle = curses.A_NORMAL
          if pos==index:
            textstyle = curses.color_pair(1)
          self.screen.addstr(firstmenuline+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
        # Now display Exit/Return at bottom of menu
        textstyle = curses.A_NORMAL
        if pos==optioncount:
          textstyle = curses.color_pair(1)
        self.screen.addstr(firstmenuline+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
        self.screen.refresh()
        # finished updating screen

      x = self.screen.getch() # Gets user input

      # What is user input?
      if x >= ord('1') and x <= ord(str(optioncount+1)):
        pos = x - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
      elif x == 258: # down arrow
        if pos < optioncount:
          pos += 1
        else: pos = 0
      elif x == 259: # up arrow
        if pos > 0:
          pos += -1
        else: pos = optioncount

    # return index of the selected item
    return pos

  def processmenu(self, menu, parent=None):
    '''
    This function calls showmenu and then acts on the selected item.
    '''

    optioncount = len(menu['options'])

    #Loop until the user exits the menu
    exitmenu = False
    while not exitmenu:
      getin = self.runmenu(menu, parent)
      if getin == optioncount:
          exitmenu = True
      elif menu['options'][getin]['type'] == FORM:
            self.screen.clear()
            self.leavemessage(menu['options'][getin]['title'])
            self.screen.clear()
      elif menu['options'][getin]['type'] == MENU:
            self.screen.clear()
            self.processmenu(menu['options'][getin], menu) # display the submenu
            self.screen.clear()
      elif menu['options'][getin]['type'] == EXITMENU:
            exitmenu = True

# Main program
if __name__ == '__main__':

  # Run Minitel
  minitel = Minitel()
  minitel.run()
