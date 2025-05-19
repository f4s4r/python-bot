This is bot for suggestions arabic books for beginners
@RecArabicBooks4BegginersBot


## Запуск с Docker

```bash
git clone https://github.com/f4s4r/python-bot.git
cd python-bot
echo "BOT_TOKEN=your_telegram_bot_token" > .env
docker build -t python-telegram-bot .
docker run --env-file .env python-telegram-bot

