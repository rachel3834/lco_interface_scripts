import requests
from os import path
from datetime import datetime

API_TOKEN = 'MY_TOKEN_HERE'
PORTAL_HOST = 'https://observe.lco.global/'
PROPOSAL = None
PROPOSAL = 'MY_PROPOSAL_CODE_HERE'
SITE = 'elp'
ENCLOSURE = None
TELESCOPE = None
PRIORITY = None

def run():

    config = {
              'lco_token': API_TOKEN,
              'lco_base_url': PORTAL_HOST
              }

    start_time = '2022-09-26 00:00'
    end_time = '2022-09-29 23:59'

    # Observations can be in one of these states:
    # {COMPLETED, PENDING, IN_PROGRESS, ABORTED, FAILED, NOT_ATTEMPTED}
    params = {
             'site': SITE,      # This parameter is apparently required
             'enclosure': ENCLOSURE,
             'telescope': TELESCOPE,
             'priority': PRIORITY,
             'proposal': PROPOSAL,
             'state': 'PENDING',
             'start_after': datetime.strptime(start_time, "%Y-%m-%d %H:%M"),
             'start_before': datetime.strptime(end_time, "%Y-%m-%d %H:%M"),
             'limit': 10000 # Otherwise the results are paginated into sets of 10
             }

    obs_set = query_for_observations(config, params, verbose=False)

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

    response = lco_interface(config, query, 'api/observations', 'GET')

    if 'results' in response.keys():
        query_set = response['results']
    else:
        query_set = []

    if verbose:
        print('Query returned '+str(len(query_set))
                +' results; filtering by proposal')

    # Now apply the other selection criteria:
    observation_set = []
    for obs in query_set:
        if obs['proposal'] == params['proposal']:
            observation_set.append(obs)

    print('Retrieved '+str(len(observation_set))
            + ' observations matching all search parameters:')
    for obs in observation_set:
        if obs['proposal'] == PROPOSAL:
            print(obs['request']['id'], obs['proposal'], obs['start'], obs['end'], obs['state'])

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
            'include_normal': True,
            'include_rr': False,
            'include_direct': False
            }
        print(payload)
        opt = input('CANCEL observation ? '+str(obs['request']['id'])+' '+str(obs['proposal'])
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
    print(url)

    if method == 'POST':
        if ur != None:
            response = requests.post(url, headers=headers, json=ur)
        else:
            response = requests.post(url, headers=headers)
    elif method == 'GET':
        response = requests.get(url, headers=headers, params=ur)
    print(response)

    json_response = response.json()
    return json_response


if __name__ == '__main__':
    run()
