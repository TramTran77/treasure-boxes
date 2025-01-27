import requests
import os
import pytd
import pandas as pd

def get_task_info(base_url, headers, ids):
  l = []
  for i in ids:
    url = base_url % i
    print(url)
    res = requests.get(url=url, headers=headers)
    if res.status_code != requests.codes.ok:
        res.raise_for_status()
    tasks = res.json()['tasks']
    for t in tasks:
        t['attemptid'] = i
    l.extend(tasks)
  return l

def insert_task_info(import_unixtime, endpoint, apikey, dest_db, dest_table, tasks):
    df = pd.DataFrame(tasks)
    df['time'] = int(import_unixtime)
    client = pytd.Client(apikey=apikey, endpoint=endpoint, database=dest_db)
    client.load_table_from_dataframe(df, dest_table, if_exists='append', fmt='msgpack')

def run(session_unixtime, dest_db, dest_table, attempt_ids, api_endpoint='api.treasuredata.com', workflow_endpoint='api-workflow.treasuredata.com'):
  id_list = attempt_ids[1:-1].split(',')
  if len(id_list) == 0:
    print('no attempt id')
    return

  workflow_url = 'https://%s/api/attempts' % workflow_endpoint + '/%s/tasks'
  headers = {'Authorization': 'TD1 %s' % os.environ['TD_API_KEY']}
  l = get_task_info(workflow_url, headers, id_list)
  if len(l) == 0:
    print('no update record')
    return
  insert_task_info(session_unixtime, 'https://%s' % api_endpoint, os.environ['TD_API_KEY'], dest_db, dest_table, l)