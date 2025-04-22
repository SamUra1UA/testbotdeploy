from telethon import TelegramClient, events
from Keys import YOUR_API_ID, YOUR_API_HASH
import asyncio
import os
import sys

API_ID = os.getenv(YOUR_API_ID)
API_HASH = os.getenv(YOUR_API_HASH)
SESSION_NAME = "gingers_session"

SOURCE_CHAT_ID = {-1002300558407, -1002270373322}
DESTINATION_CHAT_ID = -1002334681781

THREAD_MAPPING = {
    2: 483,
    16: 481,
    7: 484,
    9241: 485,
    15648: 486,
    14: 1001,
}
FALLBACK_THREAD_ID = 988

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def check_authorized():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Не авторизовано. Запусти спочатку authorize_once.py")
        exit()

client.loop.run_until_complete(check_authorized())


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
            # Відправлення медіа або тексту
            if event.message.media:
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
