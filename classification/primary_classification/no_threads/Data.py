
class Data():
    def __init__(self) -> None:
        # 路径
        self.json_path = r"./ZhongYiPapers/database/MetaData.json"
        self.save_database_path = r"./ZhongYiPapers/database/12_27"
        self.common_chinese_characters_path = r"./ZhongYiPapers/corpus/common_chinese_characters.json"
        self.prob_excel_path = r"./ZhongYiPapers/database/old/12_23新处理/frequency.xlsx"
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