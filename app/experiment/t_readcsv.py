# read csv file from web
# https: // football-data.co.uk/data.php
import pandas as pd

url = 'https://football-data.co.uk/mmz4281/2223/E0.csv'
pl = pd.read_csv(url)

print(pl.head())
pl.rename(columns={'HomeTeam': 'Home', 'AwayTeam': 'Away'}, inplace=True)
