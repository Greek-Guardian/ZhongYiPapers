import json, time, pickle
from utils import PaperData

def handle_request(paper_data:PaperData, user_dict:dict, request_dict:dict) -> dict:
    # 分类表单
    if request_dict['RequestType'] == 'Classification':
        return handle_classification(paper_data, user_dict, request_dict['Content'])
    # 获取特定uid的item
    if request_dict['RequestType'] == 'GetUIDItem':
        try:
            return next_item(paper_data, user_dict, request_dict['Content'], uid=request_dict['Content']['PaperUID'])
        except:
            uid_error = {"FeedbackType":"Error",
                                        "Content":{"Notes":"UID格式错误！",}}
            return uid_error
    # 刷新
    if request_dict['RequestType'] == 'Start':
        # 确认用户名有效
        if request_dict['Content']['UserName']==None or request_dict['Content']['UserName']=='':
            classification_error = {"FeedbackType": "Error",
                                        "Content":{"Notes":"未输入用户名，请输入用户名",}}
            return classification_error
        return next_item(paper_data, user_dict, request_dict['Content'], start=True)

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
    now = time.time()
    nowStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    manual_classification_dict = {
        'UserName': request_content['UserName'],
        'uid': request_content['PaperUID'],
        'Type': request_content['Classification'].strip(),
        'Confidence': float(request_content['Confidence']),
        'CommitTime': now,
        'CommitTimeFormat': nowStyleTime,
        'Notes': request_content['Notes'],
    }
    # 读取已分类条目
    with open(classified_items_json_path, 'r', encoding='utf-8') as f:
        classified_items = json.load(f)
    current_item_uid = request_content['PaperUID']
    current_item_json = paper_data.raw_items_dict[current_item_uid]
    # 增添新分类的条目，如果该条目已经被分类过了，则新加入本条分类
    if current_item_uid in classified_items:
        classified_items[current_item_uid]['ManualClassification'].insert(0, manual_classification_dict)
    else:
        current_item_json['ManualClassification'] = [manual_classification_dict]
        classified_items[current_item_uid] = current_item_json
    # 处理用户数据
    if request_content['UserName'] not in user_dict.keys():
        user_dict[request_content['UserName']] = {'uid_list':[], 'records':{}}
    user_dict[request_content['UserName']]['uid_list'].insert(0, manual_classification_dict['uid'])
    if manual_classification_dict['uid'] not in user_dict[request_content['UserName']]['records']:
        user_dict[request_content['UserName']]['records'][manual_classification_dict['uid']] = [manual_classification_dict]
    else:
        user_dict[request_content['UserName']]['records'][manual_classification_dict['uid']].insert(0, manual_classification_dict)
    paper_data.user_queue[request_content['UserName']] = None
    # 保存
    with open(classified_items_json_path, 'w', encoding='utf-8') as f:
        json.dump(classified_items, f, ensure_ascii=False, indent=4) # 最后一个参数会保证dump之后的结果所有的字符都能被ascii表示
    # 保存对象到文件
    try:
        with open(paper_data.item_queue_path, "wb") as file:
            pickle.dump(paper_data.item_queue, file)
    except:
        print("item_queue保存失败！")
    try:
        with open(paper_data.user_queue_path, "wb") as file:
            pickle.dump(paper_data.user_queue, file)
    except:
        print("user_queue保存失败！")
    try:
        with open(paper_data.user_dict_path, "wb") as file:
            pickle.dump(user_dict, file)
    except:
        print("user_dict保存失败！")
    # 返回下一条 item
    return next_item(paper_data, user_dict, request_content)

def next_item(paper_data:PaperData, user_dict:dict, request_content, start=False, uid=None) -> dict:
    raw_items_dict = paper_data.raw_items_dict
    if len(paper_data.item_queue)==0:
            uid_error = {"FeedbackType":"Error",
                                        "Content":{"Notes":"所有文章都已经标注完毕！",}}
            return uid_error
    if uid == None:
        # 如果没有该用户，则新建一个用户
        if request_content['UserName'] not in user_dict.keys():
            user_dict[request_content['UserName']] = {'uid_list':[], 'records':{}}
            paper_data.user_queue[request_content['UserName']] = None
        # 根据缓冲区来确定返回的uid
        if paper_data.user_queue[request_content['UserName']]!=None:
            current_item_uid = paper_data.user_queue[request_content['UserName']]
        else:
            current_item_uid = paper_data.item_queue.pop()
            paper_data.user_queue[request_content['UserName']] = current_item_uid
        # 保存对象到文件
        try:
            with open(paper_data.item_queue_path, "wb") as file:
                pickle.dump(paper_data.item_queue, file)
        except:
            print("item_queue保存失败！")
        try:
            with open(paper_data.user_queue_path, "wb") as file:
                pickle.dump(paper_data.user_queue, file)
        except:
            print("user_queue保存失败！")
        # 返回用户历史记录
        user_log_tmp = []
        if start:
            for record in user_dict[request_content['UserName']]['uid_list']:
                user_log_tmp.extend(user_dict[request_content['UserName']]['records'][record])
        else:
            try:
                user_log_tmp = user_dict[request_content['UserName']]['records'][user_dict[request_content['UserName']]['uid_list'][0]]
            except:
                pass
        user_log = []
        for record in user_log_tmp:
            record['Title'] = raw_items_dict[record['uid']]['title']
            record['Link'] = raw_items_dict[record['uid']]['link']
            record['Keywords'] = raw_items_dict[record['uid']]['keywords']
            user_log.append(record)
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
                    "Tags": raw_items_dict[current_item_uid]['tags'],
                    "user_log":user_log,
                    }
                }
    else:
        try:
            if uid not in raw_items_dict:
                uid_error = {"FeedbackType":"Error",
                                            "Content":{"Notes":"该UID不存在！",}}
                return uid_error
        except:
            uid_error = {"FeedbackType":"Error",
                                        "Content":{"Notes":"UID格式错误！",}}
            return uid_error
        # 更新缓冲区
        if paper_data.user_queue[request_content['UserName']]!=None:
            paper_data.item_queue.append(paper_data.user_queue[request_content['UserName']])
        if uid in paper_data.item_queue:
            paper_data.item_queue.remove(uid)
        paper_data.user_queue[request_content['UserName']] = uid
        # 保存对象到文件
        try:
            with open(paper_data.item_queue_path, "wb") as file:
                pickle.dump(paper_data.item_queue, file)
        except:
            print("item_queue保存失败！")
        try:
            with open(paper_data.user_queue_path, "wb") as file:
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
                    "user_log":[],
                    }
                }