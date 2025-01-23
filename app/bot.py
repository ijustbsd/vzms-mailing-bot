import asyncio
import io
import logging
import datetime as dt
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher, types

from .config import settings

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

with Path(__file__).parent.joinpath("templates/message.html").open() as f:
    email_template = f.read()

bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode=types.ParseMode.HTML)


async def create_campaign(html: str, emails_list_id: int) -> int:
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            url="https://api.dashamail.com/",
            params={
                "api_key": settings.DASHAMAIL_API_KEY,
                "method": "campaigns.create",
            },
            json={
                "list_id": [emails_list_id],
                "subject": settings.EMAIL_SUBJECT,
                "from_email": settings.EMAIL_FROM,
                "from_name": settings.NAME_FROM,
                "html": email_template.replace("%message%", html).replace("\n", "<br>"),
            },
        )

        if resp.status != 200:
            raise RuntimeError

        response = await resp.json()
        logger.info("campaigns.create response: %s", response)

        err_code = response["response"]["msg"]["err_code"]
        if err_code:
            raise RuntimeError

        return response["response"]["data"]["campaign_id"]


async def attach_file_to_campaign(
    campaign_id: int, file_url: str, file_name: str
) -> None:
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            url="https://api.dashamail.com/",
            params={
                "api_key": settings.DASHAMAIL_API_KEY,
                "method": "campaigns.attach",
                "campaign_id": campaign_id,
                "url": file_url,
                "name": file_name,
            },
        )

        if resp.status != 200:
            raise RuntimeError

        response = await resp.json()
        logger.info("campaigns.attach response: %s", response)

        err_code = response["response"]["msg"]["err_code"]
        if err_code:
            raise RuntimeError


async def schedule_campaign(campaign_id: int):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            url="https://api.dashamail.com/",
            params={
                "api_key": settings.DASHAMAIL_API_KEY,
                "method": "campaigns.update",
                "campaign_id": campaign_id,
            },
            json={
                "status": "SCHEDULE",
                "delivery_time": (dt.datetime.now() + dt.timedelta(minutes=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            },
        )

        if resp.status != 200:
            raise RuntimeError

        response = await resp.json()
        logger.info("campaigns.update response: %s", response)

        err_code = response["response"]["msg"]["err_code"]
        if err_code:
            raise RuntimeError


async def send_email(message: types.Message):
    logger.info("handle message: %s", message.message_id)

    if settings.TG_HASTAG_ALL in message.html_text:
        emails_list_id = settings.DASHAMAIL_LIST_ALL_ID
    else:
        emails_list_id = settings.DASHAMAIL_LIST_ID

    # удаляем хештег и переносы строк в конце сообщения
    email_text = (
        message.html_text.replace(f"#{settings.TG_HASTAG_ALL}", "")
        .replace(f"#{settings.TG_HASTAG}", "")
        .rstrip("\n")
    )

    campaign_id = await create_campaign(email_text, emails_list_id)
    if message.document is not None:
        file = await bot.get_file(file_id=message.document.file_id)
        file_url = bot.get_file_url(file_path=file.file_path)
        await attach_file_to_campaign(
            campaign_id=campaign_id,
            file_url=file_url,
            file_name=message.document.file_name,
        )
    await schedule_campaign(campaign_id)


def create_bot() -> Dispatcher:
    dp = Dispatcher(bot)
    dp.register_channel_post_handler(
        send_email,
        hashtags=[settings.TG_HASTAG, settings.TG_HASTAG_ALL],
        chat_id=settings.TG_CHAT_ID,
        content_types=[types.ContentType.TEXT, types.ContentType.DOCUMENT],
    )
    return dp
