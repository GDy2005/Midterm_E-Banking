// Login function
function login() {
    const user = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (user == "admin" && password == "1") {
        window.location.href = "payment.html"
    } else {
        alert("Login failed")
    }

    return false;
}