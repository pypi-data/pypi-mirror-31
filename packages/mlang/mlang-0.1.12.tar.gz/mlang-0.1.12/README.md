### 说明
mlang是一个NLP处理平台，使用它可以完成NLP常见的任务。它是mlang server的客户端。

### 安装

```pip install mlang```

### 使用

#### 基本配置
```python
from mlang_client import mclient

mclient.SERVER_URL = 'http://mlang.meizu.com'
mclient.VERSION = 'v1.0
```

#### 基础功能

```python
from mlang_client.mclient import MLang
```

- 分句
```python
txt = '魅族手机不错的，你觉得呢？'

sents = MLang.ssplit(txt)
print(sents)

sents = MLang.ssplit(txt, impl='re', pattern='[。]')
print(sents)

sents = MLang.ssplit(txt, impl='ltp')
print(sents)
```

- 分词
```python
txt = '魅族手机不错的，你觉得呢？'

tokens = MLang.tokenize(txt)
print(tokens)

tokens = MLang.tokenize(txt, impl='jieba')
print(tokens)

tokens = MLang.tokenize(txt, impl='fmm')
print(tokens)

tokens = MLang.tokenize(txt, impl='rmm')
print(tokens)
```

- 词性标记
```python
txt = '魅族手机不错的，你觉得呢？'

tokens = MLang.pos(txt)
print(tokens)

tokens = MLang.pos(txt, impl='ltp')
print(tokens)

tokens = MLang.pos(txt, impl='jieba')
print(tokens)

tokens = MLang.pos(txt, impl='jieba', revise=True, norm=True)
print(tokens)
```

- 命名实体识别
```python
txt = '魅族手机不错的，你觉得呢？'
xx = MLang.ner(txt)
print(xx)
```

- 依存句法解析
```python
txt = '魅族手机不错的，你觉得呢？'
relations = MLang.parse(txt)
print(relations)
```

- 拼音转换
```python
txt = '魅族手机不错的，你觉得呢？'
pinyins = MLang.hanzi2pinyin(txt)
print(pinyins)

pinyins = 'mei zu shou ji bu cuo de , ni jue de ne ?'
hanzis = MLang.pinyin2hanzi(pinyins)
print(hanzis)
```

- 简繁转换
```python
txt = '魅族手机不错的，你觉得呢？'
result = MLang.simplified2traditional(txt)
print(result)

txt = '魅族手機不錯的，你覺得呢？'
result = MLang.traditional2simplified(txt)
print(result)
```

#### 语料管理
将本地的语料文件上传到服务器上，使用服务器上的资源对语料进行处理。服务器上的语料通过语料id来标识。

```python
from mlang_client.mclient import MCorpus
```

- 上传语料
```python
file = 'pinglun.min.txt'
result = MCorpus.upload('pinglun', file)
print(result)
```

- 列出所有语料
```python
corpus_list = MCorpus.list()
print(corpus_list)
```

- 单个语料信息
```python
corpus = MCorpus.info('c1')
print(corpus)
```

- 删除语料
```python
MCorpus.remove('c')
```

- 下载语料
```python
MCorpus.download('pinglun', 'pinglun.c.txt')
```

#### 词表管理
词表就是一个包含很多词的文件，每个词占一行。
词表保存在服务器上，通过词表id标识
词表可在本地构建然后上传到服务器，也可以直接通过语料在服务器上进行构建。

```python
from mlang_client.mclient import MVocab
```

- 列出所有词表
```python
vocab_list = MVocab.list()
print(vocab_list)
```

- 获取单词词表信息
```python
info = MVocab.info('v1')
print(info)
```

- 上传词表
```python
MVocab.upload('xv1', 'mobile.vocab.txt')
```

- 删除词表
```python
MVocab.remove('xv1')
```

- 下载词表
```python
MVocab.download('a1', 'a1.txt')
```

- 构建词表
```python
vocabid = 'xv1'
MVocab.build(vocabid, 'a1')
vocab = MVocab.get(vocabid)
print(vocab)
print(vocab.words())
```

#### 情感分析
构建情感词库、分析一段文本的情感/观点

```python
from mlang_client.mclient import MSentimentAnalyser
```

- 计算情感分值
```python
txt = '魅族手机不错的，你觉得呢？'
score = MSentimentAnalyser.score(txt)
print(score)

is_subject = MSentimentAnalyser.is_subject(txt)
print(is_subject)
```

- 提取评价对象/情感词
```python
terms = MSentimentAnalyser.extract_terms('pinglun', s_seed=['漂亮', '不错'])
print(terms)
```

- 提取评价观点
```python
txt = '魅族手机不错的，你觉得呢？'
opinions = MSentimentAnalyser.extract_opinions(txt, target_vocab_id).data
for opinion in opinions:
    print(opinion['tmodifiers'], opinion['target']['token'], opinion['smodifiers'], opinion['sentiment']['token'], opinion['orientation'])

```

#### 文本/单词表征
将文本/单词以向量的形式表示

```python
from mlang.config import DEFAULT_W2V
from mlang.config import DEFAULT_D2V
from mlang.config import DEFAULT_VOCAB
from mlang_client.mclient import MWordRepresentation
from mlang_client.mclient import MTextRepresentation
```

- 单词表征
```python
vec = MWordRepresentation.represent('手机')
print(vec)

vec = MWordRepresentation.represent('手机', impl='w2v', w2vid=DEFAULT_W2V)
print(vec)

vec = MWordRepresentation.represent('手机', impl='onehot', vocabid=DEFAULT_VOCAB)
print(vec)
```

- 单词相似度
```python
sim = MWordRepresentation.similarity('魅族', '华为')
print(sim)
sim = MWordRepresentation.similarity('魅族', '华为', w2vid=DEFAULT_W2V)
print(sim)
```

- 文本表征
```python
txt = '魅族手机不错的，你觉得呢？'

vec = MTextRepresentation.represent(txt)
print('default:', vec)

vec = MTextRepresentation.represent(txt, impl='w2v', w2vid=DEFAULT_W2V)
print('w2v:', vec)

vec = MTextRepresentation.represent(txt, impl='d2v', d2vid=DEFAULT_D2V)
print('d2v:', vec)

vec = MTextRepresentation.represent(txt, impl='vocab', vocabid=DEFAULT_VOCAB)
print('vocab:', vec)
```

- 文本相似度
```python
txt1 = '魅族手机不错的，你觉得呢？'
txt2 = '华为的手机一般。'

sim = MTextRepresentation.similarity(txt1, txt2)
print('default:', sim)

sim = MTextRepresentation.similarity(txt1, txt2, impl='w2v', w2vid=DEFAULT_W2V)
print('w2v:', sim)

sim = MTextRepresentation.similarity(txt1, txt2, impl='d2v', d2vid=DEFAULT_D2V)
print('d2v:', sim)

sim = MTextRepresentation.similarity(txt1, txt2, impl='vocab', vocabid=DEFAULT_VOCAB)
print('vocab:', sim)
```

#### 文本/单词聚类

```python
from mlang_client.mclient import MWordCluster
from mlang_client.mclient import MTextCluster
```

- 单词聚类
```python
result = MWordCluster.fit('xv1')
print(result)
```

- 文本聚类
```python
r = MTextCluster.fit('cc1')
print(r)

r = MTextCluster.fit('cc1', represent='d2v')
print(r)

r = MTextCluster.fit('cc1', represent='vocab')
print(r)

r = MTextCluster.fit('cc1', represent='w2v', n_clusters=3)
print(r)
```

#### 语言模型
训练好的语言模型保存在服务器上，使用id来标识

```python
from mlang_client.mclient import MLM
```

- 列出所有的语言模型
```python
lms = MLM.list()
print(lms)
```

- 获得指定语言模型的信息
```python
info = MLM.info('lm1')
print(info)
```

- 预测句子概率
```python
txt = '魅族手机不错的，你觉得呢？'
prob = MLM.prob(txt)
print(prob)

txt = '魅族手机不错的，你觉呢得？'
prob = MLM.prob(txt)
print(prob)
```

- 训练语言模型
```python
MLM.build('lm1', 'a1')
```

- 下载语言模型文件
```python
MLM.download('lm1.arpa', 'lm1.arpa')
```

- 删除语言模型
```python
MLM.remove('lm1')
```

#### Word2vec模型

```python
from mlang_client.mclient import MWord2Vec
```

- 列出所有模型
```python
r = MWord2Vec.list()
print(r)
```

- 获得指定模型的信息
```python
r = MWord2Vec.info('w1')
print(r)
```

- 下载模型文件
```python
MWord2Vec.download('w1', 'w1.w2v.model')
```

- 构建模型
```python
r = MWord2Vec.build('w1', 'a1', epochs=20)
print(r)
```

- 删除模型
```python
MWord2Vec.remove('w1')
```


#### Doc2vec模型

```python
from mlang_client.mclient import MDoc2Vec
```

- 列出所有模型
```python
r = MDoc2Vec.list()
print(r)
```

- 获得指定模型的信息
```python
r = MDoc2Vec.info('d2v1')
print(r)
```

- 删除模型
```python
r = MDoc2Vec.remove('d2v1')
print(r)
```

- 下载模型文件
```python
MDoc2Vec.download('d2v1', 'd1.d2v.model')
```

- 构建模型
```python
r = MDoc2Vec.build('d2v1', 'a1')
print(r)
```


#### Seq2Seq模型

```python
from mlang_client.mclient import MSeq2Seq
```

- 列出所有模型
```python
r = MSeq2Seq.list()
print(r)
```

- 获得指定模型的信息
```python
r = MSeq2Seq.info('s2s1')
print(r)
```

- 删除指定模型
```python
r = MSeq2Seq.remove('s2s2')
print(r)
```

- 下载模型文件
```python
MSeq2Seq.download('s2s2', 's2s.model')
```

- 构建模型
```python
MSeq2Seq.build('s2s2', 'seq_c1')
```

- 预测序列
```python
txt = '魅族 的 手机 真 不错 运行 很 流畅 外观 很 漂亮'
result = MSeq2Seq.predict('sbd', txt).data

tokens = txt.split()
seqs = result.split()
for i, token in enumerate(tokens):
    print(token, seqs[i])

```
