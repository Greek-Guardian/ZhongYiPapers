from function_timer import *
import jieba
from Data import *

@my_function_timer._timer(key='scoring')
def scoring(item, data:Data, score_method = 'words'):
    item_text = item["title"] + "。" + item["abstract"] + "。"
    for keyword in item["keywords"]:
        item_text += keyword
    score = 0
    common_chinese_characters_weight = 1/5
    common_chinese_words_weight = 1/3
    if score_method == 'words':
        # 按单词打分
        item_text_WordsOrCharacters = jieba.lcut(item_text)
        prob_dict = data.excel_words
    else:
        # 按字符打分
        item_text_WordsOrCharacters = item_text
        prob_dict = data.excel_characters

    for item_text_WordOrCharacter in item_text_WordsOrCharacters:
        # 舍弃特殊字符（标点符号等）。若单词或字符为中文//英文//数字，isalnum()函数则为True
        if item_text_WordOrCharacter.isalnum():
            # 判断是否为中文
            is_Chinese = True
            for _char in item_text_WordOrCharacter:
                if not '\u4e00' <= _char <= '\u9fa5':
                    is_Chinese = False
                    break
            # 若单词或字符为英文或数字，则减1分
            if not is_Chinese:
                score -= 1
                continue
            # 判断是否包含不常用汉字
            is_common_chinese = True
            for _char in item_text_WordOrCharacter:
                if _char not in data.common_chinese_characters:
                    is_common_chinese = False
                    break
            try:
                if is_common_chinese:
                    # 若为常用中文单词，则将单词概率的1/3或1/5作为分数。
                    score += prob_dict[item_text_WordOrCharacter]['概率']*\
                        (common_chinese_characters_weight*(1-(score_method=='words'))+\
                         common_chinese_words_weight*(score_method=='words'))
                else:
                    # 若单词包含不常用汉字字符，则将概率作为分数
                    score += prob_dict[item_text_WordOrCharacter]['概率']
            except:
                # 舍弃excel中不包含的单词
                pass
    score /= len(item_text_WordsOrCharacters)
    return score