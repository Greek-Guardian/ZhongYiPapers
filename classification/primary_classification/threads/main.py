import json, jieba
from prettytable import PrettyTable
import numpy as np
from function_timer import *
from save import save_Frequency, save_Json
from corpus import corpus
from word_frequency import wordFrequency
from Data import *
import threading, multiprocessing
import concurrent.futures
from multiprocessing import Process
from copy import deepcopy
# 取消 jieba 输出日志
import logging
jieba.setLogLevel(logging.INFO)

def main(main_data:Data):
    print("读取MetaData中...")
    # 读取文章json
    with open(main_data.json_path, 'r',encoding='utf-8') as f:
        items_json = json.load(f)
    item_uids = items_json[0]
    items_json = items_json[1]
    # 主函数
    total_json_num = len(item_uids)
    Data_list = []
    print("创建类列表中...")
    for index in range(main_data.threads_num):
        Data_list.append(deepcopy(main_data))
        Data_list[index].thread_id = index
    print("开始多线程运行：")
    '''concurrent.futures.ThreadPoolExecutor'''
    # with concurrent.futures.ThreadPoolExecutor(max_workers=main_data.threads_num) as executor:
    #     # Start the load operations and mark each future with its URL
    #     future_to_url = {}
    #     for index in range(main_data.threads_num):
    #         start = index*(int(total_json_num/main_data.threads_num))
    #         end = (start + (int(total_json_num/main_data.threads_num))) if index != (main_data.threads_num-1) else None
    #         future_to_url[executor.submit(wordFrequency, item_uids[start:end], items_json, Data_list[index])] = index
    #     for future in concurrent.futures.as_completed(future_to_url):
    #         index = future_to_url[future]
    #         try:
    #             data = future.result()
    #         except Exception as exc:
    #             print(index, 'generated an exception: %s' % exc)
    #         else:
    #             print(index, 'is over')
    '''concurrent.futures.ProcessPoolExecutor'''
    # paras = []
    # for index in range(main_data.threads_num):
    #     start = index*(int(total_json_num/main_data.threads_num))
    #     end = (start + (int(total_json_num/main_data.threads_num))) if index != (main_data.threads_num-1) else None
    #     paras.append((item_uids[start:end], items_json, Data_list[index]))
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     for len_item_uids, valid_num in zip(paras, executor.map(wordFrequency, paras)):
    #         print('%d len, %d valid.' % (len_item_uids, valid_num))
    '''multiprocessing'''
    thread_queue = []
    processing_queue = multiprocessing.Queue()
    for index in range(main_data.threads_num):
        start = index*(int(total_json_num/main_data.threads_num))
        end = (start + (int(total_json_num/main_data.threads_num))) if index != (main_data.threads_num-1) else None
        thread_queue.append(Process(target=wordFrequency, args=(item_uids[start:end], items_json, Data_list[index], processing_queue)))
    for index in range(main_data.threads_num):
        thread_queue[index].start()

    Data_list = []
    for th_item in thread_queue:
        while th_item.is_alive():
            while False == processing_queue.empty():
                Data_list.append(processing_queue.get())

    for t in thread_queue:
        t.join()
        # t.terminate()
    print('All process finished.')
    # Data_list = [processing_queue.get() for j in thread_queue]
    print('All results collected.')
    '''threading'''
    # for index in range(main_data.threads_num):
    #     start = index*(int(total_json_num/main_data.threads_num))
    #     end = (start + (int(total_json_num/main_data.threads_num)) -1) if index != (main_data.threads_num-1) else -1
    #     thread_queue.append(threading.Thread(target=wordFrequency, args=(item_uids[start:end], items_json, Data_list[index])))
    #     thread_queue[index].start()
    # # total_json_num, total_valid_num = wordFrequency(item_uids, items_json, data)
    # for t in thread_queue:
    #     t.join()

    for index in range(main_data.threads_num):
        for word in Data_list[index].words:
            if word not in main_data.words:
                main_data.words[word] = Data_list[index].words[word]
            else:
                main_data.words[word] += Data_list[index].words[word]
        for character in Data_list[index].characters:
            if character not in main_data.characters:
                main_data.characters[character] = Data_list[index].characters[character]
            else:
                main_data.characters[character] += Data_list[index].characters[character]
        # main_data.my_function_timer.time_count["split_and_insert"] += Data_list[index].my_function_timer.time_count["split_and_insert"]
        # main_data.my_function_timer.time_count["scoring"] += Data_list[index].my_function_timer.time_count["scoring"]
        # main_data.my_function_timer.time_count["item_process"] += Data_list[index].my_function_timer.time_count["item_process"]
        main_data.valid_papers.update(Data_list[index].valid_papers)
        main_data.invalid_papers.update(Data_list[index].invalid_papers)
        # 得分
        main_data.valid_words_score_list.extend(Data_list[index].valid_words_score_list)
        main_data.valid_characters_score_list.extend(Data_list[index].valid_characters_score_list)
        main_data.invalid_words_score_list.extend(Data_list[index].invalid_words_score_list)
        main_data.invalid_characters_score_list.extend(Data_list[index].invalid_characters_score_list)
    main_data.valid = len(list(main_data.valid_papers.keys()))
    # 保存
    save_Frequency(main_data)
    save_Json(main_data)

    table = PrettyTable(['Total item num','Total valid num','Ratio'])
    table.add_row([total_json_num, main_data.valid, main_data.valid/total_json_num])
    print(table)

    words_score_list = main_data.valid_words_score_list + main_data.invalid_words_score_list
    characters_score_list = main_data.valid_characters_score_list + main_data.invalid_characters_score_list
    table = PrettyTable(['Variant','Mean','Var'])
    table.add_row(["Words", np.mean(words_score_list), np.var(words_score_list)])
    table.add_row(["Valid words", np.mean(main_data.valid_words_score_list), np.var(main_data.valid_words_score_list)])
    table.add_row(["Invalid words", np.mean(main_data.invalid_words_score_list), np.var(main_data.invalid_words_score_list)])
    table.add_row(["Characters", np.mean(characters_score_list), np.var(characters_score_list)])
    table.add_row(["Valid characters", np.mean(main_data.valid_characters_score_list), np.var(main_data.valid_characters_score_list)])
    table.add_row(["Invalid characters", np.mean(main_data.invalid_characters_score_list), np.var(main_data.invalid_characters_score_list)])
    print(table)

    # table = PrettyTable(['Function','Time cost'])
    # table.add_row(["split_and_insert", main_data.my_function_timer.time_count["split_and_insert"]])
    # table.add_row(["scoring", main_data.my_function_timer.time_count["scoring"]])
    # table.add_row(["item_process", main_data.my_function_timer.time_count["item_process"]])
    # print(table)

if __name__ =='__main__':
    # _ = jieba.lcut("我是世界之王")
    start_time = time.process_time()
    main_data = Data()
    main(main_data)
    end_time = time.process_time()
    print('运行时长（min）：', (end_time - start_time)/60)