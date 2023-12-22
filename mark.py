import json
def save_to(entry, filename = r'/Users/lzd/Desktop/workspace/ZhongYiPapers/papers_lzd.json'):
    try:
        # utf-8将一个汉字编码为3个字节,gbk将一个汉字编码为2个字节,
        with open(filename, 'w',encoding='utf-8') as new_f:  # 重新写入
            json.dump(entry, new_f,ensure_ascii=False,indent=4) # 最后一个参数会保证dump之后的结果所有的字符都能被ascii表示
    except json.decoder.JSONDecodeError:
        print('Make sure the json file is in valid format,[{},{}...]')

def open_json(filename = r'/Users/lzd/Desktop/workspace/ZhongYiPapers/papers_lzd.json'):
    with open(filename, 'r',encoding='utf-8') as f:
        existing_data = json.load(f)
        return existing_data

def main():
    raw_json = open_json(r"D:\vscode_workspace\ZhongYiPapers\papers_to_mark.json")
    try:
        new_json = open_json(r"D:\vscode_workspace\ZhongYiPapers\papers_marked.json")
    except:
        new_json = []
    start_index = input("起始index：")
    for index in range(len(raw_json)):
        index+=int(start_index)
        item = raw_json[index]
        print("第%d篇" % (index))
        print("标题：\n", item["title"])
        print("摘要：\n", item["abstract"])
        while 1:
            ZhongYi = input("是否是中医（Q表示True，W表示False）：")
            if(ZhongYi=="q" or ZhongYi=="w"):
                break
        if(ZhongYi=="q"):
            item["ZhongYi"] = 1
        else:
            item["ZhongYi"] = 0
        new_json.append(item)
        print("")
        index +=1
        save_to(new_json, r"D:\vscode_workspace\ZhongYiPapers\papers_marked.json")

main()