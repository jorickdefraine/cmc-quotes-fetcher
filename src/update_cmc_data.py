import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Optional

load_dotenv()
CSV_FILE = "data.csv"
API_URL = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
FIELDS = [
        'active_cryptocurrencies',
        'total_cryptocurrencies',
        'active_market_pairs',
        'active_exchanges',
        'total_exchanges',
        'eth_dominance',
        'btc_dominance',
        'eth_dominance_yesterday',
        'btc_dominance_yesterday',
        'defi_volume_24h',
        'defi_volume_24h_reported',
        'defi_market_cap',
        'defi_24h_percentage_change',
        'stablecoin_volume_24h',
        'stablecoin_volume_24h_reported',
        'stablecoin_market_cap',
        'stablecoin_24h_percentage_change',
        'derivatives_volume_24h',
        'derivatives_volume_24h_reported',
        'derivatives_24h_percentage_change',
        'total_crypto_dex_currencies',
        'today_incremental_crypto_number',
        'past_24h_incremental_crypto_number',
        'past_7d_incremental_crypto_number',
        'past_30d_incremental_crypto_number',
        'today_change_percent',
        'last_updated',
        'total_market_cap',
        'total_volume_24h',
        'total_volume_24h_reported',
        'altcoin_volume_24h',
        'altcoin_volume_24h_reported',
        'altcoin_market_cap',
        'total_market_cap_yesterday',
        'total_volume_24h_yesterday',
        'total_market_cap_yesterday_percentage_change',
        'total_volume_24h_yesterday_percentage_change',
        'date'
    ]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_filtered_coinmarketcap_data() -> Optional[Dict]:
    """Récupère les données globales de CoinMarketCap et les filtre."""
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": os.getenv('CMC_PRO_API_KEY')
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        d = data['data']
        usd_quote = d.pop('quote', {}).get('USD', {})
        flat_data = {**d, **usd_quote}
        
        # Ensure date is set
        flat_data['date'] = d.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return {field: flat_data.get(field, None) for field in FIELDS}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de connexion: {e}")
        return None

def save_to_csv(data: Dict, filename: str) -> None:
    """Sauvegarde les données dans un fichier CSV."""
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame()
    
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df.to_csv(filename, index=False)
    logger.info(f"Données mises à jour:\n{df.tail()}")

if __name__ == "__main__":
    coinmarketcap_data = get_filtered_coinmarketcap_data()
    
    if coinmarketcap_data:
        save_to_csv(coinmarketcap_data, CSV_FILE)
    else:
        logger.warning("Aucune donnée récupérée.")