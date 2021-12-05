import asyncio
import io
import logging
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher, types

from .config import settings

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

with Path(__file__).parent.joinpath("templates/message.html").open() as f:
    email_template = f.read()


async def send_email(message: types.Message):
    if settings.TG_HASTAG_ALL in message.html_text:
        email_to = settings.EMAIL_TO_ALL
    else:
        email_to = settings.EMAIL_TO

    # удаляем хештег и переносы строк в конце сообщения
    email_text = (
        message.html_text.replace(f"#{settings.TG_HASTAG}", "")
        .replace(f"#{settings.TG_HASTAG_ALL}", "")
        .rstrip("\n")
    )

    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field("from", settings.EMAIL_FROM)
        data.add_field("to", email_to)
        data.add_field("subject", settings.EMAIL_SUBJECT)
        data.add_field(
            "html",
            email_template.replace("%message%", email_text).replace("\n", "<br>"),
        )
        if message.document is not None:
            data.add_field(
                "attachment",
                await message.document.download(destination_file=io.BytesIO()),
                filename=message.document.file_name,
            )
        params = {
            "auth": aiohttp.BasicAuth("api", settings.MAILGUN_API_KEY),
            "data": data,
        }
        for _ in range(5):
            resp = await session.post(
                f"https://api.mailgun.net/v3/{settings.EMAIL_DOMAIN}/messages", **params
            )
            if resp.status == 200:
                break
            logger.warning("Mailgun response status: %s", resp.status)
            await asyncio.sleep(3)


def create_bot() -> Dispatcher:
    bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)
    dp.register_channel_post_handler(
        send_email,
        hashtags=[settings.TG_HASTAG, settings.TG_HASTAG_ALL],
        chat_id=settings.TG_CHAT_ID,
        content_types=[types.ContentType.TEXT, types.ContentType.DOCUMENT],
    )
    return dp
