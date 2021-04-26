INSTALL phonetic search plugin for elastic search
sudo bin/elasticsearch-plugin install analysis-phonetic

Create virtual environment
python3 -m venv venv
Activate virtual environment
source venv/bin/activate
Install requirement
pip3 install -r requirements.txt

Dataset
https://www.kaggle.com/edenbd/150k-lyrics-labeled-with-spotify-valence


Why fuzzy query

>>> es.indices.analyze(index="lyrics-index", body={"text": "flour flower"})
{'tokens': [{'token': 'FLR', 'start_offset': 0, 'end_offset': 5, 'type': '<ALPHANUM>', 'position': 0}, {'token': 'FLWR', 'start_offset': 6, 'end_offset': 12, 'type': '<ALPHANUM>', 'position': 1}]}
['KLRS', 'T', '0', 'FLWR']

https://stackoverflow.com/questions/38816955/elasticsearch-fuzzy-phrases


Example
{"text": "He's gonna walk like you",
 "id": 158209,
 "artist": "Miranda Cosgrove",
 "title": "Brand New You"
}

{"text": "His work like you",
 "id": 158209,
 "artist": "Miranda Cosgrove",
 "title": "Brand New You"
}

{"text": "colors to the flower",
 "id": 158353,
 "artist": "The Prodigy",
 "title": "Colours"
}


reload Index
http://127.0.0.1:5000/reload_index

Search engine template:
https://github.com/phpSoftware/search-engine-template

Highlight
https://www.elastic.co/guide/en/elasticsearch/reference/current/highlighting.html

Phonetic token
https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-phonetic-token-filter.html

Fuzzy query
https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html#query-dsl-match-query-fuzziness