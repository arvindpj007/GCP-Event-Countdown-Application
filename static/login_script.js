function register_form() {
    document.getElementById('login-form').style.display="none";
    document.getElementById('register-form').style.display="initial";
}

function login_form() {
    document.getElementById('login-form').style.display="initial";
    document.getElementById('register-form').style.display="none";
}


document.addEventListener('DOMContentLoaded',() => {
    document.getElementById('login-form').style.display="initial";
    document.getElementById('register-form').style.display="none";
});