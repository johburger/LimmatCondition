"""
Limmat condition
Luca Bosetti
v1 March 2019
v2 April 2022
v3 September 2023
v4 October 2024
v5 March 2025 --> https://github.com/bosettil/LimmatCondition.git
"""
# %%
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import requests
import urllib.request
import json
from ForecastModel import get_weekly_forecast

pd.set_option('display.max_colwidth', 500)

#get water Temperature

# Your HTML content (replace this with your actual HTML content)
html_content = requests.get("https://hydroproweb.zh.ch/Listen/AktuelleWerte/AktWassertemp.html")
# ... (your HTML content here)
# Parse the HTML content
soup = bs(html_content.content, features='html.parser')
# Find the table with the data
table = soup.find('table')
# Initialize variables to store the result
wasserTemp = ""
# Loop through the rows of the table
for row in table.find_all('tr'):
    # Find all the cells in the row
    cells = row.find_all('td')
    if len(cells) >= 2:
        # Check if the first cell (Gewässer/See) contains "Limmat-Zch. KW Letten"
        if "Limmat-Zch. KW Letten" in cells[0].text:
            # Get the value from the fourth cell (Aktueller Wert)
            aktueller_wert = cells[3].text
            wasserTemp = float(aktueller_wert.replace('\xa0', ''))

# several forecast metrics are returned for today and the next six days, always at 12:00.
forecast = get_weekly_forecast().reset_index(drop=True)
luftTemp = forecast.loc[0, 'apparent_temperature']
luftTemp_forecast = forecast.loc[1:, 'apparent_temperature']
air_temp_deviation = [[luftTemp - min(luftTemp_forecast)], [max(luftTemp_forecast) - luftTemp]]
air_temp_uncertainty = np.std(forecast.loc[1:, 'apparent_temperature'])

print(f"Water temperature is: {wasserTemp:.1f}°C")
print(f"Air temperature is: {luftTemp:.1f}°C")

limmatCon = 2.5 * wasserTemp + luftTemp

#plot the Limmat Condition
wT = np.arange(0, 30, 1)
lTu = 50 - 2.5 * wT
lTb = ((20 - wT) * 50 ** (1 / 2.4) / 20) ** 2.4
plt.plot(wT, lTu, linewidth=2, color='black')
plt.plot(wT, lTb, linewidth=2, color='black')
plt.fill_between(wT, lTb, min(lTb), alpha=0.2, color='coral')
plt.fill_between(wT, lTu, max(lTu), alpha=0.2, color='limegreen')
#rest
plt.xlabel('water temperature [°C]')
plt.ylabel('air temperature [°C]')
plt.xlim(min(wT), max(wT))
plt.ylim(0, max(lTu))
plt.grid()

if limmatCon >= 50:
    color = 'limegreen'
    message = "It's time to Limmaaaaat!"
    cmap = cm.get_cmap('Greens')
elif limmatCon < 50 and luftTemp >= ((20 - wasserTemp) * 50 ** (1 / 2.4) / 20) ** 2.4:
    message = "It's not going to be fun, but you can do it!"
    color = 'black'
    cmap = cm.get_cmap('Greys')
else:
    message = "Why going to Limmat when it's ski time?!?!"
    color = 'coral'
    cmap = cm.get_cmap('Reds')

print(message)
plt.errorbar(wasserTemp, luftTemp, yerr=air_temp_deviation, color=cmap(0.4), alpha=0.8, capsize=5,
             fmt='', markersize=8, ecolor=cmap(0.6), label="Forecast for next week")
plt.plot(wasserTemp, luftTemp, 'X', markersize=15, color=color)
plt.text(10, 45, message)

plt.show()
# %%
