# pythonRestfulNews
Python module to enable python users to use our api

## Installation
Our module can be installed via pip:

```
pip install pythonRestfullNews
```

## Usage

```python
import pythonRestfulNews as prn

#create a user:
resp = prn.create_user('email@gmail.com', 'password')

#get the token:
token = resp['token']

#make the request:
topics = 'food'
companyids = 'woolworths'
start_date = '2018-03-01T00:00:00.000Z'
end_date = '2018-03-25T00:00:00.000Z'
        
news = prn.search_news(token, topics, companyids, start_date, end_date)


```
