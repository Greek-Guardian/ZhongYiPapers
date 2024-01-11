import json

'''
把每一条entry的结果存到JSON文件里,或许还可以直接存成sql形式，
或先全部存为json，然后再在mySQL中进行数据库的构建
'''


def save_to(filename, entry_list): # 不要依次添加entry，在内存中添加完毕再写入文件
    try:
        # utf-8将一个汉字编码为3个字节,gbk将一个汉字编码为2个字节,
        with open(filename, 'r',encoding='utf-8') as f:
            existing_data = json.load(f)
            for entry in entry_list:
                existing_data.append(entry)  # 增加条目
        with open(filename, 'w',encoding='utf-8') as new_f:  # 重新写入
            json.dump(existing_data, new_f,ensure_ascii=False,indent=4) # 最后一个参数会保证dump之后的结果所有的字符都能被ascii表示
            # if entry.get('篇名',[]): # 输出文献的标题
            #     print(f"{entry['篇名']}saved")
    except json.decoder.JSONDecodeError:
        print('Make sure the json file is in valid format,[{},{}...]')


def overwrite_to(filename,entry_list):
    try:
        with open(filename, 'w',encoding='utf-8') as f:  # 直接写入
            json.dump(entry_list, f,ensure_ascii=False,indent=4)
        print(f"{filename}已重写")
    except json.decoder.JSONDecodeError:
        print('Make sure the json file is in valid format,[{},{}...]')


def read(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    return existing_data


def count(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    return len(existing_data)


def new_json_file(filename,list_data):#用于新建json文件，list_data需要满足格式要求
    # # 将Python数据结构转化为JSON字符串
    # json_data = json.dumps(list_data)
    # 写入到文件，注意如果指定文件已存在，将清空原始文件
    with open(filename, 'w',encoding='utf-8') as f:
        json.dump(list_data, f,ensure_ascii=False,indent=4)
    print(f"{filename}已新建")


# if __name__ == '__main__':
    # my_filename = 'people.json'
    # entry_list_instance = [
    #     {'name': 'Bob','age': 35},
    #     {'name':'Alice','age':20},]
    #
    # overwrite_to(my_filename, entry_list_instance)

