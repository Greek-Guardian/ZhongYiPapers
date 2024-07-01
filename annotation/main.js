function item_refresh() {
    document.getElementById('Confidence').value = 1;
    document.getElementById('ConfidenceRoll').value = 1;
    document.getElementById('Notes').value = "";
    // 接收文本框输入
    // var input = document.getElementById('myInput').value.toLowerCase();
    // 向后端python POST一个请求
    var item_json = 0;
    var item_refresh_commit_json = {"RequestType":"Start",
        "Content":{
            "UserName":document.getElementById('UserName').value
            }
    };
    fetch('http://127.0.0.1:5500/classification', {
    // fetch('http://10.168.45.117:5500/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // 这个请求的body是json的形式：{label1: value1, label2: value2}
        // body: JSON.stringify({message: input}),
        body: JSON.stringify(item_refresh_commit_json),
        mode:'cors'
    })
    .then(response => response.json())
    .then(response => {
        item_json = response
        console.log(item_json);
        if(item_json['FeedbackType'].includes("Error")){
            alert(item_json['Content']['Notes']);
        }
        else{
            json_to_table(item_json, true);
        }
    })
    .catch((error) => {console.error('Error:', error);});
}

function json_to_table(item_json, refresh){
    // 把信息打印在创建的列表里
    tmp_td = document.getElementById('UIDtext');
    var tmp_str = JSON.stringify(item_json['Content']['UID']);
    tmp_td.value = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('paperLink');
    var tmp_str = JSON.stringify(item_json['Content']['Title']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Abstract');
    var tmp_str = JSON.stringify(item_json['Content']['Abstract']);
    tmp_td.textContent = "\t" + tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Keywords');
    var tmp_str = JSON.stringify(item_json['Content']['Keywords']);
    tmp_str = tmp_str.replace(/[0-9]+/g,"");
    tmp_str = tmp_str.replace(/"/g,"");
    tmp_str = tmp_str.replace(/,/g,"，");
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Journal');
    var tmp_str = JSON.stringify(item_json['Content']['Journal']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Authors');
    var tmp_str = JSON.stringify(item_json['Content']['Authors']);
    tmp_str = tmp_str.replace(/[0-9]+/g,"");
    tmp_str = tmp_str.replace(/"/g,"");
    tmp_str = tmp_str.replace(/,/g,"，");
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Affiliations');
    var tmp_str = JSON.stringify(item_json['Content']['Affiliations']);
    tmp_str = tmp_str.replace(/[0-9]+/g,"");
    tmp_str = tmp_str.replace(/"/g,"");
    tmp_str = tmp_str.replace(/,/g,"，");
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Year');
    var tmp_str = JSON.stringify(item_json['Content']['Year']);
    // tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);
    tmp_td.textContent = tmp_str;

    tmp_td = document.getElementById('Tags');
    var tmp_str = JSON.stringify(item_json['Content']['Tags']);
    tmp_str = tmp_str.replace(/"/g,"");
    tmp_str = tmp_str.replace(/,/g,"，");
    tmp_str = tmp_str.replace("[","");
    tmp_str = tmp_str.replace("]","");
    tmp_td.textContent = tmp_str;

    tmp_td = document.getElementById('paperLink');
    var tmp_str = JSON.stringify(item_json['Content']['Link']);
    // tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);
    // tmp_td = document.getElementById('Link');
    tmp_td.setAttribute("href", tmp_str.substring(1, tmp_str.length-1));
    // const li = document.createElement('li');
    // list.appendChild(li);
    user_log_refresh(item_json['Content']['user_log'], refresh);
}

function user_log_refresh(user_log, refresh){
    user_log = user_log.reverse();
    table_tbody = document.getElementById("user_log").children[1];
    if(refresh){
    var rowNum = table_tbody.rows.length;
    for (i=0;i<rowNum;i++)
    {
        table_tbody.deleteRow(0);
    }
    }
    for (index = 0; index < user_log.length; index++) {
        var record = user_log[index];
        var tr = table_tbody.insertRow(0);
        // 序号
        var td_index = document.createElement("td");
        td_index.textContent = table_tbody.rows.length;
        tr.appendChild(td_index);
        // 标题
        var td_title = document.createElement("td");
        var title_href = document.createElement("a");
        title_href.textContent = record['Title'];
        title_href.setAttribute("href", record['Link']);
        title_href.setAttribute("target", "_blank");
        td_title.appendChild(title_href);
        tr.appendChild(td_title);
        // 关键词
        var td_keywords = document.createElement("td");
        var tmp_str = JSON.stringify(record['Keywords']);
        tmp_str = tmp_str.replace(/[0-9]+/g,"");
        tmp_str = tmp_str.replace(/"/g,"");
        tmp_str = tmp_str.replace(/,/g,"，");
        tmp_str = tmp_str.replace("[","");
        tmp_str = tmp_str.replace("]","");
        td_keywords.textContent = tmp_str;
        tr.appendChild(td_keywords);
        // 时间
        var td_time = document.createElement("td");
        td_time.textContent = record['CommitTimeFormat'];
        tr.appendChild(td_time);
        //分类
        var td_classification = document.createElement("td");
        var input_classification = document.createElement("input");
        switch(record['Type']) {
            case "zhongyi":
                input_classification.value = "中医";
                break;
            case "xiyi":
                input_classification.value = "西医";
                break;
            case "notsure":
                input_classification.value = "待定";
                break;
            default:
                input_classification.value = "待定";
        }
        input_classification.setAttribute("type", "submit");
        input_classification.setAttribute("id", record['uid']);
        input_classification.setAttribute("onclick", "get_uid(this.id)");
        td_classification.appendChild(input_classification);
        tr.appendChild(td_classification);
        // 置信度
        var td_confidence = document.createElement("td");
        td_confidence.textContent = record['Confidence'];
        tr.appendChild(td_confidence);
        // 备注
        var td_note = document.createElement("td");
        td_note.textContent = record['Notes'];
        tr.appendChild(td_note);
    }
}

function sendClassification(paper_type){
    // 接收文本框输入
    // var input = document.getElementById('myInput').value.toLowerCase();
    // 向后端python POST一个请求
    var item_json = 0;
    var classification_commit_json = {"RequestType":"Classification",
        "Content":{
            "UserName":document.getElementById('UserName').value,
            "PaperUID":document.getElementById('UIDtext').value,
            "Classification":paper_type,
            "Confidence":document.getElementById('Confidence').value,
            "Notes":document.getElementById('Notes').value,
            }
    };
    fetch('http://127.0.0.1:5500/classification', {
    // fetch('http://10.168.45.117:5500/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // 这个请求的body是json的形式：{label1: value1, label2: value2}
        // body: JSON.stringify({message: input}),
        body: JSON.stringify(classification_commit_json),
        mode:'cors'
    })
    .then(response => response.json())
    .then(response => {
        item_json = response;
        console.log(item_json);
        if(item_json['FeedbackType'].includes("Error")){
            alert(item_json['Content']['Notes']);
        }
        else{
            json_to_table(item_json, false);
        }
    })
    .catch((error) => {console.error('Error:', error);});
    document.getElementById('Confidence').value = 1;
    document.getElementById('ConfidenceRoll').value = 1;
    document.getElementById('Notes').value = "";
}


document.addEventListener("keydown",keydown);
//键盘监听，注意：在非ie浏览器和非ie内核的浏览器
//参数1：表示事件，keypress:键盘向下按；参数2：表示要触发的事件
function keydown(event){
    //表示键盘监听所触发的事件，同时传递参数event
    switch(event.keyCode){
        case 37:
            if(document.getElementById('Confidence').value>=0.01){
                var tmp_conf = Number(document.getElementById('Confidence').value)*1000;
                document.getElementById('Confidence').value = (tmp_conf - 10)/1000;
                document.getElementById('ConfidenceRoll').value = document.getElementById('Confidence').value;
            }
            break;
        case 39:
            if(document.getElementById('Confidence').value<=0.99){
                var tmp_conf = Number(document.getElementById('Confidence').value)*1000;
                document.getElementById('Confidence').value = (tmp_conf + 10)/1000;
                document.getElementById('ConfidenceRoll').value = document.getElementById('Confidence').value;
            }
            break;
        case 97:
            document.getElementById('zhongyi').click();
            break;
        case 98:
            document.getElementById('xiyi').click();
            break;
        case 99:
            document.getElementById('notsure').click();
            break;
    }
}

function get_uid(uid_to_get) {
    // if(uid_to_get.isPrototypeOf("123")){
    //     tmp = uid_to_get.value;
    //     uid_to_get = tmp;
    // }
    console.log(typeof uid_to_get);
    console.log(uid_to_get);
    var uid_get_commit_json = {"RequestType":"GetUIDItem",
        "Content":{
            "UserName":document.getElementById('UserName').value,
            "PaperUID":uid_to_get
            }
    };
    fetch('http://127.0.0.1:5500/classification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(uid_get_commit_json),
        mode:'cors'
    })
    .then(response => response.json())
    .then(response => {
        item_json = response;
        console.log(item_json);
        if(item_json['FeedbackType'].includes("Error")){
            alert(item_json['Content']['Notes']);
        }
        else{
            json_to_table(item_json, false);
        }
    })
    .catch((error) => {console.error('Error:', error);});
}