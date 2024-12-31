from base_agent import BaseAgent
from data_models import NewsDigest
import os
from telegram import Bot

class PublisherAgent(BaseAgent):
    """
    Агент-публикатор для отправки дайджестов в Telegram.
    """

    def __init__(self):
        super().__init__(name="PublisherAgent")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.telegram_bot_token or not self.chat_id:
            raise ValueError("Telegram bot token or chat ID not found in environment variables.")

        self.bot = Bot(token=self.telegram_bot_token)

    async def process(self, data: NewsDigest) -> None:
        """
        Отправляет дайджест в Telegram.

        :param data: Объект NewsDigest для публикации.
        """
        await self.log("Preparing to publish digest...")
        message = self._format_message(data)
        await self._send_message(message)

    def _format_message(self, digest: NewsDigest) -> str:
        """
        Форматирует дайджест для отправки в Telegram.

        :param digest: Объект NewsDigest.
        :return: Отформатированное сообщение.
        """
        message = f"*Date Generated:* {digest.date_generated}\n"
        if digest.region:
            message += f"*Region:* {digest.region}\n"
        message += "*Summary:*\n" + digest.summary
        return message

    async def _send_message(self, message: str) -> None:
        """
        Отправляет сообщение в Telegram.

        :param message: Текст сообщения.
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown"
            )
            await self.log("Digest successfully sent to Telegram.")
        except Exception as e:
            await self.log(f"Failed to send digest: {e}")
            raise
