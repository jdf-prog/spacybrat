
# This file define the function render_spacybart()
# that generate the html file for brat visualization of spacy dependency parsing

import spacy
import json
import uuid
from typing import Union, List

BRAT_HTML_HEADER = """
<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/gh/nlplab/brat@v1.3_Crunchy_Frog/style-vis.css"/>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/nlplab/brat@v1.3_Crunchy_Frog/client/lib/head.load.min.js"></script>
<script type="text/javascript">

    var bratLocation = 'https://cdn.jsdelivr.net/gh/nlplab/brat@v1.3_Crunchy_Frog';
    head.js(
        // External libraries
        bratLocation + '/client/lib/jquery-1.7.1.min.js',
        bratLocation + '/client/lib/jquery.svg.min.js',
        bratLocation + '/client/lib/jquery.svgdom.min.js',

        // brat helper modules
        bratLocation + '/client/src/configuration.js',
        bratLocation + '/client/src/util.js',
        bratLocation + '/client/src/annotation_log.js',
        bratLocation + '/client/lib/webfont.js',

        // brat modules
        bratLocation + '/client/src/dispatcher.js',
        bratLocation + '/client/src/url_monitor.js',
        bratLocation + '/client/src/visualizer.js'
    );

    var webFontURLs = [
        bratLocation + '/static/fonts/Astloch-Bold.ttf',
        bratLocation + '/static/fonts/PT_Sans-Caption-Web-Regular.ttf',
        bratLocation + '/static/fonts/Liberation_Sans-Regular.ttf'
    ];

    var collData = {}
    var docData = {}
</script>
"""
BRAT_HTML_TEMPLATE = """
<script type="text/javascript">
    collData["{2}"] = {0}
    docData["{2}"] = {1}

    head.ready(function() {
        // Evaluate the code from the example (with ID
        // 'embedding-entity-example') and show it to the user
        Util.embed('{2}', $.extend({}, collData["{2}"]),
                $.extend({}, docData["{2}"]), webFontURLs);
    });
</script>
<div id="{2}"></div>
"""


def posColor(posTag):
    """
    Take from CoreNLP project configuration file,
    https://github.com/stanfordnlp/CoreNLP/blob/main/src/edu/stanford/nlp/pipeline/demo/corenlp-brat.js#L71
    function posColor, line 71
    """
    if posTag.startswith('N'):
        return '#A4BCED'
    elif posTag.startswith('V') or posTag.startswith('M'):
        return '#ADF6A2'
    elif posTag.startswith('P'):
        return '#CCDAF6'
    elif posTag.startswith('I'):
        return '#FFE8BE'
    elif posTag.startswith('R') or posTag.startswith('W'):
        return '#FFFDA8'
    elif posTag.startswith('D') or posTag == 'CD':
        return '#CCADF6'
    elif posTag.startswith('J'):
        return '#FFFDA8'
    elif posTag.startswith('T'):
        return '#FFE8BE'
    elif posTag.startswith('E') or posTag.startswith('S'):
        return '#E4CBF6'
    elif posTag.startswith('CC'):
        return '#FFFFFF'
    elif posTag == 'LS' or posTag == 'FW':
        return '#FFFFFF'
    else:
        return '#E3E3E3'

# write the above Java function into python
def nerColor(nerTag):
    """
    Take from CoreNLP project configuration file,
    https://github.com/stanfordnlp/CoreNLP/blob/main/src/edu/stanford/nlp/pipeline/demo/corenlp-brat.js#L102
    function posColor, line 102
    """
    if nerTag == 'PERSON':
        return '#FFCCAA'
    elif nerTag == 'ORGANIZATION':
        return '#8FB2FF'
    elif nerTag == 'MISC':
        return '#F1F447'
    elif nerTag == 'LOCATION' or nerTag == 'COUNTRY' or nerTag == 'STATE_OR_PROVINCE' or nerTag == 'CITY':
        return '#95DFFF'
    elif nerTag == 'DATE' or nerTag == 'TIME' or nerTag == 'DURATION' or nerTag == 'SET':
        return '#9AFFE6'
    elif nerTag == 'MONEY':
        return '#FFFFFF'
    elif nerTag == 'PERCENT':
        return '#FFA22B'
    else:
        return '#E3E3E3'


def lang2spacymodels(lang:str):
    """
    Change default spacy models here
    """
    if lang == 'en':
        return 'en_core_web_sm'
    elif lang == 'zh':
        return 'zh_core_web_sm'
    elif lang == 'ja':
        return 'ja_core_news_sm'
    elif lang == 'de':
        return 'de_core_news_sm'
    elif lang == 'fr':
        return 'fr_core_news_sm'
    else:
        return 'en_core_web_sm'

def doc2dict(doc):
    sent_dict = {'sentence': doc.text, 'tokens': []}
    for token in doc:
        token_dict = {'idx': token.i,     # to differentiate same words in a sentence
                'text': token.text,
                'pos': token.pos_,
                'tag': token.tag_,
                'dep': token.dep_,
                'lemma': token.lemma_,
                'parent': token.head.i,
                'children': []}
        for child in list(token.children):
            token_dict['children'].append(child.i)
        sent_dict["tokens"].append(token_dict)
    sent_dict['tokens'].sort(key=lambda token: token['idx'])
    return sent_dict

def get_brat_data(doc, object="dep"):
    assert object in ['dep', 'ner', 'pos']
    sent_dict = doc2dict(doc)
    text = " ".join([token['text'] for token in sent_dict['tokens']])
    docData = {"entities": [], "relations": [], "text": text}
    collData = {"entity_types": [], "relation_types": []}
    entities = docData['entities']
    relations = docData['relations']
    entity_types = collData['entity_types']
    relation_types = collData['relation_types']
    cur_pos = 0
    if object in ["dep", 'pos']:
        for token in sent_dict['tokens']:
            pos_tag = token['tag']
            dep = token['dep']
            parent = sent_dict['tokens'][token['parent']]
            # add entities
            _entity = [f"T{token['idx']}", pos_tag, [[cur_pos, cur_pos + len(token['text'])]]]
            _entity_type = {
                "type": pos_tag,
                "labels": [pos_tag],
                "bgColor": posColor(pos_tag),
                "borderColor": "darken"
            }
            entities.append(_entity)
            if _entity_type not in entity_types:
                entity_types.append(_entity_type)
            # add relations
            if parent != token and object == "dep":
                _relation = [
                    f"R{token['idx']}", token['dep'],
                    [['head', f"T{parent['idx']}"], ['child', f"T{token['idx']}"]]
                ]
                _relation_type = {
                    "type": dep,
                    "labels": [dep],
                    "dashArray": "3,3",
                    "color": posColor(pos_tag),
                    "args": [
                        {"role": "head", "targets": [pos_tag]},
                        {"role": "child", "targets": [pos_tag]}
                    ]
                }
                relations.append(_relation)
                if _relation_type not in relation_types:
                    relation_types.append(_relation_type)
            cur_pos += len(token['text']) + 1
        del collData['relation_types'] # debug
    elif object == "ner":
        for i, ent in enumerate(doc.ents):
            ent_text = ent.text
            ent_type = ent.label_
            # add entities
            _entity = [f"T{i}", ent_type, [[cur_pos, cur_pos + len(ent_text)]]]
            _entity_type = {
                "type": ent_type,
                "labels": [ent_type],
                "bgColor": nerColor(ent_type),
                "borderColor": "darken"
            }
            entities.append(_entity)
            if _entity_type not in entity_types:
                entity_types.append(_entity_type)
            cur_pos += len(ent_text) + 1
    return docData, collData

def render_spacybrat(text:Union[List[str], str], save_path=None, lang='en', object='dep', id=None):
    """
    visualize dependency tree using
    spaCy for dependency parsing
    and brat for visualization
    """
    assert object in ['dep', 'ner', 'pos']
    nlp = spacy.load(lang2spacymodels(lang))
    if not isinstance(text, list):
        text = [text]
    html = BRAT_HTML_HEADER
    for i, t in enumerate(text):
        doc = nlp(t)
        print(t)
        docData, collData = get_brat_data(doc, object=object)
        _html = BRAT_HTML_TEMPLATE
        _html = _html.replace('{0}', json.dumps(collData))
        _html = _html.replace('{1}', json.dumps(docData))
        _html = _html.replace('{2}', id or str(uuid.uuid4()))
        html += "\n" + _html
    if save_path is not None:
        with open(save_path, 'w') as f:
            f.write(html)
    return html
