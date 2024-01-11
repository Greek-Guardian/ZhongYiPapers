import json
import re
import hashlib
from json_file_process import *


def preprocess(filename,result_filename):  # 将作者和单位转换为列表，有数字出现的打上标签authors[] affiliations[] tags[]
    with open(filename,'r',encoding='utf-8') as f:
        input_entries=json.load(f)
    for entry in input_entries[1:]: # 第一个为提示词
        entry['tags']=[]
        # 检查所有条目是否全面
        for value in entry.values():
            if value=="none":
                entry['tags'].append("incomplete")
        # 处理作者
        authors=entry.get('authors')
        delimiter_pattern=re.compile(r'[，；;]')
        delimiters_author=delimiter_pattern.search(authors)

        # commas_authors=re.search(r'，',authors)
        # semicolons_authors=re.search(r'；',authors)
        numbers = re.findall(r'\d', authors)
        if numbers:  # 有数字
            entry['tags'].append('with nums')

        if authors=="none":
            entry['authors']=[]
        elif delimiters_author:
            entry['authors']=re.split(delimiter_pattern,authors)
        else:  # 只有一个作者
            entry['authors']=[authors]
        # 处理单位
        affiliations = entry.get('affiliations')
        delimiters_affiliation = delimiter_pattern.search(affiliations)
        if affiliations=="none":
            entry['affiliations']=[]
        elif delimiters_affiliation:
            entry['affiliations']=re.split(delimiter_pattern,affiliations)
        else:  # 只有一个单位
            entry['affiliations'] = [affiliations]

    new_json_file(result_filename,input_entries)
    print(f"{filename}已预处理")


def generate_uid(filename):
    with open(filename,'r',encoding='utf-8') as f:
        input_entries=json.load(f)
    for article_metadata in input_entries[1:]: # 第一个为提示词
        metadata_str=f"{article_metadata['title']}{article_metadata['source']}"
        # 将中文字符转换为字节序列（UTF-8 编码）
        metadata_bytes=metadata_str.encode('utf-8')
        uid=hashlib.sha256(metadata_bytes).hexdigest()
        article_metadata['uid']=uid
    overwrite_to(filename,input_entries)
    print(f"{filename}已编码")


if __name__=='__main__':
    province = "北京"
    province_spell = "beijing"
    for year in range(2010, 2023):
        filename = '%s/%s_result%d.json' % (province, province_spell, year)
        generate_uid(filename)

