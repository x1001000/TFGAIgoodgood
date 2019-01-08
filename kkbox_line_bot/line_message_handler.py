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
        if '北一最' in event.message.text or '北一誰最' in event.message.text:
            adj = event.message.text.split('最')[1]
            adj = adj.split('的')[0].split('是')[0].split('誰')[0].split('嗎')[0].split('？')[0].split('?')[0]
            if '=' in adj or '＝' in adj:
                adj, who = adj.split('=' if '=' in adj else '＝')
                requests.get(app.config['GOOGLE_SHEETS']+'?'+adj+'='+(who if who else 'instagr.am/1001000.io'))
                reply = TextSendMessage(text='嗯哼！')
            else:
                who = requests.get(app.config['GOOGLE_SHEETS']+'?'+adj).text
                reply = TextSendMessage(text=who)
        elif 'TFGAI讚讚' == event.message.text.strip():
            reply = TextSendMessage(text='你也讚讚！你全家都讚讚！')
        elif '讚讚' == event.message.text.strip():
            reply = TextSendMessage(text='有！')
        elif 'TFGAI讚讚' in event.message.text:
            text = event.message.text.replace('TFGAI讚讚', '')
            resp = olami_svc(text)
            reply = resp.as_line_messages()
        elif '讚讚' in event.message.text:
            text = event.message.text.replace('讚讚', '')
            resp = olami_svc(text)
            reply = resp.as_line_messages()
        elif '，' == event.message.text[0]:
            text = event.message.text[1:]
            resp = olami_svc(text)
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
        payload = {'user_id':event.source.user_id, 'text':event.message.text}
        requests.post(app.config['GOOGLE_SHEETS'], data=payload)
        logger.info('Reply: {}'.format(reply))
        line_bot_api.reply_message(event.reply_token, reply)