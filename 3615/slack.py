import requests

SLACK_TOKEN = "xoxp-3673911929-3918993035-5010858377-0403b1"
SLACK_CHANNEL = "C050AQ1AB" # `minitel` channel

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
    # if has a username
    if message.get('username'):
      slack_messages_text += '{username} : {message}\n'.format(
        username=message['username'].replace('\n', ''),
        message=message['text'].replace('\n', ''),
      )
    # no username, display only text
    else:
      slack_messages_text += '{message}\n'.format(
        message=message['text'].replace('\n', ''),
      )

  return slack_messages_text


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
