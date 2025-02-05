import requests


def get_temp(city, key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric'
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return data['main']['temp']
    else:
        print('Проверьте название города')
        return None


def calorie_burned(activity, duration, key):
    api_url = f'https://api.api-ninjas.com/v1/caloriesburned?activity={activity}&duration={duration}'
    response = requests.get(api_url, headers={'X-Api-Key': key})
    if response.status_code == requests.codes.ok:
        return response.json()[0]['total_calories']
    else:
        return f"Error: {response.status_code}, {response.text}"


def get_calorie(food, key):
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
    response = requests.get(api_url + food, headers={'X-Api-Key': key})
    if response.status_code == requests.codes.ok:
        return response.json()['items'][0]['calories']
    else:
        return f"Error: {response.status_code}, {response.text}"


def calorie_count(weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age


def water_count(weight):
    return weight * 30

