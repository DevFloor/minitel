#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Topmenu and the submenus are based of the example found at this location http://blog.skeltonnetworks.com/2010/03/python-curses-custom-menu/
# The rest of the work was done by Matthew Bennett and he requests you keep these two mentions when you reuse the code :-)
# Basic code refactoring by Andrew Scheller

from time import sleep
import curses, os #curses is the interface for capturing key presses on the menu, os launches the files
screen = curses.initscr() #initializes a new window for capturing key presse
curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
curses.cbreak() # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
curses.start_color() # Lets you use colors when highlighting selected menu option
screen.keypad(1) # Capture input from keypad

# Change this to use different colors when highlighting
#curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background
h = curses.color_pair(1) #h is the coloring for a highlighted menu option
n = curses.A_NORMAL #n is the coloring for a non highlighted menu option

MENU = "menu"
COMMAND = "command"
FORM = "form"
SERVTELEMATIQUE = "Envoyer sur le serveur telematique de Numa"
EXITMENU = "exitmenu"

menu_data = {
  'title': "Livre d'Or de l apero DevFloor", 'type': MENU, 'subtitle': "Tapez le chiffre + Entree",
  'options':[
   
    { 'title': "Laisser un message", 'type': MENU, 'subtitle': "Tapez le chiffre + Entree",
        'options': [
          { 'title': "Nom", 'type': FORM },
          { 'title': "Email", 'type': FORM },
          { 'title': "Message", 'type': FORM},
          { 'title': SERVTELEMATIQUE, 'type': FORM },
        ]
    },
    { 'title': "L'histoire du DevFloor", 
      'type': MENU, 
      'subtitle': "Le DevFloor est situe dans un quartier central et anime en plein coeur\n de Paris. Nous fournissons aux residents tout le necessaire pour travailler\n et recevoir leurs partenaires et clients dans les meilleures conditions.",
      'options': []
    },
    
  ]
}

def leavemessage(field):

  if field == SERVTELEMATIQUE:
    with open("livredor.txt", "a") as f:
      f.write('{separator}'.format(separator="##############\n"))
    return

  screen.addstr(8,2, "Entrez votre " + field)
  screen.refresh()  
  curses.echo()
  userinput = screen.getstr(9, 2)
  userinput = userinput + '\n'
  curses.noecho()

  with open("livredor.txt", "a") as f:
    f.write('{field} : {userinput}'.format(field=field, userinput=userinput))

  return

# This function displays the appropriate menu and returns the option selected
def runmenu(menu, parent):

  # work out what text to display as the last menu option
  if parent is None:
    lastoption = "Exit"
    #curses.beep()
  else:
    lastoption = "Revenir au menu %s " % parent['title']

  optioncount = len(menu['options']) # how many options in this menu

  pos=0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$
  oldpos=None # used to prevent the screen being redrawn every time
  x = None #control for while loop, let's you scroll through options until return key is pressed then returns pos to program

  # Loop until return key is pressed
  while x !=ord('\n'):
    if pos != oldpos:
      oldpos = pos
      screen.border(0)
      screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
      screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu

      # Display all the menu items, showing the 'pos' item highlighted
      firstmenuline = 8
      for index in range(optioncount):
        textstyle = n
        if pos==index:
          textstyle = h
        screen.addstr(firstmenuline+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
      # Now display Exit/Return at bottom of menu
      textstyle = n
      if pos==optioncount:
        textstyle = h
      screen.addstr(firstmenuline+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
      screen.refresh()
      # finished updating screen

    x = screen.getch() # Gets user input

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

# This function calls showmenu and then acts on the selected item
def processmenu(menu, parent=None):
  optioncount = len(menu['options'])
  exitmenu = False
  while not exitmenu: #Loop until the user exits the menu
    getin = runmenu(menu, parent)
    if getin == optioncount:
        exitmenu = True
    elif menu['options'][getin]['type'] == FORM:
          screen.clear()
          leavemessage(menu['options'][getin]['title'])
          screen.clear() #clears previous screen on key press and updates display based on pos
    elif menu['options'][getin]['type'] == MENU:
          screen.clear() #clears previous screen on key press and updates display based on pos
          processmenu(menu['options'][getin], menu) # display the submenu
          screen.clear() #clears previous screen on key press and updates display based on pos
    elif menu['options'][getin]['type'] == EXITMENU:
          exitmenu = True

# Main program
processmenu(menu_data)
curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
os.system('clear')
