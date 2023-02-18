# spacybrat
Html visualization for the spacy dependency parsing using brat

## Introduction
This repository contains a simple python script to visualize the dependency parsing of a spacy document using brat.
Is supports the the visualization of: pos, dependency and named entities.

You can directly import these html content to you custom web and finish the embedding.

## Install
```python
pip install spacy
python -m spacy download <spacy-model>
```
## Usage

```python
from spacybrat import render_spacybrat
text = "The China National Space Administration is working on a project, whose details might be declared to the public next year"
pos_html = render_spacybrat(text, save_path="./examples/pos.html", object="pos", lang="en")
dep_html = render_spacybrat(text, save_path="./examples/dep.html", object="dep", lang="en")
ner_html = render_spacybrat(text, save_path="./examples/ner.html", object="ner", lang="en")
```
Then click the html file to open it in your browser, you will see the visualization of the dependency parsing respectively.
#### pos_html
![pos_html](./examples/pos.png)

#### dep_html
![dep_html](./examples/dep.png)

#### ner_html
![ner_html](./examples/ner.png)

Multiple sentences are also supported:
```python
from spacybrat import render_spacybrat
texts = ["This is a sentence", "This is another sentence"]
dep_html = render_spacybrat(texts, save_path="./examples/multi_sent_dep.html", object="dep", lang="en")
```
![multi_sent_dep_html](./examples/multi_sent_dep.png)

Multiple languages:
```python
from spacybrat import render_spacybrat
text = "给时光以生命，给岁月以文明"
dep_html = render_spacybrat(text, save_path="./examples/zh_dep.html", object="dep", lang="zh")
```
![zh_dep_html](./examples/zh_dep.png)

