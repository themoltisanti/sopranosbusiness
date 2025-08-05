# 💼💵 Soprano Business Bot

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
   git clone https://github.com/themoltisanti/sopranosbusiness.git
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
     {"symbol": "CAKE", "address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82", "chain": "bsc"},
     {"symbol": "SHIB", "address": "0x2859e4544c4bb03966803b044a93563bd2d0dd4d", "chain": "bsc"},
     {"symbol": "IKA", "address": "0x7262fb2f7a3a14c888c438a3cd9b912469a58cf60f367352c46584262e8299aa::ika::IKA", "chain": "sui"},
     {"symbol": "ZKJ", "address": "0xC71B5F631354BE6853eFe9C3Ab6b9590F8302e81", "chain":"bsc"}, 
     {"symbol": "TROLLSOL", "address": "5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2", "chain":"solana"},
     {"symbol": "HOSICO", "address": "9wK8yN6iz1ie5kEJkvZCTxyN1x5sTdNfx8yeMY8Ebonk", "chain": "solana"}
   ]
   ```
5. Запусти бота:
   ```bash
   python arbitrage.py
   ```
   
---

## 🧠 Как это работает

- Загружает токены из tokens.json
- Получает цену с MEXC (через API /ticker/price)
- Получает цену с DEXScreener по сети и адресу токена
- Вычисляет спред:
  `spread = |price_mexc - price_dex| / min(price_mexc, price_dex) * 100`
- Если спред > 5% — отправляет сообщение в Telegram.
  
---

## 💬 Доступные команды
| Команда  | Описание                                                   |
| -------- | ---------------------------------------------------------- |
| `/start` | Запускает автоматическую проверку каждые 5 минут           |
| `/check` | Делает ручную проверку токенов и отправляет текущие спреды |

(В будущем будет больше команд, некоторые будут переработаны)

---

## 📎 Примеры уведомлений
```
⚠️ Токены с спредом > 5%:
- CAKE (BSC):
  MEXC: $2.310000
  PancakeSwap (DEX): $2.180000
  Спред: 5.96%
 🔗 DEX Screener: https://dexscreener.com/bsc/0x123...
```

---

## 🙋 Обратная связь
- GitHub: @themoltisanti
- Telegram: @themoltisanti
