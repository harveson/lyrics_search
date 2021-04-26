#!/usr/bin/python
import os
from  glob import glob
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from collections import deque
from collections import defaultdict
import json

import sqlite3

def gendata():
    con = sqlite3.connect("lyrics.db")
    cur = con.cursor()
    cur.execute("select id, artist, title, lyrics from lyrics;")
    output = cur.fetchall()
    for o in output:
        mid, artist, title, lyrics = o
        r = {
            "_id": mid,
            "_index": "lyrics-index",
            "artist": artist, 
            "title": title, 
            "lyrics": lyrics
            }
        yield r
        


def build_index(indexname="lyrics-index"):
    es = Elasticsearch()
    try:
        es.indices.delete(indexname)
    except:
        pass
    phonetic_setting = {
            "settings":
            {
                "analysis": 
                {
                    "analyzer": {
                        "default": {
                            "tokenizer": "standard",
                            "filter": [ "lowercase",  "my_metaphone"]
                        }
                    },
                    "filter": {
                        "my_metaphone": {
                            "type": "phonetic",
                            "encoder": "metaphone",
                            "replace": False
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                "lyrics": {
                    "type": "text",
                    "index_prefixes": { }    
                }
                }
            }

        }
    es.indices.create(index=indexname, body=phonetic_setting)
    deque(parallel_bulk(client=es, actions=gendata(), thread_count=16), maxlen=0)
    print("Indexing done")
    return 1

def query_index(sentence, indexname="lyrics-index"):
    es = Elasticsearch()
    es.indices.refresh(index=indexname)
    analyze_default = {
        "tokenizer": "standard",
        "filter": [ "lowercase"],
        "text": sentence
    }
    words = es.indices.analyze(index=indexname, body=analyze_default)
    words = [i["token"] for i in words["tokens"]]

    analyze_phonetics = {
        "tokenizer": "standard",
        "filter": [ "lowercase", {"type": "phonetic","encoder": "metaphone","replace": True}],
        "text": sentence
    }
    phonetic_words = es.indices.analyze(index=indexname, body=analyze_phonetics)
    phonetic_words = [i["token"] for i in phonetic_words["tokens"]]
    print(phonetic_words)
    spans = []
    for i in range(len(words)):
        span =  { "span_or": {"clauses": [{"span_multi": {"match": {"fuzzy": {"lyrics": {"value": words[i], "fuzziness":"AUTO"}}}}}, {"span_multi":{"match":{"fuzzy":{"lyrics":{"value": phonetic_words[i],"fuzziness":"AUTO"}}}}}]
                            }
                }
        spans.append(span)

    query = {  
    "query":{  
        "bool":{  
            "must":[  
                {  
                "span_near":{  
                    "clauses": spans,
                    "slop": 1,
                    "in_order":True
                }
                }
            ]
        }
    },
    "highlight": {"fields": {"lyrics": {}}}
    }

    # query = {"query": {"match": {"lyrics": {"query": sentence, "fuzziness": "2"}}}, 
    #         "highlight": {"fields": {"lyrics": {}}}}
    res = es.search(index=indexname, body=query)
    rtn = []
    for hit in res['hits']['hits']:
        #rtn.append("Artist: %s, Title: %s, Lyrics: %s" % (hit["_source"]["artist"], hit["_source"]["title"], " ".join(hit["highlight"]["lyrics"]))) 
        url = "http://www.google.com/search?q=%s+%s"%("+".join(hit["_source"]["artist"].split()), "+".join(hit["_source"]["title"].split()))
        rtn.append({"artist": hit["_source"]["artist"], "title": hit["_source"]["title"], "highlight": " ".join(hit["highlight"]["lyrics"]), "url": url})
    return rtn

if __name__=="__main__":
    build_index()