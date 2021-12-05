from unittest.mock import AsyncMock

import pytest
from aioresponses import CallbackResult, aioresponses
from app.bot import send_email
from yarl import URL


@pytest.mark.asyncio
async def test_send_mail():
    def callback(url, **kwargs):
        assert url == URL("https://api.mailgun.net/v3/test_email_domain/messages")

        request_auth = kwargs["auth"]
        assert request_auth.login == "api"
        assert request_auth.password == "test_mailgun_api_key"

        request_data = kwargs["data"]
        data_fields = {field[0]["name"]: field[2] for field in request_data._fields}

        assert len(data_fields) == 5

        assert data_fields["from"] == "test_email_from"
        assert data_fields["to"] == "test_email_to"
        assert data_fields["subject"] == "test_email_subject"
        assert data_fields["html"] == (
            "<html><br>Бла-бла-бла<br><br>"
            "<i>Это сообщение было отправлено автоматически. "
            "Пожалуйста, не отвечайте на него! Почта для связи с оргкомитетом: "
            '<a href="mailto:vzms@mail.ru">vzms@mail.ru</a>. '
            "Чтобы отписаться от новостных сообщений перейдите по "
            '<a href="%mailing_list_unsubscribe_url%">ссылке</a>.</i>'
            "<br></html><br>"
        )
        assert data_fields["attachment"] == b"\xDE\xAD\xF0\x0D"

        return CallbackResult(status=200)

    async def download(destination_file):
        return b"\xDE\xAD\xF0\x0D"

    with aioresponses() as mock:
        mock.post(
            "https://api.mailgun.net/v3/test_email_domain/messages",
            callback=callback,
        )

        document = AsyncMock(file_name="test_file", download=download)
        message = AsyncMock(html_text="Бла-бла-бла\n#рассылка", document=document)

        await send_email(message=message)

        assert len(mock.requests) == 1


@pytest.mark.parametrize(
    "hashtag,to_field",
    [
        ("#рассылка", "test_email_to"),
        ("#рассылка_всем", "test_email_to_all"),
        ("#рассылка #рассылка_всем", "test_email_to_all"),
    ],
)
@pytest.mark.asyncio
async def test_send_mail_to(hashtag, to_field):
    def callback(url, **kwargs):
        request_data = kwargs["data"]
        data_fields = {field[0]["name"]: field[2] for field in request_data._fields}

        assert data_fields["to"] == to_field

        return CallbackResult(status=200)

    with aioresponses() as mock:
        mock.post(
            "https://api.mailgun.net/v3/test_email_domain/messages",
            callback=callback,
        )

        message = AsyncMock(html_text=f"Бла-бла-бла\n{hashtag}", document=None)

        await send_email(message=message)

        assert len(mock.requests) == 1
