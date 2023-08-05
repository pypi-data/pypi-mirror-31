# lionshare

Lionshare is a Python wrapper for the
[Lionshare API](https://github.com/lionsharecapital/lionshare-api). You can
get prices and market info on various cryptocurrencies.

## Installation

```
pip install lionshare
```

## Usage

```python
from lionshare import Lionshare
lionshare = Lionshare()

# All responses are in json

# Get historical prices for cryptocurrencies
prices = api.get_prices()
# Optional period parameter (hour, day, week, month, year)
prices = api.get_prices('hour')

# Get current market info for cryptocurrencies
market_info = api.get_markets()
```