import pyuseragents


headers = {
    'authority': 'cloud.argent-api.com',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9,ru-RU;q=0.8,en-US;q=0.7',
    'origin': 'https://unframed.co',
    'referer': 'https://unframed.co/',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': pyuseragents.random(),
}
