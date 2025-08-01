import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
from dotenv import load_dotenv
import os
import time
from typing import List, Tuple

# Загружаем переменные окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
if not CHAT_ID:
    raise ValueError("CHAT_ID не указан в .env. Укажи CHAT_ID чата, где работает бот.")

# Чтение токенов из tokens.json
def load_tokens():
    try:
        with open('tokens.json', 'r') as f:
            tokens = json.load(f)
        print(f"Загружено токенов: {len(tokens)} at {time.strftime('%H:%M:%S %Z, %d %B %Y')}")
        return tokens
    except FileNotFoundError:
        print("Файл tokens.json не найден.")
        return []
    except json.JSONDecodeError:
        print("Ошибка декодирования tokens.json.")
        return []

# Функция для получения цены с DEX Screener
def get_dex_price(token_address: str, chain: str):
    try:
        url = f"https://api.dexscreener.com/token-pairs/v1/{chain}/{token_address}"
        response = requests.get(url, headers={'Accept': '*/*'})
        response.raise_for_status()
        data = response.json()
        if data:
            for pair in data:
                if pair and 'baseToken' in pair and 'quoteToken' in pair:
                    quote_symbol = pair.get('quoteToken', {}).get('symbol')
                    if quote_symbol in ['USDT', 'USDC', 'BUSD', 'SOL', 'SUI'] and 'priceUsd' in pair:
                        return float(pair['priceUsd']), pair.get('dexId', 'Unknown DEX'), pair.get('pairAddress', '')
        print(f"Нет данных для {token_address} на {chain}.")
        return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка DEX API для {token_address} ({chain}): {e}")
        return None, None, None

# Функция для получения цены с MEXC API
def get_mexc_price(symbol: str) -> float:
    base_url = "https://api.mexc.com/api/v3/ticker/price"
    quote_currencies = ['USDT', 'BTC', 'BUSD']  # Возможные котировки
    for quote in quote_currencies:
        mexc_symbol = f"{symbol}{quote}".upper()  # Формат MEXC: CAKEUSDT
        try:
            params = {'symbol': mexc_symbol}
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data and 'price' in data and data['price']:
                price = float(data['price'])
                if price == 0:  # Обработка случая с нулевой ценой
                    print(f"Цена для {mexc_symbol} равна 0, возможно, токен недавно залистингован.")
                    return None
                print(f"Найдена цена для {mexc_symbol}: {price}")
                return price
            else:
                print(f"Пара {mexc_symbol} не найдена на MEXC.")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка MEXC API для {mexc_symbol}: {e}")
    
    # Если конкретная пара не найдена, попробуем получить все цены
    try:
        response = requests.get(base_url)  # Без параметров для всех пар
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            for item in data:
                if item['symbol'].startswith(symbol.upper()):
                    price = float(item['price'])
                    if price == 0:
                        print(f"Альтернативная пара {item['symbol']} имеет цену 0.")
                        return None
                    print(f"Найдена альтернативная пара для {symbol}: {item['symbol']} с ценой {price}")
                    return price
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении всех пар для {symbol}: {e}")
    
    print(f"Цена для {symbol} не найдена на MEXC.")
    return None

# Функция проверки спреда с обработкой нулей
def check_spread_logic(tokens):
    alert_list: List[Tuple] = []
    for token in tokens:
        symbol = token['symbol']
        token_address = token['address']
        chain = token['chain']

        # Проверка цены на MEXC
        mexc_price = get_mexc_price(symbol)
        if mexc_price is None or mexc_price == 0:
            print(f"Пропускаем {symbol}: цена на MEXC отсутствует или равна 0.")
            continue

        # Проверка цены на DEX
        dex_price, dex_name, pair_address = get_dex_price(token_address, chain)
        if dex_price is None or dex_price == 0:
            print(f"Пропускаем {symbol}: цена на DEX отсутствует или равна 0.")
            continue

        # Расчет спреда
        spread = abs(mexc_price - dex_price) / min(mexc_price, dex_price) * 100
        if spread > 5:
            alert_list.append((symbol, mexc_price, dex_price, dex_name, pair_address, spread, chain))

    if alert_list:
        message = "⚠️ Токены с спредом > 5%:\n"
        for symbol, mexc_p, dex_p, dex_n, pair_a, spr, chain in alert_list:
            message += (
                f"- {symbol} ({chain.upper()}):\n"
                f"  MEXC: ${mexc_p:.6f}\n"
                f"  {dex_n} (DEX): ${dex_p:.6f}\n"
                f"  Спред: {spr:.2f}%\n"
                f"  🔗 DEX Screener: https://dexscreener.com/{chain}/{pair_a}\n"
            )
        return message
    return "Нет токенов с спредом > 5%."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Приветствую! Поздравляю с покупкой подписки! Используй /check для ручной проверки или жди автоматическую каждые 5 минут. Бот отправляет токены с спредом 5% или больше.')
    context.job_queue.run_repeating(auto_check_spread, interval=300, first=0)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tokens = load_tokens()
    if not tokens:
        await update.message.reply_text("Ошибка: Не удалось загрузить токены.")
        return
    message = check_spread_logic(tokens)
    await update.message.reply_text(message)

async def auto_check_spread(context: ContextTypes.DEFAULT_TYPE):
    tokens = load_tokens()
    if not tokens:
        print("Нет токенов для автоматической проверки.")
        return
    message = check_spread_logic(tokens)
    await context.bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check))
    application.run_polling()

if __name__ == '__main__':
    main()