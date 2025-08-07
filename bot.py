import functools
import requests
from ratelimiter import RateLimiter
from config import BOT_TOKEN, CHAT_ID


@RateLimiter(max_calls=30, period=60)
def send_telegram_message(message: str):
    """
    Отправляет сообщение в Telegram чат через Bot API.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        # Если не удалось отправить сообщение, просто игнорируем ошибку
        pass


def telegram_notification_on_error(func):
    """
    Декоратор для отправки уведомления в Telegram при возникновении исключения в функции.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            message = (
                f"<b>❗️ Произошла ошибка в функции <code>{func.__name__}</code></b>\n\n"
                f"<code>{tb}</code>"
            )
            send_telegram_message(message)
            raise
    return wrapper
