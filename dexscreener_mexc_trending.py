import requests
import time
import json
from datetime import datetime, UTC

# Поддерживаемые блокчейны
CHAINS = {
    'solana': 'solana',
    'bsc': 'bsc',
    'base': 'base',
    'sui': 'sui'
}

# Фильтры для DEX (исходные строгие значения)
VOLUME_24H_MIN = 50000
VOLUME_24H_MAX = 10000000
MARKET_CAP_MIN = 100000
MARKET_CAP_MAX = 20000000
LIQUIDITY_MIN = 10000
LIQUIDITY_MAX = 500000
AGE_HOURS_MAX = 72

def get_dexscreener_tokens():
    """Получение токенов с DEX Screener (latest, boosted)"""
    tokens = []
    
    # Эндпоинт /token-profiles/latest/v1
    try:
        response = requests.get("https://api.dexscreener.com/token-profiles/latest/v1", headers={"Accept": "*/*"})
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            tokens.extend(data)
            if data:
                print(f"/token-profiles/latest/v1: Ключи первого токена: {list(data[0].keys())}")
        elif isinstance(data, dict):
            tokens.extend(data.get('tokens', []))
            if data.get('tokens'):
                print(f"/token-profiles/latest/v1: Ключи первого токена: {list(data['tokens'][0].keys())}")
        else:
            print("Неожиданный формат ответа от /token-profiles/latest/v1")
    except requests.RequestException as e:
        print(f"Ошибка при получении latest tokens: {e}")

    # Эндпоинт /token-boosts/latest/v1
    try:
        response = requests.get("https://api.dexscreener.com/token-boosts/latest/v1", headers={"Accept": "*/*"})
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            tokens.extend(data)
            if data:
                print(f"/token-boosts/latest/v1: Ключи первого токена: {list(data[0].keys())}")
        elif isinstance(data, dict):
            tokens.extend(data.get('tokens', []))
            if data.get('tokens'):
                print(f"/token-boosts/latest/v1: Ключи первого токена: {list(data['tokens'][0].keys())}")
        else:
            print("Неожиданный формат ответа от /token-boosts/latest/v1")
    except requests.RequestException as e:
        print(f"Ошибка при получении boosted tokens: {e}")

    # Пропускаем /latest/dex/search из-за ошибки 400
    return tokens

def filter_tokens(tokens):
    """Фильтрация токенов по заданным критериям (только DEX)"""
    verified_tokens = []
    notverified_tokens = []
    current_time = datetime.now(UTC)

    for token in tokens:
        try:
            chain_id = token.get('chainId', '').lower()
            if chain_id not in CHAINS:
                print(f"Токен {token.get('symbol', 'unknown')} пропущен: неподдерживаемый блокчейн {chain_id}")
                continue

            # Используем tokenAddress
            token_address = token.get('tokenAddress')
            if not token_address:
                print(f"Токен {token.get('symbol', 'unknown')} пропущен: отсутствует tokenAddress")
                continue

            response = requests.get(
                f"https://api.dexscreener.com/token-pairs/v1/{chain_id}/{token_address}",
                headers={"Accept": "*/*"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Обработка ответа: список или словарь
            if isinstance(data, list):
                pair_data = data[0] if data else {}
            elif isinstance(data, dict):
                pair_data = data.get('pairs', [{}])[0]
            else:
                print(f"Токен {token.get('symbol', 'unknown')}: неожиданный формат ответа")
                continue

            # Логирование структуры pair_data
            print(f"Токен {token.get('symbol', 'unknown')}: Ключи pair_data: {list(pair_data.keys())}")

            volume_24h = pair_data.get('volume', {}).get('h24', 0)
            market_cap = pair_data.get('marketCap', 0)
            liquidity = pair_data.get('liquidity', {}).get('usd', 0)
            created_at = pair_data.get('createdAt', 0) / 1000
            token_age = (current_time - datetime.fromtimestamp(created_at, tz=UTC)).total_seconds() / 3600
            symbol = pair_data.get('baseToken', {}).get('symbol', token.get('symbol', 'unknown'))

            # Логирование для диагностики
            print(f"Токен {symbol}: "
                  f"volume_24h={volume_24h}, market_cap={market_cap}, "
                  f"liquidity={liquidity}, age_hours={token_age}")

            token_data = {
                'symbol': symbol,
                'chain': chain_id,
                'address': token_address,
                'volume_24h': volume_24h,
                'market_cap': market_cap,
                'liquidity': liquidity,
                'age_hours': token_age
            }

            if (VOLUME_24H_MIN <= volume_24h <= VOLUME_24H_MAX and
                MARKET_CAP_MIN <= market_cap <= MARKET_CAP_MAX and
                LIQUIDITY_MIN <= liquidity <= LIQUIDITY_MAX and
                token_age <= AGE_HOURS_MAX):
                verified_tokens.append(token_data)
            else:
                notverified_tokens.append(token_data)
                print(f"Токен {symbol} не прошёл фильтры: "
                      f"volume_24h={volume_24h} (требуется {VOLUME_24H_MIN}-{VOLUME_24H_MAX}), "
                      f"market_cap={market_cap} (требуется {MARKET_CAP_MIN}-{MARKET_CAP_MAX}), "
                      f"liquidity={liquidity} (требуется {LIQUIDITY_MIN}-{LIQUIDITY_MAX}), "
                      f"age_hours={token_age} (требуется <= {AGE_HOURS_MAX})")
        except (requests.RequestException, KeyError) as e:
            print(f"Ошибка при обработке токена {token.get('symbol', 'unknown')}: {e}")
            continue

    return verified_tokens, notverified_tokens

def check_mexc_listings(tokens):
    """Проверка наличия токенов на MEXC (без фильтров)"""
    mexc_tokens = []
    try:
        response = requests.get("https://api.mexc.com/api/v3/exchangeInfo")
        response.raise_for_status()
        mexc_symbols = [symbol['symbol'] for symbol in response.json()['symbols']]
    except requests.RequestException as e:
        print(f"Ошибка при получении данных с MEXC: {e}")
        return []

    for token in tokens:
        symbol = token['symbol']
        if not symbol or symbol == 'unknown':
            print(f"Токен с адресом {token['address']} пропущен: отсутствует символ")
            continue
        for mexc_symbol in mexc_symbols:
            if symbol in mexc_symbol:
                mexc_tokens.append({
                    'symbol': symbol,
                    'chain': token['chain'],
                    'address': token['address'],
                    'volume_24h': token['volume_24h'],
                    'market_cap': token['market_cap'],
                    'liquidity': token['liquidity'],
                    'age_hours': token['age_hours'],
                    'mexc_pair': mexc_symbol
                })
                break

    return mexc_tokens

def save_to_json(tokens, filename):
    """Сохранение данных о токенах в JSON-файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=4)
        print(f"Данные успешно сохранены в {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении в JSON: {e}")

def main():
    print("Получение токенов с DEX Screener...")
    tokens = get_dexscreener_tokens()
    print(f"Получено {len(tokens)} токенов.")

    print("Фильтрация токенов (только DEX)...")
    verified_tokens, notverified_tokens = filter_tokens(tokens)
    print(f"Отфильтровано {len(verified_tokens)} токенов (прошли фильтры).")
    print(f"Не прошли фильтры {len(notverified_tokens)} токенов.")

    print("Сохранение токенов...")
    save_to_json(verified_tokens, "verified.json")
    save_to_json(notverified_tokens, "notverified.json")

    print("Проверка токенов на MEXC (без фильтров)...")
    mexc_tokens = check_mexc_listings(verified_tokens)

    if mexc_tokens:
        save_to_json(mexc_tokens, "mexc_tokens.json")
    else:
        print("Нет токенов, соответствующих критериям, для сохранения на MEXC.")

    print("\nНайденные токены, доступные на MEXC:")
    for token in mexc_tokens:
        print(f"Символ: {token['symbol']}, "
              f"Блокчейн: {token['chain']}, "
              f"Адрес: {token['address']}, "
              f"Объем (24ч): ${token['volume_24h']:,.2f}, "
              f"Рын. кап.: ${token['market_cap']:,.2f}, "
              f"Ликвидность: ${token['liquidity']:,.2f}, "
              f"Возраст (часы): {token['age_hours']:.2f}, "
              f"Пара на MEXC: {token['mexc_pair']}")

if __name__ == "__main__":
    main()