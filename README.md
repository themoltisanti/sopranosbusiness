# 💼💵 Soprano Business Bot

This bot tracks token prices on [DEXScreener](https://dexscreener.com) and [MEXC](https://www.mexc.com), calculates the difference between them (spread), and notifies you if the spread exceeds 5%.

Useful for:
- 💱 Arbitrage
- 📈 Monitoring market inefficiencies
- 🔍 Liquidity analysis

## 🛠 Features

- Fetches token prices from DEX and MEXC
- Calculates the percentage difference between them
- Sends a Telegram alert if the spread > 5%
- Automatic check every 5 minutes
- `/check` command for manual price check

---

## 📦 Installation
1. Clone the repository:
   ```
   git clone https://github.com/themoltisanti/sopranosbusiness.git
   cd sopranosbusiness
```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and configure:

   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   CHAT_ID=your_chat_id
   ```
4. Create a `tokens.json` file in the project root, for example:

   ```json
   [
     {"symbol": "CAKE", "address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82", "chain": "bsc"},
     {"symbol": "SHIB", "address": "0x2859e4544c4bb03966803b044a93563bd2d0dd4d", "chain": "bsc"},
     {"symbol": "IKA", "address": "0x7262fb2f7a3a14c888c438a3cd9b912469a58cf60f367352c46584262e8299aa::ika::IKA", "chain": "sui"},
     {"symbol": "ZKJ", "address": "0xC71B5F631354BE6853eFe9C3Ab6b9590F8302e81", "chain":"bsc"}, 
     {"symbol": "TROLLSOL", "address": "5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2", "chain":"solana"},
     {"symbol": "HOSICO", "address": "9wK8yN6iz1ie5kEJkvZCTxyN1x5sTdNfx8yeMY8Ebonk", "chain": "solana"}
   ]
   ```
5. Run the bot:

   ```bash
   python arbitrage.py
   ```

---

## 🧠 How it works

* Loads tokens from `tokens.json`
* Fetches price from MEXC (via API `/ticker/price`)
* Fetches price from DEXScreener using network and token address
* Calculates spread:

  ```text
  spread = |price_mexc - price_dex| / min(price_mexc, price_dex) * 100
  ```
* If spread > 5% — sends a Telegram message.

---

## 💬 Available commands

| Command  | Description                                             |
| -------- | ------------------------------------------------------- |
| `/start` | Starts automatic price checking every 5 minutes         |
| `/check` | Performs a manual token check and sends current spreads |

(Future updates will add more commands and features)

---

## 📎 Example Notifications

```
⚠️ Tokens with spread > 5%:
- CAKE (BSC):
  MEXC: $2.310000
  PancakeSwap (DEX): $2.180000
  Spread: 5.96%
 🔗 DEX Screener: https://dexscreener.com/bsc/0x123...
```

---

## 🙋 Feedback

* GitHub: @themoltisanti
* Telegram: @themoltisanti
