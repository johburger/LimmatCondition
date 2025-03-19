import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


def get_weekly_forecast():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 47.383,
        "longitude": 8.54,
        "hourly": ["temperature_2m", "rain", "weather_code", "cloud_cover", "apparent_temperature"]
    }
    # Process first location. Add a for-loop for multiple locations or weather models
    response = openmeteo.weather_api(url, params=params)[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_data = {"date": pd.date_range(start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                                         end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                                         freq=pd.Timedelta(seconds=hourly.Interval()), inclusive="left")}
    hourly_data.update({key: hourly.Variables(i).ValuesAsNumpy() for i, key in enumerate(params['hourly'])})

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe['hour'] = hourly_dataframe['date'].apply(lambda x: x.time().hour)
    hourly_dataframe['day'] = hourly_dataframe['date'].apply(lambda x: x.date().day)
    hourly_dataframe = hourly_dataframe[hourly_dataframe['hour'] == 12].drop(columns=['hour', 'date'])
    retry_session.close()
    cache_session.close()
    return hourly_dataframe
