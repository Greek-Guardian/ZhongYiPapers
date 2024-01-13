from queue import Queue, LifoQueue
import json, pickle

class PaperData():
    def __init__(self, database_path, classified_items_json_path, raw_items_path) -> None:
        self.database_path = database_path
        self.classified_items_json_path = classified_items_json_path
        self.raw_items_path = raw_items_path
        self.item_queue_path = self.database_path+"item_queue.pickle"
        self.user_queue_path = self.database_path+"user_queue.pickle"
        self.user_dict_path = self.database_path+"user_dict.pickle"

        # 默认该文件的格式是{{},{},{}...}
        with open(self.raw_items_path, 'r', encoding='utf-8') as f:
            self.raw_items_dict = json.load(f)
        self.raw_item_uid_list = list(self.raw_items_dict.keys())
        # self.raw_item_uid_list = self.raw_item_uid_list.sort()

        # self.item_queue = LifoQueue()
        # for item in self.raw_item_uid_list:
        #     self.item_queue.put(item)
        try:
            with open(self.item_queue_path, "rb") as file:
                self.item_queue = pickle.load(file)
            print("item_queue.pickle已读取")
        except:
            self.item_queue = self.raw_item_uid_list
            print("item_queue.pickle未读取")

        try:
            with open(self.user_queue_path, "rb") as file:
                self.user_queue = pickle.load(file)
            print("user_queue.pickle已读取")
        except:
            self.user_queue = {}
            print("user_queue.pickle未读取")