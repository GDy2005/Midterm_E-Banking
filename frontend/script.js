// Login function
async function login(event) {
    event.preventDefault(); // tránh reload trang

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
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

        localStorage.setItem("token", data.access_token);
        
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
        const res = await fetch("http://127.0.0.1:8000/userinfo", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) {
            console.error("Failed to fetch user info");
            return;
        }

        const user = await res.json(); 

        // nav-left
        const navLeft = document.querySelector(".nav-left");
        if (navLeft && user) {
            navLeft.innerHTML = `
                <div class="fullname">${user.UserName}</div>
                <div class="phone">${user.PhoneNumber}</div>
            `;
        }

        //div left
        const userBox = document.querySelector(".userInfo-box");
        if (userBox && user) {
            const maskedBalance = "*********";
            userBox.innerHTML = `
                <h2>User Infomation</h2>
                <div class="userinfo-box">
                <div class="title-div-left">Full Name:</div>
                <div class="details-div-left">${user.FullName}</div>

                <div class="title-div-left">Email: </div>
                <div class="details-div-left">${user.Email}</div>

                <div class="title-div-left">Phone: </div>
                <div class="details-div-left">${user.PhoneNumber}</div>

                <div class="balance-row">
                    <div class="title-div-left">Balance: 
                        <button id="toggleBalanceBtn">Show</button>
                    </div>
                    <div class="details-div-left balance-div">
                        <span class="balance-value">${maskedBalance}</span>
                    </div>
                </div>
                </div>
            `;
            
            // Show/Hide Balance Button
            const balanceSpan = userBox.querySelector(".balance-value");
            const toggleBtn = userBox.querySelector("#toggleBalanceBtn");

            let isShown = false;
            toggleBtn.addEventListener("click", () => {
                if (!isShown) {
                    balanceSpan.textContent = user.Balance;
                    toggleBtn.textContent = "Hide";
                    isShown = true;
                } else {
                    balanceSpan.textContent = maskedBalance;
                    toggleBtn.textContent = "Show";
                    isShown = false;
                }
            });
        }

    } catch(err) {
        console.error(err);
    }
}

document.addEventListener("DOMContentLoaded", loadUserInfo);

//Update Infomation 
async function Autofill_StudentInfo() {
    const student_id = document.getElementById("student_id").value.trim();

    if (!student_id) {
        document.getElementById("student_name").value = "";
        document.getElementById("studentinfo-id").innerText = "---";
        document.getElementById("studentinfo-name").innerText = "---";
        document.getElementById("studentinfo-email").innerText = "---";
        return;
    }

    try {
        const res_student = await fetch(`http://127.0.0.1:8000/studentinfo?student_id=${student_id}`, {
            method: "GET"
        });

        if (!res_student.ok) throw new Error("Failed to fetch student info");

        const student = await res_student.json();

        document.getElementById("student_name").value = student.FullName || "";
        document.getElementById("studentinfo-id").innerText = student.StudentID || "";
        document.getElementById("studentinfo-name").innerText = student.FullName || "";
        document.getElementById("studentinfo-email").innerText = student.Email || "";

    } catch (err) {
        console.error(err);
        document.getElementById("student_name").value = "";
        document.getElementById("studentinfo-id").innerText = "---";
        document.getElementById("studentinfo-name").innerText = "---";
        document.getElementById("studentinfo-email").innerText = "---";
    }
}

async function Autofill_TuitionInfo() {
    const student_id = document.getElementById("student_id").value.trim();
    const semester = document.getElementById("semester").value.trim();
    const token = localStorage.getItem("token");

    if (!student_id || !semester) {
        document.getElementById("show-fee").value = "";
        document.getElementById("tuitioninfo-id").innerText = "---";
        document.getElementById("tuitioninfo-semester").innerText = "---";
        document.getElementById("tuitioninfo-start").innerText = "---";
        document.getElementById("tuitioninfo-end").innerText = "---";
        document.getElementById("tuitioninfo-fee").innerText = "---";
        return;
    }

    if (!token) {
        alert("Please log in first.");
        return;
    }

    try {
        const res_tuition = await fetch(`http://127.0.0.1:8000/tuitioninfo?student_id=${student_id}&semester=${semester}`, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        }
    );

        if (!res_tuition.ok) {
            const err = await res_tuition.json();
            throw new Error(err.detail || "Failed to fetch tuition info");
        }

        const tuitioninfo = await res_tuition.json();

        document.getElementById("show-fee").value = tuitioninfo.Fee || "";
        document.getElementById("tuitioninfo-id").innerText = tuitioninfo.TuitionID || "";
        document.getElementById("tuitioninfo-semester").innerText = tuitioninfo.Semester || "";
        document.getElementById("tuitioninfo-start").innerText = tuitioninfo.BeginDate || "";
        document.getElementById("tuitioninfo-end").innerText = tuitioninfo.EndDate || "";
        document.getElementById("tuitioninfo-fee").innerText = tuitioninfo.Fee || "";

    } catch (err) {
        console.error(err);
        document.getElementById("show-fee").value = "";
        document.getElementById("tuitioninfo-id").innerText = "---";
        document.getElementById("tuitioninfo-semester").innerText = "---";
        document.getElementById("tuitioninfo-start").innerText = "---";
        document.getElementById("tuitioninfo-end").innerText = "---";
        document.getElementById("tuitioninfo-fee").innerText = "---";
    }
}