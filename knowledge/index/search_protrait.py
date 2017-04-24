# -*- coding: utf-8 -*-

import json
import csv
import os
import time
import math
import re
import heapq
from datetime import date
from datetime import datetime
from elasticsearch.helpers import scan
from get_result import uid_name_list_withtype,uid_name_list,event_id_name,uid_name_type,uid_2_name_list,event_id_name_list
import knowledge.model
from knowledge.model import *
from knowledge.extensions import db
from knowledge.global_config import *
from knowledge.global_utils import *
from knowledge.global_utils import R_RECOMMENTATION as r,ES_CLUSTER_FLOW1 as es_cluster
from knowledge.parameter import DAY
from knowledge.time_utils import ts2datetime, datetime2ts, get_db_num, date2ts

people_es_dict = ['hashtag_dict','online_pattern','topic','school_dict','domain_v3','keywords','sensitive_dict']
event_es_dict = ['geo_results','topics','keywords_list','hashtag_dict','user_results','time_results','sentiment_results']
people_normal_dict = ['importance', 'influence', 'activeness', 'sensitive']
people_tag = 'function_mark'
event_tag = 'work_tag'

class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]

def search_person_by_id(uid,user_name):#根据uid查询用户属性

    uid_list = [uid]
    result = dict()
    flag = 0
    evaluate_max = get_evaluate_max()
    search_result = es_user_portrait.mget(index=portrait_name, doc_type=portrait_type, body={"ids": uid_list})["docs"]
    if len(search_result) == 0:
        return result
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            return result
        else:
            data = item['_source']
            for k,v in data.iteritems():
                if k in people_es_dict:
                    result[k] = json.loads(v)
                elif k == people_tag:
                    flag = 1
                    work_tag = v
                    tags = work_tag.split('&')
                    tag_list = []
                    for tag in tags:
                        u,t = tag.split('_')
                        if u == user_name:
                            tag_list.append(t)
                    result[people_tag] = tag_list
                elif k in people_normal_dict:
                    result[k] = normal_index(v,evaluate_max[k])
                elif k == 'activity_geo_dict':
                    result[k] = get_people_org_track(json.loads(v))
                else:
                    if v == 'NULL':
                        result[k] = ''
                    else:
                        result[k] = v

    if flag == 0:
        result[people_tag] = []
    
    return result

def search_org_by_id(uid,user_name):#根据uid查询用户属性

    uid_list = [uid]
    result = dict()
    flag = 0
    evaluate_max = get_evaluate_max()
    search_result = es_user_portrait.mget(index=portrait_name, doc_type=portrait_type, body={"ids": uid_list})["docs"]
    if len(search_result) == 0:
        return result
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            return result
        else:
            data = item['_source']
            for k,v in data.iteritems():
                if k in people_es_dict:
                    result[k] = json.loads(v)
                elif k == people_tag:
                    flag = 1
                    work_tag = v
                    tags = work_tag.split('&')
                    tag_list = []
                    for tag in tags:
                        u,t = tag.split('_')
                        if u == user_name:
                            tag_list.append(t)
                    result[people_tag] = tag_list
                elif k in people_normal_dict:
                    result[k] = normal_index(v,evaluate_max[k])
                elif k == 'activity_geo_dict':
                    result[k] = get_people_org_track(json.loads(v))
                else:
                    if v == 'NULL':
                        result[k] = ''
                    else:
                        result[k] = v

    if flag == 0:
        result[people_tag] = []
        
    return result

def search_bci(uid):#获取用户的粉丝数、关注数和微博数

    uid_list = [uid]
    date = 1480176000#time.time()
    bci_date = ts2datetime(date - DAY)
    index_name = 'bci_' + ''.join(bci_date.split('-'))
    index_type = 'bci'
    user_bci_result = es_cluster.mget(index=index_name, doc_type=index_type, body={'ids':uid_list})['docs']
    if len(user_bci_result):
        return {'fansnum':'', 'statusnum':'', 'friendnum':''}
    result = {'fansnum':'', 'statusnum':'', 'friendnum':''}
    for item in user_bci_result:
        if not item['found']:
            return result
        else:
            data = item['_source']
            fansnum = data['user_fansnum']
            friendsnum = data['user_friendsnum']
            statusnum = data['origin_weibo_number']+data['retweeted_weibo_number']
    result = {'fansnum':fansnum, 'statusnum':statusnum, 'friendnum':friendsnum}
    return result

def get_interaction(uid):#获取用户的交互情况

    uidlist = [uid]
    ts = get_db_num(time.time())    
    retweet_uid = []
    search_result = es_retweet.mget(index=retweet_index_name_pre+str(ts), doc_type=retweet_index_type, body={"ids": uidlist})["docs"]
    keyword = TopkHeap(10)
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            continue
        else:
            data = item['_source']['uid_retweet']
            data = eval(data)
            for k,v in data.iteritems():
                if uid == k:
                    continue                    
                keyword.Push((v,k))
            keyword_data = keyword.TopK()
            for item in keyword_data:
                retweet_uid.append(item[1])

    search_result = es_retweet.mget(index=be_retweet_index_name_pre+str(ts), doc_type=be_retweet_index_type, body={"ids": uidlist})["docs"]
    beretweet_uid = []
    keyword = TopkHeap(10)
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            continue
        else:
            data = item['_source']['uid_be_retweet']
            data = eval(data)
            for k,v in data.iteritems():
                if uid == k:
                    continue
                keyword.Push((v,k))
            keyword_data = keyword.TopK()
            for item in keyword_data:
                beretweet_uid.append(item[1])
  
    search_result = es_comment.mget(index=comment_index_name_pre+str(ts), doc_type=comment_index_type, body={"ids": uidlist})["docs"]
    comment_uid = []
    keyword = TopkHeap(10)
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            continue
        else:
            data = item['_source']['uid_comment']
            data = eval(data)
            for k,v in data.iteritems():
                if uid == k:
                    continue
                keyword.Push((v,k))
            keyword_data = keyword.TopK()
            for item in keyword_data:
                comment_uid.append(item[1])

    search_result = es_comment.mget(index=be_comment_index_name_pre+str(ts), doc_type=be_comment_index_type, body={"ids": uidlist})["docs"]
    becomment_uid = []
    keyword = TopkHeap(10)
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            continue
        else:
            data = item['_source']['uid_be_comment']
            data = eval(data)
            for k,v in data.iteritems():
                if uid == k:
                    continue
                keyword.Push((v,k))
            keyword_data = keyword.TopK()
            for item in keyword_data:
                becomment_uid.append(item[1])

    if len(retweet_uid):
        retweet_list = uid_name_list_withtype(retweet_uid)
        if retweet_list == '-1':
            retweet_list = {}
    else:
        retweet_list = {}

    if len(beretweet_uid):
        beretweet_list = uid_name_list_withtype(beretweet_uid)
        if beretweet_list == '-1':
            beretweet_list = {}
    else:
        beretweet_list = {}

    if len(comment_uid):
        comment_list = uid_name_list_withtype(comment_uid)
        if comment_list == '-1':
            comment_list = {}
    else:
        comment_list = {}

    if len(becomment_uid):
        becomment_list = uid_name_list_withtype(becomment_uid)
        if becomment_list == '-1':
            becomment_list = {}
    else:
        becomment_list = {}

    return {'retweet':retweet_list,'beretweet':beretweet_list,'comment':comment_list,'becomment':becomment_list}

def get_people_org_track(activity_geo_dict):#根据用户地理位置计算轨迹

    results = []
    now_date_ts = datetime2ts(ts2datetime(int(time.time())))
    start_ts = now_date_ts - DAY * len(activity_geo_dict)
    #step2: iter date to get month track
    for geo_item in activity_geo_dict:
        iter_date = ts2datetime(start_ts)
        sort_day_dict = sorted(geo_item.items(), key=lambda x:x[1], reverse=True)
        if sort_day_dict:
            results.append([iter_date, sort_day_dict[0][0]])
        else:
            results.append([iter_date, ''])
        start_ts = start_ts + DAY

    geolist = []
    line_list = []
    index_city = 0
    for i in results:
        if i[1] and i[1].split('\t')[0] == u'中国':
            geolist.append(i[1])
    geolist = [i for i in set(geolist)]
    for x in range(len(results)-1):
        if results[x][1] != '' and results[x+1][1]!='' and results[x][1].split('\t')[0] == u'中国' and results[x+1][1].split('\t')[0] == u'中国':
            if results[x][1] !=  results[x+1][1]:
                line_list.append([results[x][1], results[x+1][1]])
    return {'city':geolist, 'line':line_list}

def get_people_weibo(uid):#根据uid查询微博文本

    time_str = '2016-11-27'#ts2datetime(int(time.time()))
    query_body = {
        "query":{
            "bool":{
                "must":[{'term':{'uid':uid}}],
            }
        }
    }
    result = []
    search_results = es_flow_text.search(index=flow_text_index_name_pre+time_str, doc_type=flow_text_index_type, body=query_body)['hits']['hits']
    if len(search_results) > 0:
        for item in search_results:
            mid = item['_id'].encode('utf-8')
            data = item['_source']
            text = data['text']
            comment = data['comment']
            retweeted = data['retweeted']
            ts = ts2date(data['timestamp'])
            result.append({'mid':mid,'text':text,'time':ts,'comment':comment,'retweeted':retweeted})

    return result            

def search_event_by_id(uid,user_name):#根据uid查询事件属性

    uid_list = [uid]
    result = dict()
    flag = 0
    evaluate_max = get_evaluate_max()
    search_result = es_event.mget(index=event_analysis_name, doc_type=event_text_type, body={"ids": uid_list})["docs"]
    if len(search_result) == 0:
        return result
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            return result
        else:
            data = item['_source']
            for k,v in data.iteritems():
                if k in event_es_dict:
                    if k == 'topics':#lda运行结果
                        topic_list = []
                        topics = json.loads(v)
                        for topic in topics:
                            row = []
                            words = topic[1].split(' + ')
                            for word in words:
                                w,t = word.split('*')
                                t = t.strip('\"')
                                row.append(t)
                            topic_list.append(row)
                        result[k] = topic_list
                    elif k == 'user_results':#用户影响力归一化
                        v_dict = dict()
                        users = json.loads(v)
                        for k1,v1 in users.iteritems():
                            inf = v1['influ']
                            nor_inf = normal_index(inf,evaluate_max['influence'])
                            if nor_inf > 100:#还有大于100的
                                nor_inf = 100
                            v1['influ'] = nor_inf
                            v_dict[k1] = v1
                        result[k] = v_dict
                    else:
                        result[k] = json.loads(v)
                elif k == event_tag:
                    flag = 1
                    work_tag = v
                    tags = work_tag.split('&')
                    tag_list = []
                    for tag in tags:
                        u,t = tag.split('_')
                        if u == user_name:
                            tag_list.append(t)
                    result[event_tag] = tag_list
                elif k == 'event_type':
                    try:
                        category = EN_CH_EVENT[v.strip()]
                    except KeyError:
                        category = ''
                    result[k] = category
                else:
                    if v == 'NULL':
                        result[k] = ''
                    else:
                        result[k] = v

    if flag == 0:
        result[event_tag] = []

    return result

def get_event_weibo(event_id):#根据事件id获取微博文本

    result = []
    uid_list = []
    s_re = scan(es_event, query={'query':{'match_all':{}}},index=event_id, doc_type="text")
    count = 0
    while True:
        try:
            scan_re = s_re.next()
            _id = scan_re['_id']
            source = scan_re['_source']
            mid = source['mid']
            uid = source['uid']
            text = source['text']
            comment = source['comment']
            retweeted = source['retweeted']
            ts = ts2date(source['timestamp'])
            result.append({'mid':mid,'uid':uid,'text':text,'time':ts,'comment':comment,'retweeted':retweeted})
            uid_list.append(uid)
            count = count + 1
            if count >= 1500:
                break
        except StopIteration:
            print "all done"
            break

    if len(uid_list):
        uname_list = uid_name_type(uid_list)
        if uname_list == '-1':
            uname_list = dict()
    else:
        uname_list = dict()

    all_result = []
    media_result = []
    people_result = []
    if len(uname_list):
        for item in result:
            uid = item['uid']
            item['name'] = uname_list[uid]['name']
            all_result.append(item)
            u_type = uname_list[uid]['type']
            if str(u_type) in ['3']:#媒体微博
                media_result.append(item)
            elif str(u_type) in ['-1','0','200','220']:#网民微博
                people_result.append(item)
            else:
                pass

    return all_result,media_result,people_result

def get_event_weibo_by_type(event_id,type_list):#根据事件id获取微博文本

    result = []
    uid_list = []
    s_re = scan(es_event, query={'query':{'match_all':{}}},index=event_id, doc_type="text")
    while True:
        try:
            scan_re = s_re.next()
            _id = scan_re['_id']
            source = scan_re['_source']
            mid = source['mid']
            uid = source['uid']
            text = source['text']
            comment = source['comment']
            retweeted = source['retweeted']
            ts = ts2date(source['timestamp'])
            result.append({'mid':mid,'uid':uid,'text':text,'time':ts,'comment':comment,'retweeted':retweeted})
            uid_list.append(uid)
        except StopIteration:
            print "all done"
            break

    if len(uid_list):
        uname_list = uid_name_type(uid_list)
        if uname_list == '-1':
            uname_list = dict()
    else:
        uname_list = dict()

    new_result = []
    if len(uname_list):
        for item in result:
            uid = item['uid']
            u_type = uname_list[uid]['type']
            if str(u_type) in type_list:
                item['name'] = uname_list[uid]['name']
                new_result.append(item)

    return new_result

def search_neo4j_by_uid(uid,index_name,index_primary):

    p_string = 'START n=node:%s(%s="%s"),m=node:%s("%s:*") MATCH (n)-[]-(m) return m LIMIT 10' % (index_name,index_primary,uid,node_index_name,people_primary)
    p_result = graph.run(p_string)
    p_list = []
    for item in p_result:
        id_key = dict(item[0]).values()[0]
        if id_key not in p_list:
            p_list.append(id_key)
        else:
            continue

    if len(p_list):
        peo_name = uid_2_name_list(p_list)
        if peo_name == '-1':
            peo_name = []
    else:
        peo_name = []

    p_string = 'START n=node:%s(%s="%s"),m=node:%s("%s:*") MATCH (n)-[]-(m) return m LIMIT 10' % (index_name,index_primary,uid,org_index_name,org_primary)
    p_result = graph.run(p_string)
    o_list = []
    for item in p_result:
        id_key = dict(item[0]).values()[0]
        if id_key not in o_list:
            o_list.append(id_key)
        else:
            continue

    if len(o_list):
        org_name = uid_2_name_list(o_list)
        if org_name == '-1':
            org_name = []
    else:
        org_name = []

    p_string = 'START n=node:%s(%s="%s"),m=node:%s("%s:*") MATCH (n)-[]-(m) return m LIMIT 10' % (index_name,index_primary,uid,event_index_name,event_primary)
    p_result = graph.run(p_string)
    event_list = []
    for item in p_result:
        id_key = dict(item[0]).values()[0]
        if id_key not in event_list:
            event_list.append(id_key)
        else:
            continue

    if len(event_list):
        event_name = event_id_name_list(event_list)
    else:
        event_name = []

    relation_name = {'people':peo_name,'org':org_name,'event':event_name}

    return relation_name


def search_related_docs(uid,es_host,es_name,es_type):
    
    uid_list = [uid]
    result = []
    search_result = es_host.mget(index=es_name, doc_type=es_type, body={"ids": uid_list})["docs"]
    if len(search_result) == 0:
        return result
    for item in search_result:
        uid = item['_id']
        if not item['found']:
            return result
        else:
            data = item['_source']
            docs = data['related_docs']
            result = docs.split('+')

    return result

def rank_people_card_data(rank_data,rank_type):#对人物数据排序

    new_dict = []
    if rank_type == 'peo_influence':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['influence'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])
    elif rank_type == 'peo_activity':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['activeness'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])
    elif rank_type == 'peo_sensitivity':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['importance'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])

    return new_dict

def rank_event_card_data(rank_data,rank_type):#对事件数据排序

    new_dict = []
    if rank_type == 'event_weibo':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['weibo'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])
    elif rank_type == 'event_people':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['people'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])
    elif rank_type == 'event_time':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            ts = date2ts(v['time_ts'])
            keyword.Push((ts,k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])

    return new_dict    

def rank_org_card_data(rank_data,rank_type):#对机构数据排序

    new_dict = []
    if rank_type == 'org_influence':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['influence'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])
    elif rank_type == 'org_activity':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['activeness'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])
    elif rank_type == 'org_sensitivity':
        keyword = TopkHeap(len(rank_data))
        for k,v in rank_data.iteritems():
            keyword.Push((v['importance'],k,v))
        keyword_data = keyword.TopK()        
        for item in keyword_data:
            new_dict.append([item[1],item[2]])

    return new_dict
