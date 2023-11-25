import requests
import json
import random
import config
from sparkdesk_api.core import SparkAPI

def get_plan(original, user_prompt):
    url = config.api_base
    # make s to be a string
    s = ' '.join(original)
    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "You are a travel planner, user wants to go to one place,you need to find the most related place in s, the only you need to reply is [city names] given at first **don't change the langueage or fromat in original strings s** s = [" + s + "]user:" + user_prompt
            }
        ]
    })

    headers = {
        'Authorization': 'Bearer ' + config.api,
        'User-Agent': 'Chrome/118.0.0.0',
        'Content-Type': 'application/json'
    }
    print('thinking...')
    response = requests.request("POST", url, headers=headers, data=payload)

    response_dict = json.loads(response.text)

    # 提取content字段的值
    content = response_dict['choices'][0]['message']['content']
    a = []

    print(content)
    for city in original:
        if city in content:
            a.append(city)

    if a == [] or a == original or a is None:
        print('Seems no response or have a API issue, try again，We give you a random city')
        a = [original[random.randint(0, len(original) - 1)]]
        return a

    result = [a[0]]
    print('done')
    print('the plan is: ', a)
    return result


def get_from_spark(original, user):
    sparkAPI = SparkAPI(
        app_id=config.app_id,
        api_secret=config.api_secret,
        api_key=config.api_key
    )
    s = ' '.join(original)
    print('thinking...')
    content = sparkAPI.chat("You are a travel planner, user wants to go to one place,you need to find the most related place in s, the only you need to reply is [city names] given to you **don't change the langueage or format in original strings s** s = [" + s + "]user:" + user)
    print(content)
    a = []
    for city in original:
        if city in content:
            a.append(city)

    if a == [] or a == original or a is None:
        print('Seems no response or have a API issue, try again，We give you a random city')
        a = [original[random.randint(0, len(original) - 1)]]
        return a

    result = [a[0]]
    print('done')
    print('the plan is: ', a)
    return result