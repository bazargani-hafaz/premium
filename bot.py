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


def utf16_len(text: str) -> int:
    """Telegram Bot API uses UTF-16 code-unit offsets for MessageEntity."""
    return len(text.encode("utf-16-le")) // 2


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message is None or not message.text:
        return

    text = message.text

    if TARGET_EMOJI not in text:
        return

    parts = text.split(TARGET_EMOJI)
    output_parts = []
    entities = []
    current_offset = 0

    for index, part in enumerate(parts):
        output_parts.append(part)
        current_offset += utf16_len(part)

        if index < len(parts) - 1:
            # Keep one visible emoji character as the entity placeholder.
            output_parts.append("🔻")
            entities.append(
                MessageEntity(
                    type=MessageEntity.CUSTOM_EMOJI,
                    offset=current_offset,
                    length=utf16_len("🔻"),
                    custom_emoji_id=PREMIUM_EMOJI_ID,
                )
            )
            current_offset += utf16_len("🔻")

    output_text = "".join(output_parts)

    try:
        await message.reply_text(
            text=output_text,
            entities=entities,
            disable_web_page_preview=True,
        )
    except Exception:
        logger.exception("Failed to send converted message")
        # Fallback: send the text without entities instead of crashing the bot.
        await message.reply_text(
            text=output_text,
            disable_web_page_preview=True,
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled exception:", exc_info=context.error)


def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is missing. "
            "Add BOT_TOKEN in Railway Variables."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    logger.info("Premium Emoji Bot started")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
