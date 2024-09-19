# UEFA Euros History and 2024 Prediction
## Description
Euros 2024 predictions utilizing predictive modeling and machine learning.
## 1. Objective
* This project aims to delve into the UEFA Euros' historical significance and contemporary relevance in European football. By analyzing inaugural matches, host cities, and team performances, it seeks to understand the tournament's evolution. Additionally, it examines correlations between World Cup success and Euros performance, competitiveness relative to other continental championships, and the impact of hosting nations. Using predictive modeling, the project forecasts match outcomes and predicts the Euro 2024 winner, providing valuable insights for all and enhancing understanding of tournament dynamics.

## 2. Install Dependencies

```
pip install -r requirements.txt
```

## 3. Custom Information
* Run in order: get_data.py > clean_data.py > integrate_data.py > analyze_visualize.ipynb
* get_data.py, integrate_data.py and the geolocator part in analyze_visualize may take some time (up to 30 minutes)
* Included a rate limiter with geolocator due to recent TimeoutError (used to work cleanly last week but not as well this week so the rate limiter aids us getting the result albeit we may get extra error messages depending on the day)
