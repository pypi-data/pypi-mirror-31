# opensecrets_api
A python library to interact with the (opensecrets.org)[opensecrets.org] api.

## installation
This package can be installed using pip 
`pip install opensecrets_api`

## usage
Create an account with (opensecrets.org)[opensecrets.org] and obtain an api_key

    from opensecrets_api import OpenSecrets
    o = OpenSecrets('api_key')
    o.get_legislators('CA')
    
Documentation for the methods can be found in `opensecrets_api/__init__.py`

## license

opensecrets_api is distributed under the MIT license 