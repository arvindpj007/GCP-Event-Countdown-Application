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

function login_user(){
    var username= document.getElementById('login_username').value;
    var password= document.getElementById('login_password').value;
    if(username && password)
    {
        reqJSON('POST','/loginUser',username+' '+password)
        .then(({status,data}) =>{
            if(data == '0') {
                alert('Incorrect Username or Password');
                document.location.reload();
            }
            else {
                alert('User authenticated');
                window.location.href= "/update_session";
            }
        });
    }
    else
    {
        alert('Username or Password is not entered');
    }
}

function register_user(){
    var username= document.getElementById('register_username').value;
    var password= document.getElementById('register_password').value;
    if(username && password)
    {
        reqJSON('POST','/registerUser',username+' '+password)
        .then(({status,data}) =>{
            alert('user added successfully');
            document.location.reload();
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