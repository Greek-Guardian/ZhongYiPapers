import json, time, pickle
from utils import User, PaperData

def handle_request(paper_data:PaperData, user_dict:dict, request_dict:dict) -> dict:
    # 分类表单
    if request_dict['RequestType'] == 'Classification':
        return handle_classification(paper_data, user_dict, request_dict['Content'])
    # 请求获取上一个 item
    # if request_dict['RequestType'] == 'GetLastItem':
    #     # 确认用户名有效
    #     if request_dict['Content']['UserName']==None or request_dict['Content']['UserName']=='':
    #         request_error = {"FeedbackType": "Error",
    #                                     "Content":{"Notes":"未输入用户名，请输入用户名",}}
    #         return request_error
    #     return next_item(paper_data, last_item=request_dict['Content']['UserName'])
    # 请求获取特定 item
    if request_dict['RequestType'] == 'GetUIDItem':
        # # 确认 uid 有效
        # if type(request_dict['Content']['PaperUID'])!=int:
        #     request_error = {"FeedbackType": "Error",
        #                                 "Content":{"Notes":"UID数据类型错误",}}
        #     return request_error
        if request_dict['Content']['PaperUID'] not in paper_data.raw_item_uid_list:
            request_error = {"FeedbackType": "Error",
                                        "Content":{"Notes":"此UID不存在",}}
            return request_error
        return next_item(paper_data, user_dict, uid=request_dict['Content']['UID'])
    # 刷新
    if request_dict['RequestType'] == 'Start':
        # 确认用户名有效
        if request_dict['Content']['UserName']==None or request_dict['Content']['UserName']=='':
            classification_error = {"FeedbackType": "Error",
                                        "Content":{"Notes":"未输入用户名，请输入用户名",}}
            return classification_error
        return next_item(paper_data, user_dict, request_content=request_dict['Content'])

def handle_classification(paper_data:PaperData, user_dict:dict, request_content:dict) -> dict:
    classified_items_json_path = paper_data.classified_items_json_path
    # 确认用户名有效
    if request_content['UserName'] not in user_dict.keys():
        classification_error = {"FeedbackType": "Error",
                                    "Content":{"Notes":"用户名错误",}}
        return classification_error
    # 确认 uid 正确
    try:
        if request_content['PaperUID'] != paper_data.user_queue[request_content['UserName']]:
            classification_error = {"FeedbackType": "Error",
                                        "Content":{"Notes":"当前文章的UID和服务器维护的UID"+current_item_uid+"不同，请重新登录",}}
            return classification_error
    except:
        classification_error = {"FeedbackType": "Error",
                                    "Content":{"Notes":"UID错误",}}
        return classification_error
    # 确认分类有效
    if request_content['Classification'].strip() not in ['zhongyi', 'xiyi', 'notsure']:
        classification_error = {"FeedbackType": "Error",
                                    "Content":{"Notes":"分类错误，分类为："+str(request_content['Classification']),}}
        return classification_error
    # 确认置信度有效
    try:
        if float(request_content['Confidence'])>1 or float(request_content['Confidence'])<0:
            classification_error = {"FeedbackType": "Error",
                                        "Content":{"Notes":"置信度范围错误（要求[0,1]）",}}
            return classification_error
    except:
        classification_error = {"FeedbackType": "Error",
                                    "Content":{"Notes":"置信度数据类型错误",}}
        return classification_error
    # 将 content 转化为合适的 dict 格式
    manual_classification_dict = {
        'UserName': request_content['UserName'],
        'Type': request_content['Classification'].strip(),
        'Confidence': float(request_content['Confidence']),
        'CommitTime': time.time(),
        'Notes': request_content['Notes'],
    }
    # 读取已分类条目
    with open(classified_items_json_path, 'r', encoding='utf-8') as f:
        classified_items = json.load(f)
    current_item_uid = request_content['PaperUID']
    current_item_json = paper_data.raw_items_dict[current_item_uid]
    # 增添新分类的条目，如果该条目已经被分类过了，则新加入本条分类
    if current_item_uid in classified_items:
        classified_items[current_item_uid]['ManualClassification'].append(manual_classification_dict)
    else:
        current_item_json['ManualClassification'] = [manual_classification_dict]
        classified_items[current_item_uid] = current_item_json
    # 处理用户数据
    if request_content['UserName'] not in user_dict.keys():
        user_dict[request_content['UserName']] = User(request_content['UserName'])
    user_dict[request_content['UserName']].items_labeled.append(request_content['PaperUID'])
    paper_data.user_queue[request_content['UserName']] = None
    # 保存
    with open(classified_items_json_path, 'w', encoding='utf-8') as f:
        json.dump(classified_items, f, ensure_ascii=False, indent=4) # 最后一个参数会保证dump之后的结果所有的字符都能被ascii表示
    # 保存对象到文件
    try:
        with open("item_queue.pickle", "wb") as file:
            pickle.dump(paper_data.item_queue, file)
    except:
        print("item_queue保存失败！")
    try:
        with open("user_queue.pickle", "wb") as file:
            pickle.dump(paper_data.user_queue, file)
    except:
        print("user_queue保存失败！")
    try:
        for user in list(user_dict.keys()):
            with open("user_"+user+"_dict.pickle", "wb") as file:
                pickle.dump(user_dict[user], file)
    except:
        print("user_dict保存失败！")
    # 返回下一条 item
    return next_item(paper_data, user_dict, request_content=request_content)

def next_item(paper_data:PaperData, user_dict:dict, uid=None, request_content=None) -> dict:
    raw_items_dict = paper_data.raw_items_dict
    if len(paper_data.item_queue)==0:
            uid_error = {"FeedbackType":"Error",
                                        "Content":{"Notes":"所有文章都已经标注完毕！",}}
            return uid_error
    if request_content != None:
        # 如果没有该用户，则新建一个用户
        if request_content['UserName'] not in user_dict.keys():
            user_dict[request_content['UserName']] = User(request_content['UserName'])
            paper_data.user_queue[request_content['UserName']] = None
        # 根据缓冲区来确定返回的uid
        if paper_data.user_queue[request_content['UserName']]!=None:
            current_item_uid = paper_data.user_queue[request_content['UserName']]
        else:
            current_item_uid = paper_data.item_queue.pop()
            paper_data.user_queue[request_content['UserName']] = current_item_uid
        # 保存对象到文件
        try:
            with open("item_queue.pickle", "wb") as file:
                pickle.dump(paper_data.item_queue, file)
        except:
            print("item_queue保存失败！")
        try:
            with open("user_queue.pickle", "wb") as file:
                pickle.dump(paper_data.user_queue, file)
        except:
            print("user_queue保存失败！")
        # TODO:
        # 返回用户历史记录
        user_log = user_dict[request_content['UserName']]
        return {"FeedbackType":"ItemContent",
                "Content":{
                    "Title":raw_items_dict[current_item_uid]['title'],
                    "UID":current_item_uid,
                    "Authors":raw_items_dict[current_item_uid]['authors'],
                    "Affiliations":raw_items_dict[current_item_uid]['affiliations'],
                    "Journal": raw_items_dict[current_item_uid]['journal'],
                    "Year": raw_items_dict[current_item_uid]['year'],
                    "Abstract":raw_items_dict[current_item_uid]['abstract'],
                    "Keywords":raw_items_dict[current_item_uid]['keywords'],
                    "Link": raw_items_dict[current_item_uid]['link'],
                    }
                }
    if uid!=None:
        if uid not in raw_items_dict:
            uid_error = {"FeedbackType":"Error",
                                        "Content":{"Notes":"该UID不存在！",}}
            return uid_error
        # 更新缓冲区
        if paper_data.user_queue[request_content['UserName']]!=None:
            paper_data.item_queue.append(paper_data.user_queue[request_content['UserName']])
        paper_data.user_queue[request_content['UserName']] = uid
        # 保存对象到文件
        try:
            with open("item_queue.pickle", "wb") as file:
                pickle.dump(paper_data.item_queue, file)
        except:
            print("item_queue保存失败！")
        try:
            with open("user_queue.pickle", "wb") as file:
                pickle.dump(paper_data.user_queue, file)
        except:
            print("user_queue保存失败！")
        return {"FeedbackType":"ItemContent",
                "Content":{
                    "Title":raw_items_dict[uid]['title'],
                    "UID":uid,
                    "Authors":raw_items_dict[uid]['authors'],
                    "Affiliations":raw_items_dict[uid]['affiliations'],
                    "Journal": raw_items_dict[uid]['journal'],
                    "Year": raw_items_dict[uid]['year'],
                    "Abstract":raw_items_dict[uid]['abstract'],
                    "Keywords":raw_items_dict[uid]['keywords'],
                    "Link": raw_items_dict[uid]['link'],
                    }
                }