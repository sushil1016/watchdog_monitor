
import json
def my_func():
    var = '',''
    test_list= [12,13,14,15]
    test_bool = True
    if (True):
        var = test_list,test_bool
    else:
        var = test_list,False
    return var

osd_list, status=my_func()
print status
print osd_list
exit()
'''

json_response = '{"cpeid": 1212,"enforceRule": true,"rulesMap":[{"error": 1212,"type": "time-depth","timeFrom": 2313213213,"timeTo": 213123},{"error": 1016,"type": "time-depth","timeFrom": 121212,"timeTo": 87878}]}'

parsed_json = json.loads(json_response)

forced_sampling = parsed_json['enforceRule']
#print(forced_sampling)

rule_engine_err_list=[]
for item in parsed_json['rulesMap']:
    print (item)
    rule_engine_err_list.append(item['error'])

print ("osd list from rule engine for sampling",(rule_engine_err_list))

osd_list=[1,7,1016,5,9]
print("osd list from PH="+str(osd_list))

sampling_list = list((set(osd_list).intersection(rule_engine_err_list)))
print("to be sampled==>"+str(sampling_list)) #Return this as it is for osd use case
new_osd_list = list((set(osd_list).difference(sampling_list)))
print("to be returned back"+str(new_osd_list)) #Do sampling of this and return a dict

sampling_info_list = [] # Contains list of dictionary containing sampling information
if not new_osd_list:
    print('no rule to do sampling')
else:
    for osd in sampling_list:
        for xx in parsed_json['rulesMap']:
            if xx['error'] == osd:
                info = dict()
                info['error'] = xx['error']
                info['from_date'] = xx['timeFrom']
                info['to_date'] = xx['timeTo']
                sampling_info_list.append(info)

if sampling_info_list:
    print(sampling_info_list)


exit()
#for item in parsed_json['rulesMap']:
#    lst.append(item)

#print(lst)
    #for key,value in item.items():
    #    print(key,value)

osd_list=[1890 , 1212, 8989, 8985, 1016]
content=[]
for osd in osd_list:
    for xx in lst:
        #print(' server(osd) '+str(osd)+" rule(osd) "+str(xx['error']))
        if osd == xx['error']:
            #print("One OSD matched for sampling ",osd)
            info={}
            info['error']=xx['error']
            info['from_date']=xx['timeFrom']
            info['to_date'] = xx['timeTo']
            content.append(info)

print (content)

for key,value in parsed_json['rulesMap'][0].items():
    print(key,value)

print(parsed_json['rulesMap'][0]['type'])
#for key, value in json_response['rulesMap'].items():
    #print(key,value)
    '''

