import os
import logging
from telegram import Update, MessageEntity
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
PREMIUM_EMOJI_ID = "5938385748121096724"
TARGET_EMOJI = "[🔻](https://web.telegram.org/k/assets/img/emoji/1f53b.png)"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    if TARGET_EMOJI not in text:
        await update.message.reply_text(
            "❌ الگوی ایموجی 🔻 در متن پیدا نشد."
        )
        return

    parts = text.split(TARGET_EMOJI)
    output_text = ""
    entities = []

    for index, part in enumerate(parts):
        output_text += part

        if index < len(parts) - 1:
            offset = len(output_text.encode("utf-16-le")) // 2
            output_text += "🔻"
            entities.append(
                MessageEntity(
                    type=MessageEntity.CUSTOM_EMOJI,
                    offset=offset,
                    length=2,
                    custom_emoji_id=PREMIUM_EMOJI_ID,
                )
            )

    await update.message.reply_text(
        text=output_text,
        entities=entities,
        disable_web_page_preview=True,
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    logger.info("Premium Emoji Bot started")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
