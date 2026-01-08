const API_BASE_URL = 'http://localhost:8000';

let authToken = localStorage.getItem('authToken');
let currentUserId = localStorage.getItem('userId');

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (authToken && currentUserId) {
        showMainContent();
        loadKYCStatus();
        loadDocuments();
    } else {
        showLoginForm();
    }
});

function showLoginForm() {
    document.getElementById('login-form').style.display = 'flex';
    document.getElementById('user-info').style.display = 'none';
    document.getElementById('main-content').style.display = 'none';
}

function showMainContent() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('user-info').style.display = 'flex';
    document.getElementById('current-user').textContent = currentUserId;
    document.getElementById('main-content').style.display = 'block';
}

async function login() {
    const userId = document.getElementById('user-id').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('auth-error');

    if (!userId || !password) {
        errorEl.textContent = 'Please enter both User ID and Password';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                password: password
            })
        });

        let data;
        try {
            data = await response.json();
        } catch (e) {
            // If response is not JSON, get text
            const text = await response.text();
            errorEl.textContent = `Server error: ${text.substring(0, 100)}`;
            console.error('Login error - non-JSON response:', text);
            return;
        }

        if (response.ok) {
            authToken = data.access_token;
            currentUserId = data.user_id;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('userId', currentUserId);
            errorEl.textContent = '';
            showMainContent();
            loadKYCStatus();
            loadDocuments();
        } else {
            errorEl.textContent = data.detail || 'Login failed';
        }
    } catch (error) {
        errorEl.textContent = 'Error connecting to server: ' + error.message;
        console.error('Login error:', error);
    }
}

function logout() {
    authToken = null;
    currentUserId = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    showLoginForm();
}

function getAuthHeaders() {
    return {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
    };
}

async function loadKYCStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/kyc/status`, {
            headers: getAuthHeaders()
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayKYCStatus(data);
        } else {
            document.getElementById('kyc-status').innerHTML = 
                '<p class="error">Failed to load KYC status</p>';
        }
    } catch (error) {
        console.error('Error loading KYC status:', error);
        document.getElementById('kyc-status').innerHTML = 
            '<p class="error">Error connecting to server</p>';
    }
}

function displayKYCStatus(data) {
    const statusEl = document.getElementById('kyc-status');
    const verification = data.verification || {};
    const documents = data.documents || [];

    let html = '<h3>Verification Status</h3>';
    
    if (verification) {
        html += `
            <div class="status-item">
                <span>Overall Status:</span>
                <strong>${verification.kyc_status || 'Not Started'}</strong>
            </div>
            <div class="status-item">
                <span>KYC Level:</span>
                <strong>${verification.kyc_level || 'None'}</strong>
            </div>
            <div class="status-item">
                <span>Photo Verified:</span>
                <strong>${verification.photo_verified ? 'Yes' : 'No'}</strong>
            </div>
            <div class="status-item">
                <span>Aadhaar Verified:</span>
                <strong>${verification.aadhaar_verified ? 'Yes' : 'No'}</strong>
            </div>
            <div class="status-item">
                <span>PAN Verified:</span>
                <strong>${verification.pan_verified ? 'Yes' : 'No'}</strong>
            </div>
        `;

        if (verification.face_match_score !== null) {
            html += `
                <div class="status-item">
                    <span>Face Match Score:</span>
                    <strong>${verification.face_match_score}%</strong>
                </div>
            `;
        }
    } else {
        html += '<p>No verification record found. Upload documents to get started.</p>';
    }

    statusEl.innerHTML = html;

    // Update document status badges
    updateDocumentStatusBadges(documents);
}

function updateDocumentStatusBadges(documents) {
    const statusMap = {
        'photo': 'photo-status',
        'aadhaar': 'aadhaar-status',
        'pan': 'pan-status'
    };

    // Reset all badges
    Object.values(statusMap).forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = 'Not Uploaded';
            el.className = 'status-badge';
        }
    });

    // Update with actual status
    documents.forEach(doc => {
        const badgeId = statusMap[doc.document_type];
        if (badgeId) {
            const el = document.getElementById(badgeId);
            if (el) {
                el.textContent = doc.verification_status || 'Pending';
                el.className = `status-badge ${doc.verification_status || 'pending'}`;
            }
        }
    });
}

function previewFile(type) {
    const fileInput = document.getElementById(`${type}-file`);
    const preview = document.getElementById(`${type}-preview`);
    const file = fileInput.files[0];

    if (file) {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `<p>PDF file selected: ${file.name}</p>`;
        }
    }
}

async function uploadDocument(type) {
    const fileInput = document.getElementById(`${type}-file`);
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file first');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', type);

    const uploadBtn = document.getElementById(`${type}-upload-btn`);
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/kyc/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            alert('Document uploaded successfully!');
            loadKYCStatus();
            loadDocuments();
            fileInput.value = '';
            document.getElementById(`${type}-preview`).innerHTML = '';
        } else {
            alert(data.detail || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('Error uploading document');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = `Upload ${type.charAt(0).toUpperCase() + type.slice(1)}`;
    }
}

async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/kyc/documents`, {
            headers: getAuthHeaders()
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayDocuments(data.documents || []);
        } else {
            document.getElementById('documents-list').innerHTML = 
                '<p class="error">Failed to load documents</p>';
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        document.getElementById('documents-list').innerHTML = 
            '<p class="error">Error connecting to server</p>';
    }
}

function displayDocuments(documents) {
    const listEl = document.getElementById('documents-list');

    if (documents.length === 0) {
        listEl.innerHTML = '<p>No documents uploaded yet.</p>';
        return;
    }

    let html = '';
    documents.forEach(doc => {
        const date = new Date(doc.uploaded_at).toLocaleString();
        html += `
            <div class="document-item">
                <div class="document-info">
                    <h4>${doc.document_type.charAt(0).toUpperCase() + doc.document_type.slice(1)}</h4>
                    <p>Status: <strong>${doc.verification_status}</strong></p>
                    <p>Uploaded: ${date}</p>
                    ${doc.validation_score ? `<p>Validation Score: ${doc.validation_score}%</p>` : ''}
                    ${doc.verification_notes ? `<p>Notes: ${doc.verification_notes}</p>` : ''}
                </div>
            </div>
        `;
    });

    listEl.innerHTML = html;
}

async function triggerVerification() {
    const verifyBtn = document.getElementById('verify-btn');
    verifyBtn.disabled = true;
    verifyBtn.textContent = 'Verifying...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/kyc/verify`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        const data = await response.json();

        if (response.ok) {
            alert('Verification process completed!');
            loadKYCStatus();
            loadDocuments();
        } else {
            alert(data.detail || 'Verification failed');
        }
    } catch (error) {
        console.error('Verification error:', error);
        alert('Error triggering verification');
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.textContent = 'Trigger Verification';
    }
}

function refreshStatus() {
    loadKYCStatus();
    loadDocuments();
}

// Check if all documents are verified to enable verify button
setInterval(() => {
    const photoStatus = document.getElementById('photo-status');
    const aadhaarStatus = document.getElementById('aadhaar-status');
    const panStatus = document.getElementById('pan-status');
    
    const allVerified = 
        photoStatus && photoStatus.classList.contains('verified') &&
        aadhaarStatus && aadhaarStatus.classList.contains('verified') &&
        panStatus && panStatus.classList.contains('verified');
    
    const verifyBtn = document.getElementById('verify-btn');
    if (verifyBtn) {
        verifyBtn.disabled = !allVerified;
    }
}, 1000);
