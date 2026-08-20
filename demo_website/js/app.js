// Logic mô phỏng (Demo Mode) cho ứng dụng
document.addEventListener('DOMContentLoaded', () => {
    
    // Toast Notification System
    const createToastContainer = () => {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    };

    window.showToast = (message, type = 'info') => {
        const container = createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let iconHtml = '';
        if(type === 'success') iconHtml = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        else if(type === 'error') iconHtml = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
        else iconHtml = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';

        toast.innerHTML = `
            <div class="toast-icon">${iconHtml}</div>
            <div class="toast-content">${message}</div>
        `;
        
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };

    // Handling Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value.toLowerCase();
            const password = document.getElementById('password').value;
            const submitBtn = loginForm.querySelector('button[type="submit"]');

            if (!email || !password) {
                window.showToast('Vui lòng nhập đầy đủ thông tin.', 'error');
                return;
            }

            // Simulate loading
            submitBtn.textContent = 'Đang xử lý...';
            submitBtn.disabled = true;

            setTimeout(() => {
                let role = '';
                if (email.includes('admin')) {
                    role = 'admin';
                } else if (email.includes('teacher') || email.includes('gv')) {
                    role = 'teacher';
                } else {
                    role = 'student'; // Mặc định là sinh viên
                }

                localStorage.setItem('userRole', role);
                localStorage.setItem('userEmail', email);

                window.showToast(`Đăng nhập thành công với quyền ${role.toUpperCase()}`, 'success');
                
                setTimeout(() => {
                    window.location.href = `dashboard-${role}.html`;
                }, 1000);

            }, 1000); // 1s mock delay
        });
    }

    // Handling Register form submission
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const submitBtn = registerForm.querySelector('button[type="submit"]');

            if (password !== confirmPassword) {
                window.showToast('Mật khẩu xác nhận không khớp.', 'error');
                return;
            }

            submitBtn.textContent = 'Đang xử lý...';
            submitBtn.disabled = true;

            setTimeout(() => {
                window.showToast('Đăng ký tài khoản thành công! Đang chuyển hướng...', 'success');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            }, 1000);
        });
    }

    // Tab switching logic
    const sidebarLinks = document.querySelectorAll('.sidebar-nav-item[data-target]');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-target');
            if(!targetId) return;
            
            // Remove active from all sidebar links
            sidebarLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Hide all tab sections
            document.querySelectorAll('.tab-section').forEach(sec => {
                sec.classList.remove('active');
            });
            
            // Show target
            const targetSec = document.getElementById(targetId);
            if(targetSec) {
                targetSec.classList.add('active');
            }
        });
    });

    // Bind demo actions for buttons inside dashboard
    const demoButtons = document.querySelectorAll('.demo-action');
    demoButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const actionName = e.currentTarget.getAttribute('data-action') || 'Chức năng';
            
            if (actionName.includes('Chat AI')) {
                openChatModal(actionName);
            } else if (actionName.includes('Tải lên') || actionName.includes('Chọn File')) {
                openUploadModal();
            } else if (actionName.includes('Thêm người dùng mới')) {
                openAddUserModal();
            } else {
                window.showToast(`[Demo] Đã kích hoạt: ${actionName}`, 'success');
            }
        });
    });

    function createModalOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        document.body.appendChild(overlay);
        return overlay;
    }

    // Modal: Chat AI
    function openChatModal(title) {
        const overlay = createModalOverlay();
        overlay.innerHTML = `
            <div class="modal-box">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="chat-container" id="chatContainer">
                    <div class="chat-bubble chat-ai">Xin chào! Tôi là Trợ lý AI DAU. Bạn có câu hỏi gì về tài liệu này?</div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <input type="text" id="chatInput" class="form-control" placeholder="Nhập câu hỏi của bạn...">
                    <button id="sendChatBtn" class="btn btn-primary">Gửi</button>
                </div>
            </div>
        `;
        setTimeout(() => overlay.classList.add('show'), 10);

        overlay.querySelector('.close-btn').onclick = () => {
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        };

        const sendBtn = overlay.querySelector('#sendChatBtn');
        const chatInput = overlay.querySelector('#chatInput');
        const chatContainer = overlay.querySelector('#chatContainer');

        sendBtn.onclick = () => {
            const val = chatInput.value.trim();
            if(!val) return;
            
            // Add user msg
            chatContainer.innerHTML += `<div class="chat-bubble chat-user">${val}</div>`;
            chatInput.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Add AI thinking
            const thinkingId = 'think-' + Date.now();
            chatContainer.innerHTML += `<div class="chat-bubble chat-ai" id="${thinkingId}">Đang suy nghĩ...</div>`;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            setTimeout(() => {
                document.getElementById(thinkingId).textContent = 'Dựa trên nội dung tài liệu, đây là một chủ đề thú vị. (Đoạn này được tạo tự động bởi AI mô phỏng).';
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 1000);
        };
    }

    // Modal: Upload File
    function openUploadModal() {
        const overlay = createModalOverlay();
        overlay.innerHTML = `
            <div class="modal-box">
                <div class="modal-header">
                    <h3 class="modal-title">Tải lên Tài liệu mới</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="form-group">
                    <label>Tên tài liệu</label>
                    <input type="text" class="form-control" placeholder="Nhập tên tài liệu..." value="Tai_Lieu_Moi.pdf">
                </div>
                <div class="form-group">
                    <label>Chọn môn học</label>
                    <select class="form-control">
                        <option>Lịch sử Kiến trúc</option>
                        <option>Nguyên lý Thiết kế</option>
                        <option>Cấu tạo Kiến trúc</option>
                    </select>
                </div>
                <button id="startUploadBtn" class="btn btn-primary" style="width:100%;">Bắt đầu Tải lên</button>
                <div class="progress-bar-container" id="uploadProgress">
                    <div class="progress-bar" id="progressBarInner"></div>
                </div>
            </div>
        `;
        setTimeout(() => overlay.classList.add('show'), 10);

        overlay.querySelector('.close-btn').onclick = () => {
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        };

        overlay.querySelector('#startUploadBtn').onclick = function() {
            this.disabled = true;
            this.textContent = 'Đang tải lên...';
            const progress = overlay.querySelector('#uploadProgress');
            const inner = overlay.querySelector('#progressBarInner');
            progress.style.display = 'block';
            
            setTimeout(() => inner.style.width = '30%', 100);
            setTimeout(() => inner.style.width = '70%', 600);
            setTimeout(() => {
                inner.style.width = '100%';
                window.showToast('Tải lên thành công! AI đang tiến hành Ingest.', 'success');
                setTimeout(() => {
                    overlay.classList.remove('show');
                    setTimeout(() => overlay.remove(), 300);
                }, 1000);
            }, 1200);
        };
    }

    // Modal: Add User
    function openAddUserModal() {
        const overlay = createModalOverlay();
        overlay.innerHTML = `
            <div class="modal-box">
                <div class="modal-header">
                    <h3 class="modal-title">Thêm người dùng mới</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="newEmail" class="form-control" placeholder="vd: user@dau.edu.vn">
                </div>
                <div class="form-group">
                    <label>Vai trò</label>
                    <select id="newRole" class="form-control">
                        <option value="Sinh viên">Sinh viên</option>
                        <option value="Giáo viên">Giáo viên</option>
                    </select>
                </div>
                <button id="saveUserBtn" class="btn btn-primary" style="width:100%;">Lưu Người dùng</button>
            </div>
        `;
        setTimeout(() => overlay.classList.add('show'), 10);

        overlay.querySelector('.close-btn').onclick = () => {
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        };

        overlay.querySelector('#saveUserBtn').onclick = () => {
            const email = overlay.querySelector('#newEmail').value;
            const role = overlay.querySelector('#newRole').value;
            if(!email) {
                window.showToast('Vui lòng nhập email!', 'error');
                return;
            }

            const tbody = document.getElementById('user-table-body');
            if(tbody) {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #f1f5f9';
                tr.innerHTML = `
                    <td style="padding: 16px 12px; font-weight: 500;">${email}</td>
                    <td style="padding: 16px 12px;">
                        <span style="background-color: #f1f5f9; color: #475569; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">${role}</span>
                    </td>
                    <td style="padding: 16px 12px;">
                        <span style="color: #10b981; font-weight: 500;">● Active</span>
                    </td>
                    <td style="padding: 16px 12px; text-align: right;">
                        <button class="btn btn-outline demo-action" style="padding: 4px 10px; font-size: 0.8rem;">Khóa</button>
                    </td>
                `;
                tbody.insertBefore(tr, tbody.firstChild);
            }
            
            window.showToast('Đã thêm người dùng thành công!', 'success');
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        };
    }
    
    // Load User info on dashboard
    const userRoleEl = document.getElementById('userRoleName');
    const userEmailEl = document.getElementById('userEmailDisplay');
    if(userRoleEl || userEmailEl) {
        const role = localStorage.getItem('userRole') || 'Khách';
        const email = localStorage.getItem('userEmail') || 'guest@dau.edu.vn';
        
        let roleName = 'Sinh viên';
        if (role === 'admin') roleName = 'Quản trị viên (Admin)';
        if (role === 'teacher') roleName = 'Giáo viên';
        
        if (userRoleEl) userRoleEl.textContent = roleName;
        if (userEmailEl) userEmailEl.textContent = email;
    }
    
    // Logout handling
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.clear();
            window.showToast('Đã đăng xuất', 'info');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 800);
        });
    }
});
