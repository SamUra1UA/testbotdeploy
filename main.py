from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaWebPage
import asyncio
import os
import sys

API_ID = os.getenv("YOUR_API_ID")
API_HASH = os.getenv("YOUR_API_HASH")
SESSION_NAME = "gingers_session"

SOURCE_CHAT_ID = {-1002293398473, -1002270373322}
DESTINATION_CHAT_ID = -1002334681781

THREAD_MAPPING = {
    3830: 2817,
    35311: 2815,
    679: 2813,
    45795: 2811,
    45155: 2809,
    597: 2807,
    5914: 2805,
    674: 2803,
    13144: 2801,
    596: 2799,
    13781: 2797,
}
FALLBACK_THREAD_ID = 988

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


@client.on(events.NewMessage(chats=SOURCE_CHAT_ID))
async def forward_message(event):
    try:
        destination_thread = None

        # Якщо канал без гілок
        if event.chat_id in {-1002270373322}:
            destination_thread = FALLBACK_THREAD_ID

        # Якщо це відповідь, спробуй знайти thread
        elif event.message.reply_to:
            thread_id = event.message.reply_to.reply_to_msg_id
            if thread_id in THREAD_MAPPING:
                destination_thread = THREAD_MAPPING[thread_id]

        if destination_thread:
            media = event.message.media

            # Перевірка чи це web page
            if media and isinstance(media, MessageMediaWebPage):
                await client.send_message(
                    DESTINATION_CHAT_ID,
                    event.message.message,
                    reply_to=destination_thread
                )
            elif media:
                await client.send_file(
                    DESTINATION_CHAT_ID,
                    file=event.message.media,
                    caption=event.message.message,
                    reply_to=destination_thread
                )
            else:
                await client.send_message(
                    DESTINATION_CHAT_ID,
                    event.message.message,
                    reply_to=destination_thread
                )
            print(f"✅ Переслано в гілку {destination_thread}")
        else:
            print("⚠️ Повідомлення пропущене: немає відповідної гілки.")

    except Exception as e:
        print(f"❌ Помилка при обробці повідомлення: {e}")
        await asyncio.sleep(2)  # Затримка для зниження навантаження


async def main():
    print("🚀 Бот запущено...")
    while True:
        try:
            await client.run_until_disconnected()
        except Exception as e:
            print(f"❗ Помилка при підключенні: {e}")
            print("🔁 Перепідключення через 1 секунду...")
            await asyncio.sleep(1)

            # Спроба перезапуску скрипта
            print("🔄 Перезапуск скрипта...")
            os.execv(sys.executable, ['python'] + sys.argv)


with client:
    client.loop.run_until_complete(main())
