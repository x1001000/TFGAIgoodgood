import requests, random, logging

from kkbox_line_bot import app
from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp.error import NlpServiceError

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, VideoMessage, VideoSendMessage, AudioMessage

logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(app.config['LINE_CHANNEL_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(app.config['LINE_CHANNEL_SECRET'])

def ig():
    r = requests.get('https://www.instagram.com/explore/locations/262402199/')
    for line in r.text.splitlines():
        if '>window._sharedData' in line:
            shortcode = random.choice(line.split('shortcode":"')[1:])[:11]
            r = requests.get(f'https://www.instagram.com/p/{shortcode}')
            for line in r.text.splitlines():
                if 'og:image' in line:
                    return f'https://www.instagram.com/p/{shortcode}'#line.split('"')[-2]

@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    logger.debug(event)
    olami_svc = olami.OlamiService(app.config['OLAMI_APP_KEY'],
                                   app.config['OLAMI_APP_SECRET'],
                                   cusid=None)#event.source.user_id)
    msg_txt = event.message.text.strip()
    reply = None
    try:
        if '北一最' in msg_txt or '北一誰最' in msg_txt:
            adj = msg_txt.split('最')[1]
            for x in '的是誰呢ㄋ啊阿ㄚ嗎嘛ㄇ？?':
                adj = adj.split(x)[0]
            if '=' in adj or '＝' in adj:
                adj, who = adj.split('=' if '=' in adj else '＝')
                if adj and who:
                    requests.get(app.config['GOOGLE_SHEETS']+'?'+adj+'='+who)
                    reply = TextSendMessage(text='是喔！')
                else:
                    reply = TextSendMessage(text='蛤？')                    
            else:
                who = requests.get(app.config['GOOGLE_SHEETS']+'?'+adj).text
                reply = TextSendMessage(text=who)
        elif '口罩' in msg_txt:
            reply = TextSendMessage(text='geobingan.info/#/event/mask')
        elif '讚讚' in msg_txt:
            reply = TextSendMessage(text=ig())
            #reply = ImageSendMessage(
            #    original_content_url=ig(),
            #    preview_image_url=ig())
            #resp = olami_svc(msg_txt[2:])
            #reply = resp.as_line_messages()
        #if event.source.user_id == 'U277d1a8cf7717e27e5d7d46971a64f65':
        #    reply = ImageSendMessage(
        #        original_content_url='https://www.1001000.io/img/cucumber.gif',
        #        preview_image_url='https://www.1001000.io/img/cucumber.jpg')
        #if '發財' in msg_txt or '發大財' in msg_txt:
        #    reply = ImageSendMessage(
        #        original_content_url='https://www.1001000.io/img/whiteeye.gif',
        #        preview_image_url='https://www.1001000.io/img/whiteeye.gif')
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
        if reply:
            logger.info(reply)
            line_bot_api.reply_message(event.reply_token, reply)

@webhook_handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = '.jpg'
    elif isinstance(event.message, VideoMessage):
        ext = '.mp4'
    elif isinstance(event.message, AudioMessage):
        ext = '.m4a'
    else:
        return
    payload = {'text':event.message.id+ext, 'user_id':event.source.user_id}
    try:
        payload['group_id'] = event.source.group_id
    except:
        pass
    try:
        payload['room_id'] = event.source.room_id
    except:
        pass
    requests.post(app.config['GOOGLE_SHEETS'], data=payload)