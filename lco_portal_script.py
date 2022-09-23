import requests
from os import path
from datetime import datetime

# UNCOMMENT ME!  When you have set up your local copy of default_config.py
from local_config import config, params

def run():

    obs_set = query_for_observations(config, params, verbose=True)

    cancel_observations(config, obs_set)

def query_for_observations(config, params, verbose=True):
    """Function to query for a list of observations matching the parameters
    specified"""

    # The API accepts only the following criteria:
    api_criteria = ['site', 'enclosure', 'telescope', 'start_after',
                    'start_before', 'priority', 'state']
    query = {}
    for key in api_criteria:
        if key in params.keys() and params[key]:
            query[key] = params[key]

    if verbose:
        print('Submitting query: '+repr(query))

    # The results are paginated, and attempts to override this using the limit
    # parameter were not successful.  So we need to loop through the pages
    query_set = lco_interface_paginated_get(config,query)

    if verbose:
        print('Query returned '+str(len(query_set))+' results')
        for obs in query_set:
            print(obs['id'], obs['proposal'], obs['start'], obs['end'], obs['state'])

    # Now apply the other selection criteria:
    print('Filtering query set by proposal code')
    observation_set = []
    for obs in query_set:
        if obs['proposal'] == params['proposal']:
            observation_set.append(obs)

    print('Retrieved '+str(len(observation_set))
            + ' observations matching all search parameters:')
    for obs in observation_set:
        print(obs['id'], obs['proposal'], obs['start'], obs['end'], obs['state'])

    return observation_set

def cancel_observations(config, obs_set):
    """Function loops through the provided set of observations and asks for
    user confirmation before cancelling"""

    for obs in obs_set:
        payload = {
            'ids': [obs['id']],
            # These specify which observation types to include in the set to be
            # canceled. This will protect you from accidentally cancelling an
            # observation that was placed by the scheduler
            'include_normal': False,
            'include_rr': False,
            'include_direct': True
            }
        print(payload)
        opt = input('CANCEL observation ? '+str(obs['id'])+' '+str(obs['proposal'])
                +' '+str(obs['start'])+' '+str(obs['end'])+' '+str(obs['state'])
                +' ? Press y to confirm or any other key to skip: ')
        if opt == 'y':
            response = lco_interface(config, payload, 'api/observations/cancel', 'POST')
            print(response)
            print('Proceeding with cancellation')
        else:
            print('OK, not cancelling')

def lco_interface(config,ur,end_point,method):
    """Function to communicate with various APIs of the LCO network.
    ur should be a user request while end_point is the URL string which
    should be concatenated to the observe portal path to complete the URL.
    Accepted end_points are:
        "userrequests"
        "userrequests/cadence"
        "userrequests/<id>/cancel"
        "api/observations"
        "api/observations/cancel/"
    Accepted methods are:
        POST GET
    """

    headers = {'Authorization': 'Token ' + config['lco_token']}

    if end_point[0:1] == '/':
        end_point = end_point[1:]
    if end_point[-1:] != '/':
        end_point = end_point+'/'
    url = path.join(config['lco_base_url'],end_point)

    if method == 'POST':
        if ur != None:
            response = requests.post(url, headers=headers, json=ur)
        else:
            response = requests.post(url, headers=headers)
    elif method == 'GET':
        response = requests.get(url, headers=headers, params=ur)

    json_response = response.json()

    return json_response

def lco_interface_paginated_get(config,ur):
    """Function to communicate with various APIs of the LCO network.
    ur should be a user request while end_point is the URL string which
    should be concatenated to the observe portal path to complete the URL.
    Accepted end_points are:
        "api/observations"
    Accepted methods are:
        GET
    """
    end_point = 'api/observations'
    method = 'GET'

    headers = {'Authorization': 'Token ' + config['lco_token']}

    if end_point[0:1] == '/':
        end_point = end_point[1:]
    if end_point[-1:] != '/':
        end_point = end_point+'/'
    url = path.join(config['lco_base_url'],end_point)
    print(url)

    response = requests.get(url, headers=headers, params=ur)
    json_response = response.json()
    results = json_response['results']
    print('Initial number of search matches: '+str(json_response['count']))
    print('Looping over paginated results...')

    while 'next' in json_response.keys() and json_response['next']:
        url = json_response['next']
        #print('Fetching page '+url)
        response = requests.get(url, headers=headers, params=ur)
        json_response = response.json()

        if 'results' in json_response.keys():
            for entry in json_response['results']:
                results.append(entry)
        #print(len(results))

    return results


if __name__ == '__main__':
    run()
