the_most = {
    '嗆':'大黃瓜彭安安',
    '萌':'小雞',
    '邊':'百千',
    '北七':'妳啊不然咧😂'}

import requests

import logging


from kkbox_line_bot import app
from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp.error import NlpServiceError

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(app.config['LINE_CHANNEL_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(app.config['LINE_CHANNEL_SECRET'])


@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    logger.debug('event: ' + str(event))
    olami_svc = olami.OlamiService(app.config['OLAMI_APP_KEY'],
                                   app.config['OLAMI_APP_SECRET'],
                                   cusid=event.source.user_id)
    try:
        if '北一誰最' in event.message.text:
            try:
                adj = event.message.text.split('北一誰最')[1]
                adj = adj.split('？')[0]
                adj = adj.split('?')[0]
                who = the_most.get(adj, '不好說 ┐(´д`)┌')
            except:
                who = '蛤？'
            reply = TextSendMessage(text=who)
        elif 'TFGAI讚讚' == event.message.text.strip():
            reply = TextSendMessage(text='你也讚讚你全家都讚讚')
        elif 'TFGAI讚讚' in event.message.text:
            event.message.text = event.message.text.replace('TFGAI讚讚', '')
            resp = olami_svc(event.message.text)
            reply = resp.as_line_messages()
        elif '讚讚' in event.message.text:
            event.message.text = event.message.text.replace('讚讚', '')
            resp = olami_svc(event.message.text)
            reply = resp.as_line_messages()
        elif '，' == event.message.text[0]:
            event.message.text = event.message.text[1:]
            resp = olami_svc(event.message.text)
            reply = resp.as_line_messages()
    except NlpServiceError as e:
        err_msg = 'NLP service is currently unavailable: {}'.format(repr(e))
        logger.error(err_msg)
        reply = TextSendMessage(text=err_msg)
    except Exception as e:
        err_msg = 'Unexpected error: {}'.format(repr(e))
        logger.exception(err_msg)
        reply = TextSendMessage(text=err_msg)
    finally:
        requests.post(app.config['GOOGLE_SHEETS'], data={'content'=event.message.text})
        logger.info('Reply: {}'.format(reply))
        line_bot_api.reply_message(event.reply_token, reply)