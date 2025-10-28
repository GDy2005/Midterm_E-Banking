// Login function
function login() {
    const user = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (user === "admin" && password === "1") {
        const page = document.getElementById("page-transition");
        page.classList.add("fade-out");

        setTimeout(() => {
            window.location.href = "payment.html";
        }, 600);
    } else {
        alert("Login failed");
    }

    return false;
}