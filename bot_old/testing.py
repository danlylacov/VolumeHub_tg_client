import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_ADRESS = os.environ['API_URL']


action_name = 'iГЕНЕТИКО '

figi = requests.get(f'{API_ADRESS}/get_figi_by_action_name/{action_name[:-1]}').json()
print(figi)

book = requests.get(f'{API_ADRESS}/get_order_book_percent/{figi}').json()


print(book)


