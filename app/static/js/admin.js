/**
 * Admin Dashboard JavaScript
 */

let currentTicketId = null;
let statsChart = null;
let categoryChart = null;
let statusChart = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load initial data (wrapped to avoid unhandled exceptions)
    try {
        loadStatistics();
    } catch (e) {
        console.error('loadStatistics failed', e);
    }
    try {
        loadTickets();
    } catch (e) {
        console.error('loadTickets failed', e);
    }
    try {
        loadTeams();
    } catch (e) {
        console.error('loadTeams failed', e);
    }

    // Set up chart update interval
    try {
        setInterval(loadStatistics, 30000); // Refresh every 30 seconds
    } catch (e) {
        console.error('setInterval failed', e);
    }
});

/**
 * Show specific tab
 */
function showTab(tabName, ev) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.sidebar .list-group-item').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tabId = tabName + 'Tab'; // e.g., 'tickets' -> 'ticketsTab'
    const tabElement = document.getElementById(tabId);
    if (tabElement) {
        tabElement.classList.add('active');
        console.log('Activated tab:', tabId);
    } else {
        console.error('Tab not found:', tabId);
    }
    
    // Highlight active button
    try {
        if (ev && ev.currentTarget) {
            ev.currentTarget.classList.add('active');
        } else if (ev && ev.target) {
            ev.target.classList.add('active');
        } else {
            // fallback: find matching sidebar button by text
            const btn = Array.from(document.querySelectorAll('.sidebar .list-group-item')).find(b => {
                return b.textContent.trim().toLowerCase().includes(tabName);
            });
            if (btn) btn.classList.add('active');
        }
    } catch (e) {
        // ignore
    }
    
    // Load data specific to tab
    if (tabName === 'tickets') {
        loadTickets();
    } else if (tabName === 'teams') {
        loadTeams();
    }
}

/**
 * Load dashboard statistics
 */
async function loadStatistics() {
    try {
        const response = await fetch('/admin/api/statistics');
        if (!response.ok) {
            console.error('Failed to load statistics', response.status);
            return;
        }
        const stats = await response.json();

        // Update stat cards (guard elements exist)
        const totalEl = document.getElementById('totalTickets');
        const resolvedEl = document.getElementById('resolvedTickets');
        const openEl = document.getElementById('openTickets');
        const criticalEl = document.getElementById('criticalTickets');
        if (totalEl) totalEl.textContent = stats.total_tickets || 0;
        if (resolvedEl) resolvedEl.textContent = stats.resolved_tickets || 0;
        if (openEl) openEl.textContent = stats.open_tickets || 0;
        if (criticalEl) criticalEl.textContent = stats.critical_tickets || 0;

        // Update category chart
        try { updateCategoryChart(stats.by_category || {}); } catch (e) { console.error(e); }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

/**
 * Load all tickets
 */
async function loadTickets() {
    try {
        const filters = {
            status: document.getElementById('statusFilter')?.value || '',
            category: document.getElementById('categoryFilter')?.value || '',
            priority: document.getElementById('priorityFilter')?.value || ''
        };
        
        // Build query string
        const queryParams = new URLSearchParams();
        if (filters.status) queryParams.append('status', filters.status);
        if (filters.category) queryParams.append('category', filters.category);
        if (filters.priority) queryParams.append('priority', filters.priority);
        
        const response = await fetch(`/admin/api/tickets?${queryParams}`);
        if (!response.ok) {
            console.error('Failed to fetch tickets', response.status);
            const tbodyErr = document.getElementById('ticketsTableBody');
            if (tbodyErr) tbodyErr.innerHTML = '<tr><td colspan="8" class="text-center text-danger py-4">Failed to load tickets</td></tr>';
            return;
        }

        const tickets = await response.json();
        console.log('Tickets fetched:', tickets);

        // Populate table
        const tbody = document.getElementById('ticketsTableBody');
        if (!tbody) {
            console.error('tbody element not found');
            return;
        }
        if (!Array.isArray(tickets) || tickets.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-4">No tickets found</td></tr>';
            return;
        }

        tbody.innerHTML = tickets.map(ticket => `
            <tr>
                <td>
                    <strong><a href="#" onclick="showTicketDetail('${ticket.ticket_id}'); return false;">${ticket.ticket_id}</a></strong>
                </td>
                <td>${escapeHtml(ticket.user_name || '')}</td>
                <td><span class="badge bg-info">${escapeHtml(ticket.category || 'General')}</span></td>
                <td>${getPriorityBadge(ticket.priority || 'P3 - Medium')}</td>
                <td>${getStatusBadge(ticket.status || 'Open')}</td>
                <td>${escapeHtml(ticket.assigned_to || 'Unassigned')}</td>
                <td>${formatDate(ticket.created_timestamp || '')}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="editTicket('${ticket.ticket_id}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        console.log('Table populated with', tickets.length, 'tickets');
    } catch (error) {
        console.error('Error loading tickets:', error);
        const tbody = document.getElementById('ticketsTableBody');
        if (tbody) tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger py-4">Error: ' + error.message + '</td></tr>';
    }
}

/**
 * Load support teams
 */
async function loadTeams() {
    try {
        const response = await fetch('/admin/api/teams');
        const teams = await response.json();
        
        const container = document.getElementById('teamsContainer');
        container.innerHTML = Object.entries(teams).map(([teamName, teamData]) => `
            <div class="col-md-4">
                <div class="team-card">
                    <h5><i class="bi bi-people-fill"></i> ${escapeHtml(teamName)}</h5>
                    <p class="text-muted small mb-2">
                        <strong>Email:</strong> ${escapeHtml(teamData.email)}
                    </p>
                    <p class="text-muted small mb-2">
                        <strong>Capacity:</strong> ${teamData.members.length} members
                    </p>
                    <p class="text-muted small">
                        <strong>Expertise:</strong><br>
                        <small>${(teamData.expertise || []).join(', ') || 'General'}</small>
                    </p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading teams:', error);
    }
}

/**
 * Show ticket detail modal
 */
async function showTicketDetail(ticketId) {
    currentTicketId = ticketId;
    try {
        const response = await fetch(`/admin/api/ticket/${ticketId}`);
        const data = await response.json();
        
        const ticket = data.ticket;
        const history = data.history || [];
        
        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <h6>Ticket ID</h6>
                    <p><strong>${escapeHtml(ticket.ticket_id)}</strong></p>
                </div>
                <div class="col-md-6">
                    <h6>Status</h6>
                    <p>${getStatusBadge(ticket.status)}</p>
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <h6>User Name</h6>
                    <p>${escapeHtml(ticket.user_name)}</p>
                </div>
                <div class="col-md-6">
                    <h6>Email</h6>
                    <p>${escapeHtml(ticket.user_email)}</p>
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <h6>Category</h6>
                    <p><span class="badge bg-info">${escapeHtml(ticket.category)}</span></p>
                </div>
                <div class="col-md-6">
                    <h6>Priority</h6>
                    <p>${getPriorityBadge(ticket.priority)}</p>
                </div>
            </div>
            
            <div class="mb-3">
                <h6>Description (Original)</h6>
                <p>${escapeHtml(ticket.original_description)}</p>
            </div>
            
            <div class="mb-3">
                <h6>Description (Corrected)</h6>
                <p>${escapeHtml(ticket.corrected_description)}</p>
            </div>
            
            <div class="mb-3">
                <h6>Assigned To</h6>
                <input type="text" class="form-control" id="modalAssignedTo" value="${escapeHtml(ticket.assigned_to)}">
            </div>
            
            <div class="mb-3">
                <h6>Resolution Notes</h6>
                <textarea class="form-control" id="modalNotes" rows="4">${escapeHtml(ticket.resolution_notes || '')}</textarea>
            </div>
            
            <div class="mb-3">
                <h6>History</h6>
                <div class="timeline">
                    ${history.map(entry => `
                        <div class="mb-2 pb-2 border-bottom">
                            <small class="text-muted">${formatDate(entry.timestamp)}</small>
                            <p class="mb-0"><strong>${escapeHtml(entry.action)}</strong> by ${escapeHtml(entry.performed_by)}</p>
                            <small class="text-muted">${escapeHtml(entry.details)}</small>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('ticketModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading ticket:', error);
        alert('Failed to load ticket details');
    }
}

/**
 * Edit ticket
 */
function editTicket(ticketId) {
    showTicketDetail(ticketId);
}

/**
 * Load ticket details by ID
 */
async function loadTicketDetails() {
    const ticketId = document.getElementById('ticketIdInput').value.trim();
    if (!ticketId) {
        alert('Please enter a ticket ID');
        return;
    }
    showTicketDetail(ticketId);
}

/**
 * Update ticket status
 */
async function updateTicketStatus() {
    const assignedTo = document.getElementById('modalAssignedTo').value;
    const notes = document.getElementById('modalNotes').value;
    
    try {
        const response = await fetch(`/admin/api/ticket/${currentTicketId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                assigned_to: assignedTo,
                resolution_notes: notes
            })
        });
        
        if (response.ok) {
            alert('Ticket updated successfully');
            loadTickets();
            bootstrap.Modal.getInstance(document.getElementById('ticketModal')).hide();
        } else {
            alert('Failed to update ticket');
        }
    } catch (error) {
        console.error('Error updating ticket:', error);
        alert('Error updating ticket');
    }
}

/**
 * Download report
 */
async function downloadReport(type) {
    try {
        // Show loading indicator
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Generating...';
        btn.disabled = true;
        
        console.log('Downloading report type:', type);
        
        const response = await fetch(`/admin/api/reports/download?type=${type}`);
        
        if (!response.ok) {
            console.error('Download failed with status:', response.status);
            const errorText = await response.text();
            console.error('Error response:', errorText);
            alert('Failed to download report: ' + errorText);
            btn.innerHTML = originalText;
            btn.disabled = false;
            return;
        }
        
        const blob = await response.blob();
        console.log('Blob size:', blob.size);
        
        if (blob.size === 0) {
            alert('Error: Empty report file generated');
            btn.innerHTML = originalText;
            btn.disabled = false;
            return;
        }
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Generate filename based on type
        const timestamp = new Date().getTime();
        const typeNames = {
            'all': 'All_Tickets',
            'summary': 'Summary_Report',
            'category': 'By_Category',
            'date': 'By_Date',
            'history': 'With_History'
        };
        const typeName = typeNames[type] || type;
        link.download = `tickets_${typeName}_${timestamp}.xlsx`;
        
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
        
        console.log('Report downloaded successfully');
        btn.innerHTML = originalText;
        btn.disabled = false;
    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Error downloading report: ' + error.message);
        const btn = event.target.closest('button');
        btn.innerHTML = '<i class="bi bi-download"></i> Download Excel';
        btn.disabled = false;
    }
}

/**
 * Update category chart
 */
function updateCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                data: Object.values(categoryData),
                backgroundColor: [
                    '#4472C4',
                    '#70AD47',
                    '#FFC000',
                    '#E74C3C',
                    '#5B9BD5',
                    '#2E75B6',
                    '#FF6B6B',
                    '#95E1D3'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Get priority badge
 */
function getPriorityBadge(priority) {
    const priorityMap = {
        'P1 - Critical': '<span class="badge bg-danger">Critical</span>',
        'P2 - High': '<span class="badge bg-warning">High</span>',
        'P3 - Medium': '<span class="badge bg-info">Medium</span>',
        'P4 - Low': '<span class="badge bg-success">Low</span>'
    };
    return priorityMap[priority] || `<span class="badge bg-secondary">${priority}</span>`;
}

/**
 * Get status badge
 */
function getStatusBadge(status) {
    const statusMap = {
        'Open': '<span class="badge bg-danger">Open</span>',
        'Assigned': '<span class="badge bg-warning">Assigned</span>',
        'In Progress': '<span class="badge bg-info">In Progress</span>',
        'Resolved': '<span class="badge bg-success">Resolved</span>',
        'Closed': '<span class="badge bg-secondary">Closed</span>'
    };
    return statusMap[status] || `<span class="badge bg-secondary">${status}</span>`;
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
 * Escape HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}
