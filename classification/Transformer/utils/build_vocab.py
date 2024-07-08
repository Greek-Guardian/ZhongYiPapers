import tqdm
import json
import pickle as pkl

'''统计词表'''

MAX_VOCAB_SIZE = 10000  # 词表长度限制
CLS, SEP, MASK, UNK, PAD = '<CLS>', '<SEP>', '<MASK>', '<UNK>', '<PAD>'
min_freq = 1

# 读取标题和摘要
save_path = r"D:\vscode_workspace\database\titles_keywords.json"
with open(save_path, "rb") as file:
    titles_keywords = json.load(file)

# 整理词表
tokenizer = lambda x: [y for y in x]
vocab_dic = {}
for title in tqdm.tqdm(titles_keywords.keys()):
    content = title
    for keyword in titles_keywords[title]:
        content += keyword
    for word in tokenizer(content):
        vocab_dic[word] = vocab_dic.get(word, 0) + 1
vocab_list = sorted([_ for _ in vocab_dic.items() if _[1] >= min_freq], key=lambda x: x[1], reverse=True)[:MAX_VOCAB_SIZE]
vocab_dic = {word_count[0]: idx for idx, word_count in enumerate(vocab_list)}
vocab_dic.update({CLS: len(vocab_dic), SEP: len(vocab_dic) + 1, MASK: len(vocab_dic) + 2, UNK: len(vocab_dic) + 3, PAD: len(vocab_dic) + 4})
print(len(vocab_dic))
print(vocab_dic)

# 保存词表
pkl.dump(vocab_dic, open(r"D:\vscode_workspace\database\vocab.pkl", 'wb'))