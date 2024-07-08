import jieba, json
from function_timer import *
from scoring import scoring
from Data import *
from tqdm import tqdm

@my_function_timer._timer(key='split_and_insert')
def split_and_insert(item, data:Data, ZhongYi_or_not):
    def valid(strs):
        #检验是否全是中文字符
        for _char in strs:
            if not '\u4e00' <= _char <= '\u9fa5':
                return False
        return True

    def word_insert(word, data:Data, ZhongYi_or_not):
        # 对words字典中的对应key进行value的增加
        if word in data.words:
            data.words[word] = [data.words[word][0]+1, data.words[word][1]+ZhongYi_or_not]
        else:
            data.words[word] = [1, 0+ZhongYi_or_not]

    def character_insert(character, data:Data, ZhongYi_or_not):
        if character in data.characters:
            data.characters[character] = [data.characters[character][0]+1, data.characters[character][1]+ZhongYi_or_not]
        else:
            data.characters[character] = [1, 0+ZhongYi_or_not]

    json_keys = ["title", "abstract", "keywords"]
    for json_key in json_keys:
        if json_key == 'keywords':
            tmp_str = ''
            for keyword in item[json_key]:
                tmp_str += keyword
            item_words = jieba.lcut(tmp_str)
        else:
            item_words = jieba.lcut(item[json_key])
        for item_word in item_words:
            if valid(item_word):
                word_insert(item_word, data, ZhongYi_or_not)
        for cha in item[json_key]:
            if valid(cha):
                character_insert(cha, data, ZhongYi_or_not)

def wordFrequency(item_uids, items_json, data:Data, processing_queue):
    # 优先处理的条目
    most_common_word_list = ["中医", "中药", "中医药", "中西医"]
    # 中医文章的数量
    valid_num = 0

    def check_and_checkGrammar(word, item_text):
        if word in item_text:
            if word in jieba.lcut(item_text):
                return True
        return False

    @my_function_timer._timer(key='item_process')
    def item_process(item, identify_word, valid_or_not):
        split_and_insert(item, data, valid_or_not)
        words_score = scoring(item, data, score_method='words')
        characters_score = scoring(item, data, score_method='characters')
        if valid_or_not:
            data.valid_papers[item["title"]] = {
                "abstract": item["abstract"],
                "keywords": item["keywords"],
                "identify_word": identify_word,
                "words_score": words_score,
                "characters_score": characters_score,
                "valid": valid_or_not,
            }
            data.valid_words_score_list.append(words_score)
            data.valid_characters_score_list.append(characters_score)
        else:
            data.invalid_papers[item["title"]] = {
                "abstract": item["abstract"],
                "keywords": item["keywords"],
                "identify_word": identify_word,
                "words_score": words_score,
                "characters_score": characters_score,
                "valid": valid_or_not,
            }
            data.invalid_words_score_list.append(words_score)
            data.invalid_characters_score_list.append(characters_score)

    pbar = tqdm(item_uids)
    # count = 0
    for uid in pbar:
        pbar.set_description("Processing %s" % data.thread_id) # 设置描述
        # count += 1
        # if count>2000:
        #     break
        item = items_json[uid]
        item_text = item["title"] + "。" + item["abstract"] + "。"
        for keyword in item["keywords"]:
            item_text += keyword
        continue_tag = False
        # 处理最常见的单词
        for most_common_word in most_common_word_list:
            if check_and_checkGrammar(most_common_word, item_text):
                valid_num += 1
                item_process(item, most_common_word, True)
                continue_tag = True
                break
        if continue_tag:
            continue
        # 遍历整个corpus，寻找item中出现的单词
        for word in data.zhongyi_corpus:
            if word in item_text:
                valid_num += 1
                item_process(item, word, True)
                continue_tag = True
                break
        if continue_tag:
            continue
        # 本篇文章未找到中医关键词
        item_process(item, "", False)
        data.valid += valid_num
    processing_queue.put(data)
    return