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
// Change Page function
const navItems = document.querySelectorAll('.nav-item[data-target]');
const sections = document.querySelectorAll('#payment-page, #transaction-page, #invest-page');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        // Bỏ active khỏi tất cả
        navItems.forEach(i => i.classList.remove('active'));

        // Thêm active vào item được click
        item.classList.add('active');

        // Ẩn tất cả section
        sections.forEach(sec => sec.classList.add('hidden'));

        // Hiện section tương ứng
        const target = item.getAttribute('data-target');
        if (target) {
            document.getElementById(target).classList.remove('hidden');
        }
    });
});
