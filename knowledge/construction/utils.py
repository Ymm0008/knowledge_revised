# -*- coding: UTF-8 -*-
'''
recommentation
save uid list should be in
'''
import  os
import IP
import sys
import time
import datetime
import math
import json
import redis
import math
from xpinyin import Pinyin
from py2neo.ext.batman import ManualIndexManager
from py2neo.ext.batman import ManualIndexWriteBatch
from py2neo.ogm import GraphObject, Property
from py2neo import Node, Relationship
from elasticsearch import Elasticsearch
# from update_activeness_record import update_record_index
from knowledge.global_utils import es_event, graph, R_RECOMMENTATION as r
# from knowledge.global_utils import R_RECOMMENTATION_OUT as r_out
from knowledge.global_utils import R_CLUSTER_FLOW3 as r_cluster
from knowledge.global_utils import R_CLUSTER_FLOW2 as r_cluster2, R_SENSITIVE_REDIS as sensitvie_r
from knowledge.global_utils import es_user_portrait as es, es_prediction, getconn, closeAll
from knowledge.global_utils import es_recommendation_result, recommendation_index_name, recommendation_index_type
from knowledge.global_utils import es_user_profile, portrait_index_name, portrait_index_type, profile_index_name, profile_index_type
from knowledge.global_utils import ES_CLUSTER_FLOW1 as es_cluster, es_wiki
from knowledge.global_utils import p_column, o_column, e_column, s_column, g_column, es_group
from knowledge.global_utils import es_related_docs, user_docs_name, user_docs_type, event_docs_name, event_docs_type
from knowledge.global_utils import es_bci_history, sensitive_index_name, sensitive_index_type,event_name_search,user_name_search
from knowledge.time_utils import ts2datetime, datetime2ts
from knowledge.global_config import event_task_name, event_task_type, event_analysis_name, event_text_type,\
special_event_primary, group_primary, special_event_name, special_event_type, group_name, group_type,org_list,peo_list,\
              key_type_dict
from knowledge.global_config import node_index_name, event_index_name, special_event_node, group_node, people_primary,event_primary,\
                other_rel, event_other, user_tag, organization_tag, relation_dict, org_primary, org_index_name, wiki_type_name,\
                wiki_index_name, wiki_url_index_name, wiki_primary
from knowledge.parameter import DAY, WEEK, RUN_TYPE, RUN_TEST_TIME,MAX_VALUE,sensitive_score_dict
from knowledge.extensions import db
from knowledge.model import PeopleHistory, EventHistory
from BeautifulSoup import BeautifulSoup
# from knowledge.cron.event_analysis.event_compute import immediate_compute
p = Pinyin()
WEEK = 7

def identify_in(data, uid_list):
    in_status = 1
    compute_status = 0
    compute_hash_name = 'compute'
    compute_uid = r.hkeys(compute_hash_name)
    for item in data:
        date = item[0] # identify the date form '2013-09-01' with web
        uid = item[1]
        status = item[2]
        relation_string = item[3]
        recommend_style = item[4]
        submit_user = item[5]
        node_type = item[6]
        value_string = []
        # identify_in_hashname = "identify_in_" + str(date)
        # r.hset(identify_in_hashname, uid, in_status)
        if status == '1':
            in_date = date
            compute_status = '1'
        elif status == '2':
            in_date = date
            compute_status = '2'
        relation_list = relation_string.split(',')
        r.hset(compute_hash_name, uid, json.dumps([in_date, compute_status, node_type, relation_list, submit_user, recommend_style]))
    return 1

#submit new task and identify the task name unique in es-group_result and save it to redis list
def submit_task(input_data):
    status = 0 # mark it can not submit
    task_name = input_data['task_name']
    submit_user = input_data['submit_user']
    task_id = input_data['task_id']
    try:
        result = es_recommendation_result.get(index=recommendation_index_name, doc_type=recommendation_index_type, id=task_id)['_source']
    except:
        status = 1
    
    if status != 0 and 'uid_file' not in input_data:
        input_data['status'] = 0 # mark the task not compute
        count = len(json.loads(input_data['uid_list']))
        input_data['count'] = count
        input_data['submit_user'] = submit_user
        # add_es_dict = {'task_information': input_data, 'query_condition':''}
        es_recommendation_result.index(index=recommendation_index_name, doc_type=recommendation_index_type, id=task_id, body=input_data)
        if input_data['cal_style'] == 0:
            group_analysis_queue_name = 'recommendation_in_now'
        if input_data['cal_style'] == 1:
            group_analysis_queue_name = 'recommendation_in_later'
        r.lpush(group_analysis_queue_name, json.dumps(input_data))
    return status

# identify in by upload file to admin user
# input_data = {'date':'2013-09-01', 'upload_data':[], 'user':submit_user}
def submit_identify_in_uid(input_data):
    print input_data,'00000000000'
    in_date = input_data['date']
    submit_user = input_data['user']
    operation_type = input_data['operation_type']
    compute_status = str(input_data['compute_status'])
    relation_string = input_data['relation_string'] 
    recommend_style = input_data['recommend_style']
    node_type = str(input_data['node_type'])
    hashname_submit = 'submit_recomment_' + in_date
    hashname_influence = 'recomment_' + in_date + '_influence'
    hashname_sensitive = 'recomment_' + in_date + '_sensitive'
    compute_hash_name = 'compute'
    # submit_user_recomment = 'recomment_' + submit_user + '_' + str(date)
    auto_recomment_set = set(r.hkeys(hashname_influence)) | set(r.hkeys(hashname_sensitive))
    upload_data = input_data['upload_data']
    uid_list = []
    invalid_uid_list = []
    if recommend_style == 'upload':
        line_list = upload_data
        # print line_list,'====8888===='
        for line in line_list:
            uid = line.strip('\r')
            # print len(str(uid)),'!!!0000000000999999999999'
            if len(str(uid))==10:
               uid_list.append(uid)
            else:
                invalid_uid_list.append(uid)
    if recommend_style == 'write':
        line_list = upload_data
        # print line_list,'====8888===='
        for line in line_list:
            uid = line
            if len(str(uid))==10:
               uid_list.append(uid)
            else:
                invalid_uid_list.append(uid)
    if len(invalid_uid_list) != 0:
        return 0, 'invalid user info', invalid_uid_list
    #identify the uid is not exist in user_portrait and compute
    #step1: filter in user_portrait
    new_uid_list = []
    have_in_uid_list = []
    try:
        exist_portrait_result = es.mget(index=portrait_index_name, doc_type=portrait_index_type, body={'ids':uid_list}, _source=False)['docs']
    except:
        exist_portrait_result = []
    if exist_portrait_result:
        for exist_item in exist_portrait_result:
            if exist_item['found'] == False:
                new_uid_list.append(exist_item['_id'])
            else:
                have_in_uid_list.append(exist_item['_id'])
    else:
        new_uid_list = uid_list
   
    #step2: filter in compute
    new_uid_set = set(new_uid_list)
    # compute_set = set(r.hkeys('compute'))
    compute_set = set([])
    in_uid_set = list(new_uid_set - compute_set)
    print 'new_uid_set:', new_uid_set 
    print 'in_uid_set:', in_uid_set
    if len(in_uid_set)==0:
        return 0, 'all user in'
    #identify the final add user
    final_submit_user_list = []
    for in_item in in_uid_set:
        # if in_item in auto_recomment_set:
        #     tmp = json.loads(r.hget(hashname_submit, in_item))
        #     recommentor_list = tmp['operation'].split('&')
        #     recommentor_list.append(str(submit_user))
        #     new_list = list(set(recommentor_list))
        #     tmp['operation'] = '&'.join(new_list)
        # else:
        #     tmp = {'system':'0', 'operation':submit_user}
        if operation_type == 'submit':
            relation_list = relation_string.split(',')
            r.hset(compute_hash_name, in_item, json.dumps([in_date, compute_status, node_type, relation_list, submit_user, recommend_style]))
            # r.hset(hashname_submit, in_item, json.dumps(tmp))
            # r.hset(submit_user_recomment, in_item, '0')
        final_submit_user_list.append(in_item)
    return 1, invalid_uid_list, have_in_uid_list, final_submit_user_list

def get_final_submit_user_info(uid_list):
    final_results = []
    try:
        profile_results = es_user_profile.mget(index=profile_index_name, doc_type=profile_index_type, body={'ids': uid_list})['docs']
    except:
        profile_results = []
    try:
        bci_history_results =es_bci_history.mget(index=bci_history_index_name, doc_type=bci_history_index_type, body={'ids': uid_list})['docs']
    except:
        bci_history_results = []
    #get bci_history max value
    now_time_ts = time.time()
    search_date_ts = datetime2ts(ts2datetime(now_time_ts - DAY))
    bci_key = 'bci_' + str(search_date_ts)
    query_body = {
        'query':{
             'match_all':{}
        },
        'sort': [{bci_key:{'order': 'desc'}}],
        'size': 1
    }
    try:
        bci_max_result = es_bci_history.search(index=bci_history_index_name, doc_type=bci_history_index_type, body=query_body, _source=False, fields=[bci_key])['hits']['hits']
    except:
       bci_max_result = {}
    if bci_max_result:
        bci_max_value = bci_max_result[0]['fields'][bci_key][0]
    else:
        bci_max_value = MAX_VALUE
    iter_count = 0
    for uid in uid_list:
        try:
            profile_item = profile_results[iter_count]
        except:
            profile_item = {}
        try:
            bci_history_item = bci_history_results[iter_count]
        except:
            bci_history_item = {}
        if profile_item and profile_item['found'] == True:
            uname = profile_item['_source']['nick_name']
            location = profile_item['_source']['user_location']
        else:
            uname = ''
            location = ''
        if bci_history_item and bci_history_item['found'] == True:
            fansnum = bci_history_item['_source']['user_fansnum']
            statusnum = bci_history_item['_source']['weibo_month_sum']
            try:
                bci = bci_history_item['_source'][bci_key]
                normal_bci = math.log(bci / bci_max_value * 9 + 1, 10) * 100
            except:
                normal_bci = ''
        else:
            fansnum = ''
            statusnum = ''
            normal_bci = ''
        final_results.append([uid, uname, location, fansnum, statusnum, normal_bci])
        iter_count += 1

    return final_results

def submit_identify_in(input_data):
    result_mark = False
    result_mark = submit_identify_in_uid(input_data)
    print result_mark,'====333333333333333============'
    # if len(result_mark) == 4:
    #     final_submit_user_list = result_mark[-1]
    #     if final_submit_user_list:
    #         final_submit_user_info = get_final_submit_user_info(final_submit_user_list)
    #     else:
    #         final_submit_user_listuser_info = []
    #     result_mark = list(result_mark)[:3]
    #     result_mark.append(final_submit_user_info)
    return result_mark

# show recommentation in uid
def recommentation_in(input_ts, recomment_type, submit_user, node_type):
    date = ts2datetime(input_ts)
    recomment_results = []
    # read from redis
    results = []
    hash_name = 'recomment_'+str(date) + "_" + recomment_type + "_" + node_type
    identify_in_hashname = "identify_in_" + str(date)
    # submit_user_recomment = "recomment_" + submit_user + "_" + str(date) # 用户自推荐名单
    results = r.hgetall(hash_name)
    if not results:
        return []
    # search from user_profile to rich the show information
    recommend_list = set(r.hkeys(hash_name))
    identify_in_list = set(r.hkeys("compute"))
    # submit_user_recomment = set(r.hkeys(submit_user_recomment))
    recomment_results = list(recommend_list - identify_in_list)
    # recomment_results = list(set(recomment_results) - submit_user_recomment)

    if recomment_results:
        results = get_user_detail(date, recomment_results[:1000], 'show_in', recomment_type)
    else:
        results = []
    return results


#get user detail
#output: uid, uname, location, fansnum, statusnum, influence
def get_user_detail(date, input_result, status, user_type="influence", auth=""):
    bci_date = ts2datetime(datetime2ts(date) - DAY)
    results = []
    if status=='show_in':
        uid_list = input_result
    if status=='show_compute':
        uid_list = input_result.keys()
    if status=='show_in_history':
        uid_list = input_result.keys()
    if date!='all':
        index_name = 'bci_' + ''.join(bci_date.split('-'))
    else:
        now_ts = time.time()
        now_date = ts2datetime(now_ts)
        index_name = 'bci_' + ''.join(now_date.split('-'))
    # tmp_ts = str(datetime2ts(date) - DAY)  #delete 04-11
    tmp_ts = str(datetime2ts(date))
    sensitive_string = "sensitive_score_" + tmp_ts
    query_sensitive_body = {
        "query":{
            "match_all":{}
        },
        "size":1,
        "sort":{sensitive_string:{"order":"desc"}}
    }
    try:
        top_sensitive_result = es_bci_history.search(index=sensitive_index_name, doc_type=sensitive_index_type, body=query_sensitive_body, _source=False, fields=[sensitive_string])['hits']['hits']
        top_sensitive = top_sensitive_result[0]['fields'][sensitive_string][0]
        # print top_sensitive_result,'---------'
    except Exception, reason:
        print Exception, reason
        top_sensitive = 400
    index_type = 'bci'
    user_bci_result = es_cluster.mget(index=index_name, doc_type=index_type, body={'ids':uid_list}, _source=True)['docs']  #INFLUENCE,fans,status
    user_profile_result = es_user_profile.mget(index='weibo_user', doc_type='user', body={'ids':uid_list}, _source=True)['docs'] #个人姓名，注册地
    # bci_history_result = es_bci_history.mget(index=bci_history_index_name, doc_type=bci_history_index_type, body={"ids":uid_list}, fields=['user_fansnum', 'weibo_month_sum'])['docs']
    sensitive_history_result = es_bci_history.mget(index=sensitive_index_name, doc_type=sensitive_index_type, body={'ids':uid_list}, fields=[sensitive_string], _source=False)['docs']
    max_evaluate_influ = get_evaluate_max_i(index_name)
    for i in range(0, len(uid_list)):
        uid = uid_list[i]
        bci_dict = user_bci_result[i]
        profile_dict = user_profile_result[i]
        # bci_history_dict = bci_history_result[i]
        sensitive_history_dict = sensitive_history_result[i]
        #print sensitive_history_dict
        try:
            bci_source = bci_dict['_source']
        except:
            bci_source = None
        if bci_source:
            influence = bci_source['user_index']
            influence = math.log(influence/float(max_evaluate_influ['user_index']) * 9 + 1 ,10)
            influence = influence * 100
        else:
            influence = 0
        try:
            profile_source = profile_dict['_source']
        except:
            profile_source = None
        if profile_source:
            uname = profile_source['nick_name'] 
            location = profile_source['user_location']
            try:
                fansnum = bci_dict['fields']['user_fansnum'][0]
            except:
                fansnum = 0
            try:
                statusnum = bci_dict['fields']['weibo_month_sum'][0]
            except:
                statusnum = 0
        else:
            uname = uid
            location = ''
            try:
                fansnum = bci_dict['fields']['user_fansnum'][0]
            except:
                fansnum = 0
            try:
                statusnum = bci_dict['fields']['weibo_month_sum'][0]
            except:
                statusnum = 0
        if status == 'show_in':
            if user_type == "sensitive":
                tmp_ts = datetime2ts(date) - DAY
                print "sensitive_"+str(tmp_ts)
                tmp_data = sensitvie_r.hget("sensitive_"+str(tmp_ts), uid)
                if tmp_data:
                    sensitive_dict = json.loads(tmp_data)
                    # print uid, sensitive_dict,'============'
                    sensitive_words = sensitive_dict.keys()
                else:
                    sensitive_words = []
                if sensitive_history_dict.get('fields',0):
                    sensitive_value = math.log(sensitive_history_dict['fields'][sensitive_string][0]/float(top_sensitive)*9+1, 10)*100
                    #print "sensitive_value", sensitive_value
                else:
                    sensitive_value = 0
                results.append([uid, uname, location, fansnum, statusnum, sensitive_value, sensitive_words, influence])
            else:
                results.append([uid, uname, location, fansnum, statusnum, influence])
            if auth:
                hashname_submit = "submit_recomment_" + date
                tmp_data = json.loads(r.hget(hashname_submit, uid))
                recommend_list = (tmp_data['operation']).split('&')
                admin_list = []
                admin_list.append(tmp_data['system'])
                admin_list.append(list(set(recommend_list)))
                admin_list.append(len(recommend_list))
                results[-1].extend(admin_list)
        if status == 'show_compute':
            in_date = json.loads(input_result[uid])[0]
            compute_status = json.loads(input_result[uid])[1]
            if compute_status == '1':
                compute_status = '3'
            results.append([uid, uname, location, fansnum, statusnum, influence, in_date, compute_status])
        if status == 'show_in_history':
            in_status = input_result[uid]
            if user_type == "sensitive":
                tmp_ts = datetime2ts(date) - DAY
                tmp_data = sensitvie_r.hget("sensitive_"+str(tmp_ts), uid)
                if tmp_data:
                    sensitive_dict = json.loads(tmp_data)
                    sensitive_words = sensitive_dict.keys()
                if sensitive_history_dict.get('fields', 0):
                    sensitive_value = math.log(sensitive_history_dict['fields'][sensitive_string][0]/float(top_sensitive)*9+1, 10)*100
                else:
                    sensitive_value = 0
                results.append([uid, uname, location, fansnum, statusnum, influence, in_status, sensitive_words, sensitive_value])
            else:
                results.append([uid, uname, location, fansnum, statusnum, influence, in_status])

    return results

def get_evaluate_max_i(index_name):
    max_result = {}
    index_type = 'bci'
    evaluate_index = ['user_index']
    for evaluate in evaluate_index:
        query_body = {
            'query':{
                'match_all':{}
                },
            'size':1,
            'sort':[{evaluate: {'order': 'desc'}}]
            }
        # try:
        result = es_cluster.search(index=index_name, doc_type=index_type, body=query_body)['hits']['hits']
        # except Exception, e:
        # raise e
        max_evaluate = result[0]['_source'][evaluate]
        max_result[evaluate] = max_evaluate
    return max_result

def recommentation_in_auto(date, submit_user, node_type):
    results = []
    #run type
    if RUN_TYPE == 1:
        now_date = search_date
    else:
        now_date = ts2datetime(datetime2ts(RUN_TEST_TIME))
    recomment_hash_name = 'recomment_' + now_date + '_auto_' + node_type
    # print recomment_hash_name,'============'
    recomment_influence_hash_name = 'recomment_' + now_date + '_influence_' + node_type
    recomment_sensitive_hash_name = 'recomment_' + now_date + '_sensitive_' + node_type
    # recomment_submit_hash_name = 'recomment_' + submit_user + '_' + now_date
    recomment_compute_hash_name = 'compute'
    # #step1: get auto
    # auto_result = r.hget(recomment_hash_name, 'auto')
    # if auto_result:
    #     auto_user_list = json.loads(auto_result)
    # else:
    #     auto_user_list = []
    #step2: get admin user result
    admin_result = r.hget(recomment_hash_name, submit_user)
    admin_user_list = []
    if admin_result:
        admin_result_dict = json.loads(admin_result)
    else:
        return None
    final_result = []
    #step3: get union user and filter compute/influence/sensitive
    for k,v in admin_result_dict.iteritems():
        admin_user_list = v
        union_user_auto_set = set(admin_user_list)
        influence_user = set(r.hkeys(recomment_influence_hash_name))
        sensitive_user = set(r.hkeys(recomment_sensitive_hash_name))
        compute_user = set(r.hkeys(recomment_compute_hash_name))
        # been_submit_user = set(r.hkeys(recomment_submit_hash_name))
        filter_union_user = union_user_auto_set - (influence_user | sensitive_user | compute_user)
        auto_user_list = list(filter_union_user)
        #step4: get user detail
        if auto_user_list == []:
            return auto_user_list
        results = get_user_detail(now_date, auto_user_list, 'show_in', 'auto')
        for detail in results:  #add root
            re_detail = detail
            re_detail.append(k)
            final_result.append(re_detail)
    return final_result

def submit_event(input_data):
    print input_data,'555555555555555'
    if not input_data.has_key('name'):
        name_s = input_data['keywords'].split('&')[:3]
        print name_s,'==='
        name_string = '&'.join(name_s)
        input_data['name'] = name_string
    if input_data.has_key('mid'):
        # event_id = mid
        input_data['en_name'] = input_data['mid']
        del input_data['mid']
    else:
        e_name = input_data['name']
        e_name_string = ''.join(e_name.split('&'))
        event_id = p.get_pinyin(e_name_string)+'-'+str(input_data['event_ts'])  #+str(int(time.time()))
        event_id = event_id.lower()
        print event_id,'event_id,000000000'
        input_data['en_name'] = event_id

    if not input_data.has_key('start_ts'):
        start_ts = input_data['event_ts'] - 2*DAY
        input_data['start_ts'] = start_ts
    if not input_data.has_key('end_ts'):
        end_ts = input_data['event_ts'] + 5*DAY
        input_data['end_ts'] = end_ts
    input_data['submit_ts'] = int(time.time())
    del input_data['event_ts']
    # result = es_event.delete(index=event_task_name, doc_type=event_task_type, id=input_data['en_name'])
    try:
        result = es_event.get(index=event_task_name, doc_type=event_task_type, id=input_data['en_name'])['_source']
        return '0'
    except:
        es_event.index(index=event_task_name, doc_type=event_task_type, id=input_data['en_name'], body=input_data)
        if input_data['immediate_compute'] == '1':
            os.system("nohup python ./knowledge/cron/event_analysis/event_compute.py imme %s &" % event_id)
    return '1'

def update_event(event_id, relation_compute):
    relation_compute = '&'.join(relation_compute.split(','))
    result = es_event.get(index=event_task_name, doc_type=event_task_type, id=event_id)['_source']
    # print result
    now_ts = int(time.time())
    if result['end_ts'] < now_ts:
        es_event.update(index=event_task_name, doc_type=event_task_type, id=event_id, body={'doc':{'end_ts':now_ts,'relation_compute':relation_compute}})

    os.system("nohup python ./knowledge/cron/event_analysis/event_compute.py imme %s &" % event_id)
    # immediate_compute(event_id)

def show_weibo_list(message_type,ts,sort_item):
    event_id_all = es_event.search(index=event_analysis_name, doc_type=event_text_type,\
                   body={"query":{"match_all":{}},"size":10000},fields=['_id'])['hits']['hits']
    # print event_id_all,'all event id'
    event_ids = []
    for i in event_id_all:
        print i
        event_ids.append(i['_id'])
    query_body = {
        "query": {
            "bool":{
                "must":[
                    {"term":{"type": int(message_type)}},
                    {"term": {"detect_ts": int(ts)}}
                ]
            }
        },
        "size": 100,
        "sort":{sort_item:{"order": "desc"}}
    }

    text_results = []
    uid_list = []
    text_keys = ["text", "retweeted","keywords_string","mid", "comment", "user_fansnum", "timestamp", "geo", "uid"]
    es_results = es_prediction.search(index="social_sensing_text",doc_type="text", body=query_body)["hits"]["hits"]
    if not es_results:
        return []

    for item in es_results:
        if item['_source']['mid'] in event_ids:
            print item['_source']['mid']
            continue
        item = item["_source"]
        tmp = dict()
        for key in text_keys:
            tmp[key] = item[key]
        text_results.append(tmp)
        uid_list.append(item["uid"])

    profile_results = es_user_profile.mget(index=profile_index_name,doc_type=profile_index_type, body={"ids":uid_list})["docs"]
    for i in range(len(uid_list)):
        tmp_profile = profile_results[i]
        if tmp_profile["found"]:
            tmp = dict()
            tmp["photo_url"] = tmp_profile["_source"]["photo_url"]
            tmp["nick_name"] = tmp_profile["_source"]["nick_name"]
            if not tmp["nick_name"]:
                tmp["nick_name"] = uid_list[i]
            text_results[i].update(tmp)
        else:
            tmp = dict()
            tmp["photo_url"] = ""
            tmp["nick_name"] = tmp_profile["_id"]
            text_results[i].update(tmp)

    return text_results

def submit_event_file(input_data):
    submit_ts = input_data['submit_ts']
    relation_compute = input_data['relation_compute']
    immediate_compute = input_data['immediate_compute']
    submit_user = input_data['submit_user']
    recommend_style = input_data['recommend_style']
    compute_status = input_data['compute_status']
    file_data = input_data['upload_data']
    start_ts = input_data['start_ts']
    end_ts = input_data['end_ts']
    result_flag = False
    valid_event = 0
    total_event = len(file_data)
    for line in file_data:
        print line
        event = {}
        try:
            keywords = line.strip('\r')
        except:
            keywords = line
        if keywords == '':
            return 'not null'
        event['keywords'] = keywords
        event['event_ts'] = int(time.time())
        event['submit_ts'] = submit_ts
        event['start_ts'] = start_ts
        event['end_ts'] = end_ts
        event['relation_compute'] = relation_compute
        event['immediate_compute'] = immediate_compute
        event['submit_user'] = submit_user
        event['recommend_style'] = recommend_style
        event['compute_status'] = compute_status
        result = submit_event(event)
        print result,'ppppppppppppppppppppppp'
        if result == '1':
            valid_event += 1
    if valid_event == total_event:
        result_flag = True
    return result_flag, valid_event

def relation_add(input_data):
    print input_data, type(input_data),'------------'
    result_detail = [False]
    rel_num = 0
    for i in input_data:
        rel_num += 1
        node_key1 = i[0]
        node1_id = i[1]
        node1_index_name = i[2]
        rel = i[3]
        node_key2 = i[4]
        node2_id = i[5]
        node2_index_name = i[6]
        result = create_node_or_node_rel(node_key1, node1_id, node1_index_name, rel, node_key2, node2_id, node2_index_name)
        # return result
        if result == 'have relation':
            result_detail.append(rel_num)
            return result_detail
        if result == 'node does not exist':
            result_detail.append(rel_num)
            return result_detail
    result_detail[0] = True
    return result_detail

def show_relation(node_key1, node1_id, node1_index_name, node_key2, node2_id, node2_index_name):
    Index = ManualIndexManager(graph)
    node_index = Index.get_index(Node, node1_index_name)
    group_index = Index.get_index(Node, node2_index_name)
    print node_index
    print group_index
    tx = graph.begin()
    node1 = node_index.get(node_key1, node1_id)[0]
    node2 = group_index.get(node_key2, node2_id)[0]
    if not (node1 and node2):
        print "node does not exist"
        return 'does not exist'
    c_string = "START start_node=node:%s(%s='%s'),end_node=node:%s(%s='%s') MATCH (start_node)-[r]-(end_node) RETURN r" % (
    node1_index_name,node_key1, node1_id, node2_index_name, node_key2, node2_id)
    # return c_string
    print c_string
    result = graph.run(c_string)
    # print result
    rel_list = []
    for item in result:
        relation = dict(item)['r'].type()
        relation_ch = relation_dict[relation]
        if relation in [other_rel, event_other, organization_tag, user_tag]:
            relation_name = dict(item)['r']['name']
            relaiton_name_list = relation_name.split(',')
            # print relaiton_name_list, 'relaiton_name_list,99999999999999'
            for i_name in relaiton_name_list:
                relation_ch2 = relation_ch+ '-' +i_name
                relation = relation +'&' + relation_name
                rel_list.append(relation_ch2)
        else:
            rel_list.append(relation_ch)
    rel_list = [i for i in set(rel_list)]
    if node_key1 == 'uid' or node_key1 == 'org_id':
        node1_name = user_name_search(node1_id)
    else:
        node1_name = event_name_search(node1_id)

    if node_key2 == 'uid' or node_key2 == 'org_id':
        node2_name = user_name_search(node2_id)
    else:
        node2_name = event_name_search(node2_id)

    return [{'rel_list':rel_list, 'node1':[node1_id, node1_name, node_key1], 'node2':[node2_id, node2_name, node_key2]}]

def delete_relation(node_key1, node1_id, node1_index_name, rel_union, node_key2, node2_id, node2_index_name):
    Index = ManualIndexManager(graph)
    node_index = Index.get_index(Node, node1_index_name)
    group_index = Index.get_index(Node, node2_index_name)
    print node_index
    print group_index
    tx = graph.begin()
    node1 = node_index.get(node_key1, node1_id)[0]
    node2 = group_index.get(node_key2, node2_id)[0]
    if not (node1 and node2):
        print "node does not exist"
        return 'does not exist'
    rel = rel_union.split(',')[0]
    if rel in [other_rel, event_other, organization_tag, user_tag]:
        print rel_union,'************'
        rel_name = rel_union.split(',')[1:]
        # print rel_name, '=============='
        c_string = "START start_node=node:%s(%s='%s'), end_node=node:%s(%s='%s') \
                    MATCH (start_node)-[r:%s]-(end_node) RETURN type(r), r.name" % (node1_index_name,\
                    node_key1, node1_id, node2_index_name, node_key2, node2_id, rel)
        result = graph.run(c_string)
        exist_relation = []
        for i in result:
            dict_i = dict(i)
            exist_relation = dict_i['r.name'].split(',')
        if exist_relation:
            del_string = "START start_node=node:%s(%s='%s'),end_node=node:%s(%s='%s') \
                   MATCH (start_node)-[r:%s]->(end_node) delete r" % (node1_index_name,\
                    node_key1, node1_id, node2_index_name, node_key2, node2_id, rel)
            result = graph.run(del_string)
        exist_relation3 = set(exist_relation)-set(rel_name)
        print exist_relation3,'1111100000000000'
        exist_relation2 = [i for i in exist_relation3]
        add_relation_string = ','.join(exist_relation2)
        print add_relation_string,'add_relation_string'
        if add_relation_string == '':
            return '1'
        c_string = "START start_node=node:%s(%s='%s'),end_node=node:%s(%s='%s')\
                create (start_node)-[r:%s {name:'%s'} ]->(end_node)  " %(node1_index_name,\
                node_key1, node1_id, node2_index_name, node_key2, node2_id, rel, add_relation_string)
        print c_string
        try:
            result = graph.run(c_string)
        except:
            return 0
    else:
        c_string = "START start_node=node:%s(%s='%s'),end_node=node:%s(%s='%s')\
                match (start_node)-[r:%s]-(end_node) delete r " %(node1_index_name,\
                node_key1, node1_id, node2_index_name, node_key2, node2_id, rel)
        print c_string
        try:
            result = graph.run(c_string)
        except:
            return '0'
        # for i in result:
        #     print i
    return '1'

    #     rel = Relationship(node1, rel, node2)
    #     graph.create(rel)
    #     print "create success"
    # return True

def create_node_or_node_rel(node_key1, node1_id, node1_index_name, rel_union, node_key2, node2_id, node2_index_name):
    Index = ManualIndexManager(graph)
    node_index = Index.get_index(Node, node1_index_name)
    group_index = Index.get_index(Node, node2_index_name)
    print node_index
    print group_index
    tx = graph.begin()
    node1 = node_index.get(node_key1, node1_id)[0]
    node2 = group_index.get(node_key2, node2_id)[0]
    if not (node1 and node2):
        print "node does not exist"
        return 'does not exist'
    rel = rel_union.split(',')[0]
    if rel in [other_rel, event_other, organization_tag, user_tag]:
        print rel_union,'************'
        rel_name = rel_union.split(',')[1:]
        # print rel_name,'=============='
        c_string = "START start_node=node:%s(%s='%s'), end_node=node:%s(%s='%s') \
                    MATCH (start_node)-[r:%s]->(end_node) RETURN type(r), r.name" % (node1_index_name,\
                    node_key1, node1_id, node2_index_name, node_key2, node2_id, rel)
        result = graph.run(c_string)
        exist_relation = []
        for i in result:
            dict_i = dict(i)
            exist_relation = dict_i['r.name'].split(',')
        if exist_relation:
            del_string = "START start_node=node:%s(%s='%s'),end_node=node:%s(%s='%s') \
                   MATCH (start_node)-[r:%s]->(end_node) delete r" % (node1_index_name,\
                    node_key1, node1_id, node2_index_name, node_key2, node2_id, rel)
            result = graph.run(del_string)
        exist_relation.extend(rel_name)
        print exist_relation,'00000000000'
        exist_relation2 = [i for i in set(exist_relation)]
        add_relation_string = ','.join(exist_relation2)
        c_string = "START start_node=node:%s(%s='%s'),end_node=node:%s(%s='%s')\
                create (start_node)-[r:%s {name:'%s'} ]->(end_node)  " %(node1_index_name,\
                node_key1, node1_id, node2_index_name, node_key2, node2_id, rel, add_relation_string)
        result = graph.run(c_string)
    else:
        rel = Relationship(node1, rel, node2)
        graph.create(rel)
        print "create success"
    return True

def search_event(item, field, submit_user):
    query_body = {
        "query":{
            'bool':{
                'should':[
                    {"wildcard":{'keywords':'*'+str(item.encode('utf-8'))+'*'}},            
                    {"wildcard":{'en_name':'*'+str(item.encode('utf-8'))+'*'}},            
                    {"wildcard":{'name':'*'+str(item.encode('utf-8'))+'*'}}         
                ]
            }

        },
        'size':10
    }
    result = []
    try:
        event_result = es_event.search(index=event_analysis_name, doc_type=event_text_type, \
                body=query_body, fields=field)['hits']['hits']  #fields=['name','en_name']
    except:
        return 'does not exist'
    for i in event_result:
        event = []
        i_fields = i['fields']
        for j in field:
            if not i_fields.has_key(j):
                event.append('')
                continue
            if j == 'keywords':
                keywords = i_fields[j][0].split('&')
                keywords = keywords[:5]
                event.append(keywords)
            elif j == 'work_tag':
                tag = deal_editor_tag(i_fields[j][0], submit_user)[0]
                event.append(tag)
            else:
                event.append(i_fields[j][0])
        result.append(event)
    return result

def search_event_time_limit(item, field, start_ts, end_ts, submit_user):
    query_body = {
        "query":{
            "bool":{
                "must":[
                    {"range":{
                        "submit_ts":{
                            "gte": start_ts,
                            "lte": end_ts
                        }
                    }}
                ],
                'should':[
                    {"wildcard":{'keywords':'*'+str(item.encode('utf-8'))+'*'}},            
                    {"wildcard":{'en_name':'*'+str(item.encode('utf-8'))+'*'}},            
                    {"wildcard":{'name':'*'+str(item.encode('utf-8'))+'*'}}         
                ]
            }
        }
    }
    e_nodes_list = {}
    # event_relation =[]
    result = []
    try:
        event_result = es_event.search(index=event_analysis_name, doc_type=event_text_type, \
                body=query_body, fields=field)['hits']['hits']  #fields=['name','en_name']
    except:
        return 'does not exist'
    for i in event_result:
        event = []
        i_fields = i['fields']
        for j in field:
            if not i_fields.has_key(j):
                event.append('')
                continue
            if j == 'keywords':
                keywords = i_fields[j][0].split('&')
                keywords = keywords[:5]
                event.append(keywords)
            elif j == 'work_tag':
                tag = deal_editor_tag(i_fields[j][0], submit_user)[0]
                event.append(tag)
            else:
                event.append(i_fields[j][0])
        result.append(event)
    return result

def get_evaluate_max():
    max_result = {}
    evaluate_index = ['importance', 'influence', 'activeness', 'sensitive']
    for evaluate in evaluate_index:
        query_body = {
            'query':{
                'match_all':{}
                },
            'size': 1,
            'sort': [{evaluate: {'order': 'desc'}}]
            }
        try:
            result = es.search(index=portrait_index_name, doc_type=portrait_index_type, body=query_body)['hits']['hits']
        except Exception, e:
            raise e
        max_evaluate = result[0]['_source'][evaluate]
        max_result[evaluate] = max_evaluate
    return max_result

def search_user_type(uid_list):
    type_list = es_user_profile.mget(index=profile_index_name, doc_type=profile_index_type, \
                body={'ids': uid_list},_source=False, fields=['id', 'verified_type'])['docs']
    user_list1 = []
    org_list1 = []
    for i in type_list:
        if i['found'] == False:
            user_list1.append(i['_id'])
        else:
            if not i['fields'].has_key('verified_type'):
                user_list1.append(i['_id'])
                continue
            verified_type = i['fields']['verified_type'][0]
            if int(verified_type) in org_list:
                org_list1.append(i['_id'])
            else:
                user_list1.append(i['_id'])
    return user_list1,org_list1

def search_user(item, field, submit_user, node_type):
    evaluate_max = get_evaluate_max()
    query_body = {
        "query":{
            'bool':{
                'should':[
                    {"wildcard":{'uid':'*'+str(item.encode('utf-8'))+'*'}},            
                    {"wildcard":{'uname':'*'+str(item.encode('utf-8'))+'*'}}
                ]
            }

        },
        'size':10
    }
    only_uid = []
    user_uid_list = []

    try:
        name_results = es.search(index=portrait_index_name, doc_type=portrait_index_type, \
                body=query_body, fields= field)['hits']['hits']
    except:
        print '00000'
        return 'does not exist'
    for i in name_results:
        only_uid.append(i['fields']['uid'][0])
    print only_uid
    if not only_uid:
        return 'does not exist'
    if node_type == 'User':
        user_uid = search_user_type(only_uid)[0]
    elif node_type == 'Org':
        print '--------------'
        user_uid = search_user_type(only_uid)[1]
        print user_uid,'=========='
    result = []
    for i in name_results:
        # print i,'-------------'
        if i['fields']['uid'][0] not in user_uid:
            continue
        event = []
        # if i['found'] == False:
        #     event.append(i['_id'])
        #     continue
        i_fields = i['fields']
        for j in field:
            if not i_fields.has_key(j):
                event.append('')
                continue
            if j == 'keywords':
                keywords = i_fields[j][0].split('&')
                keywords = keywords[:5]
                event.append(keywords)
            elif j == 'function_mark':
                tag = deal_user_tag(i_fields[j][0], submit_user)[0]
                event.append(tag)
            elif j in ['influence', 'sensitive', 'activeness']:
                event.append(math.log(i_fields[j][0] / (evaluate_max[j] * 9+1) + 1, 10) * 100)
            else:
                event.append(i_fields[j][0])
        result.append(event)
    return result

def search_user_time_limit(item, field, start_ts, end_ts, editor):
    query_body = {
        "query":{
            # "uid":uid_list #-------------------!!!!!
            "bool":{
                "must":[
                    {"range":{
                        "submit_ts":{
                            "gte": start_ts,
                            "lte": end_ts
                             }
                        }
                    }
                ],
                'should':[
                    {"wildcard":{'uid':'*'+str(item.encode('utf-8'))+'*'}},            
                    {"wildcard":{'uname':'*'+str(item.encode('utf-8'))+'*'}}
                ]
            }
        }
    }
    try:
        name_results = es.search(index=portrait_index_name, doc_type=portrait_index_type, \
                body=query_body, fields= field)['hits']['hits']
    except:
        return 'does not exist'
    
    result = []
    for i in name_results:
        event = []
        # if i['found'] == False:
        #     event.append(i['_id'])
        #     continue
        i_fields = i['fields']
        for j in field:
            if not i_fields.has_key(j):
                event.append('')
                continue
            if j == 'keywords_string':
                keywords = i_fields[j][0].split('&')
                keywords = keywords[:5]
                event.append(keywords)
            elif j == 'function_mark':
                tag = deal_editor_tag(i_fields[j][0], editor)[0]
                event.append(tag)
            else:
                event.append(i_fields[j][0])
        result.append(event)
    return result

def search_node_time_limit(node_type, item, start_ts, end_ts, editor):
    if node_type == 'User' or node_type == 'Org':
        field = p_column
        # field = ['uid', 'uname','location', 'influence', 'activeness', 'sensitive','keywords_string', 'user_tag']
        node_result = search_user_time_limit(item, field, start_ts, end_ts, editor)
    if node_type == 'Event':
        # field = ['en_name', 'submit_ts',  'uid_counts', 'weibo_counts']
        field = ['en_name','name','event_type','real_time','real_geo','uid_counts','weibo_counts','keywords','work_tag']
        node_result = search_event_time_limit(item, field, start_ts, end_ts, editor)
    return node_result

def search_user_file(item):
    try:
        file_link = es_related_docs.get(index=user_docs_name,doc_type=user_docs_type, id=item)['_source']['related_docs']
    except:
        return []
    print file_link,'============'
    file_list = file_link.split('+')
    return file_list

def search_event_file(item):
    try:
        file_link = es_related_docs.get(index=event_docs_name,doc_type=event_docs_type, id=item)['_source']['related_docs']
    except:
        return []
    file_list = file_link.split('+')
    return file_list

def show_node_detail(node_type, item, submit_user):
    if node_type == 'User' or node_type == 'Org':
        index_key2 = group_primary
        field = p_column
        field = ['uid', 'uname','domain', 'topic_string', "function_description"]
        if node_type == 'User':
            index_n = node_index_name
            index_key = people_primary
        if node_type == 'Org':
            index_n = org_index_name
            index_key = org_primary
        node_key = group_node
        node_result = search_user(item, field, '',node_type)[0]
        tag = deal_user_tag(item, submit_user )[0]
        node_result.append(tag)
        file_link = search_user_file(item)
        node_result.append(file_link)

    if node_type == 'Event':
        index_key2 = special_event_primary
        field = ['en_name','name','real_geo','real_time','event_type', 'start_ts', 'end_ts','real_person', \
                 'real_auth','work_tag', 'description']
        node_result = search_event(item, field, submit_user)[0]
        # tag = deal_event_tag(item, submit_user)[0]
        # node_result.append([tag,1])
        file_link = search_event_file(item)
        node_result.append(file_link)
        index_n = event_index_name
        index_key = event_primary
        node_key = special_event_node

    s_string = 'START s3 = node:%s(%s="%s") MATCH (s3)-[r]-(s0:%s) return s0' \
               %(index_n, index_key, item, node_key)
    # return s_string
    event_result = graph.run(s_string)
    events = []
    for special_event in event_result:
        # return special_event
        ch_name = search_ch_name(special_event[0][index_key2], index_key2)
        events.append(ch_name)
    # result = node_result[0]
    node_result.append(events)
    return node_result

def search_ch_name(en_name, node_type):
    # return node_type,'000000000000'
    if node_type == group_primary:
        result_name = es_group.get(index=group_name, doc_type=group_type, id=en_name, fields=['group_name'])['fields']['group_name'][0]

    elif node_type == special_event_primary:
        result_name = es_event.get(index=special_event_name, doc_type=special_event_type, id=en_name,\
                            fields=['topic_name'])['fields']['topic_name'][0]
    return result_name

def edit_node():
    pass

def node_delete(node_type, item, submit_user):
    if node_type == 'User':
        try:
            es.delete(index=portrait_index_name, doc_type=portrait_index_type, id=item)
        except:
            # pass
            return 'not in es'
        index_n = node_index_name
        index_key = people_primary
    if node_type == 'Org':
        try:
            es.delete(index=portrait_index_name, doc_type=portrait_index_type, id=item)
        except:
            return 'not in es'
        index_n = org_index_name
        index_key = org_primary
    if node_type == 'Event':
        try:
            es_event.delete(index=event_analysis_name,doc_type=event_text_type, id=item)
            es_event.delete(index=event_task_name, doc_type=event_task_type, id=item)
        except:
            return 'not in es'
        index_n = event_index_name
        index_key = event_primary
    s_string = 'START s3 = node:%s(%s="%s") MATCH (s0)-[r]-(s3) delete r, s3' \
               %(index_n, index_key, item)
    # print s_string,'========'
    try:
        event_result = graph.run(s_string)
        # print event_result,'========'
        # for i in event_result:
        #     print i,'=------'
        return '1'
    except:
        return '0'


def deal_user_tag(item ,submit_user):
    try:
        tag = es.get(index=portrait_index_name,doc_type=portrait_index_type, id=item)['_source']['function_mark']
    except:
        return ['','']
    # return result
    # tag = tag_value
    print tag,'======!!=========='
    tag_list = tag.split('&')
    left_tag = []
    keep_tag = []
    for i in tag_list:
        user_tag = i.split('_')
        if user_tag[0] == submit_user:
            keep_tag.append(user_tag[1])
        else:
            left_tag.append(i)
    return [keep_tag, left_tag]

def deal_event_tag(item ,submit_user):
    try:
        tag = es_event.get(index=event_analysis_name,doc_type=event_text_type, id=item)['_source']['work_tag']
    except:
        return ['','']
    # return result
    # tag = tag_value
    print tag,'=============!!==='
    tag_list = tag.split('&')
    left_tag = []
    keep_tag = []
    for i in tag_list:
        user_tag = i.split('_')
        if user_tag[0] == submit_user:
            keep_tag.append(user_tag[1])
        else:
            left_tag.append(i)
    return [keep_tag, left_tag]

def deal_editor_tag(tag ,submit_user):
    print tag,'=============!!==='
    tag_list = tag.split('&')
    left_tag = []
    keep_tag = []
    for i in tag_list:
        user_tag = i.split('_')
        if user_tag[0] == submit_user:
            keep_tag.append(user_tag[1])
        else:
            left_tag.append(i)
    return [keep_tag, left_tag]



def show_wiki(data):
    print data,'data'
    name = data['name']
    conn = getconn()
    cur = conn.cursor()
    sql = "select Url from wiki where Name=%s "
    html_id = cur.execute(sql, (name,))
    print html_id,'-----------'
    if html_id:
        html_id_sql = cur.fetchmany(html_id)
        url = html_id_sql[0][0]
    else:
        return ''
    if data.has_key('url'):
        url = data['url']
    # result = {}
    # return url
    # try:
    #     search_results = es_wiki.get(index=wiki_index_name, doc_type=wiki_type_name, id=url)['_source']
    #     print search_results
    #     # return search_results['content']
    # except:
    #     return ''
    # result['content'] = search_results['content']
    # result['name'] = search_results['name']
    # result['url'] = search_results['url']
    print url
    sql = "select WikiID from wiki where Url=%s "
    html_id = cur.execute(sql, (url,))
    # print html_id,'----------'
    if not html_id:
        html_code = ''
    else:
        html_id_sql = cur.fetchmany(html_id)
        closeAll(conn, cur)
        f = open('/mnt/mfs/wiki/data/'+str(html_id_sql[0][0])+'.html', 'r')
        content_text = f.read()
    soup = BeautifulSoup(content_text)
    content_text = soup.find('div', {'id': 'mw-content-text'})
    # print type(content_text),'000999'
    # result['html'] = str(content_text)
    # print content_text,'============'
    return str(content_text)

def show_wiki_basic(data):
    conn = getconn()
    cur = conn.cursor()
    name = data['name']
    sql = "select Url from wiki where Name=%s "
    html_id = cur.execute(sql, (name,))
    if html_id:
        html_id_sql = cur.fetchmany(html_id)
        url = html_id_sql[0][0]
    else:
        return ''
    # if data.has_key('url'):
    #     url = data['url']
    result = {}
    # return url
    try:
        search_results = es_wiki.get(index=wiki_index_name, doc_type=wiki_type_name, id=url)['_source']
        # print search_results
        # return search_results['content']
    except:
        return ''
    result['content'] = search_results['content']
    result['name'] = search_results['name']
    result['url'] = search_results['url']
    closeAll(conn, cur)
    return result

def search_user_idname(uid_list):
    result = []
    exist_portrait_result = es.mget(index=portrait_index_name, doc_type=portrait_index_type, body={'ids':uid_list}, fields=['uid','uname'], _source=False)['docs']
    for i in exist_portrait_result:
        if i['found'] == False:
            continue
            # result.append([i['_id'], i['_id']])
        else:
            name = i['fields']['uname'][0]
            if name == '':
                name = i['_id']
            result.append([i['_id'], name])
    return result

def search_event_idname(uid_list):
    result = []
    exist_portrait_result = es_event.mget(index=event_analysis_name, doc_type=event_text_type, body={'ids':uid_list}, fields=['en_name','name'], _source=False)['docs']
    for i in exist_portrait_result:
        if i['found'] == False:
            continue
            # result.append([i['_id'], i['_id']])
        else:
            name = i['fields']['name'][0]
            if name == '':
                name = i['_id']
            result.append([i['_id'], name])
    return result

def show_wiki_related(data):
    conn = getconn()
    cur = conn.cursor()
    print data,'00009999'
    name = data['name']
    print name,'name'
    sql = "select Url from wiki where Name=%s "
    html_id = cur.execute(sql, (name,))
    if html_id:
        html_id_sql = cur.fetchmany(html_id)
        url = html_id_sql[0][0]
    else:
        return ''
    # if data.has_key('url'):
    #     url = data['url']
    result = {}
    
    # url = data['url']
    s_string = 'start d=node:'+ wiki_url_index_name +'('+wiki_primary+ '="' + url +'") match (d)-[r]-(e) return labels(e), e'
    print s_string
    result = graph.run(s_string)
    node_result = {}
    for i in result:
        ii = dict(i)
        node_label = ii['labels(e)'][0]
        basic_key = key_type_dict[node_label]
        node_id = ii['e'][basic_key]
        try:
            node_result[node_label].append(node_id)
        except:
            node_result[node_label] = []
            node_result[node_label].append(node_id)
    final_result = {}
    final_result['User'] = []
    final_result['Org'] = []
    final_result['Event'] = []
    for k,v in node_result.iteritems():
        if k == 'User':
            final_result[k] = search_user_idname(v)
        if k == 'Org':
            final_result[k] = search_user_idname(v)
        if k == 'Event':
            final_result[k] = search_event_idname(v)
    return final_result

def wikinode_exist(data):
    conn = getconn()
    cur = conn.cursor()
    print data,'00009999'
    name = data['name']
    print name,'name'
    sql = "select Url from wiki where Name=%s "
    html_id = cur.execute(sql, (name,))
    if html_id:
    	return '1'
    else:
        return '0'
    closeAll(conn, cur)
