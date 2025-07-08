import requests

url = "http://localhost:5000/log-anomaly"
headers = {"Content-Type": "application/json"}
data = {
  "name": "GAZP",
  "priceCurrent": 180.5,
  "volume": 15000,
  "priceDailyChangeAsPercentage": 2.5,
  "priceMinuteChangeAsPercentage": -1.2,
  "time": "2025-07-01T15:51:00.000Z",
  "candlesLastHour": [
    {
      "open": 178.0,
      "high": 182.0,
      "low": 177.5,
      "close": 180.5,
      "volume": 15000,
      "timestamp": "2025-07-01T15:51:00.000Z"
    },
    {
      "open": 177.5,
      "high": 179.0,
      "low": 177.0,
      "close": 178.0,
      "volume": 12000,
      "timestamp": "2025-07-01T15:50:00.000Z"
    }
  ]
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())