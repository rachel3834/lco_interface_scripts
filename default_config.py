from datetime import datetime

API_TOKEN = 'YOUR_LCO_PORTAL_TOKEN_HERE'
PORTAL_HOST = 'https://observe.lco.global/'
PROPOSAL = None
PROPOSAL = 'YOUR_PROPOSAL_CODE_HERE'  # Or None
SITE = 'elp'    # Site code is required
ENCLOSURE = None
TELESCOPE = None
PRIORITY = None

config = {
    'lco_token': API_TOKEN,
    'lco_base_url': PORTAL_HOST
}

# SET A DATE RANGE
start_time = 'YYYY-MM-DD HH:MM'
end_time = 'YYYY-MM-DD HH:MM'

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
         }
