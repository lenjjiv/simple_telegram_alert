from bot import telegram_notification_on_error

@telegram_notification_on_error
def main():
    raise ValueError("Тестовая ошибка")

if __name__ == "__main__":
    main()