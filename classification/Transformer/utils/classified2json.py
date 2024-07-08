import json

save_path = r"D:\vscode_workspace\database\MetaData.json"
with open(save_path, "rb") as file:
    metadata = json.load(file)

save_path = r"D:\vscode_workspace\database\classified_items_json.json"
with open(save_path, "rb") as file:
    classified_items_json = json.load(file)

dataset_raw_format = {}
sum = 0
for item_key in classified_items_json.keys():
    item_log_latest = classified_items_json[item_key]['ManualClassification'][0]
    for item_log in classified_items_json[item_key]['ManualClassification']:
        if item_log['CommitTime'] > item_log_latest['CommitTime']:
            item_log_latest = item_log
    if (item_log_latest['UserName'] != 'sun') and (item_log_latest['UserName'] != '郭玉杰'):
        continue
    sum += 1
    # if item_log_latest['Type']==''
    dataset_raw_format[classified_items_json[item_key]['title']] = [metadata[1][item_key]['keywords'], 1 if item_log_latest['Type']=='zhongyi' else 0]

save_path = r"D:\vscode_workspace\database\titles_keywords.json"
with open(save_path, "w", encoding='utf-8') as file:
    json.dump(dataset_raw_format, file, ensure_ascii=False, indent=4)