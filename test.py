import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ta.volatility import AverageTrueRange

# --- Configuration ---
DATA_FILE = 'ada_historical_data.csv'  # Remplacez par le chemin de vos données historiques
ATR_PERIOD = 14
MULTIPLIER_RANGE = [1.0, 1.5, 2.0, 2.5, 3.0]  # Les multiplicateurs à tester

def load_data(file_path):
    """Charge les données historiques."""
    data = pd.read_csv(file_path)
    data['datetime'] = pd.to_datetime(data['datetime'])
    data.set_index('datetime', inplace=True)
    return data

def calculate_atr_bands(data, multiplier):
    """Calcule les bandes ATR dynamiques pour un multiplicateur donné."""
    atr = AverageTrueRange(high=data['high'], low=data['low'], close=data['close'], window=ATR_PERIOD)
    data['ATR'] = atr.average_true_range()
    data['Upper Band'] = data['close'] + (data['ATR'] * multiplier)
    data['Lower Band'] = data['close'] - (data['ATR'] * multiplier)
    return data

def plot_atr_bands(data, multiplier, ax):
    """Affiche les bandes ATR dynamiques sur un axe spécifique."""
    ax.plot(data['close'], label='Close', color='black', linewidth=1.5)
    ax.plot(data['Upper Band'], label=f'Upper Band (x{multiplier})', linestyle='--', color='blue')
    ax.plot(data['Lower Band'], label=f'Lower Band (x{multiplier})', linestyle='--', color='red')
    ax.set_title(f'ATR Bands with Multiplier {multiplier}')
    ax.legend()

# --- Main Script ---
if __name__ == "__main__":
    # Charger les données
    data = load_data(DATA_FILE)

    # Limiter aux 2 derniers mois
    last_two_months = data[data.index >= (data.index.max() - pd.DateOffset(months=2))]

    # Créer une figure avec des sous-graphiques
    fig, axes = plt.subplots(len(MULTIPLIER_RANGE), 1, figsize=(12, 6 * len(MULTIPLIER_RANGE)))

    # Tester les multiplicateurs
    for i, multiplier in enumerate(MULTIPLIER_RANGE):
        print(f"Testing multiplier: {multiplier}")
        data_with_bands = calculate_atr_bands(last_two_months.copy(), multiplier)
        plot_atr_bands(data_with_bands, multiplier, axes[i])

    # Ajuster l'espacement entre les sous-graphiques
    plt.tight_layout()
    plt.show()

    print("Test des multiplicateurs terminé.")
