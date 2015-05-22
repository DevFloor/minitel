import curses

class MinitelBaseScreen(object):
  '''
  The base Screen. Does nothing.
  '''

  def __init__(self, title):
    assert(title is not None)
    self.title = title

  def __str__(self):
    return '{0}<title:{1}>'.format(self.__class__.__name__, self.title)

  def fetch(self, minitel):
    '''
    Preloads screen data.
    '''
    pass

  def pre_fetch(self, minitel):
    '''
    Called before fetch.
    '''
    pass

  def run(self, minitel, parent):
    '''
    Runs the screen.
    '''
    raise StandardError('MinitelBaseScreen is abstract')

class MinitelExitScreen(MinitelBaseScreen):
  '''
  Exit screen. Returns None to exit.
  '''

  def run(self, minitel, parent):
    # return None to exit
    return None

class MinitelMenuScreen(MinitelBaseScreen):
  '''
  A screen to display a menu.
  '''

  def __init__(self, title, subtitle=None, show_logo=False, submenus=[]):
    assert(title is not None)
    self.title = title
    self.subtitle = subtitle
    self.submenus = submenus
    self.show_logo = show_logo

  def run(self, minitel, parent):
    '''
    This function displays the appropriate menu and returns the option selected.
    '''

    # show logo if necessary
    if self.show_logo:
      minitel.show_logo()

    # work out what text to display as the last menu option
    if parent is None:
      lastoption = "Quitter 3615 NUMA"
    else:
      lastoption = "Revenir au menu {0}".format(parent.title)

    # how many options in this menu
    optioncount = len(self.submenus)

    # pre fetch hook
    self.pre_fetch(minitel=minitel)

    # fetch menu
    # will allow the menu to preload data if needed
    self.fetch(minitel=minitel)

    # pos is the zero-based index of the hightlighted menu option
    pos=0
    # used to prevent the screen being redrawn every time
    oldpos=None
    # control for while loop, let's you scroll through options until return key
    # is pressed then returns pos to program
    x = None

    # Loop until return key is pressed
    while x != ord('\n'):
      if pos != oldpos:
        oldpos = pos
        minitel.screen.border(0)

        line = 2
        line = minitel.write(line, 2, self.title, pspace=1, style=curses.A_STANDOUT)
        line = minitel.write(line, 2, self.subtitle, pspace=1, style=curses.A_BOLD)

        # display menu items, showing the 'pos' item highlighted
        for index in range(optioncount):
          line = minitel.write(line, 4, "%d - %s" % (index+1, self.submenus[index].title), style=(curses.A_STANDOUT if pos == index else curses.A_NORMAL))

        # display exit
        line = minitel.write(line, 4, "%d - %s" % (optioncount+1, lastoption), style=(curses.A_STANDOUT if pos == optioncount else curses.A_NORMAL))

        # refresh
        minitel.screen.refresh()

      # Gets user input
      x = minitel.screen.getch(line, 4)

      # What is user input?
      if x >= ord('1') and x <= ord(str(optioncount+1)):
        # convert keypress back to a number, then subtract 1 to get index
        pos = x - ord('0') - 1
      elif x == 258: # down arrow
        if pos < optioncount:
          pos += 1
        else:
          curses.beep()
      elif x == 259: # up arrow
        if pos > 0:
          pos -= 1
        else:
          curses.beep()
      elif x != ord('\n'):
        curses.beep()

    # clear
    minitel.screen.clear()

    # select the new menu
    if pos == optioncount:
      return None
    return self.submenus[pos]

class MinitelFormMenuScreen(MinitelMenuScreen):
  '''
  A screen to prompt the user to fill a form.
  '''

  def __init__(self, *args, **kwargs):
    super(MinitelFormMenuScreen, self).__init__(*args, **kwargs)
    self.form_values = {}

  def submit(self, minitel):
    '''
    Submits the form.
    '''
    pass

class MinitelFormSubmitScreen(MinitelBaseScreen):
  '''
  A screen to submit a form.
  Parent must be a MinitelFormMenuScreen.
  '''

  def run(self, minitel, parent):
    assert(isinstance(parent, MinitelFormMenuScreen))

    # call submit() to submit the form
    parent.submit(minitel)

class MinitelFormInputScreen(MinitelBaseScreen):
  '''
  A screen to prompt the user for a form input.
  Parent must be a MinitelFormMenuScreen.
  '''

  def __init__(self, title):
    self.title = title
    self.show_logo = False

  def run(self, minitel, parent):
    assert(isinstance(parent, MinitelFormMenuScreen))

    minitel.screen.border(0)

    line = 2
    line = minitel.write(line, 2, parent.title, pspace=1, style=curses.A_STANDOUT)
    line = minitel.write(line,2, "Entrez votre {0}: ".format(self.title))

    minitel.screen.refresh()

    # get user input
    userinput = minitel.get_user_input(line, 2)

    # keep data in leavemessage_dict
    parent.form_values[self.title] = userinput

    # clear
    minitel.screen.clear()
