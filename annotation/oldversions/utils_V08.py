from queue import Queue, LifoQueue
import json, pickle

class PaperData():
    def __init__(self, \
                    classified_items_json_path = r"D:\vscode_workspace\ZhongYiPapers\manual_labeling_html\Database\classified_items_json.json", \
                    raw_items_path = r"D:\vscode_workspace\ZhongYiPapers\manual_labeling_html\Database\raw_items.json") -> None:
        self.classified_items_json_path = classified_items_json_path
        self.raw_items_path = raw_items_path

        # 默认该文件的格式是{{},{},{}...}
        with open(self.raw_items_path, 'r', encoding='utf-8') as f:
            self.raw_items_dict = json.load(f)
        self.raw_item_uid_list = list(self.raw_items_dict.keys())
        # self.raw_item_uid_list = self.raw_item_uid_list.sort()

        # self.item_queue = LifoQueue()
        # for item in self.raw_item_uid_list:
        #     self.item_queue.put(item)
        try:
            with open("item_queue.pickle", "rb") as file:
                self.item_queue = pickle.load(file)
            print("item_queue.pickle已读取")
        except:
            self.item_queue = self.raw_item_uid_list
            print("item_queue.pickle未读取")

        try:
            with open("user_queue.pickle", "rb") as file:
                self.user_queue = pickle.load(file)
            print("user_queue.pickle已读取")
        except:
            self.user_queue = {}
            print("user_queue.pickle未读取")

class User():
    def __init__(self, name) -> None:
        self.name = name
        self.items_labeled = []