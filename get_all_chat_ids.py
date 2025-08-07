import requests
import json
from collections import defaultdict
from config import BOT_TOKEN


def get_bot_info():
    """Получает информацию о боте"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    response = requests.get(url)
    if response.status_code == 200:
        bot_info = response.json()
        print(f"🤖 Информация о боте:")
        print(f"   Имя: {bot_info['result']['first_name']}")
        print(f"   Username: @{bot_info['result']['username']}")
        print(f"   ID: {bot_info['result']['id']}")
        print()
        return bot_info['result']
    else:
        print(f"❌ Ошибка получения информации о боте: {response.text}")
        return None

def get_all_chat_ids():
    """Получает ID всех чатов, в которых присутствует бот"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    # Получаем обновления с большим лимитом
    params = {
        'limit': 100,
        'timeout': 0
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"❌ Ошибка получения обновлений: {response.text}")
        return []
    
    updates = response.json()
    
    if not updates.get('ok'):
        print(f"❌ Ошибка API: {updates.get('description', 'Неизвестная ошибка')}")
        return []
    
    chats = defaultdict(dict)
    
    for update in updates['result']:
        chat = None
        
        # Обрабатываем разные типы обновлений
        if 'message' in update:
            chat = update['message']['chat']
        elif 'edited_message' in update:
            chat = update['edited_message']['chat']
        elif 'channel_post' in update:
            chat = update['channel_post']['chat']
        elif 'edited_channel_post' in update:
            chat = update['edited_channel_post']['chat']
        elif 'callback_query' in update:
            chat = update['callback_query']['message']['chat']
        elif 'inline_query' in update:
            # Для inline_query нет прямого chat_id, но есть from_user
            user = update['inline_query']['from']
            chat = {
                'id': user['id'],
                'type': 'private',
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'username': user.get('username', '')
            }
        
        if chat:
            chat_id = chat['id']
            if chat_id not in chats:
                chats[chat_id] = {
                    'id': chat_id,
                    'type': chat['type'],
                    'title': chat.get('title', ''),
                    'first_name': chat.get('first_name', ''),
                    'last_name': chat.get('last_name', ''),
                    'username': chat.get('username', ''),
                    'last_activity': update.get('date', 0)
                }
    
    return list(chats.values())

def get_webhook_info():
    """Получает информацию о webhook, если он настроен"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(url)
    if response.status_code == 200:
        webhook_info = response.json()
        if webhook_info['result']['url']:
            print(f"🔗 Webhook настроен: {webhook_info['result']['url']}")
            return webhook_info['result']
        else:
            print("🔗 Webhook не настроен")
            return None
    return None

def main():
    print("🔍 Поиск всех чатов, в которых присутствует бот...")
    print("=" * 60)
    
    # Получаем информацию о боте
    bot_info = get_bot_info()
    if not bot_info:
        return
    
    # Проверяем webhook
    webhook_info = get_webhook_info()
    print()
    
    # Получаем все чаты
    chats = get_all_chat_ids()
    
    if not chats:
        print("📭 Бот не найден ни в одном чате или нет обновлений")
        print("\n💡 Возможные причины:")
        print("   - Бот еще не был добавлен ни в один чат")
        print("   - Бот не получал сообщений/обновлений")
        print("   - Обновления были очищены")
        print("\n🔧 Рекомендации:")
        print("   1. Добавьте бота в чат и отправьте ему сообщение")
        print("   2. Используйте команду /start в личном чате с ботом")
        print("   3. Подождите несколько минут и попробуйте снова")
        return
    
    print(f"📋 Найдено чатов: {len(chats)}")
    print("=" * 60)
    
    # Группируем чаты по типу
    private_chats = [chat for chat in chats if chat['type'] == 'private']
    group_chats = [chat for chat in chats if chat['type'] == 'group']
    supergroup_chats = [chat for chat in chats if chat['type'] == 'supergroup']
    channel_chats = [chat for chat in chats if chat['type'] == 'channel']
    
    # Выводим личные чаты
    if private_chats:
        print(f"\n👤 Личные чаты ({len(private_chats)}):")
        for chat in private_chats:
            name = f"{chat['first_name']} {chat['last_name']}".strip()
            username = f"@{chat['username']}" if chat['username'] else "без username"
            print(f"   ID: {chat['id']} | {name} | {username}")
    
    # Выводим групповые чаты
    if group_chats:
        print(f"\n👥 Группы ({len(group_chats)}):")
        for chat in group_chats:
            title = chat['title'] or "Без названия"
            print(f"   ID: {chat['id']} | {title}")
    
    # Выводим супергруппы
    if supergroup_chats:
        print(f"\n🚀 Супергруппы ({len(supergroup_chats)}):")
        for chat in supergroup_chats:
            title = chat['title'] or "Без названия"
            username = f"@{chat['username']}" if chat['username'] else "без username"
            print(f"   ID: {chat['id']} | {title} | {username}")
    
    # Выводим каналы
    if channel_chats:
        print(f"\n📢 Каналы ({len(channel_chats)}):")
        for chat in channel_chats:
            title = chat['title'] or "Без названия"
            username = f"@{chat['username']}" if chat['username'] else "без username"
            print(f"   ID: {chat['id']} | {title} | {username}")
    
    print("\n" + "=" * 60)
    print("💡 Использование ID:")
    print("   - Для личных чатов: используйте числовой ID")
    print("   - Для групп/супергрупп: используйте числовой ID (с минусом)")
    print("   - Для каналов: используйте числовой ID (с минусом)")
    print("   - Для публичных чатов: можно использовать @username")
    
    # Сохраняем результаты в файл
    with open('chat_ids.json', 'w', encoding='utf-8') as f:
        json.dump({
            'bot_info': bot_info,
            'chats': chats,
            'summary': {
                'total': len(chats),
                'private': len(private_chats),
                'groups': len(group_chats),
                'supergroups': len(supergroup_chats),
                'channels': len(channel_chats)
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в файл 'chat_ids.json'")

if __name__ == "__main__":
    main() 