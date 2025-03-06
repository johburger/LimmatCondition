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
import requests
import urllib.request
import json
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
    

#get air Temperature

with urllib.request.urlopen('https://data.geo.admin.ch/ch.meteoschweiz.messwerte-lufttemperatur-10min/ch.meteoschweiz.messwerte-lufttemperatur-10min_de.json') as url:
    data = json.load(url)

for i in data['features']:
    if i['properties']['station_name'] == 'Zürich / Affoltern':
        luftTemp = i['properties']['value']

print("Water temperature is: ", wasserTemp, "°C")
print("Air temperature is: ", luftTemp, "°C")

limmatCon = 2.5*wasserTemp + luftTemp
  

#plot the Limmat Condition
wT = np.arange(0,30,1)
lTu = 50-2.5*wT
lTb = ((20-wT)*50**(1/2.4)/20)**2.4
plt.plot(wT, lTu,linewidth=2, color='black')
plt.plot(wT, lTb,linewidth=2, color='black')
plt.fill_between(wT, lTb, min(lTb), alpha=0.2,color='coral')
plt.fill_between(wT, lTu, max(lTu), alpha=0.2,color='limegreen')
#rest
plt.xlabel('water temperature [°C]')
plt.ylabel('air temperature [°C]')
plt.xlim(min(wT),max(wT))
plt.ylim(0, max(lTu))
plt.grid()

if limmatCon>=50:
    print("It's time to Limmaaaaat!")
    plt.plot(wasserTemp, luftTemp,'X', markersize=15, color='limegreen')
    plt.text(10,45,"It's time to Limmaaaaat!")    
elif limmatCon<50 and luftTemp>=((20-wasserTemp)*50**(1/2.4)/20)**2.4:
    print("It's not going to be fun, but you can do it!")
    plt.plot(wasserTemp, luftTemp,'X', markersize=15, color='black')
    plt.text(10,45,"It's not going to be fun, but you can do it!")   
else:
    print("Why going to Limmat when it's ski time?!?!")
    plt.plot(wasserTemp, luftTemp,'X', markersize=15, color='coral')
    plt.text(10,45,"Why going to Limmat when it's ski time?!?!")  
    
plt.show()
# %%
