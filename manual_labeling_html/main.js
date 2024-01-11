function item_refresh() {
    // 接收文本框输入
    // var input = document.getElementById('myInput').value.toLowerCase();
    // 向后端python POST一个请求
    var item_json = 0;
    fetch('http://127.0.0.1:5500/classification', {
    // fetch('http://10.168.45.117:5500/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // 这个请求的body是json的形式：{label1: value1, label2: value2}
        // body: JSON.stringify({message: input}),
        body: JSON.stringify({"RequestType":"Start","Content":{}}),
        mode:'cors'
    })
    .then(response => response.json())
    .then(response => {
        item_json = response
        console.log(item_json);
        json_to_table(item_json)
    })
    .catch((error) => {console.error('Error:', error);});
}

function json_to_table(item_json){
    // 把信息打印在创建的列表里
    var tmp_str = JSON.stringify(item_json['Content']['UID']);
    tmp_td = document.getElementById('UID');
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Title');
    var tmp_str = JSON.stringify(item_json['Content']['Title']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Abstract');
    var tmp_str = JSON.stringify(item_json['Content']['Abstract']);
    tmp_td.textContent = "\t" + tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Keywords');
    var tmp_str = JSON.stringify(item_json['Content']['Keywords']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Journal');
    var tmp_str = JSON.stringify(item_json['Content']['Journal']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Authors');
    var tmp_str = JSON.stringify(item_json['Content']['Authors']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Affiliations');
    var tmp_str = JSON.stringify(item_json['Content']['Affiliations']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);

    tmp_td = document.getElementById('Year');
    var tmp_str = JSON.stringify(item_json['Content']['Year']);
    // tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);
    tmp_td.textContent = tmp_str;

    tmp_td = document.getElementById('paperLink');
    var tmp_str = JSON.stringify(item_json['Content']['Link']);
    tmp_td.textContent = tmp_str.substring(1, tmp_str.length-1);
    // tmp_td = document.getElementById('Link');
    tmp_td.setAttribute("href", tmp_str.substring(1, tmp_str.length-1))
    // const li = document.createElement('li');
    // list.appendChild(li);
}

function sendClassification(){
    // 接收文本框输入
    // var input = document.getElementById('myInput').value.toLowerCase();
    // 向后端python POST一个请求
    var item_json = 0;
    var classification_commit_json = {"RequestType":"Classification",
        "Content":{
            "UserName":document.getElementById('UserName').value,
            "PaperUID":document.getElementById('UID').textContent,
            "Classification":document.getElementById('zhongyi').value,
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
        item_json = response
        console.log(item_json);
        json_to_table(item_json);
    })
    .catch((error) => {console.error('Error:', error);});
}