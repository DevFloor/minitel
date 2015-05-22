import requests
import HTMLParser

SLACK_TOKEN = "xoxp-3673911929-3918993035-5010858377-0403b1"
SLACK_CHANNEL = "C050AQ1AB" # `minitel` channel

username_cache = {}

html_parser = HTMLParser.HTMLParser()

def get_slack_messages():

  # GET /channels.history
  r = requests.get(
    url="https://slack.com/api/channels.history",
    params = {
      "token":SLACK_TOKEN,
      "channel":SLACK_CHANNEL,
      "count":"10",
    },
  )

  # get messages
  messages = r.json()['messages']

  # format text
  slack_messages_text = ''
  for message in messages:
    # ignore messages without text
    if not message.get('text'):
      continue

    message_text = message['text'].replace('\n', '')
    message_text = html_parser.unescape(message_text)

    # if has a username
    if message.get('username'):
      slack_messages_text += '{username} : {message}\n'.format(
        username=message['username'].replace('\n', ''),
        message=message_text,
      )
    # if has a user
    elif message.get('user'):
      slack_messages_text += '{username} : {message}\n'.format(
        username=get_slack_username(message.get('user')).replace('\n', ''),
        message=message_text,
      )
    # no username, display only text
    else:
      slack_messages_text += '{message}\n'.format(
        message=message_text,
      )

  return slack_messages_text

def _fetch_slack_username(user_id):
  r = requests.get(
      url="https://slack.com/api/users.info",
      params = {
          "token":SLACK_TOKEN,
          "user":user_id,
      },
  )
  return r.json()['user']['name']

def get_slack_username(user_id):
  # check if in cache
  if username_cache.get(user_id):
    return username_cache.get(user_id)

  # fetch username
  username = _fetch_slack_username(user_id)

  # cache
  username_cache[user_id] = username

  return username

def post_slack_message(text, username='Minitel'):
  requests.post(
    url="https://slack.com/api/chat.postMessage",
    params = {
      "token":SLACK_TOKEN,
    },
    data = {
      "username":username,
      "icon_url":"http://mazaheri.s3.amazonaws.com/minitel.png",
      "channel":SLACK_CHANNEL,
      "text":text,
    },
  )
