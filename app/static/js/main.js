/**
 * IT Support Service Desk - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form submission
    const ticketForm = document.getElementById('ticketForm');
    if (ticketForm) {
        ticketForm.addEventListener('submit', handleFormSubmit);
    }

    // Initialize track form submission
    const trackForm = document.getElementById('trackForm');
    if (trackForm) {
        trackForm.addEventListener('submit', handleTrackSubmit);
    }

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

/**
 * Handle ticket tracking form submission
 */
async function handleTrackSubmit(e) {
    e.preventDefault();
    
    showLoadingSpinner(true);
    
    try {
        const ticketId = document.getElementById('trackTicketId').value.trim();
        
        if (!ticketId) {
            showAlert('error', 'Please enter a ticket ID');
            showLoadingSpinner(false);
            return;
        }
        
        // Fetch ticket by ID
        const response = await fetch(`/api/ticket/${encodeURIComponent(ticketId)}`);
        const result = await response.json();
        
        const resultsDiv = document.getElementById('ticketResults');
        const noResultsDiv = document.getElementById('noResults');
        const detailDiv = document.getElementById('ticketDetail');
        
        if (response.ok && result.ticket) {
            // Show ticket details
            detailDiv.innerHTML = createDetailedTicketCard(result.ticket);
            resultsDiv.classList.remove('d-none');
            noResultsDiv.classList.add('d-none');
            
            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        } else {
            // No ticket found
            resultsDiv.classList.add('d-none');
            noResultsDiv.classList.remove('d-none');
            noResultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('error', 'Failed to search ticket');
    } finally {
        showLoadingSpinner(false);
    }
}

/**
 * Create detailed ticket card HTML
 */
function createDetailedTicketCard(ticket) {
    const statusBadgeClass = {
        'Open': 'warning',
        'Assigned': 'info',
        'In Progress': 'primary',
        'Resolved': 'success',
        'Closed': 'secondary'
    }[ticket.status] || 'secondary';
    
    const priorityBadgeClass = {
        'P1 - Critical': 'danger',
        'P2 - High': 'warning',
        'P3 - Medium': 'info',
        'P4 - Low': 'secondary'
    }[ticket.priority] || 'secondary';
    
    const timeline = Array.isArray(ticket.history) && ticket.history.length > 0 ? `
        <div class="mt-4 pt-4 border-top">
            <h6><i class="bi bi-clock-history"></i> Ticket History</h6>
            ${ticket.history.map(entry => `
                <div class="mb-3 pb-2 border-bottom">
                    <small class="text-muted">${formatDate(entry.timestamp || entry.created_at)}</small>
                    <p class="mb-1"><strong>${escapeHtml(entry.action || entry.status)}</strong></p>
                    ${entry.details ? `<small class="text-muted">${escapeHtml(entry.details)}</small>` : ''}
                </div>
            `).join('')}
        </div>
    ` : '';
    
    return `
        <div class="card border-start border-4" style="border-color: var(--bs-${statusBadgeClass});">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-4">
                    <div>
                        <h4 class="card-title mb-2">
                            <i class="bi bi-ticket-detailed"></i> Ticket #${escapeHtml(ticket.id || ticket.ticket_id)}
                        </h4>
                        <small class="text-muted">Created: ${formatDate(ticket.created_timestamp || ticket.created_at)}</small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${statusBadgeClass} p-2">${escapeHtml(ticket.status)}</span>
                        <br><br>
                        <span class="badge bg-${priorityBadgeClass} p-2">${escapeHtml(ticket.priority)}</span>
                    </div>
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-6">
                        <h6 class="text-muted fw-semibold">User Information</h6>
                        <p class="mb-1"><strong>Name:</strong> ${escapeHtml(ticket.user_name)}</p>
                        <p class="mb-1"><strong>Email:</strong> ${escapeHtml(ticket.user_email)}</p>
                        ${ticket.phone ? `<p class="mb-0"><strong>Phone:</strong> ${escapeHtml(ticket.phone)}</p>` : ''}
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-muted fw-semibold">Ticket Information</h6>
                        <p class="mb-1"><strong>Category:</strong> <span class="badge bg-info">${escapeHtml(ticket.category || 'General')}</span></p>
                        <p class="mb-1"><strong>Department:</strong> ${escapeHtml(ticket.department || 'Not specified')}</p>
                        <p class="mb-0"><strong>Assigned To:</strong> ${escapeHtml(ticket.assigned_to || 'Not assigned yet')}</p>
                    </div>
                </div>
                
                <div class="mb-4">
                    <h6 class="text-muted fw-semibold">Issue Description</h6>
                    <p class="bg-light p-3 rounded">${escapeHtml(ticket.corrected_description || ticket.original_description || '')}</p>
                </div>
                
                ${ticket.resolution_notes ? `
                    <div class="alert alert-success mb-4">
                        <h6 class="alert-heading"><i class="bi bi-check-circle"></i> Resolution</h6>
                        <p class="mb-0">${escapeHtml(ticket.resolution_notes)}</p>
                    </div>
                ` : `
                    <div class="alert alert-info mb-4">
                        <h6 class="alert-heading"><i class="bi bi-info-circle"></i> Status Update</h6>
                        <p class="mb-0">Your ticket is being processed by our support team. We will contact you soon.</p>
                    </div>
                `}
                
                ${timeline}
            </div>
        </div>
    `;
}

/**
 * Handle ticket form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Show loading spinner
    showLoadingSpinner(true);
    
    try {
        // Collect form data
        const formData = {
            user_name: document.getElementById('userName').value.trim(),
            user_email: document.getElementById('userEmail').value.trim(),
            department: document.getElementById('department').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            asset_id: document.getElementById('assetId') ? document.getElementById('assetId').value.trim() : '',
            description: document.getElementById('description').value.trim()
        };
        
        // Validate required fields
        if (!formData.user_name || !formData.user_email || !formData.description || !formData.asset_id) {
            showAlert('error', 'Please fill in all required fields');
            showLoadingSpinner(false);
            return;
        }
        
        // Validate email format
        if (!isValidEmail(formData.user_email)) {
            showAlert('error', 'Please enter a valid email address');
            showLoadingSpinner(false);
            return;
        }
        
        // Send request to server
        const response = await fetch('/api/create-ticket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Show success message
            showSuccessMessage(result.ticket_id, formData.user_name);
            
            // Reset form
            document.getElementById('ticketForm').reset();
            
            // Scroll to success message
            document.getElementById('successAlert').scrollIntoView({ behavior: 'smooth' });
        } else {
            showAlert('error', result.message || 'Failed to create ticket');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('error', 'Network error. Please try again.');
    } finally {
        showLoadingSpinner(false);
    }
}

/**
 * Show success message
 */
function showSuccessMessage(ticketId, userName) {
    const successAlert = document.getElementById('successAlert');
    const successMessage = document.getElementById('successMessage');
    
    successMessage.innerHTML = `
        <strong>Hello ${escapeHtml(userName)}!</strong><br>
        Your ticket has been successfully created and assigned to the appropriate support team.
        <br><br>
        Status: <strong>Assigned & Processing</strong><br>
        Expected Response: <strong>2-4 hours</strong>
    `;
    
    document.getElementById('ticketId').textContent = ticketId;
    successAlert.classList.remove('d-none');
}

/**
 * Show alert message
 */
function showAlert(type, message) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : 'check-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of form
    const form = document.getElementById('ticketForm');
    form.parentElement.insertBefore(alertDiv, form);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Show/hide loading spinner
 */
function showLoadingSpinner(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('d-none');
    } else {
        spinner.classList.add('d-none');
    }
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Set issue description from quick buttons
 */
function setIssue(issueText) {
    document.getElementById('description').value = issueText;
    document.getElementById('description').focus();
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show notification
 */
function showNotification(title, message, type = 'info') {
    // You can use browser notifications API if permitted
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: message,
            icon: '/static/img/icon.png'
        });
    }
}
