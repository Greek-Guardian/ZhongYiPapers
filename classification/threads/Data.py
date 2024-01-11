import json, os
import pandas as pd
from function_timer import FunctionTimer

class Data():
    def __init__(self) -> None:
        # 路径
        self.prob_excel_path = r"ZhongYiPapers/database/12_27/frequency.xlsx"
        self.save_database_path = r"./ZhongYiPapers/database/12_28"
        self.json_path = r"./ZhongYiPapers/database/MetaData.json"
        self.common_chinese_characters_path = r"./ZhongYiPapers/corpus/common_chinese_characters.json"
        self.exception_path = r"./ZhongYiPapers/corpus/不包含的词汇.txt"
        self.corpus_path = r"./ZhongYiPapers/corpus/corpus"
        #
        self.words = {}
        self.characters = {}
        self.valid_papers = {}
        self.invalid_papers = {}
        # 得分
        self.valid_words_score_list = []
        self.valid_characters_score_list = []
        self.invalid_words_score_list = []
        self.invalid_characters_score_list = []
        # 词频
        self.excel_words = None
        self.excel_characters = None
        # 词库
        self.common_chinese_characters = None
        self.zhongyi_corpus = None
        # 多线程
        self.threads_num = 6
        self.valid = 0
        self.thread_id = -1
        # 函数计时器
        # self.my_function_timer = FunctionTimer()
        # 读取常用汉字
        with open(self.common_chinese_characters_path, 'r',encoding='utf-8') as f:
            self.common_chinese_characters = json.load(f)
            self.common_chinese_characters = set(self.common_chinese_characters)
        # 读取词频
        self.excel_words = pd.DataFrame(pd.read_excel(self.prob_excel_path, sheet_name='words', header=0, index_col=0))
        self.excel_words = self.excel_words.to_dict('index')
        self.excel_characters = pd.DataFrame(pd.read_excel(self.prob_excel_path, sheet_name='characters', header=0, index_col=0))
        self.excel_characters = self.excel_characters.to_dict('index')
        # 读取中医词库
        self.zhongyi_corpus = self.corpus()

    def corpus(self):
        def exception_list(exception_path):
            _exception_list_ = []
            with open(exception_path, 'r', encoding='utf-8') as f:
                exception_data = f.readlines()
                for index in range(len(exception_data)):
                    exception_data[index] = str(exception_data[index][:-1])
                _exception_list_.extend(exception_data)
            return _exception_list_

        filenames = os.listdir(self.corpus_path)
        _corpus_ = []
        for filename in filenames:
            try:
                with open(self.corpus_path+r"/"+filename, 'r', encoding='gbk') as f:
                    _corpus_data = f.readlines()
                    for index in range(len(_corpus_data)):
                        _corpus_data[index] = _corpus_data[index].strip()
                    _corpus_.extend(_corpus_data)
            except:
                with open(self.corpus_path+r"/"+filename, 'r', encoding='utf-8') as f:
                    _corpus_data = f.readlines()
                    for index in range(len(_corpus_data)):
                        _corpus_data[index] = _corpus_data[index].strip()
                    _corpus_.extend(_corpus_data)
        # 删除 exception list 中的单词
        _corpus_exception_list_ = exception_list(self.exception_path)
        for _corpus_exception_word_ in _corpus_exception_list_:
            try:
                _corpus_.__delitem__(_corpus_.index(_corpus_exception_word_))
            except:
                pass
        return _corpus_