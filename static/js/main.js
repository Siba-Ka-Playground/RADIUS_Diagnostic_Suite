function getTimestamp() {
    const d = new Date();
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}.${d.getMilliseconds().toString().padStart(3, '0')}`;
}

function logToTerminal(colorClass, msg) {
    const term = document.getElementById('terminal');
    term.innerHTML += `<div class="log-entry"><span class="c-gray">[${getTimestamp()}]</span> <span class="${colorClass}">${msg}</span></div>`;
    term.scrollTop = term.scrollHeight;
}

function clearTerminal() {
    document.getElementById('terminal').innerHTML = '';
    logToTerminal('c-cyan', '[SYSTEM] Console Cleared.');
}

// === TOAST NOTIFICATION SYSTEM ===
function showToast(message, type) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerText = message;
    
    container.appendChild(toast);
    
    // Auto remove after 4.5 seconds
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 400); 
    }, 4500);
}

function handleResponse(data) {
    data.logs.forEach(l => logToTerminal(l.color, l.msg));

    if (data.status === 'challenge') {
        showToast('MFA Challenge Triggered', 'challenge');
        document.getElementById('mfa-section').style.display = 'block';
        document.getElementById('challenge-msg').innerText = data.reply_msg;
        document.getElementById('state_hex').value = data.state_hex;
        
        if (data.auto_token) {
            document.getElementById('mfa_input').value = data.auto_token;
        } else {
            document.getElementById('mfa_input').value = '';
            document.getElementById('mfa_input').focus();
        }
    } else if (data.status === 'success') {
        showToast('Access Granted: Authentication Successful', 'success');
        document.getElementById('mfa-section').style.display = 'none';
    } else if (data.status === 'reject') {
        showToast('Access Denied: Invalid Credentials', 'error');
        document.getElementById('mfa-section').style.display = 'none';
    } else if (data.status === 'error') {
        showToast('System/Network Error Encountered', 'error');
    }
}

async function initiateAttack() {
    // NEW: Capture Server Config fields
    const server_ip = document.getElementById('server_ip').value.trim();
    const shared_secret = document.getElementById('shared_secret').value.trim();
    const nas_ip = document.getElementById('nas_ip').value.trim();
    
    // Capture Payload fields
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const totp_secret = document.getElementById('totp_secret').value.trim();

    if (!server_ip || !shared_secret) {
        logToTerminal('c-red', '[ERROR] Target IdP Server IP and Shared Secret are required.');
        showToast('Missing Server Configuration', 'error');
        return;
    }

    if (!username || !password) {
        logToTerminal('c-red', '[ERROR] Target Identity and Primary Secret are required.');
        showToast('Missing Username or Password', 'error');
        return;
    }

    document.getElementById('mfa-section').style.display = 'none';
    logToTerminal('c-cyan', `\n[--- NEW SESSION INITIATED ---]`);
    logToTerminal('c-blue', `[INFO] Building payload for target: ${username}`);
    
    try {
        const res = await fetch('/api/primary', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ server_ip, shared_secret, nas_ip, username, password, totp_secret })
        });
        handleResponse(await res.json());
    } catch (e) {
        logToTerminal('c-red', `[FATAL] Local Request Error: ${e.message}`);
        showToast('Connection to Backend Failed', 'error');
    }
}

async function transmitMfa() {
    // NEW: Capture Server Config fields
    const server_ip = document.getElementById('server_ip').value.trim();
    const shared_secret = document.getElementById('shared_secret').value.trim();
    const nas_ip = document.getElementById('nas_ip').value.trim();

    // Capture Payload fields
    const username = document.getElementById('username').value.trim();
    const mfa_input = document.getElementById('mfa_input').value.trim();
    const state_hex = document.getElementById('state_hex').value;
    const totp_secret = document.getElementById('totp_secret').value.trim();

    if (!mfa_input) {
        logToTerminal('c-yellow', '[WARN] Cannot transmit empty response parameter.');
        showToast('OTP Input Cannot Be Empty', 'challenge');
        return;
    }

    try {
        const res = await fetch('/api/mfa', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ server_ip, shared_secret, nas_ip, username, mfa_input, state_hex, totp_secret })
        });
        handleResponse(await res.json());
    } catch (e) {
        logToTerminal('c-red', `[FATAL] Local Request Error: ${e.message}`);
        showToast('Connection to Backend Failed', 'error');
    }
}