// Clipboard utility for BMAD Forge

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} - Whether copy was successful
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Failed to copy to clipboard:', err);
        return false;
    }
}

/**
 * Copy element content to clipboard
 * @param {string} elementId - ID of the element to copy
 * @returns {Promise<boolean>} - Whether copy was successful
 */
async function copyElementContent(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Element with ID "${elementId}" not found`);
        return false;
    }
    
    const text = element.textContent || element.innerText;
    return await copyToClipboard(text);
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Toast type (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-secondary';
    
    const toastHtml = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'info-circle'}"></i>
                    ${type.charAt(0).toUpperCase() + type.slice(1)}
                </strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();
    
    // Remove after hiding
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

/**
 * Copy button click handler
 */
function initCopyButton(buttonId, sourceId) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    button.addEventListener('click', async () => {
        const success = await copyElementContent(sourceId);
        
        if (success) {
            // Update button text temporarily
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check me-1"></i>Copied!';
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-success');
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.add('btn-outline-primary');
                button.classList.remove('btn-success');
            }, 2000);
        } else {
            showToast('Failed to copy to clipboard', 'error');
        }
    });
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize copy buttons if they exist
    initCopyButton('copyBtn', 'promptContent');
});
