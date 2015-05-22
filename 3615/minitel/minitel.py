from time import sleep
import curses, os

class Minitel(object):

  def __init__(self):
    super(Minitel, self).__init__()

  def run(self, menu_root):

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
    self.runmenu(menu_root)

    # Important!
    # This closes out the menu system and returns you to the bash prompt.
    curses.endwin()
    os.system('clear')

  def write(self, line, column, text, pspace=0, style=curses.A_NORMAL):
    '''
    Writes text.
      `line`    line number
      `column`  column number
      `text`    the text to print
      `pspace`  the paragraph space after the text block
      `style`   the curse style
    '''

    text_lines = text.split('\n')
    for text_line in text_lines:
      self.screen.addstr(line, column, text_line, style)
      line += 1

    return (line + pspace)

  def get_user_input(self, line, column):
    # get user input (with echo)
    curses.echo()
    userinput = self.screen.getstr(line, column)
    curses.noecho()

    return userinput.strip()

  def show_quick_message(self, message, title=None, time=None):

    self.screen.border(0)

    line = 2
    if title:
      line = self.write(line, 2, title, pspace=1, style=curses.A_STANDOUT)
    line = self.write(line, 2, message)

    self.screen.refresh()

    # sleep
    if time is not None:
      sleep(time)

    # clear
    self.screen.clear()

  def show_logo(self):

    # get logo
    with open('logo.txt', 'r') as f:
      logo = f.read()

    # display logo
    self.screen.border(0)
    self.write(2, 2, logo)
    self.screen.refresh()

    # wait for user input
    self.screen.getch()

    # clear
    self.screen.clear()

  def runmenu(self, menu, parent=None):
    '''
    This function calls showmenu and then acts on the selected item.
    '''

    # loop until the user exits the menu
    while True:
      new_menu = menu.run(
        minitel=self,
        parent=parent,
      )

      # if new_menu is None, exit
      if new_menu is None:
        break

      # run child
      self.runmenu(menu=new_menu, parent=menu)
