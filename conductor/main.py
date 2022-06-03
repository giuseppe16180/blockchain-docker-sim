# %%
from regex import F
import requests
import random

url = 'http://localhost:5002'

def random_data() -> str:
    subjects = ['Alice', 'Bob', 'Carl', 'Dave', 'Eve', 'Frank', 'George', 'Harry', 'Ida']
    verbs = ['likes', 'dislikes', 'wants', 'hates', 'enjoys', 'loves', 'hates', 'wants', 'likes']
    objects = ['mango', 'banana', 'strawberry', 'pineapple', 'peach', 'pear', 'apple', 'peach', 'mango']
    return f'{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}'


response = requests.get(f'{url}/mine')

if response.status_code == 200:
    response_dict = response.json()
    print(f'{response_dict}')
else:
    print(f'{response.status_code} - {response.reason}')


#post on http://localhost:5000/transactions/new
data = {'sender': 'Alice', 'recipient': 'Bob', 'amount': '5'}
response = requests.post(f'{url}/transactions/new', json=data)

if response.status_code == 201:
    response_dict = response.json()
    print(f'{response_dict}')
else:
    print(f'{response.status_code}')



# %% getting chain

response = requests.get(f'{url}/chain')

if response.status_code == 200:
    response_dict = response.json()
    print(f'{response_dict}')
else:
    print(f'{response.status_code}')



# %%





