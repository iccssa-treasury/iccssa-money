import requests, json
from datetime import datetime, timedelta
from config import settings

def fetchRates(src='CNY', dst='GBP'):
  url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={src}&to_symbol={dst}&apikey={settings.FX_API_KEY}&outputsize=full'
  response = requests.get(url).json()
  with open('fx.json', 'w') as f:
    json.dump(response, f, indent=2)

def getRate(date=None):
  date = firstWorkingDayBefore(date or datetime.now().date())
  try:
    with open('fx.json','r') as f:
      data = json.load(f)
    return float(data['Time Series FX (Daily)'][str(date)]['4. close'])
  except KeyError:
    fetchRates()
    with open('fx.json','r') as f:
      data = json.load(f)
    return float(data['Time Series FX (Daily)'][str(date)]['4. close'])

def firstWorkingDayBefore(date):
  date -= timedelta(days=1)
  while (date.weekday() > 4):
    date -= timedelta(days=1)
  return date

def exchange(amount, src, date=None):
  dst = '英镑'
  if src == dst:
    return amount
  elif src == '人民币':
    return int(amount * getRate(date))