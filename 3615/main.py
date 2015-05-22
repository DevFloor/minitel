#!/usr/bin/env python
# -*- coding: utf-8 -*-

from minitel.minitel import Minitel
from minitel.screen import MinitelMenuScreen
from minitel.screen import MinitelFormMenuScreen
from minitel.screen import MinitelFormInputScreen
from minitel.screen import MinitelFormSubmitScreen

from utils.slack import get_slack_messages, post_slack_message

#
# Custom Screens
#

class MinitelLeaveMessageFormMenuScreen(MinitelFormMenuScreen):
  '''
  A form screen to leave messages.
  '''

  def submit(self, minitel):
    '''
    Leaves a messages.
    '''

    # show quick message
    minitel.show_quick_message(
      title=self.title,
      message='Envoi du message...'
    )

    # write to file
    with open("livredor.txt", "a") as f:
      for field in ['Nom', 'Email', 'Message']:
        f.write('{field} : {userinput}\n'.format(
          field=field,
          userinput=self.form_values.get(field) or '[Pas de {0}]'.format(field),
        ))
      f.write('==============\n')

    # send Slack message
    if field == 'Message':
      post_slack_message(
        text=self.form_values.get('Message') or '[Pas de message]',
        username='{0} via Minitel'.format(self.form_values.get('Nom') or 'Anonyme'),
      )

    # show quick message
    minitel.show_quick_message(
      title=self.title,
      message=' > Message teletransmit avec succes !',
      time=2,
    )

class MinitelGetSlackMessagesScreen(MinitelMenuScreen):
  '''
  A screen to show Slack Messages.
  '''

  def pre_fetch(self, minitel):
    minitel.show_quick_message(
      title=self.title,
      message='Chargement des messages...'
    )

  def fetch(self, minitel):
    try:
      self.subtitle = get_slack_messages()
    except Exception:
      self.subtitle = ' > Une erreur est survenue pendant la teletransmission'

#
# Build menus
#

menu_leave_message = MinitelLeaveMessageFormMenuScreen(
  title='Laisser un message',
  subtitle='Tapez le chiffre + Entree',
  submenus=[
    MinitelFormInputScreen('Nom'),
    MinitelFormInputScreen('Email'),
    MinitelFormInputScreen('Message'),
    MinitelFormSubmitScreen('Envoyer sur le serveur telematique de Numa'),
  ]
)

menu_get_messages = MinitelGetSlackMessagesScreen(
  title='Consulter les messages',
)

menu_history = MinitelMenuScreen(
  title="L'histoire du DevFloor",
  subtitle='''Le DevFloor est situe dans un quartier central et anime en plein coeur
de Paris. Nous fournissons aux residents tout le necessaire pour travailler
et recevoir leurs partenaires et clients dans les meilleures conditions.''',
)

menu_root = MinitelMenuScreen(
  title="Livre d'Or de l'apero DevFloor",
  subtitle="Tapez le chiffre + Entree",
  show_logo=True,
  submenus=[
    menu_leave_message,
    menu_get_messages,
    menu_history,
  ]
)

# Main program
if __name__ == '__main__':

  # Run Minitel
  minitel = Minitel()
  minitel.run(menu_root)
