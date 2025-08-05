

function navigationClick(event) {
    const headerLinks = document.querySelectorAll('div.header ul li');
    headerLinks.forEach( (e, i) => {
        if(e.querySelector('a')) {
            e.querySelector('a').classList.remove('active');
        }
    })
    event.srcElement.classList.add('active');
}

const MediaType = {
    KME: 1,
    Live: 201,
};

function setCurrentUser(userInfo) {
    window.sessionStorage.setItem('user-info', JSON.stringify(userInfo));
}

function getCurrentUser() {
    const userInfo = window.sessionStorage.getItem('user-info');
    if(userInfo) {
        const userInfoObj = JSON.parse(userInfo);
        return userInfoObj;
    }
}

async function fetchHelper(url, method, body) {
    const startTime = Date.now();
    const headers = {}
    if(method === 'POST') {
        headers['Content-Type'] = 'application/json';
    }
    var data = await fetch(url, {
        method,
        body,
        headers
    });
    const xhrMessages = data.headers.get('x-xhr-messages');
    const xhrTime = Date.now() - startTime;
    const result = await data.json();

    writeXhrLogs(url, xhrMessages, xhrTime);
    return { response: data, body: result }
}

function writeXhrLogs(callUri, data, xhrTime) {
    const uri = callUri.substring(window.location.origin.length);
    console.log(data);
    if(!data) {
        return;
    }
    const container = window.top.document.getElementById('xhrlog');
    container.innerHTML += `<div class="table-single-cell-row">${uri} / ${xhrTime}ms</div>`;
    let arr = JSON.parse(data);
    
    for(let i in arr) {
        let objectStatus = '';
        if(arr[i].isCached) {
            objectStatus = "cached";
        } else if (arr[i].isFetched) {
            objectStatus = "fetched";
        } else if (arr[i].isCreated) {
            objectStatus = "created";
        }
        const msg = (arr[i].msg && arr[i].msg !== undefined)? arr[i].msg: '';
        var row = `<div class="table-row"><div class="cell">${arr[i].objectType}</div>`;
        row += `<div class="cell">${objectStatus}</div><div class="cell">${msg}</div>`;
        container.innerHTML += row;
    }
}

function onLoad() {
    return;
    const formInfoStr = window.sessionStorage.getItem('cnc-demo-app-form-values');
    if(formInfoStr) {
        const formInfo = JSON.parse(formInfoStr);
        if(formInfo) {
            for(let key in formInfo) {
                document.getElementById(key).value = formInfo[key];
                if(key === 'setAsModerator') {
                    document.getElementById(key).checked = formInfo[key];
                }
            }
        }
    }
}
onLoad();