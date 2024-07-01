from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from request_handler import handle_request
from utils import PaperData
import pickle, os

database_path = r"D:\vscode_workspace\ZhongYiPapers\manual_labeling_html\Database\\"
classified_items_json_path = database_path + r"classified_items_json.json"
# raw_items_path = database_path + r"raw_items.json"
raw_items_path = r"D:\vscode_workspace\database\MetaData.json"

if __name__ == '__main__':
    # 初始化文章数据
    paper_data = PaperData(database_path, classified_items_json_path, raw_items_path)
    # 初始化用户数据
    try:
        with open(paper_data.user_dict_path, "rb") as file:
            user_dict = pickle.load(file)
        print("user_dict.pickle已读取")
    except:
        user_dict = {}
        print("user_dict.pickle未读取")

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
        message = handle_request(paper_data, user_dict, data)
        print("Output:", message)
        print("-"*50)
        # （直接return就可以，python的库会帮我们做这个传送操作）
        # 传送的信息仍然是json格式：{'answer':SparkApi.answer}
        return jsonify(message)

    # 一直运行一个端口号为5500的端口，如果端口接收到了信息，则触发上面的chat()函数
    app.run(port=5500)

