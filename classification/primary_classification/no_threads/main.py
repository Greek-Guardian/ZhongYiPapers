import json, os
import pandas as pd
from prettytable import PrettyTable
import numpy as np
from function_timer import *
from save import save_Frequency, save_Json
from ZhongYiPapers.classification.no_threads.corpus import corpus
from word_frequency import wordFrequency
from Data import *

data = Data()

def main(data:Data):
    # 读取常用汉字
    with open(data.common_chinese_characters_path, 'r',encoding='utf-8') as f:
        data.common_chinese_characters = json.load(f)
        data.common_chinese_characters = set(data.common_chinese_characters)
    # 读取词频
    data.excel_words = pd.DataFrame(pd.read_excel(data.prob_excel_path, sheet_name='words', header=0, index_col=0))
    data.excel_words = data.excel_words.to_dict('index')
    data.excel_characters = pd.DataFrame(pd.read_excel(data.prob_excel_path, sheet_name='characters', header=0, index_col=0))
    data.excel_characters = data.excel_characters.to_dict('index')
    # 读取中医词库
    data.zhongyi_corpus = corpus(data)
    # 主函数
    total_json_num, total_valid_num = wordFrequency(data.json_path, data)
    # 保存
    save_Frequency(data)
    save_Json(data)

    table = PrettyTable(['Total item num','Total valid num','Ratio'])
    table.add_row([total_json_num, total_valid_num, total_valid_num/total_json_num])
    print(table)

    words_score_list = data.valid_words_score_list + data.invalid_words_score_list
    characters_score_list = data.valid_characters_score_list + data.invalid_characters_score_list
    table = PrettyTable(['Variant','Mean','Var'])
    table.add_row(["Words", np.mean(words_score_list), np.var(words_score_list)])
    table.add_row(["Valid words", np.mean(data.valid_words_score_list), np.var(data.valid_words_score_list)])
    table.add_row(["Invalid words", np.mean(data.invalid_words_score_list), np.var(data.invalid_words_score_list)])
    table.add_row(["Characters", np.mean(characters_score_list), np.var(characters_score_list)])
    table.add_row(["Valid characters", np.mean(data.valid_characters_score_list), np.var(data.valid_characters_score_list)])
    table.add_row(["Invalid characters", np.mean(data.invalid_characters_score_list), np.var(data.invalid_characters_score_list)])
    print(table)

    table = PrettyTable(['Function','Time cost'])
    table.add_row(["split_and_insert", my_function_timer.time_count["split_and_insert"]])
    table.add_row(["scoring", my_function_timer.time_count["scoring"]])
    table.add_row(["item_process", my_function_timer.time_count["item_process"]])
    print(table)

main(data)