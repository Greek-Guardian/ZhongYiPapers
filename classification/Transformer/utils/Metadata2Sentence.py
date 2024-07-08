import json

save_path = r"D:\vscode_workspace\database\MetaData.json"
with open(save_path, "rb") as file:
    metadata = json.load(file)

titles = {}
for uid in metadata[1].keys():
    titles[metadata[1][uid]['title']] = metadata[1][uid]['keywords']

save_path = r"D:\vscode_workspace\database\titles_keywords.json"
with open(save_path, "w", encoding='utf-8') as file:
    json.dump(titles, file, ensure_ascii=False, indent=4)