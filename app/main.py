import io
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv('API_TOKEN')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
EMAIL_DOMAIN = os.getenv('EMAIL_DOMAIN')
LIST_ADDRESS = os.getenv('LIST_ADDRESS')
CHAT_ID = os.getenv('CHAT_ID')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


email_template = open('base.html').read()


@dp.channel_post_handler(
    hashtags=['рассылка'],
    chat_id=CHAT_ID,
    content_types=[types.ContentType.TEXT, types.ContentType.DOCUMENT])
async def send_welcome(message: types.Message):
    # удаляем хештег и переносы строк в конце сообщения
    email_text = message.html_text.replace('#рассылка', '').rstrip('\n')

    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('from', 'ВЗМШ 2021<vzmsh@mail.math-vsu.ru>')
        data.add_field('to', LIST_ADDRESS)
        data.add_field('subject', 'Оргкомитет ВЗМШ')
        data.add_field('html', email_template.replace('%message%', email_text).replace('\n', '<br>'))
        if message.document is not None:
            data.add_field(
                'attachment',
                await message.document.download(destination=io.BytesIO()),
                filename=message.document.file_name
            )
        params = {
            'auth': aiohttp.BasicAuth('api', MAILGUN_API_KEY),
            'data': data
        }
        await session.post(f'https://api.mailgun.net/v3/{EMAIL_DOMAIN}/messages', **params)


if __name__ == '__main__':
    executor.start_polling(dp)
