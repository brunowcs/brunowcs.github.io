
import telegram
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from logger import *

import pytesseract as ocr

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import numpy as np
import cv2

from PIL import Image
import PIL.Image

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files (x86)\Tesseract-OCR\tesseract'

logger.setLevel(logging.DEBUG)

updater = Updater('')


def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

updater.dispatcher.add_handler(CommandHandler('hello', hello))

def start(bot, update):
    update.message.reply_text(
        'Ola {}, bem-vindo ao bot Forex Lets! '.format(update.message.from_user.first_name))

updater.dispatcher.add_handler(CommandHandler('start', start))


def photo_handler(bot, update):
    file_id = update.message.photo
    file = bot.getFile(update.message.photo[-1].file_id)
    print ("file_id: " + str(update.message.photo[-1].file_id))
    file.download("photo" +str(update.message.photo[-1].file_id)+".jpg")
    phrase = ocr.image_to_string(Image.open("photo" + str(update.message.photo[-1].file_id) + ".jpg"))
    print(phrase.encode(encoding='UTF-8', errors='strict'))
    text = phrase.encode(encoding='UTF-8', errors='strict')
    update.message.reply_text(
        '{} '.format(text))


updater.dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))






updater.start_polling()
updater.idle()
