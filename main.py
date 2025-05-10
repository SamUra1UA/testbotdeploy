from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaWebPage
import asyncio
import os
import sys
import json

API_ID = os.getenv("YOUR_API_ID")
API_HASH = os.getenv("YOUR_API_HASH")
SESSION_NAME = "gingers_session"

SOURCE_CHAT_ID = [-1002293398473, -1002270373322, -1002293398473]
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
    56053:3851,
    57918:3852,
}
FALLBACK_THREAD_ID = 988

MESSAGE_MAPPING_FILE = 'message_mapping.json'

# Завантаження мапи відповідей
try:
    with open(MESSAGE_MAPPING_FILE, 'r') as f:
        MESSAGE_MAPPING = {int(k): int(v) for k, v in json.load(f).items()}
except FileNotFoundError:
    MESSAGE_MAPPING = {}

def save_mapping():
    with open(MESSAGE_MAPPING_FILE, 'w') as f:
        json.dump(MESSAGE_MAPPING, f)

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHAT_ID))
async def forward_message(event):
    try:
        destination_thread = None

        # Якщо це канал без гілок
        if event.chat_id == -1002270373322:
            destination_thread = FALLBACK_THREAD_ID

            # Але все одно шукаємо відповідь на старе повідомлення
            if event.message.reply_to:
                source_reply_id = event.message.reply_to.reply_to_msg_id
                if source_reply_id in MESSAGE_MAPPING:
                    destination_thread = MESSAGE_MAPPING[source_reply_id]

        # Якщо це канал з гілками
        else:
            if event.message.reply_to:
                source_reply_id = event.message.reply_to.reply_to_msg_id
                if source_reply_id in THREAD_MAPPING:
                    destination_thread = THREAD_MAPPING[source_reply_id]
                elif source_reply_id in MESSAGE_MAPPING:
                    destination_thread = MESSAGE_MAPPING[source_reply_id]

        if destination_thread:
            media = event.message.media
            buttons = event.message.buttons

            sent_message = None

            # Перевірка чи це web page
            if media and isinstance(media, MessageMediaWebPage):
                sent_message = await client.send_message(
                    DESTINATION_CHAT_ID,
                    event.message.message,
                    reply_to=destination_thread,
                    buttons=buttons
                )
            elif media:
                sent_message = await client.send_file(
                    DESTINATION_CHAT_ID,
                    file=event.message.media,
                    caption=event.message.message,
                    reply_to=destination_thread,
                    buttons=buttons
                )
            else:
                sent_message = await client.send_message(
                    DESTINATION_CHAT_ID,
                    event.message.message,
                    reply_to=destination_thread,
                    buttons=buttons
                )

            # Зберігаємо відповідність source id -> destination id
            MESSAGE_MAPPING[event.message.id] = sent_message.id
            save_mapping()

            print(f"✅ Переслано {event.message.id} ➔ {sent_message.id} у гілку {destination_thread}")
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

            # Перезапуск скрипта
            print("🔄 Перезапуск скрипта...")
            os.execv(sys.executable, ['python'] + sys.argv)

with client:
    client.loop.run_until_complete(main())
