# CUnlp v0.3.1 (beta) [![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/jrkns/cunlp/blob/master/LICENSE)


## What is CUnlp?
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a python library for NLP tasks in thai language by using machine learning approach running on [TensorFlow](https://github.com/tensorflow/tensorflow) and [Keras](https://github.com/keras-team/keras).

## Features List
#### Model
- Word tokenization
- POS tagging
- Sentiment analysis (soon)
- Topic analysis (soon)
- Latent analysis (soon)
- Review analysis (soon)

#### Embedding
- Word2Vector
- Compare word similarity
- K-nearest word similarity
- Word substitution
- Initialize embeddings

and more..

## Requirement
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Now our library only supported <strong>Python3</strong> with [TensorFlow v1.4.0rc0+](https://github.com/tensorflow/tensorflow) and [Keras v2.1.5+](https://github.com/keras-team/keras) installed.

## Installation
Directly install via PyPI
```
$ pip install cunlp
```

## Usage

```python
import cunlp as cu

# Word tokenization
sentence = "สวัสดีชาวโลกเรามาช่วยตัดคำให้"
tokens_in_list = cu.model.tokenize(sentence)
tokens_in_string = cu.model.tokenize(sentence, listing=False)

# POS tagging
sentence = "ฉันชอบกินอาหารจีน"
tokens_of_sentence = cu.model.tokenize(sentence)
pos_of_words = cu.model.pos(tokens_of_sentence)

# Word embedding
word_a = "หมา"
word_b = "แมว"
word_c = "เสื้อฮาวาย"
vector_of_word_a = cu.embedding.vectorize(word_a)
vector_and_word_of_word_a = cu.embedding.vectorize_in_depth(word_a)
substituted_word_c = cu.embedding.substitute(word_c)

similarity_score = cu.embedding.compare_similarity(word_a, word_b)
similarity_score_with_substitution = cu.embedding.compare_similarity(word_a, word_b, sub=True)

top_three_similar = cu.embedding.most_similarity(word_c, rank=3)
top_three_similar_with_substitution = cu.embedding.most_similarity(word_c, rank=3, sub=True)
```

## API
```
https://cunlp-api.herokuapp.com/tokenize?sentence=ทดสอบการตัดคำอย่างง่าย
https://cunlp-api.herokuapp.com/pos?sentence=ฉันชอบกินอาหารจีนมาก
https://cunlp-api.herokuapp.com/vectorize?word=แมว
https://cunlp-api.herokuapp.com/compare_similarity?word1=แมว&word2=หมา
```
*For testing only!

## Benchmark
| Task | Precision | Recall | F1-score  | Detail | 
| ------------- |:-------:|:-------:|:-------:|:-------:|
| Word tokenization  | 0.97072 | 0.97052 | 0.97062 | on BEST2010 |
| Word embedding | - | - | - | [view](http://projector.tensorflow.org/?config=https://raw.githubusercontent.com/jrkns/cunlp/master/material/config-projector.json) |
| POS tagging | 0.81327 | 0.75963 | 0.78554 | [view](https://github.com/jrkns/cunlp/blob/master/material/benchmark_pos.md) |


## Contributor

<div>
<a href="https://github.com/jrkns"><img align="left" src="https://avatars.githubusercontent.com/jrkns" height="70px" width="70px;"/></a><b>Danupat Khamnuansin</b>
<br>
<a href="https://github.com/jrkns">jrkns</a>
<br>
</div>
<br>
<br>
<div>
<a href="https://github.com/nattasit-m"><img align="left" src="https://avatars.githubusercontent.com/nattasit-m" height="70px" width="70px;"/></a><b>Nuttasit Mahakusolsirikul</b>
<br>
<a href="https://github.com/nattasit-m">nattasit-m</a>
<br>
</div>
