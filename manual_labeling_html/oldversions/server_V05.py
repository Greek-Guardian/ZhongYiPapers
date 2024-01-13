from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from request_handler import handle_request
import json
import pickle
from queue import Queue

class PaperData():
    def __init__(self) -> None:
        self.classified_items_json_path = r"D:\vscode_workspace\ZhongYiPapers\manual_labeling_html\Database\classified_items_json.json"
        self.raw_items_path = r"D:\vscode_workspace\ZhongYiPapers\manual_labeling_html\Database\raw_items.json"
        # 默认该文件的格式是{{},{},{}...}
        with open(self.raw_items_path, 'r', encoding='utf-8') as f:
            self.raw_items_dict = json.load(f)
        self.raw_item_uid_list = list(self.raw_items_dict.keys())
        # raw_item_uid_list = raw_item_uid_list.sort()
        self.current_item_uid_list_index = 0
        self.current_item_uid = self.raw_item_uid_list[self.current_item_uid_list_index]
        self.current_item_json = self.raw_items_dict[self.current_item_uid]

class User():
    def __init__(self, name) -> None:
        self.name = name
        self.items_labeled = []

if __name__ == '__main__':
    paper_data = PaperData()

    # # 保存对象到文件
    # with open("users.pickle", "wb") as file:
    #     pickle.dump(user_list, file)
    # 从文件中加载对象
    try:
        with open("users.pickle", "rb") as file:
            user_list = pickle.load(file)
    except:
        user_list = []

    # 后台主程序从这里开始运行
    app = Flask(__name__)
    # app.run(
    #   host='10.168.45.117',
    #   port= 5500,
    #   debug=True
    # )

    @app.route('/classification', methods=['POST'])
    @cross_origin() # 允许跨域访问
    def chat():
        # 接受前端发来的信息
        data = request.get_json()
        print("Input:", data)
        message = handle_request(paper_data, data)
        print("Output:", message)
        # （直接return就可以，python的库会帮我们做这个传送操作）
        # 传送的信息仍然是json格式：{'answer':SparkApi.answer}
        return jsonify(message)

    # 一直运行一个端口号为5500的端口，如果端口接收到了信息，则触发上面的chat()函数
    app.run(port=5500)

