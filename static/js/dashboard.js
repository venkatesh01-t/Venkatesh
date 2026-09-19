// ==============================================================================
// VENTKATESH BABU — INTERACTIVE PORTFOLIO DASHBOARD CONTROLLER
// ==============================================================================

let currentFilter = 'all';
let searchQuery = '';
let messages = [];
let activeMessage = null;
let searchDebounceTimer = null;
let trajectoryChartInstance = null;
let topicsChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchMessages();
    initAnalyticsCharts();
});

// ==============================================================================
// 1. DATA FETCHING & RENDERING
// ==============================================================================

async function fetchMessages(keepSelectionId = null) {
    const listEl = document.getElementById('messagesList');
    try {
        const url = `${API_MESSAGES_URL}?q=${encodeURIComponent(searchQuery)}&filter=${currentFilter}`;
        const res = await fetch(url);
        const data = await res.json();

        if (data.success) {
            messages = data.messages;
            renderMessagesList(messages);

            // Maintain selection or select first
            if (keepSelectionId) {
                const stillExists = messages.find(m => m.id === keepSelectionId);
                if (stillExists) {
                    selectMessage(stillExists.id, false);
                } else if (messages.length > 0) {
                    selectMessage(messages[0].id, false);
                } else {
                    deselectMessage();
                }
            } else if (messages.length > 0 && !activeMessage) {
                selectMessage(messages[0].id, false);
            } else if (messages.length === 0) {
                deselectMessage();
            }
        }
    } catch (err) {
        console.error("Failed to load messages:", err);
        listEl.innerHTML = `<div class="p-8 text-center text-rose-400 text-xs">Failed to load messages. Please check server.</div>`;
    }
}

function renderMessagesList(msgList) {
    const listEl = document.getElementById('messagesList');

    if (!msgList || msgList.length === 0) {
        listEl.innerHTML = `
            <div class="p-12 text-center text-slate-500 text-xs flex flex-col items-center gap-2">
                <i class="fas fa-inbox text-3xl text-slate-600 mb-1"></i>
                <span class="font-medium text-slate-400">No inquiries found</span>
                <span class="text-[11px] text-slate-500">Try adjusting search or filter parameters.</span>
            </div>
        `;
        return;
    }

    listEl.innerHTML = msgList.map(m => {
        const isSelected = activeMessage && activeMessage.id === m.id;
        const initials = getInitials(m.name);
        const unreadDot = !m.is_read ? `<span class="w-2 h-2 rounded-full bg-teal-400 flex-shrink-0 animate-pulse"></span>` : '';
        const starIcon = m.is_starred ? 'fas fa-star text-amber-400' : 'far fa-star text-slate-600 hover:text-amber-400';
        const repliedBadge = m.replied ? `<span class="text-[10px] text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded font-mono">Replied</span>` : '';

        return `
            <div onclick="selectMessage(${m.id})" class="p-4 cursor-pointer transition-all flex items-start gap-3 relative group hover:bg-slate-900/60 ${isSelected ? 'msg-selected' : ''}" id="msg-card-${m.id}">
                <!-- Sender Initials Avatar -->
                <div class="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700/60 text-teal-400 font-bold text-xs flex items-center justify-center flex-shrink-0">
                    ${initials}
                </div>

                <!-- Message Snippet -->
                <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between gap-1 mb-1">
                        <div class="flex items-center gap-1.5 truncate">
                            ${unreadDot}
                            <span class="font-bold text-xs ${!m.is_read ? 'text-white' : 'text-slate-300'} truncate">${escapeHtml(m.name)}</span>
                        </div>
                        <span class="text-[10px] font-mono text-slate-500 flex-shrink-0">${m.relative_time}</span>
                    </div>

                    <p class="text-xs font-semibold text-slate-200 truncate mb-1">${escapeHtml(m.subject)}</p>
                    <p class="text-[11px] text-slate-400 line-clamp-1">${escapeHtml(m.message)}</p>

                    <div class="flex items-center justify-between mt-2 pt-1">
                        <div class="flex items-center gap-1.5">
                            ${repliedBadge}
                        </div>
                        <!-- Star button -->
                        <button onclick="event.stopPropagation(); toggleStarInline(${m.id})" class="p-1 text-xs transition-transform active:scale-125" title="Star inquiry">
                            <i class="${starIcon}"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function selectMessage(id, markAsReadImmediately = true) {
    const msg = messages.find(m => m.id === id);
    if (!msg) return;

    activeMessage = msg;

    // Update selected class in DOM
    document.querySelectorAll('[id^="msg-card-"]').forEach(el => el.classList.remove('msg-selected'));
    const activeEl = document.getElementById(`msg-card-${id}`);
    if (activeEl) activeEl.classList.add('msg-selected');

    // Switch view panes
    document.getElementById('emptyDetailState').classList.add('hidden');
    document.getElementById('activeDetailState').classList.remove('hidden');

    // Populate Right Pane Details
    document.getElementById('detailAvatar').innerText = getInitials(msg.name);
    document.getElementById('detailName').innerText = msg.name;
    const emailLink = document.getElementById('detailEmail');
    emailLink.innerText = msg.email;
    emailLink.href = `mailto:${msg.email}`;
    document.getElementById('detailDate').innerText = `${msg.date_formatted} • ${msg.time_formatted}`;
    document.getElementById('detailIp').innerText = msg.ip_address;
    document.getElementById('detailDevice').innerText = formatUserAgent(msg.user_agent);
    document.getElementById('detailSubject').innerText = msg.subject;
    document.getElementById('detailMessage').innerText = msg.message;

    // Status Badges
    const statusBadge = document.getElementById('detailStatusBadge');
    if (!msg.is_read) {
        statusBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30";
        statusBadge.innerText = "New";
    } else if (msg.replied) {
        statusBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30";
        statusBadge.innerText = "Replied";
    } else {
        statusBadge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700";
        statusBadge.innerText = "Read";
    }

    // Toggle Buttons
    const textToggle = document.getElementById('textToggleRead');
    textToggle.innerText = msg.is_read ? 'Mark Unread' : 'Mark Read';

    const starIcon = document.getElementById('iconToggleStar');
    starIcon.className = msg.is_starred ? 'fas fa-star text-amber-400' : 'far fa-star text-slate-400';

    // Previous Reply History
    const prevReplyBox = document.getElementById('previousReplyBox');
    if (msg.replied && msg.reply_content) {
        prevReplyBox.classList.remove('hidden');
        document.getElementById('prevReplyDate').innerText = msg.replied_at || '';
        document.getElementById('prevReplySubject').innerText = msg.reply_subject || 'Reply';
        document.getElementById('prevReplyContent').innerText = msg.reply_content;
    } else {
        prevReplyBox.classList.add('hidden');
    }

    // Pre-fill Reply Composer
    document.getElementById('replySubject').value = msg.subject.toLowerCase().startsWith('re:') ? msg.subject : `Re: ${msg.subject}`;
    document.getElementById('replyBody').value = '';
    document.getElementById('replyStatusMsg').innerText = '';

    // Auto mark as read if new
    if (!msg.is_read && markAsReadImmediately) {
        toggleStatus(msg.id, 'toggle_read', false);
    }
}

function deselectMessage() {
    activeMessage = null;
    document.getElementById('emptyDetailState').classList.remove('hidden');
    document.getElementById('activeDetailState').classList.add('hidden');
}

// ==============================================================================
// 2. SEARCH & FILTER CONTROLS
// ==============================================================================

function setFilter(filterName, btn) {
    currentFilter = filterName;
    document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('tab-active');
        b.classList.add('text-slate-400');
    });
    btn.classList.add('tab-active');
    btn.classList.remove('text-slate-400');
    fetchMessages();
}

function debounceSearch() {
    clearTimeout(searchDebounceTimer);
    const val = document.getElementById('searchInput').value.trim();
    const clearBtn = document.getElementById('clearSearchBtn');
    
    if (val) {
        clearBtn.classList.remove('hidden');
    } else {
        clearBtn.classList.add('hidden');
    }

    searchDebounceTimer = setTimeout(() => {
        searchQuery = val;
        fetchMessages();
    }, 280);
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('clearSearchBtn').classList.add('hidden');
    searchQuery = '';
    fetchMessages();
}

// ==============================================================================
// 3. STATUS ACTIONS & AJAX MUTATIONS
// ==============================================================================

async function toggleStatus(id, action, refreshList = true) {
    try {
        const res = await fetch(API_TOGGLE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({ id: id, action: action })
        });
        const data = await res.json();

        if (data.success) {
            // Update local memory
            const m = messages.find(item => item.id === id);
            if (m) {
                if (action === 'toggle_read') {
                    m.is_read = data.is_read;
                    updateKpiBadge('unread', data.is_read ? -1 : 1);
                } else if (action === 'toggle_star') {
                    m.is_starred = data.is_starred;
                    updateKpiBadge('starred', data.is_starred ? 1 : -1);
                } else if (action === 'toggle_replied') {
                    m.replied = data.replied;
                    updateKpiBadge('replied', data.replied ? 1 : -1);
                } else if (action === 'delete') {
                    messages = messages.filter(item => item.id !== id);
                    showToast('Message deleted.', true);
                    fetchMessages();
                    return;
                }
            }

            if (refreshList) {
                renderMessagesList(messages);
                if (activeMessage && activeMessage.id === id) {
                    selectMessage(id, false);
                }
            }
        }
    } catch (err) {
        console.error("Action failed:", err);
        showToast('Action failed. Try again.', false);
    }
}

function toggleActiveRead() {
    if (!activeMessage) return;
    toggleStatus(activeMessage.id, 'toggle_read', true);
}

function toggleActiveStar() {
    if (!activeMessage) return;
    toggleStatus(activeMessage.id, 'toggle_star', true);
}

function toggleStarInline(id) {
    toggleStatus(id, 'toggle_star', true);
}

function deleteActiveMessage() {
    if (!activeMessage) return;
    if (confirm(`Are you sure you want to delete message from "${activeMessage.name}"?`)) {
        toggleStatus(activeMessage.id, 'delete', true);
    }
}

// ==============================================================================
// 4. DIRECT EMAIL REPLY COMPOSER (GOOGLE SMTP)
// ==============================================================================

async function sendDirectReply() {
    if (!activeMessage) return;

    const subject = document.getElementById('replySubject').value.trim();
    const replyBody = document.getElementById('replyBody').value.trim();
    const btn = document.getElementById('btnSendReply');
    const statusMsg = document.getElementById('replyStatusMsg');

    if (!subject || !replyBody) {
        showToast('Subject and message content cannot be empty.', false);
        return;
    }

    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin text-xs"></i> <span>Sending...</span>`;
    statusMsg.className = "text-xs font-semibold text-teal-400 flex items-center gap-1.5";
    statusMsg.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Dispatching via Google SMTP...`;

    try {
        const res = await fetch(API_REPLY_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({
                message_id: activeMessage.id,
                subject: subject,
                reply_body: replyBody
            })
        });

        const data = await res.json();

        if (res.ok && data.success) {
            showToast(`Email delivered to ${activeMessage.email}!`, true);
            statusMsg.className = "text-xs font-semibold text-emerald-400";
            statusMsg.innerText = "Reply sent successfully!";

            // Update local state
            activeMessage.replied = true;
            activeMessage.is_read = true;
            activeMessage.reply_subject = subject;
            activeMessage.reply_content = replyBody;
            activeMessage.replied_at = "Just now";

            updateKpiBadge('replied', 1);
            renderMessagesList(messages);
            selectMessage(activeMessage.id, false);

            document.getElementById('replyBody').value = '';
        } else {
            statusMsg.className = "text-xs font-semibold text-rose-400";
            statusMsg.innerText = data.error || "Failed to send email.";
            showToast(data.error || "Delivery failed.", false);
        }
    } catch (err) {
        console.error("Reply error:", err);
        statusMsg.className = "text-xs font-semibold text-rose-400";
        statusMsg.innerText = "Network error while sending email.";
        showToast("Error connecting to server.", false);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>Send Reply</span> <i class="fas fa-paper-plane text-[10px]"></i>`;
    }
}

function applyCannedTemplate(selectEl) {
    if (!activeMessage) return;
    const val = selectEl.value;
    const bodyEl = document.getElementById('replyBody');
    const sender = activeMessage.name.split(' ')[0] || activeMessage.name;

    const templates = {
        consultation: `Hi ${sender},\n\nThank you for reaching out! I would love to discuss your requirements in more detail.\n\nCould you please let me know your availability for a brief 15-minute consultation call or Google Meet this week?\n\nLooking forward to speaking with you!\n\nBest regards,\nVenkatesh Babu`,
        proposal: `Hi ${sender},\n\nThank you for reaching out regarding "${activeMessage.subject}".\n\nI have reviewed your inquiry and have experience building similar high-performance Python, automation, and API systems. I am excited to collaborate on this project.\n\nPlease feel free to share any additional specifications or documentation so I can prepare a structured project roadmap.\n\nBest regards,\nVenkatesh Babu`,
        general: `Hi ${sender},\n\nThank you for getting in touch! I have received your message regarding "${activeMessage.subject}".\n\nI am currently reviewing the details and will provide a comprehensive response shortly.\n\nBest regards,\nVenkatesh Babu`
    };

    if (templates[val]) {
        bodyEl.value = templates[val];
    }
    selectEl.value = "";
}

// ==============================================================================
// 5. GOOGLE SMTP HEALTH CHECK
// ==============================================================================

async function testSmtpConnection() {
    showToast('Testing Google SMTP connection...', true);
    try {
        const res = await fetch(API_SMTP_TEST_URL);
        const data = await res.json();
        if (data.success) {
            showToast(data.message, true);
        } else {
            showToast(data.error, false);
        }
    } catch (e) {
        showToast('SMTP Test Error: ' + e.message, false);
    }
}

// ==============================================================================
// 6. CHART.JS ANALYTICS INITIALIZATION
// ==============================================================================

async function initAnalyticsCharts() {
    try {
        const res = await fetch(API_ANALYTICS_URL);
        const data = await res.json();

        if (!data.success) return;

        // 1. Inquiries Velocity (Area Gradient Line Chart)
        const ctxTrend = document.getElementById('trajectoryChart');
        if (ctxTrend) {
            const labels = data.trend.map(d => d.label);
            const counts = data.trend.map(d => d.count);

            const gradient = ctxTrend.getContext('2d').createLinearGradient(0, 0, 0, 220);
            gradient.addColorStop(0, 'rgba(20, 184, 166, 0.45)');
            gradient.addColorStop(1, 'rgba(20, 184, 166, 0.0)');

            if (trajectoryChartInstance) trajectoryChartInstance.destroy();

            trajectoryChartInstance = new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Inquiries',
                        data: counts,
                        borderColor: '#14b8a6',
                        borderWidth: 2.5,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#14b8a6',
                        pointHoverRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#0f172a',
                            borderColor: '#334155',
                            borderWidth: 1,
                            padding: 10,
                            titleColor: '#94a3b8',
                            bodyColor: '#f8fafc',
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#64748b', font: { size: 11 } }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1, color: '#64748b', font: { size: 11 } },
                            grid: { color: 'rgba(51, 65, 85, 0.25)' }
                        }
                    }
                }
            });
        }

        // 2. Topics Donut Chart
        const ctxTopics = document.getElementById('topicsChart');
        if (ctxTopics) {
            if (topicsChartInstance) topicsChartInstance.destroy();

            topicsChartInstance = new Chart(ctxTopics, {
                type: 'doughnut',
                data: {
                    labels: data.topics.labels,
                    datasets: [{
                        data: data.topics.data,
                        backgroundColor: [
                            '#14b8a6', // Teal
                            '#8b5cf6', // Purple
                            '#06b6d4', // Cyan
                            '#f59e0b', // Amber
                            '#64748b', // Slate
                        ],
                        borderWidth: 2,
                        borderColor: '#0f172a',
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '72%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 10,
                                padding: 8,
                                color: '#94a3b8',
                                font: { size: 10 }
                            }
                        }
                    }
                }
            });
        }
    } catch (err) {
        console.error("Failed to load analytics charts:", err);
    }
}

// ==============================================================================
// 7. UTILITY HELPERS
// ==============================================================================

function getInitials(name) {
    if (!name) return '??';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function formatUserAgent(ua) {
    if (!ua) return 'Unknown Client';
    if (ua.includes('Chrome')) return 'Chrome / Desktop';
    if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Safari / Apple';
    if (ua.includes('Firefox')) return 'Firefox';
    if (ua.includes('Mobile')) return 'Mobile Browser';
    return ua.slice(0, 24);
}

function copyDetailEmail() {
    if (!activeMessage) return;
    navigator.clipboard.writeText(activeMessage.email).then(() => {
        showToast('Email address copied to clipboard!', true);
    });
}

function showToast(message, isSuccess = true) {
    const toast = document.getElementById('toastNotification');
    const toastMsg = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    toastMsg.innerText = message;
    toastIcon.className = isSuccess ? 'fas fa-check-circle text-emerald-400 text-base' : 'fas fa-exclamation-circle text-rose-400 text-base';

    toast.classList.remove('translate-y-20', 'opacity-0');
    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 4000);
}

function updateKpiBadge(type, delta) {
    const el = document.getElementById(`stat-${type}`);
    if (el) {
        const curr = parseInt(el.innerText) || 0;
        el.innerText = Math.max(0, curr + delta);
    }
}
