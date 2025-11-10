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
    async function Autofill() {
        const student_id = document.getElementById("student_id").value.trim();
        const semester = document.getElementById("semester").value.trim();
        const token = localStorage.getItem("token");

        if (student_id && !semester) {
            document.getElementById("show-fee").value = "";
            document.getElementById("tuitioninfo-id").innerText = "---";
            document.getElementById("tuitioninfo-semester").innerText = "---";
            document.getElementById("tuitioninfo-start").innerText = "---";
            document.getElementById("tuitioninfo-end").innerText = "---";
            document.getElementById("tuitioninfo-fee").innerText = "---";
        }

        if (!student_id) {
            document.getElementById("student_name").value = "";
            document.getElementById("studentinfo-id").innerText = "---";
            document.getElementById("studentinfo-name").innerText = "---";
            document.getElementById("studentinfo-email").innerText = "---";
        }

        if (!semester) {
            document.getElementById("show-fee").value = "";
            document.getElementById("tuitioninfo-id").innerText = "---";
            document.getElementById("tuitioninfo-semester").innerText = "---";
            document.getElementById("tuitioninfo-start").innerText = "---";
            document.getElementById("tuitioninfo-end").innerText = "---";
            document.getElementById("tuitioninfo-fee").innerText = "---";
        }

        if (!token) {
            alert("Please log in first.");
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

        try {
            const res_tuition = await fetch(`http://127.0.0.1:8000/tuitioninfo?student_id=${student_id}&semester=${semester}`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });

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


// --------- OTP ---------

document.addEventListener("DOMContentLoaded", () => {
  const confirmBtnPage = document.querySelector('.confirm-btn'); // nút Confirm ở payment page
  const otpPopup = document.getElementById('otpPopup'); // popup container
  const closeOtpBtn = document.getElementById('closeOtpBtn');
  const confirmOtpBtn = document.getElementById('confirmOtpBtn');

  // Nếu popup chưa có, dừng (an toàn)
  if (!otpPopup) return;

  // Helper: show / hide popup
  function openOtpPopup() {
    otpPopup.classList.add('visible');
    // xóa input cũ
    const inputs = otpPopup.querySelectorAll('.otp-inputs input');
    inputs.forEach(i => i.value = '');
    // focus ô đầu tiên (delay nhỏ để element render)
    setTimeout(() => { if (inputs[0]) inputs[0].focus(); }, 50);
  }
  function closeOtpPopup() {
    otpPopup.classList.remove('visible');
  }

  // Nút Confirm ở page => mở popup
  if (confirmBtnPage) {
    confirmBtnPage.addEventListener('click', (e) => {
    console.log("Confirm button clicked");
      e.preventDefault && e.preventDefault();
      // (tại đây bạn có thể kiểm tra dữ liệu trước khi mở popup)
      openOtpPopup();
    });
  }

  // Cancel trong popup
  if (closeOtpBtn) {
    closeOtpBtn.addEventListener('click', (e) => {
    e.preventDefault();
    closeOtpPopup();
    });

  }

  // Confirm trong popup
  if (confirmOtpBtn) {
    confirmOtpBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const inputs = otpPopup.querySelectorAll('.otp-inputs input');
      const otpCode = Array.from(inputs).map(i => i.value.trim()).join('');
      if (otpCode.length < inputs.length) {
        alert("Vui lòng nhập đủ 6 chữ số OTP!");
        return;
      }

      // TODO: gọi API verify OTP nếu cần (ví dụ fetch('/verify', {method:'POST', body:...}))
      // Hiện tạm alert rồi đóng popup
      alert(`Mã OTP của bạn: ${otpCode}`);
      closeOtpPopup();
    });
  }

  // --- Scoping behavior cho các ô input (paste, auto focus, backspace, arrow) ---
  const inputs = otpPopup.querySelectorAll('.otp-inputs input');
  inputs.forEach((input, index) => {
    // chỉ cho nhập số
    input.addEventListener('input', (e) => {
      let value = e.target.value.replace(/[^0-9]/g, '');
      e.target.value = value;

      // nếu paste/nhập nhiều ký tự
      if (value.length > 1) {
        const chars = value.split('');
        inputs[index].value = chars[0];
        for (let i = 1; i < chars.length && index + i < inputs.length; i++) {
          inputs[index + i].value = chars[i];
        }
        const nextIndex = index + Math.min(chars.length, inputs.length - index);
        if (nextIndex < inputs.length) inputs[nextIndex].focus();
        return;
      }

      if (value.length === 1 && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === "Backspace" && !input.value && index > 0) {
        inputs[index - 1].focus();
      }
    });

    input.addEventListener('keyup', (e) => {
      if (e.key === "ArrowLeft" && index > 0) inputs[index - 1].focus();
      if (e.key === "ArrowRight" && index < inputs.length - 1) inputs[index + 1].focus();
    });

    input.addEventListener('paste', (e) => {
      e.preventDefault();
      const pasteData = e.clipboardData.getData("text").replace(/[^0-9]/g, "");
      const chars = pasteData.split('');
      for (let i = 0; i < inputs.length; i++) {
        inputs[i].value = chars[i] || "";
      }
      const lastFilled = Math.min(chars.length, inputs.length) - 1;
      if (lastFilled >= 0) inputs[lastFilled].focus();
    });
  });

  // đóng popup khi click ra ngoài hộp (tuỳ chọn)
  otpPopup.addEventListener('click', (e) => {
    if (e.target === otpPopup) closeOtpPopup();
  });
});