# coding: UTF-8
import torch
import numpy as np
import pickle as pkl
from tqdm import tqdm
from datetime import timedelta
import time, json, random, os

class Config(object):

    """配置参数"""
    def __init__(self):
        self.database_path = r"/home/liangzida/workspace/ZhongYiPapers/manual_labeling_html/Database/"
        self.titles_keywords_path = self.database_path + '/titles_keywords.json'
        self.classified_titles_keywords_path = self.database_path + '/classified_titles_keywords.json'
        self.vocab_path = self.database_path + '/vocab.pkl'                            # 词表
        save_paths = os.listdir(self.database_path + '/Transformer/saved_dict/')
        exp_index = 1
        while True:
            if str(exp_index) not in save_paths:
                break
            else:
                exp_index += 1
        os.makedirs(self.database_path + '/Transformer/saved_dict/' + str(exp_index))
        self.save_path = self.database_path + '/Transformer/saved_dict/' + str(exp_index) + '/model'          # 模型训练结果
        self.log_path = self.database_path + '/Transformer/log/model'
        self.class_list = ['xiyi', 'zhongyi']                                          # 类别名单
        self.vocab_list = [x[:-1] for x in open(
            self.database_path + '/vocab.txt', encoding='utf-8').readlines()]          # 类别名单
        self.vocab_size = len(self.vocab_list)                                         # 类别数
        self.num_classes = len(self.class_list)                                        # 类别数
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')     # 设备
        self.train_ratio = 0.9

        self.dropout = 0.5                                              # 随机失活
        self.require_improvement = 3000000                                 # 若超过1000epoch效果还没提升，则提前结束训练
        self.n_vocab = None                                             # 词表大小，在运行时赋值
        self.num_epochs = 200                                           # epoch数
        self.batch_size = 128                                           # mini-batch大小
        self.shuffle = True
        self.padding = False
        self.pad_size = 250                                             # 每句话处理成的长度(短填长切)
        self.learning_rate = 5e-4                                       # 学习率
        self.embed = 300                                                # 字向量维度
        self.dim_model = 300
        self.hidden = 1024
        self.last_hidden = 512
        self.num_head = 5
        self.num_encoder = 2

MAX_VOCAB_SIZE = 10000  # 词表长度限制
CLS, SEP, MASK, UNK, PAD = '<CLS>', '<SEP>', '<MASK>', '<UNK>', '<PAD>'

def build_dataset(config, dataset_type='unlabeled'):
    # 读取数据集
    # config.save_path = r"D:\vscode_workspace\database\titles_keywords.json.json"
    if dataset_type == 'unlabeled':
        with open(config.titles_keywords_path, "r", encoding='utf-8') as file:
            titles_keywords = json.load(file)
    else:
        with open(config.classified_titles_keywords_path, "r", encoding='utf-8') as file:
            titles_keywords = json.load(file)
    # 以字分割
    tokenizer = lambda x: [y for y in x]  # char-level
    # 读取词表
    vocab = pkl.load(open(config.vocab_path, 'rb'))
    print(f"Vocab size: {len(vocab)}")

    def load_dataset(dataset_type='unlabeled', padding=False, pad_size=320):
        contents = []
        for title in tqdm(titles_keywords.keys()):
            token = [CLS]
            token.extend(tokenizer(title))
            if dataset_type == 'unlabeled':
                for keyword in titles_keywords[title]:
                    token.append(SEP)
                    token.extend(tokenizer(keyword))
            else:
                for keyword in titles_keywords[title][0]:
                    token.append(SEP)
                    token.extend(tokenizer(keyword))
            seq_len = len(token)
            if padding:
                if len(token) < pad_size:
                    token.extend([PAD] * (pad_size - len(token)))
                else:
                    token = token[:pad_size]
                    seq_len = pad_size
            # word to id
            words_line = []
            for word in token:
                words_line.append(vocab.get(word, vocab.get(UNK)))
            contents.append((words_line, -1 if dataset_type == 'unlabeled' else titles_keywords[title][1], seq_len))
        # 打乱数据集顺序，使得train和dev数据集分布相同
        random.shuffle(contents)
        raw_contents = contents
        ratio = config.train_ratio
        return raw_contents[:int(len(raw_contents)*(ratio))], raw_contents[int(len(raw_contents)*(ratio)):], raw_contents[int(len(raw_contents)*(ratio)):]
        # if data_type=='train':
        #     contents = raw_contents[:int(len(raw_contents)*(ratio))]
        # elif data_type=='dev':
        #     contents = raw_contents[int(len(raw_contents)*(ratio)):]
        # else:
        #     contents = raw_contents[int(len(raw_contents)*(ratio)):]
        # return contents
    train, dev, test = load_dataset(dataset_type=dataset_type, padding=config.padding, pad_size=config.pad_size)
    # dev = load_dataset(dataset_type=dataset_type, padding=config.padding, pad_size=config.pad_size, data_type='dev')
    # test = load_dataset(dataset_type=dataset_type, padding=config.padding, pad_size=config.pad_size, data_type='test')
    # test = load_dataset(padding=config.padding, pad_size=config.pad_size, data_type='test')
    return vocab, train, dev, test

class DatasetIterater(object):
    def __init__(self, batches, batch_size, shuffle, device):
        self.batch_size = batch_size
        self.batches = batches
        self.n_batches = len(batches) // batch_size
        self.residue = False  # 记录batch数量是否为整数
        if (self.n_batches==0) or (len(batches) % self.n_batches != 0):
            self.residue = True
        self.index = 0
        self.shuffle = shuffle
        self.device = device
        if self.shuffle:
            random.shuffle(self.batches)

    def _to_tensor(self, datas):
        x = torch.LongTensor([_[0] for _ in datas]).to(self.device)
        y = torch.LongTensor([_[1] for _ in datas]).to(self.device)

        # pad前的长度(超过pad_size的设为pad_size)
        seq_len = torch.LongTensor([_[2] for _ in datas]).to(self.device)
        return (x, seq_len), y

    def __next__(self):
        if self.residue and self.index == self.n_batches:
            batches = self.batches[self.index * self.batch_size: len(self.batches)]
            self.index += 1
            batches = self._to_tensor(batches)
            return batches

        elif self.index >= self.n_batches:
            self.index = 0
            if self.shuffle:
                random.shuffle(self.batches)
            raise StopIteration
        else:
            batches = self.batches[self.index * self.batch_size: (self.index + 1) * self.batch_size]
            self.index += 1
            batches = self._to_tensor(batches)
            return batches

    def __iter__(self):
        return self

    def __len__(self):
        if self.residue:
            return self.n_batches + 1
        else:
            return self.n_batches

class DatasetIterater_no_padding(object):
    def __init__(self, data, batch_size, shuffle, device):
        self.data = data
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.device = device
        # 按照序列长度对数据进行分类
        self.data_sized = {}
        for item in self.data:
            if item[2] not in self.data_sized:
                self.data_sized[item[2]] = [item]
            else:
                self.data_sized[item[2]].append(item)
        # 将不同序列长度的数据导入进迭代器中
        self.data_iters = []
        self.index = 0
        self.batch_num = 0
        for seq_len in self.data_sized:
            self.data_iters.append(DatasetIterater(self.data_sized[seq_len], batch_size, shuffle, device))
            # 计算batch数量
            self.batch_num += len(self.data_iters[self.index])
            self.index += 1
        self.index = 0
        # 数据index队列
        self.iter_queue = list(range(len(self.data_iters)))

    def __next__(self):
        if self.shuffle:
            # 如果遍历完毕则索引归零，队列重置
            if len(self.iter_queue)==0:
                self.index = 0
                self.iter_queue = list(range(len(self.data_iters)))
                raise StopIteration
            # 随机选取某个序列长度的数据集
            _index = random.randint(0, len(self.iter_queue)-1)
            result = next(self.data_iters[self.iter_queue[_index]])
            # 如果该数据集遍历完毕，则从队列里删除该数据集
            if self.data_iters[self.iter_queue[_index]].index==len(self.data_iters[self.iter_queue[_index]]):
                try:
                    _ = next(self.data_iters[self.iter_queue[_index]])
                except:
                    pass
                del self.iter_queue[_index]
            self.index += 1
            return result
        else:
            # 如果遍历完毕则索引归零，队列重置
            if len(self.iter_queue)==0:
                self.index = 0
                self.iter_queue = list(range(len(self.data_iters)))
                raise StopIteration
            _index = 0
            result = next(self.data_iters[self.iter_queue[_index]])
            # 如果该数据集遍历完毕，则从队列里删除该数据集
            if self.data_iters[self.iter_queue[_index]].index==len(self.data_iters[self.iter_queue[_index]]):
                try:
                    _ = next(self.data_iters[self.iter_queue[_index]])
                except:
                    pass
                del self.iter_queue[_index]
            self.index += 1
            return result

    def __iter__(self):
        return self

    def __len__(self):
        return self.batch_num

def build_iterator(dataset, config):
    if config.padding:
        iter = DatasetIterater(dataset, config.batch_size, config.shuffle, config.device)
    else:
        iter = DatasetIterater_no_padding(dataset, config.batch_size, config.shuffle, config.device)
    return iter


def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif)))

