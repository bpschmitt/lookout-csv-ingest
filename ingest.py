import os
import csv
import asyncio
import aiohttp
from asyncio_throttle import Throttler
import json

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
    
    headers = {'Content-Type': 'application/json','Api-Key': apiKey}
    async with throttler:
        async with session.post(url, data = json.dumps(payload), headers = headers) as response:
            json_response = response
            print(str(line_count) + ' --- ' + str(json_response))


def createPayload(rows):
    chunks = 1000
    allPayloads = []
    measurements = {}
    metricslist = []
    counter = 0

    print('total rows: ' + str(len(rows)))

    for r in rows:

        if counter < chunks:
            counter += 1
            for k,v in metrics.items():
                measurements['name'] = k
                measurements['type'] = 'gauge'
                measurements['value'] = float(r[int(v)])
                measurements['timestamp'] = int(r[0])
                measurements['attributes'] = {'app.name': r[1], 'host.name': r[2]}
                metricslist.append(measurements)
                measurements = {}
        else:
            counter = 0
            allPayloads.append([{'metrics': metricslist}])
            metricslist = []

    return allPayloads

async def main():
    timestamps = []
    rows = []
    tasks = []
    throttler = Throttler(rate_limit=1500, period=1)
    conn = aiohttp.TCPConnector(limit=1500)

    with open(inputFile) as f:
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader)
        async with aiohttp.ClientSession(connector=conn) as session:
            line_count = 0
            prev_ts = 0
            for row in csv_reader:
                
                if line_count < 2000000:
                    line_count += 1
                    if prev_ts != row[0]:
                        prev_ts = row[0]
                        timestamps.append(row[0])

                    rows.append(row)
                else:
                    break
            

            payloads = createPayload(rows)
            print('chunks: ' + str(len(payloads) + 1))
           

            line_count = 0
            for p in payloads:
                line_count += 1
                tasks.append(await sendIt(session, p, throttler, line_count))
            
            print('Here we go...')
            await asyncio.gather(*tasks)
            print('Complete!')

            f.close()

asyncio.run(main())

