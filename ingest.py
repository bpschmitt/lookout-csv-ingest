import os
import csv
import asyncio
import aiohttp
from asyncio_throttle import Throttler
import json
from time import sleep

'''
500 unique timestamps
1322501 lines
timeStamp, appName, hostName, cpu_idle, mem_util, txnCount, errCount

[{
  "common": {
      "key": "value"
  },
  "metrics": [{
      "key": "value"
  }]
}]
'''

inputFile = os.environ['FILENAME']
apiKey = os.environ['API_KEY']
url = os.environ['API_ENDPOINT']
metrics = {'cpu_idle':3 ,'mem_util': 4,'transaction_count': 5,'error_count': 6}


async def sendIt(session, payload, throttler, line_count):
    
    d = [payload]
    headers = {'Content-Type': 'application/json','Api-Key': apiKey}
    async with throttler:
        async with session.post(url, data = json.dumps(d), headers = headers) as response:
            json_response = response
            print(str(line_count) + ' --- ' + str(json_response))


async def createPayload(row):
    payload = {}
    common = {}
    measurements = {}
    metricslist = []

    common['app.name'] = row[1]
    common['host.name'] = row[2]
    
    for k,v in metrics.items():
        measurements['name'] = k
        measurements['type'] = 'gauge'
        measurements['value'] = float(row[int(v)])
        metricslist.append(measurements)
        measurements = {}

    payload['common'] = {'timestamp': int(row[0]), 'attributes': common}
    payload['metrics'] = metricslist    
    
    return payload

async def main():
    tasks = []
    throttler = Throttler(rate_limit=10000, period=1)
    conn = aiohttp.TCPConnector(limit=10000)

    with open(inputFile) as f:
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader)
        async with aiohttp.ClientSession(connector=conn) as session:
            line_count = 0
            for row in csv_reader:
                line_count += 1
                print('Appending row ' + str(line_count))
                tasks.append(sendIt(session, await createPayload(row), throttler, line_count))
            
            print('Here we go...')
            await asyncio.gather(*tasks)
            print('Complete!')
            f.close()

asyncio.run(main())

