# 📊 Soprano Business Bot

Этот бот отслеживает цены токенов на биржах [DEXScreener](https://dexscreener.com) и [MEXC](https://www.mexc.com), определяет разницу между ними (спред) и уведомляет, если спред превышает 5%.

Полезен для:
- 💱 Арбитража
- 📈 Мониторинга рыночной неэффективности
- 🔍 Анализа ликвидности

## 🛠 Возможности

- Получает цены токенов с DEX и MEXC
- Вычисляет процентное различие между ними
- Отправляет алерт в Telegram, если спред > 5%
- Автоматическая проверка каждые 5 минут
- Команда `/check` для ручного запроса

---

## 📦 Установка
1. Клонируй репозиторий:
   ```bash
   git clone https://github.com/vxlxsco/sopranosbusiness
   cd sopranosbusiness
   ```
2. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создай файл `.env` и настрой:

   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   CHAT_ID=your_chat_id
   ```
4. Создай файл `tokens.json` в корне проекта, например:
   ```bash
   [
     {
    "symbol": "CAKE",
    "address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82",
    "chain": "bsc"
     },
     {
    "symbol": "SUI",
    "address": "0x1234567890abcdef",
    "chain": "sui"
     }
   ]
   ```
5. Запусти бота:
   ```bash
   python arbitrage.py
   ```
   
---

## 🧠 Как это работает

   -Загружает токены из tokens.json
   -Получает цену с MEXC (через API /ticker/price)
   -Получает цену с DEXScreener по сети и адресу токена
   -Вычисляет спред:
   `spread = |price_mexc - price_dex| / min(price_mexc, price_dex) * 100`
   Если спред > 5% — отправляет сообщение в Telegram.
