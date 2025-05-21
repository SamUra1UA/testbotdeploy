import re
from telethon import TelegramClient, events, Button
from telethon.tl.types import MessageMediaWebPage
import asyncio
import os
import sys
import json

API_ID = os.getenv("YOUR_API_ID")
API_HASH = os.getenv("YOUR_API_HASH")
SESSION_NAME = "gingers_session"

SOURCE_CHAT_ID = [-1002293398473, -1002270373322, -1002293398473, -1002628565313, -1002696474292]
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
FALLBACK_THREAD_ID_2 = 5054
FALLBACK_THREAD_ID_TEST = 5057

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

def extract_links(text):
    """Витягує всі URL з тексту"""
    if not text:
        return []
    url_pattern = r'(https?://[^\s]+)'
    return re.findall(url_pattern, text)

def generate_link_buttons(links):
    """Генерує кнопки для посилань"""
    return [Button.url(f"🔗 Link {i+1}", link) for i, link in enumerate(links)]

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHAT_ID))
async def forward_message(event):
    try:
        destination_thread = None

        media = event.message.media
        text = event.message.message or ""
        original_buttons = event.message.buttons or []
        links = extract_links(text)
        link_buttons = generate_link_buttons(links)
        combined_buttons = original_buttons + [[btn] for btn in link_buttons] if link_buttons else original_buttons

        # Канал без гілок
        if event.chat_id == -1002270373322:
            destination_thread = FALLBACK_THREAD_ID
            if event.message.reply_to:
                source_reply_id = event.message.reply_to.reply_to_msg_id
                if source_reply_id in MESSAGE_MAPPING:
                    destination_thread = MESSAGE_MAPPING[source_reply_id]

        elif event.chat_id == -1002628565313:
            destination_thread = FALLBACK_THREAD_ID_2
            if event.message.reply_to:
                source_reply_id = event.message.reply_to.reply_to_msg_id
                if source_reply_id in MESSAGE_MAPPING:
                    destination_thread = MESSAGE_MAPPING[source_reply_id]

        elif event.chat_id == -1002696474292:
            destination_thread = FALLBACK_THREAD_ID_TEST
            if event.message.reply_to:
                source_reply_id = event.message.reply_to.reply_to_msg_id
                if source_reply_id in MESSAGE_MAPPING:
                    destination_thread = MESSAGE_MAPPING[source_reply_id]

        # Канали з гілками
        else:
            if event.message.reply_to:
                source_reply_id = event.message.reply_to.reply_to_msg_id
                if source_reply_id in THREAD_MAPPING:
                    destination_thread = THREAD_MAPPING[source_reply_id]
                elif source_reply_id in MESSAGE_MAPPING:
                    destination_thread = MESSAGE_MAPPING[source_reply_id]

        if not destination_thread:
            print("⚠️ Повідомлення пропущене: немає відповідної гілки.")
            return

        sent_message = None

        if media:
            sent_message = await client.send_file(
                DESTINATION_CHAT_ID,
                file=media,
                caption=text,
                reply_to=destination_thread,
                buttons=combined_buttons
            )
        else:
            sent_message = await client.send_message(
                DESTINATION_CHAT_ID,
                text,
                reply_to=destination_thread,
                buttons=combined_buttons
            )

        # Зберігаємо відповідність ID
        MESSAGE_MAPPING[event.message.id] = sent_message.id
        save_mapping()

        print(f"✅ Переслано {event.message.id} ➔ {sent_message.id} у гілку {destination_thread}")

    except Exception as e:
        print(f"❌ Помилка при обробці повідомлення: {e}")
        await asyncio.sleep(2)

async def main():
    print("🚀 Бот запущено...")
    while True:
        try:
            await client.run_until_disconnected()
        except Exception as e:
            print(f"❗ Помилка при підключенні: {e}")
            print("🔁 Перепідключення через 1 секунду...")
            await asyncio.sleep(1)
            print("🔄 Перезапуск скрипта...")
            os.execv(sys.executable, ['python'] + sys.argv)

with client:
    client.loop.run_until_complete(main())
