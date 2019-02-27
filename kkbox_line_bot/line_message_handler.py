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
                                   cusid=None)#event.source.user_id)
    msg_txt = event.message.text.strip()
    try:
        if msg_txt == '讚讚' or msg_txt == 'TFGAI讚讚':
            reply = TextSendMessage(text='有！' if msg_txt == '讚讚' else '你也讚讚！你全家都讚讚！')
        elif '北一最' in msg_txt or '北一誰最' in msg_txt:
            adj = msg_txt.split('最')[1]
            for x in '的是誰啊阿ㄚ嗎嘛ㄇ讚讚？?':
                adj = adj.split(x)[0]
            if '=' in adj or '＝' in adj:
                adj, who = adj.split('=' if '=' in adj else '＝')
                requests.get(app.config['GOOGLE_SHEETS']+'?'+adj+'='+(who if who else 'instagr.am/1001000.io'))
                reply = TextSendMessage(text='嗯哼！')
            else:
                who = requests.get(app.config['GOOGLE_SHEETS']+'?'+adj).text
                reply = TextSendMessage(text=who)
        elif '讚讚' in msg_txt or 'TFGAI讚讚' in msg_txt:
            resp = olami_svc(msg_txt.replace('TFGAI讚讚', '').replace('讚讚', ''))
            reply = resp.as_line_messages()
        elif msg_txt[0] == ',' or msg_txt[0] == '，':
            resp = olami_svc(msg_txt[1:])
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
        payload = {'text':msg_txt, 'user_id':event.source.user_id}
        try:
            payload['group_id'] = event.source.group_id
        except:
            pass
        try:
            payload['room_id'] = event.source.room_id
        except:
            pass
        requests.post(app.config['GOOGLE_SHEETS'], data=payload)
        logger.info('Reply: {}'.format(reply))
        line_bot_api.reply_message(event.reply_token, reply)