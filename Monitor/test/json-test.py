import requests
import sys
sys.path.append("interface")

import json

u_json= [
  {
    "pri.store.size": "650b",
    "health": "yellow",
    "status": "open",
    "index": "twitter",
    "pri": "5",
    "rep": "1",
    "docs.count": "0",
    "docs.deleted": "0",
    "store.size": "650b"
  }
]
jsa=['foo', {'bar': ('baz', None, 1.0, 2)}]
#json_config=[{"cpeid":"12345"},{"cpeid":"89765"},{"cpeid":"7012345"}]
#print(json.dumps(json_config))
while True:
  print('calling server')
  json_config=requests.get('http://10.197.54.164:9200/_cat/indices/1*?format=json')
  if json_config.status_code == 200:
    break
#json_list=list(json_config)
#print(json_list)
data = {"has_error":True}
data.update({"cpe":30})
print(data)
xx=json_config.json()
x=0
dev_list=[]
for key,value in xx[0]:
  print (key,value)
for key in xx:
  if key['indexy']:
    dev_list.append(key['index'])


data.update({"cpe_ids":str(dev_list)})
print(data)
print("---------------------")
exit()

for i in xx:
  print(i)
  data.update(i)
print('--------------')
print(data)
print('--------------')
dev_list = []
for key in xx:
  dev_list.append(key['cpeid'])

dev_list.append("has_error")

print(dev_list)

exit()

res=u_json[1:-1]
print (type(res))
eval(str(res))
print (type(res))
print(res.json())


res = json.dumps(u_json)
res = res[1:-1]
print((res))

print(type(res))

print(res.json())

