# coding: UTF-8
import time
import torch
import numpy as np
from utils import *
from train_eval import train
from model import *

if __name__ == '__main__':

    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed_all(1)
    torch.backends.cudnn.deterministic = True  # 保证每次结果一样

    start_time = time.time()
    print("Loading data...")
    config = Config()

    vocab, train_dataset, dev_dataset, test_dataset = build_dataset(config)
    _, train_dataset_labeled, dev_dataset_labeled, test_dataset_labeled = build_dataset(config, dataset_type='labeled')

    train_iter = build_iterator(train_dataset, config)
    dev_iter = build_iterator(dev_dataset, config)
    test_iter = build_iterator(test_dataset, config)

    train_iter_labeled = build_iterator(train_dataset_labeled, config)
    dev_iter_labeled = build_iterator(dev_dataset_labeled, config)
    test_iter_labeled = build_iterator(test_dataset_labeled, config)

    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)

    # 计算loss的weight
    with open(config.titles_keywords_path, "r", encoding='utf-8') as file:
        titles_keywords = json.load(file)
        vocab_freq = [0]*len(vocab)
        tokenizer = lambda x: [y for y in x]
        for title in titles_keywords.keys():
            vocab_freq[vocab['<CLS>']] +=1
            title_token = tokenizer(title)
            for token in title_token:
                vocab_freq[vocab[token]] += 1
            for keyword in titles_keywords[title]:
                vocab_freq[vocab['<SEP>']] +=1
                keyword_token = tokenizer(keyword)
                for token in keyword_token:
                    vocab_freq[vocab[token]] += 1
        vocab_freq[-1] = 1
        vocab_freq[-2] = 1
        vocab_freq[-3] = 1

        vocab_freq = np.array(vocab_freq)
        loss_weight = max(vocab_freq) / vocab_freq
        loss_weight = loss_weight**0.5
        loss_weight = loss_weight**0.5
        # loss_weight = loss_weight**0.5
        loss_weight = torch.FloatTensor(loss_weight).to(config.device)
        loss_weight = None

    # train
    config.n_vocab = len(vocab)
    model = Model(config).to(config.device)
    print(model.parameters)
    train(config, model, vocab, loss_weight, train_iter, dev_iter, test_iter, train_iter_labeled, dev_iter_labeled, test_iter_labeled)
