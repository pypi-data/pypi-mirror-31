import requests
import logging

from wia import Wia

'''
wia_post:
    args:
        path:   string specifying url path
        kwargs: variable-length dict which can
                contain data for post request
'''
def post(path, kwargs):
    url = generate_url(path)
    headers = generate_headers(path)

    if 'file' in kwargs:
        logging.debug("Has file argument.")
        kwargsCopy = dict(kwargs)
        del kwargsCopy['file']
        if type(kwargs['file']) is str :
            with open(kwargs['file'], 'rb') as f:
                r = requests.post(url, data=kwargsCopy, headers=headers, files={'file': f})
        else:
            r = requests.post(url, data=kwargsCopy, headers=headers, files={'file': kwargs['file']})
            kwargs['file'].close()

    else:
        logging.debug("No file argument. Posting as JSON.")
        r = requests.post(url, json=kwargs, headers=headers)
    return r

'''
wia_put:
    args:
        path:   string specifying url path
        kwargs: variable-length dict which can
                contain data for put request
'''
def put(path, kwargs):
    url = generate_url(path)
    headers = generate_headers(path)
    data = kwargs
    r = requests.put(url, json=data, headers=headers)
    return r

'''
wia_get:
    args:
        path:   string specifying url path
        kwargs: variable-length dict which can
                contain query params
'''
def get(path, **kwargs):
    url = generate_url(path)
    headers = generate_headers(path)

    r = requests.get(url, headers=headers, params=kwargs)
    return r

'''
wia_delete:
    args:
        path: string specifying url path
'''
def delete(path):
    url = generate_url(path)
    headers = generate_headers(path)

    r = requests.delete(url, headers=headers)
    return r

def generate_url(path):
    if path is None:
        path = ''

    url = Wia().rest_config['protocol'] + '://' + Wia().rest_config['host'] + '/' + Wia().rest_config['basePath'] + '/' + path

    logging.debug('URL: %s', url)

    return url

def generate_headers(path):
    headers = {}

    if Wia().app_key is not None:
        headers['x-app-key'] = Wia().app_key


    if Wia().access_token is not None:
        headers['Authorization'] = 'Bearer ' + Wia().access_token


    return headers
