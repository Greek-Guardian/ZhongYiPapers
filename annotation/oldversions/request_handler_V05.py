import json, time

def handle_request(paper_data, request_dict:dict) -> dict:
    # 分类表单
    if request_dict['RequestType'] == 'Classification':
        return handle_classification(paper_data, request_dict['Content'])
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
        # 确认 uid 有效
        if type(request_dict['Content']['PaperUID'])!=int:
            request_error = {"FeedbackType": "Error",
                                        "Content":{"Notes":"UID数据类型错误",}}
            return request_error
        return next_item(paper_data, uid=request_dict['Content']['UID'])
    # 刷新 item
    if request_dict['RequestType'] == 'Start':
        return next_item(paper_data, )

def handle_classification(paper_data, request_content:dict) -> dict:
    current_item_uid = paper_data.current_item_uid
    current_item_json = paper_data.current_item_json
    classified_items_json_path = paper_data.classified_items_json_path
    # 确认 uid 正确
    try:
        if request_content['PaperUID']!=current_item_uid:
            classification_error = {"FeedbackType": "Error",
                                        "Content":{"Notes":"当前文章的UID和服务器维护的UID"+current_item_uid+"不同，请刷新",}}
            return classification_error
    except:
        classification_error = {"FeedbackType": "Error",
                                    "Content":{"Notes":"UID数据类型错误",}}
        return classification_error
    # 确认用户名有效
    if request_content['UserName']==None or request_content['UserName']=='':
        classification_error = {"FeedbackType": "Error",
                                    "Content":{"Notes":"未输入用户名，请输入用户名",}}
        return classification_error
    # 确认分类有效
    if request_content['Classification'].strip()!='on' and request_content['Classification'].strip()!='off':
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
        'Type': 'zhongyi' if request_content['Classification']=='on' else 'xiyi',
        'Confidence': float(request_content['Confidence']),
        'CommitTime': time.time(),
        'Notes': request_content['Notes'],
    }
    # 读取已分类条目
    with open(classified_items_json_path, 'r', encoding='utf-8') as f:
        classified_items = json.load(f)
    # 增添新分类的条目，如果该条目已经被分类过了，则新加入本条分类
    if current_item_uid in classified_items:
        classified_items[current_item_uid]['ManualClassification'].append(manual_classification_dict)
    else:
        current_item_json['ManualClassification'] = [manual_classification_dict]
        classified_items.append(current_item_json)
    # 保存
    with open(classified_items_json_path, 'w', encoding='utf-8') as f:
        json.dump(classified_items, f, ensure_ascii=False, indent=4) # 最后一个参数会保证dump之后的结果所有的字符都能被ascii表示
    # 返回下一条 item
    # return next_item(paper_data, current_uidAndUser=(request_content['PaperUID'], request_content['UserName']))
    return next_item(paper_data, next_item=True)

def next_item(paper_data, uid=None, next_item=False) -> dict:
# def next_item(paper_data, current_uidAndUser=None, uid=None, review=None) -> dict:
    if next_item:
        paper_data.current_item_uid_list_index += 1
        paper_data.current_item_uid_list_index %= len(paper_data.raw_item_uid_list)
        paper_data.current_item_uid = paper_data.raw_item_uid_list[paper_data.current_item_uid_list_index]
        paper_data.current_item_json = paper_data.raw_items_dict[paper_data.current_item_uid]
    raw_items_dict = paper_data.raw_items_dict
    raw_item_uid_list = paper_data.raw_item_uid_list
    current_item_uid_list_index = paper_data.current_item_uid_list_index
    if uid!=None:
        if uid not in raw_items_dict:
            uid_error = {"FeedbackType":"Error",
                                        "Content":{"Notes":"该UID不存在！",}}
            return uid_error
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
    return {"FeedbackType":"ItemContent",
            "Content":{
                "Title":raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['title'],
                "UID":raw_item_uid_list[current_item_uid_list_index],
                "Authors":raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['authors'],
                "Affiliations":raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['affiliations'],
                "Journal": raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['journal'],
                "Year": raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['year'],
                "Abstract":raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['abstract'],
                "Keywords":raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['keywords'],
                "Link": raw_items_dict[raw_item_uid_list[current_item_uid_list_index]]['link'],
                }
            }