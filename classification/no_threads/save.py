import json, openpyxl
from Data import *

def save_to(entry, filename):
    try:
        # utf-8将一个汉字编码为3个字节,gbk将一个汉字编码为2个字节,
        with open(filename, 'w',encoding='utf-8') as new_f:  # 重新写入
            json.dump(entry, new_f,ensure_ascii=False,indent=4) # 最后一个参数会保证dump之后的结果所有的字符都能被ascii表示
    except json.decoder.JSONDecodeError:
        print('Make sure the json file is in valid format,[{},{}...]')

def save_Frequency(data:Data):
    # 保存到json
    save_to(data.words, data.save_database_path + '/' + r"words.json")
    save_to(data.characters, data.save_database_path +'/' + r"characters.json")
    # 保存到excel
    workbook = openpyxl.Workbook()
    word_sheet = workbook.active
    word_sheet.title = 'words'
    word_sheet.append(['单词', '出现次数', '中医次数', '概率'])
    for word in data.words.keys():
        prob = data.words[word][1] / data.words[word][0]
        word_sheet.append([word, data.words[word][0], data.words[word][1], prob])
    character_sheet = workbook.create_sheet(index=1, title="characters")
    character_sheet.append(['单词', '出现次数', '中医次数', '概率'])
    for character in data.characters.keys():
        prob = data.characters[character][1] / data.characters[character][0]
        character_sheet.append([character, data.characters[character][0], data.characters[character][1], prob])
    workbook.save(data.save_database_path + "/" + 'frequency.xlsx')

def save_Json(data:Data):
    save_to(data.valid_papers, data.save_database_path + '/' + 'valid_papers.json')
    save_to(data.invalid_papers, data.save_database_path + '/' + 'invalid_papers.json')