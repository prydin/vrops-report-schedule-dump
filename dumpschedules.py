import requests
import json
import urllib3
import os
import argparse
from datetime import datetime
from functools import lru_cache

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VRopsClient:
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url_base = ''

    token = ''

    def __init__(self, url_base, username=None, password=None, token=None):
        if token:
            # vR Ops cloud login
            self.url_base = url_base + '/suite-api/api'
            credentials = 'refresh_token=' + token
            result = requests.post(url='https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize',
                                   headers={ 'Content-Type': 'application/x-www-form-urlencoded' },
                                   data=credentials,
                                   verify=False)
            if result.status_code != 200:
                print(str(result.status_code) + ' ' + str(result.content))
                exit(1)
            json_data = json.loads(result.content)
            token = json_data['access_token']
            self.headers['Authorization'] = 'CSPToken ' + token
        else:
            # On-prem login
            self.url_base = url_base + '/suite-api/api'
            credentials = json.dumps({'username': username, 'password': password})
            result = requests.post(url=self.url_base + '/auth/token/acquire',
                                   data=credentials,
                                   verify=False, headers=self.headers)
            if result.status_code != 200:
                print(str(result.status_code) + ' ' + str(result.content))
                exit(1)
            json_data = json.loads(result.content)
            token = json_data['token']
            self.headers['Authorization'] = 'vRealizeOpsToken ' + token

    def get(self, url):
        return requests.get(url=self.url_base + url,
                              headers=self.headers,
                              verify=False)
        return result

    @lru_cache(maxsize = 1000)
    def get_resource_name(self, id):
        r = self.get('/resources/' + id).json()
        return r['resourceKey']['resourceKindKey'] + ':' + r['resourceKey']['name']


# Main program
#
parser = argparse.ArgumentParser(description='dlreport');
parser.add_argument('--url', help='The vR Ops URL', required=True)
parser.add_argument('--user', type=str, help='The vR Op suser', required=False)
parser.add_argument('--password', help='The vR Ops password', required=False)
parser.add_argument('--token', help='The vR Ops API Token (cloud only)', required=False)
parser.add_argument('--report', help='Report name', required=False)
parser.add_argument('--output', help='Output file', required=True)
args = parser.parse_args()

report_name = args.report
if args.user and args.password and not args.token:
    vrops = VRopsClient(args.url, username=args.user, password=args.password)
elif args.token:
    vrops = VRopsClient(args.url, token=args.token)
else:
    print('Either user/password or token must be specified')
    os.exit(1)

if args.report:
    reports = vrops.get('/reportdefinitions?name=' + report_name).json()['reportDefinitions']
    if len(reports) == 0:
        print('Report not found')
        os.exit(1)
else:
    reports = vrops.get('/reportdefinitions').json()['reportDefinitions']
    reports.sort(key=lambda r: r['name'])

f = open(args.output, 'w')
with f:
    for report in reports:
        data = vrops.get('/reportdefinitions/%s/schedules' % report['id']).json()
        if not 'reportSchedules' in data:
            continue
        schedules = data['reportSchedules']
        for schedule in schedules:
            startDate = datetime.strptime(schedule['startDate'], "%m/%d/%Y")
            startDate.replace(hour=int(schedule['startHour']), minute=int(schedule['startMinute']))
            resourceNames = ','.join(list(map(lambda r: '"' + vrops.get_resource_name(r) + '"', schedule['resourceId'])))
            f.write('"%s","%s","%s",%s\n' % (report['name'], schedule['reportScheduleType'], startDate, resourceNames))
