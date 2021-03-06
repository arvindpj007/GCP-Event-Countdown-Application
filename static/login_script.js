function reqJSON(method, url, data) {
  return new Promise((resolve, reject) => {
    let xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.responseType = 'json';
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve({status: xhr.status, data: xhr.response});
      } else {
        reject({status: xhr.status, data: xhr.response});
      }
    };
    xhr.onerror = () => {
      reject({status: xhr.status, data: xhr.response});
    };
    xhr.send(data);
  });
}

function register_form() {
    document.getElementById('login-form').style.display="none";
    document.getElementById('register_username').value= "";
    document.getElementById('register_password').value= "";
    document.getElementById('register-form').style.display="initial";
}

function login_form() {
    document.getElementById('login-form').style.display="initial";
    document.getElementById('login_username').value= "";
    document.getElementById('login_password').value= "";
    document.getElementById('register-form').style.display="none";
}

async function post_loginUser(username,password) {
    return await reqJSON('POST','/loginUser',username+' '+password);
}

function login_user(){
    var username= document.getElementById('login_username').value;
    var password= document.getElementById('login_password').value;
    if(username && password)
    {
        post_loginUser(username,password)
        .then(({status,data}) =>{
            if(data == '0') {
                alert('Incorrect Username or Password');
                document.location.reload();
            }
            else {
                alert('User authenticated');
                window.location.href= '/';
            }
        });
    }
    else
    {
        alert('Username or Password is not entered');
    }
}

async function post_registerUser(username,password) {
    return await reqJSON('POST','/registerUser',username+' '+password);
}

function register_user(){
    var username= document.getElementById('register_username').value;
    var password= document.getElementById('register_password').value;
    if(username && password)
    {
        post_registerUser(username,password)
        .then(({status,data}) =>{
            alert('user added successfully');
             window.location.href= '/';
        });
    }
    else
    {
        alert('Username or Password is not entered');
    }
}


document.addEventListener('DOMContentLoaded',() => {
    document.getElementById('login-form').style.display="initial";
    document.getElementById('register-form').style.display="none";
});

function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}

document.addEventListener('DOMContentLoaded', ()=>{
   var state = getCookie('state');
   var nonce = getCookie('nonce');
   var clientid = "145521786032-soglnbfd91ivkn97t9uou964p0di6ldb.apps.googleusercontent.com";
   var url = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=" +
        clientid +
       "&scope=openid%20email&state=" +
       state +
       "&nonce=" +
       nonce +
       "&redirect_uri=https%3A//" +
       "countdown-252800.appspot.com/oidauth";
   document.getElementById('g_login').href = url;
   document.getElementById('g_register').href = url;
});