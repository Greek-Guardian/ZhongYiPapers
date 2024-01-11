import os
from Data import *

def corpus(data:Data):
    def exception_list(exception_path):
        _exception_list_ = []
        with open(exception_path, 'r', encoding='utf-8') as f:
            exception_data = f.readlines()
            for index in range(len(exception_data)):
                exception_data[index] = str(exception_data[index][:-1])
            _exception_list_.extend(exception_data)
        return _exception_list_

    filenames = os.listdir(data.corpus_path)
    _corpus_ = []
    for filename in filenames:
        try:
            with open(data.corpus_path+r"/"+filename, 'r', encoding='gbk') as f:
                _corpus_data = f.readlines()
                for index in range(len(_corpus_data)):
                    _corpus_data[index] = _corpus_data[index].strip()
                _corpus_.extend(_corpus_data)
        except:
            with open(data.corpus_path+r"/"+filename, 'r', encoding='utf-8') as f:
                _corpus_data = f.readlines()
                for index in range(len(_corpus_data)):
                    _corpus_data[index] = _corpus_data[index].strip()
                _corpus_.extend(_corpus_data)
    # 删除 exception list 中的单词
    _corpus_exception_list_ = exception_list(data.exception_path)
    for _corpus_exception_word_ in _corpus_exception_list_:
        try:
            _corpus_.__delitem__(_corpus_.index(_corpus_exception_word_))
        except:
            pass
    return _corpus_