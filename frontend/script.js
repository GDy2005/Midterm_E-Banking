// Login function
async function login(event) {
    event.preventDefault(); // tránh reload trang

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const err = await response.json();
            alert(err.detail);
            return;
        }

        const data = await response.json();
        console.log(data); // hoặc lưu token vào localStorage
        
        window.location.href = "payment.html";

    } catch (error) {
        console.error("Error:", error);
        alert("Cannot connect to server.");
    }
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

// Get User Info to page
async function loadUserInfo() {
    const token = localStorage.getItem("token");

    if (!token) return;

    try {
        const res = await fetch("http://127.0.0.1:8000/me", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            console.error("Failed to fetch user info");
            return;
        }

        const user = await res.json();

        updateNavUser(user);

        
    } catch(err) {
        console.error(err);
    }
};

document.addEventListener("DOMContentLoaded", () => {
    loadUserInfo();
});

function updateNavUser(user) {
    const navLeft = document.querySelector(".nav-left");
    navLeft.textContent = `${user.FullName} | ${user.PhoneNumber}`;
}
