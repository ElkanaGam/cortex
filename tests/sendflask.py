import requests

if __name__ == '__main__':
    r = requests.post('http://127.0.0.1:8000/snapshot', data='hello')
    print(r.text)