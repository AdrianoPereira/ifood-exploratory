import requests
import json

with open('authentication', 'r') as file:
    lines = file.readlines()
    ACCESS_KEY = lines[0].replace('\n', '').split('=')[1]
    SECRET_KEY = lines[1].replace('\n', '').split('=')[1]

print('ACCESS_KEY: ', ACCESS_KEY)
print('SECRET_KEY: ', SECRET_KEY)

CEP = '12227160'
SESSION_TOKEN, SET_COOKIES, JSESSIONID = None, None, None
MSG = ''

def get_restaurants(location_id):
    url = 'https://wsloja.ifood.com.br/ifood-ws-v3/restaurant/list'
    headers = {
        'User-Agent': 'Special',
        'Host': 'wsloja.ifood.com.br',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'session_token': SESSION_TOKEN,
        'Cookie': JSESSIONID
    }
    filters = 'filterJson=' + '{"cuisineTypes":[], "delivery":true, ' \
                              '"freeDeliveryFee":"true", "locationId": ' + str(location_id) + ',' \
    '"page":1, "pageSize":5000, "paymentType":[],' \
    '"sort":"0", "togo":false}'

    r = requests.post(url, headers=headers, data=filters)
    return json.loads(r.text)


def get_menu(restaurant):
    url = 'https://wsloja.ifood.com.br/ifood-ws-v3/restaurant/menu?restaurantId=%s'%(restaurant['restaurantId'])
    headers = {
        'User-Agent': 'Special',
        'Host': 'wsloja.ifood.com.br',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'session_token': SESSION_TOKEN,
        'Cookie': JSESSIONID
    }
    r = requests.get(url, headers=headers)
    data = json.loads(r.text)

    temp = '\n'
    try:
        for promo in data['data']['menu'][0]['itens']:
            temp += ('|--> %s: %.2f dól\n' % (promo['description'], promo['unitPrice']))
    except IndexError:
        pass
    return temp

def telegram_bot_sendtext(bot_message):
    with open('authentication', 'r') as file:
        lines = file.readlines()
        bot_token = lines[2].replace('\n', '').split('=')[1]
    bot_chatID = '-1001427930264'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)
    print(response.status_code)

    return response.json()

if __name__ == "__main__":
    #authenticate
    url = 'https://wsloja.ifood.com.br/ifood-ws-v3/app/config'
    headers = {
        'access_key': ACCESS_KEY,
        'secret_key': SECRET_KEY,
        'Host': 'wsloja.ifood.com.br',
        'User-Agent': 'special'
    }
    r = requests.get(url, headers=headers)
    SESSION_TOKEN = r.headers['session_token']
    SET_COOKIES = r.headers['Set-Cookie']
    JSESSIONID = SET_COOKIES[0:SET_COOKIES.find(';')]

    #get location
    url = 'https://wsloja.ifood.com.br/ifood-ws-v3/address/locationsByZipCode?zipCode=%s'%(CEP)
    headers = {
        'User-Agent': 'Special',
        'Host': 'wsloja.ifood.com.br',
        'session_token': SESSION_TOKEN,
        'Cookie': JSESSIONID
    }
    r = requests.get(url, headers=headers)
    dataloc = json.loads(r.text)
    locationId = dataloc['data']['locations'][0]['locationId']

    # restaurants = get_restaurants(CEP)
    # print(restaurants)
    MSG = '=-----Lista do Xadrez, By Seu Companheiro Lula-----=\n'
    print(restaurants['data']['list'][0].keys())

    for restaurant in restaurants['data']['list']:
        if restaurant['closed'] == False:
            MSG += restaurant['name'].upper()
            MSG += get_menu(restaurant)
            MSG += '\n'

    print(MSG)
    print(telegram_bot_sendtext(str(MSG[:4000])))
#
