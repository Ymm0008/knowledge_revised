# -*-coding:utf-8-*-

import redis
from py2neo import Graph
from elasticsearch import Elasticsearch
from global_config import *
import math
from time_utils import ts2datetime, datetime2ts, ts2date
import MySQLdb
# from config import mysql_charset, mysql_db, mysql_host, mysql_passwd, mysql_port, mysql_user

# user profile info
es_user_profile = Elasticsearch(user_profile_host, timeout=600)
profile_index_name = "weibo_user"
profile_index_type = "user"

# user portrait system
es_user_portrait = Elasticsearch(user_portrait_host, timeout=600)
es_bci = Elasticsearch(bci_es_host, timeout=600)

#related_docs
es_related_docs = Elasticsearch(user_portrait_host, timeout=600)

es_bci_history = Elasticsearch(user_profile_host, timeout=600)

# es_social_sensing
es_social_sensing_text = Elasticsearch(social_sensing_text, timeout=600)
es_prediction = es_social_sensing_text 

sensing_compute_interval = 2*3600
#recommendation task
es_recommendation_result = Elasticsearch(user_portrait_host, timeout=600)

es_retweet = Elasticsearch(retweet_comment_es_host, timeout=600)
es_comment = Elasticsearch(retweet_comment_es_host, timeout = 600)
be_es_retweet = Elasticsearch(retweet_comment_es_host, timeout=600)
be_es_comment = Elasticsearch(retweet_comment_es_host, timeout = 600)
ES_CLUSTER_FLOW1 = Elasticsearch(bci_es_host, timeout = 600)


es_tag = Elasticsearch(user_portrait_host, timeout=600)

# flow text system
es_flow_text = Elasticsearch(flow_text_host, timeout=600)

# social sensing
es_social_sensing_text = Elasticsearch(social_sensing_text, timeout=600)

# km user portrait
es_km_user_portrait = Elasticsearch(km_user_portrait_host,timeout=600)

# km event 
es_event = Elasticsearch(event_host, timeout=600)

es_sim = Elasticsearch(event_host, timeout=600)

es_group = Elasticsearch(event_host, timeout=600)
es_special_event = Elasticsearch(event_host, timeout=600)
# The process state is stored
es_calculate_status = Elasticsearch(calculate_status_host, timeout=600)

es_wiki = Elasticsearch(wiki_host, timeout=600)

graph = Graph(neo4j_data_path, user=neo4j_name, password=neo4j_password)

r = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

# user portrait interface: push user into redis list
r_user = redis.StrictRedis(host=redis_host, port=redis_port, db=10)
r_user_hash_name = 'compute'
r_user_update_hash_name = 'user_update'
r_user_update_long_hash_name = 'user_update_long'

#jln  event redis
topic_queue_name='EVENT_portrait_task'

flow_text_index_name_pre = 'flow_text_' # flow text: 'flow_text_2013-09-01'
flow_text_index_type = 'text'
portrait_index_name = 'user_portrait_0312' # user portrait
portrait_index_type = 'user'
# week retweet/be_retweet relation es
retweet_index_name_pre = '1225_retweet_' # retweet: 'retweet_1' or 'retweet_2'
retweet_index_type = 'user'
be_retweet_index_name_pre = '1225_be_retweet_' #be_retweet: 'be_retweet_1'/'be_retweet_2'
be_retweet_index_type = 'user'
# week comment/be_comment relation es
comment_index_name_pre = '1225_comment_'
comment_index_type = 'user'
be_comment_index_name_pre = '1225_be_comment_'
be_comment_index_type = 'user'
#es for bci history
bci_history_index_name = 'bci_history'
bci_history_index_type = 'bci'

#recommendation_user
recommendation_index_name = 'recommendation_in_user'
recommendation_index_type = 'user'

bci_day_pre = 'bci_'
bci_day_type = 'bci'

# es for tag
tag_index_name = 'custom_attribute'
tag_index_type = 'attribute'

#es for related docs
user_docs_name = 'user_docs'
user_docs_type = 'docs'
event_docs_name = 'event_docs'
event_docs_type = 'docs'

def _default_es_cluster_flow1(host=ES_CLUSTER_HOST_FLOW1):
    es = Elasticsearch(host, timeout=60, retry_on_timeout=True, max_retries=6)
    return es

# 存储user_portrait的重要度/活跃度/影响力和敏感度，与es_flow1一致
ES_COPY_USER_PORTRAIT = _default_es_cluster_flow1(host=ES_COPY_USER_PORTAIT_HOST)
COPY_USER_PORTRAIT_INFLUENCE = "copy_user_portrait_influence"
COPY_USER_PORTRAIT_INFLUENCE_TYPE = 'bci'
COPY_USER_PORTRAIT_IMPORTANCE = "copy_user_portrait_importance"
COPY_USER_PORTRAIT_IMPORTANCE_TYPE = 'importance'
COPY_USER_PORTRAIT_ACTIVENESS = "copy_user_portrait_activeness"
COPY_USER_PORTRAIT_ACTIVENESS_TYPE = 'activeness'
COPY_USER_PORTRAIT_SENSITIVE = "copy_user_portrait_sensitive"
COPY_USER_PORTRAIT_SENSITIVE_TYPE = 'sensitive'

# #weibo_user
# profile_index_name = 'weibo_user'  # user profile es
# profile_index_type = 'user'

#recommendation_in
ES_DAILY_RANK = _default_es_cluster_flow1(host=ES_COPY_USER_PORTAIT_HOST)

# es for activeness history, influence history and pagerank
#copy_portrait_index_name = 'user_portrait_1222'#'this_is_a_copy_user_portrait'
copy_portrait_index_name = 'this_is_a_copy_user_portrait'
copy_portrait_index_type = 'user'

#es_sensitive
sensitive_index_name = 'sensitive_history'
sensitive_index_type = 'sensitive'

#neo4j
graph = Graph(neo4j_data_path, user=neo4j_name, password=neo4j_password)

#wiki   mysql
def getconn():
    conn = MySQLdb.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        passwd=mysql_passwd,
        db=mysql_db,
        charset=mysql_charset
    )
    return conn

def closeAll(conn, cur):
    cur.close()
    conn.commit()
    conn.close()



#neo4j查询事件名

# event2id
def event_name_to_id(en_name):
    query_body = {
        "query":{
            "match":{
                'name':en_name
            }
        }
    }
    name_results = es_event.search(index=event_name, doc_type=event_type, \
                body=query_body,fields=['en_name'])['hits']['hits'][0]['fields']
    for k,v in name_results.iteritems():
        ch_name = v[0]
    return ch_name

# event_search_sth
def es_search_sth(en_name,fields_list):
    print fields_list
    query_body = {
        "query":{
            "match":{
                'en_name':en_name
            }
        }
    }
    sth_results = es_event.search(index=event_analysis_name, doc_type=event_type, \
                body=query_body,fields=fields_list)['hits']['hits'][0]['fields']
    for k,v in sth_results.iteritems():
        sth_name = v[0]
    return sth_name

#es：事件id查找事件名
def event_name_search(en_name):
    query_body = {
        "query":{
            "match":{
                '_id':en_name
            }
        }
    }
    name_results = es_event.search(index=event_analysis_name, doc_type=event_text_type, \
                body=query_body,fields=['name'])['hits']['hits'][0]['fields']
    for k,v in name_results.iteritems():
        ch_name = v[0]
    return ch_name

#查找uid对应的字段
def user_search_sth(en_name,fields_list):
    query_body = {
        "query":{
            "match":{
                '_id':en_name
            }
        }
    }
    try:
        name_results = es_user_portrait.search(index=portrait_index_name, doc_type=portrait_index_type, \
                body=query_body, fields=fields_list)['hits']['hits'][0]['fields']
    except:
        name_dict = {}
        for i in fields_list:
            name_dict[i] =''
        return name_dict
    name_dict = {}
    for k,v in name_results.iteritems():
        name_dict[k] = v[0]
    # print ch_name.encode('utf-8')
    return name_dict

#查找uid对应的名字
def user_name_search(en_name):
    query_body = {
        "query":{
            "match":{
                '_id':en_name
            }
        }
    }
    try:
        name_results = es_user_portrait.search(index=portrait_name, doc_type=portrait_type, \
                body=query_body, fields=['uname'])['hits']['hits'][0]['fields']
    except:
        return en_name
    for k,v in name_results.iteritems():
        ch_name = v[0]
        if ch_name == '':
            ch_name = en_name
    # print ch_name.encode('utf-8')
    return ch_name

#查找该专题下事件关联的用户信息,用户卡片
def related_user_search(uid_list,sort_flag):
    query_body = {
        'query':{
            'terms':{'uid':uid_list}
            },
        'size':200,
        "sort": [{sort_flag:'desc'}]
    }
    fields_list = ['activeness', 'influence','sensitive','uname','fansnum',\
                   'domain','topic_string','user_tag','uid','photo_url','activity_geo_aggs', 'statusnum']

    event_detail = es_user_portrait.search(index=portrait_name, doc_type=portrait_type, \
                body=query_body, _source=False, fields=fields_list)['hits']['hits']
    detail_result = []
    for i in event_detail:
        fields = i['fields']
        detail = dict()
        for i in fields_list:
            try:
                detail[i] = fields[i][0]
            except:
                detail[i] = 'null'
        detail_result.append(detail)
    return detail_result

def deal_event_tag(tag ,submit_user):
    # tag = es_event.get(index=event_analysis_name,doc_type=event_text_type, id=item)['_source']['work_tag'][0]
    # return result
    # tag = tag_value
    # print tag,'=============!!==='
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

# 查找该专题下的包含事件卡片信息，事件卡片
def event_detail_search(eid_list, submit_user):
    if not eid_list:
        return []
    fields_list = ['en_name','name', 'event_type','real_time', 'real_geo', 'uid_counts', 'weibo_counts', 'keywords', 'work_tag']
    only_eid = []
    event_id_list = []
    u_nodes_list = {}
    e_nodes_list = {}
    event_relation =[]
    # try:
    event_result = es_event.mget(index=event_analysis_name, doc_type=event_text_type, \
            body={'ids':eid_list}, fields=fields_list)['docs']
    # except:
    #     return 'node does not exist'
    result = []
    for i in event_result:
        event = []
        # print i
        if not i['found']:
            continue
        i_fields = i['fields']
        for j in fields_list:
            if not i_fields.has_key(j):
                event.append('')
                continue
            if j == 'keywords':
                keywords = i_fields[j][0].split('&')
                keywords = keywords[:5]
                event.append(keywords)
            elif j == 'work_tag':
                tag = deal_event_tag(i_fields[j][0], submit_user)[0]
                event.append(tag)
            elif j == 'event_type':
                try:
                    event.append(EN_CH_EVENT[i_fields[j][0].strip()])
                except KeyError:
                    event.append('')
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
            result = es_user_portrait.search(index=portrait_index_name, doc_type=portrait_index_type, body=query_body)['hits']['hits']
        except Exception, e:
            raise e
        max_evaluate = result[0]['_source'][evaluate]
        max_result[evaluate] = max_evaluate
    return max_result

def deal_user_tag(tag,submit_user):
    # tag = es.get(index=portrait_index_name,doc_type=portrait_index_type, id=item)['_source']['function_mark']
    # print tag,'======!!=========='
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

def user_detail_search(uid_list,submit_user):
    evaluate_max = get_evaluate_max()
    if not uid_list:
        return []
    fields_list = p_column
    only_eid = []
    event_id_list = []
    u_nodes_list = {}
    e_nodes_list = {}
    event_relation =[]
    # try:
    uid_result = es_user_portrait.mget(index=portrait_index_name, doc_type=portrait_index_type, \
            body={'ids':uid_list}, fields=fields_list)['docs']
    result = []
    for i in uid_result:
        event = []
        if i['found'] == False:
            event.append(i['_id'])
            continue
        i_fields = i['fields']
        for j in fields_list:
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
        event.append(search_type(i['_id']))
        result.append(event)
    return result

def search_type(uid):
    try:
        type_list = es_user_profile.get(index=profile_index_name, doc_type=profile_index_type, \
                id=uid,fields=['id', 'verified_type'])
    except:
        return 'user'
    user_list1 = []
    org_list1 = []
    # print type_list
    type_name = ''

    if type_list['found'] == False:
        return 'user'
        # user_list1.append(i['_id'])
    else:
        if not type_list['fields'].has_key('verified_type'):
            return 'user'
        verified_type = type_list['fields']['verified_type'][0]
        if int(verified_type) in org_list:
            type_name = 'org'
        else:
            type_name = 'user'
    return type_name


def get_group(g_name, submit_user):
    if g_name == '': 
        theme_detail = es_group.search(index=group_name, doc_type=group_type,\
            body={'query':{'term':{'user':submit_user}}})['hits']['hits']
    else:
        query_body = {
            "query":{
                'bool':{
                    'must':[
                        {'match':   {"user":submit_user}},         
                        {'match':   {"group_name":g_name}},         
                    ]

                }

            },
            'size':100
        }
        theme_detail = es_group.search(index=group_name, doc_type=group_type,\
            body=query_body)['hits']['hits']
    theme_result = []
    for i in theme_detail:
        topic_id = i['_id']
        theme_name = i['_source']['group_name']
        contain_event = i['_source']['people_count']
        auto_label = i['_source']['label'].split('&')[:5]
        try:
            work_tag = i['_source']['k_label'].split('&')
        # work_tag = deal_event_tag(work_tag, submit_user)[0]
        except:
            work_tag = []
        submit_ts = ts2date(i['_source']['create_ts'])
        theme_result.append([topic_id, theme_name, contain_event, auto_label, work_tag, submit_ts])
    return theme_result

def get_theme(theme_name, submit_user):
    if theme_name == '': 
        theme_detail = es_special_event.search(index=special_event_name, doc_type=special_event_type,\
            body={'query':{'term':{'user':submit_user}}})['hits']['hits']
    else:
        query_body = {
            "query":{
                'bool':{
                    'must':[
                        {'match':   {"user":submit_user}},         
                        {'match':   {"topic_name":theme_name}},         
                    ]

                }

            },
            'size':100
        }
        theme_detail = es_event.search(index=special_event_name, doc_type=special_event_type,\
            body=query_body)['hits']['hits']
    theme_result = []
    for i in theme_detail:
        topic_id = i['_id']
        theme_name = i['_source']['topic_name']
        contain_event = i['_source']['event_count']
        auto_label = i['_source']['label'].split('&')[:5]
        try:
            work_tag = i['_source']['k_label'].split('&')
        # work_tag = deal_event_tag(work_tag, submit_user)[0]
        except:
            work_tag = []
        submit_ts = ts2date(i['_source']['create_ts'])
        theme_result.append([topic_id, theme_name, contain_event, auto_label, work_tag, submit_ts])
    return theme_result

#jln
R_CLUSTER_FLOW1 = redis.StrictRedis(host=REDIS_CLUSTER_HOST_FLOW1, port=REDIS_CLUSTER_PORT_FLOW1)
R_CLUSTER_FLOW2 = redis.StrictRedis(host=REDIS_CLUSTER_HOST_FLOW2, port=REDIS_CLUSTER_PORT_FLOW2)
######
R_CLUSTER_FLOW3 = redis.StrictRedis(host=REDIS_CLUSTER_HOST_FLOW3, port=REDIS_CLUSTER_PORT_FLOW3)
R_CLUSTER_FLOW4 = redis.StrictRedis(host=REDIS_CLUSTER_HOST_FLOW4, port=REDIS_CLUSTER_PORT_FLOW4)
R_SENSITIVE_REDIS = redis.StrictRedis(host=SENSITIVE_REDIS_HOST, port=SENSITIVE_REDIS_POST)

def _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=1):
    return redis.StrictRedis(host, port, db)
redis_flow_text_mid = _default_redis(host=REDIS_TEXT_MID_HOST, port=REDIS_TEXT_MID_PORT, db=2)

redis_host_list = ["1", "2"]
#use to save retweet/be_retweet
retweet_r_1 = _default_redis(host=RETWEET_REDIS_HOST,port=RETWEET_REDIS_PORT, db=1)
retweet_r_2 = _default_redis(host=RETWEET_REDIS_HOST, port=RETWEET_REDIS_PORT, db=2)
retweet_redis_dict = {'1':retweet_r_1, '2':retweet_r_2}
#use to save comment/be_comment
comment_r_1 = _default_redis(host=COMMENT_REDIS_HOST, port=COMMENT_REDIS_PORT, db=1)
comment_r_2 = _default_redis(host=COMMENT_REDIS_HOST, port=COMMENT_REDIS_PORT, db=2)
comment_redis_dict = {'1':comment_r_1, '2':comment_r_2}
#use to save network retweet/be_retweet
daily_retweet_redis = _default_redis(host=REDIS_CLUSTER_HOST_FLOW1,port=REDIS_CLUSTER_PORT_FLOW1,db=4)


R_0 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
R_1 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=1)
R_2 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=2)
R_3 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=3)
R_4 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=4)
R_5 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=5)
R_6 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=6)
R_7 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=7)
R_8 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=8)
R_9 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=9)
R_10 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=10)
R_11 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=11)
#bci_history jln
R_12 = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=12)

R_DICT = {'0':R_0, '1':R_1, '2':R_2, '3':R_3, '4':R_4, '5':R_5, '6':R_6, '7':R_7,\
          '8':R_8, '9':R_9, '10':R_10, '11':R_11, '12':R_12}

R_SENTIMENT_ALL = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=11)
#use to save user domain in user_portrait
R_DOMAIN = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=12)
r_domain_name = 'user_domain'
#use to save user topic in user_portrait
R_TOPIC = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=13)
r_topic_name = 'user_topic'
#use to save domain sentiment trend
R_DOMAIN_SENTIMENT = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=12)
r_domain_sentiment_pre = 'sentiment_domain_'
#use to save topic sentiment trend
R_TOPIC_SENTIMENT = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=13)
r_topic_sentiment_pre = 'sentiment_topic_'



#use to save sentiment keywords task information to redis queue
R_SENTIMENT_KEYWORDS = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=10)
r_sentiment_keywords_name = 'sentiment_keywords_task'


#use to save sentiment keywords task information to redis queue
R_NETWORK_KEYWORDS = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=10)
r_network_keywords_name = 'network_keywords_task'

# social sensing redis
R_SOCIAL_SENSING = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=14)

topic_queue_name = 'topics_task'
#jln   add topic computing in db15
R_ADMIN = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

#use to write portrait user list to redis as queue for update_day and update_week
update_day_redis = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=5)
UPDATE_DAY_REDIS_KEY = 'update_day'
update_week_redis  = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=5)
UPDATE_WEEK_REDIS_KEY = 'update_week'
update_month_redis = _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=5)
UPDATE_MONTH_REDIS_KEY = 'update_month'

#recommendation_in 
R_RECOMMENTATION  = _default_redis(host=REDIS_RECOMMEND_HOST, port=REDIS_RECOMMEND_PORT, db=1)
r_recommendation_in_now = 'recommendation_in_now'
r_recommendation_in_after = 'recommendation_in_after'

'''
# elasticsearch initialize, one for user_profile, one for user_portrait
es_user_profile = Elasticsearch(USER_PROFILE_ES_HOST, timeout = 600)
es_sensitive = Elasticsearch(USER_PROFILE_ES_HOST, timeout=600)
es_user_portrait = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 6000)
es_social_sensing = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_prediction = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_flow_text = Elasticsearch(FLOW_TEXT_ES_HOST, timeout=600)
es_group_result = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout=1000)
es_retweet = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_comment = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_be_comment = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_copy_portrait = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_tag = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout=600)
es_sentiment_task = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_network_task = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_rank_task = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout = 600)
es_operation = Elasticsearch(USER_PORTRAIT_ES_HOST, timeout=600)

# elasticsearch index_name and index_type
profile_index_name = 'weibo_user'  # user profile es
profile_index_type = 'user'
portrait_index_name = 'user_portrait_1222' # user portrait
portrait_index_type = 'user'
flow_text_index_name_pre = 'flow_text_' # flow text: 'flow_text_2013-09-01'
flow_text_index_type = 'text'
# week retweet/be_retweet relation es
retweet_index_name_pre = '1225_retweet_' # retweet: 'retweet_1' or 'retweet_2'
retweet_index_type = 'user'
be_retweet_index_name_pre = '1225_be_retweet_' #be_retweet: 'be_retweet_1'/'be_retweet_2'
be_retweet_index_type = 'user'
# week comment/be_comment relation es
comment_index_name_pre = '1225_comment_'
comment_index_type = 'user'
be_comment_index_name_pre = '1225_be_comment_'
be_comment_index_type = 'user'
# es for activeness history, influence history and pagerank
#copy_portrait_index_name = 'user_portrait_1222'#'this_is_a_copy_user_portrait'
copy_portrait_index_name = 'this_is_a_copy_user_portrait'
copy_portrait_index_type = 'user'
# es for group detect and analysis
group_index_name = 'group_manage'
group_index_type = 'group'

# es for sentiment keywords task
sentiment_keywords_index_name = 'sentiment_keywords_task'
sentiment_keywords_index_type = 'sentiment'

# es for social sensing
sensing_index_name = 'manage_sensing_task'
sensing_doc_type = 'task'

#es for bci history
bci_history_index_name = 'bci_history'
bci_history_index_type = 'bci'

#es_sensitive
sensitive_index_name = 'sensitive_history'
sensitive_index_type = 'sensitive'

# 存储user_portrait的重要度/活跃度/影响力和敏感度，与es_flow1一致
ES_COPY_USER_PORTRAIT = _default_es_cluster_flow1(host=ES_COPY_USER_PORTAIT_HOST)
COPY_USER_PORTRAIT_INFLUENCE = "copy_user_portrait_influence"
COPY_USER_PORTRAIT_INFLUENCE_TYPE = 'bci'
COPY_USER_PORTRAIT_IMPORTANCE = "copy_user_portrait_importance"
COPY_USER_PORTRAIT_IMPORTANCE_TYPE = 'importance'
COPY_USER_PORTRAIT_ACTIVENESS = "copy_user_portrait_activeness"
COPY_USER_PORTRAIT_ACTIVENESS_TYPE = 'activeness'
COPY_USER_PORTRAIT_SENSITIVE = "copy_user_portrait_sensitive"
COPY_USER_PORTRAIT_SENSITIVE_TYPE = 'sensitive'
'''
'''
jln:query_to_es
2016.8.8
'''
def getTopicByNameStEt(topic,start_date,end_date):

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'start_ts':start_date}},
                    {'term':{'end_ts':end_date}},
                    {'term':{'name':topic}}
                ]
            }
        }
    }
    search_result = topic_es.search(index=topic_index_name,doc_type=topic_index_type,body=query_body)['hits']['hits']
    return search_result

def getWeiboByNameStEt(topic,start_date,end_date):
    print weibo_es
    query_body= {
        'query':{
            'filtered':{
                'filter':{
                    'range':{'timestamp':{'gte':start_date,'lte':end_date}}
                    }
            }
        }
    }
    search_result = weibo_es.search(index=topic,doc_type=weibo_index_type,body=query_body)
    print search_result
    return search_result

#结果展示字段
p_column = ['uid','uname','location','influence','activeness','sensitive','keywords_string','function_mark']
o_column = ['uid','uname','location','influence','activeness','sensitive','keywords_string','function_mark']
e_column = ['name','event_type','real_time','real_geo','uid_counts','weibo_counts','keywords','work_tag']
s_column = ['topic_name','event','create_ts','k_label','label']
g_column = ['group_name','people_count','create_ts','k_label','label']


es_list = [es_user_portrait,es_user_portrait,es_event,es_special_event,es_group]
es_index_list  = [portrait_index_name,portrait_index_name,event_analysis_name,special_event_name,group_name]
es_type_list = [portrait_index_type,portrait_index_type,event_type,special_event_type,group_type]
column_list = [p_column,o_column,e_column,s_column,g_column]
tag_list = ['function_mark','function_mark','work_tag','topic_name','group_name']

def get_user_info(uid_list,uname):
    query_body = {
        'query':{
            'terms':{
                'uid':uid_list
            },
            'terms':{
                'verify_type':user_list
            }
        }
    }
    print 'vvvvvvvvvvvvvvvvv'
    result = es_user_portrait.search(index=portrait_index_name,doc_type=portrait_index_type,body=query_body,fields=column_list[i])['hits']['hits']
    print result
    return result 
    '''
    max_influence =  get_max_index('influence')
    max_activeness = get_max_index('activeness')
    max_sensitive = get_max_index('sensitive')
    info_result = []
    for i in result:
        i = i['_source']
        print i
        i['influence'] = normal_index(i['influence'],max_influence)
        i['activeness'] = normal_index(i['activeness'],max_influence)
        i['sensitive'] = normal_index(i['sensitive'],max_influence)
    '''

# 获取最大值
def get_max_index_peo(term):
    query_body = {
        'query':{
            'terms':{'verify_type':peo_list}
        },
        'size':1,
        'sort':[{term: {'order': 'desc'}}]
        }
    try:
        iter_max_value = es_user_portrait.search(index=portrait_index_name, doc_type=portrait_index_type, \
                        body=query_body)['hits']['hits']
    except Exception, e:
        raise e
    iter_max = iter_max_value[0]['_source'][term]

    return iter_max


# 获取最大值
def get_max_index_org(term):
    query_body = {
        'query':{
            'terms':{'verify_type':org_list}
        },
        'size':1,
        'sort':[{term: {'order': 'desc'}}]
        }
    try:
        iter_max_value = es_user_portrait.search(index=portrait_index_name, doc_type=portrait_index_type, \
                        body=query_body)['hits']['hits']
    except Exception, e:
        raise e
    iter_max = iter_max_value[0]['_source'][term]

    return iter_max

def normal_index(index, max_index):
    try:
        normal_value = math.log((index / max_index) * 9 + 1, 10) * 100
        return normal_value
    except:
        return index
def get_org_info(uid_list,uname):
    pass

def deal_event_tag(tag ,submit_user):
    # tag = es_event.get(index=event_analysis_name,doc_type=event_text_type, id=item)['_source']['work_tag'][0]
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
