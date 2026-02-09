"""
Service Desk Automation System - Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import sys
import os
from datetime import datetime, timedelta
import json

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from spelling_corrector import SpellingCorrector
from database import TicketDatabase, ExcelReportGenerator
from ticket_router import TicketRouter, TicketAssignment
from email_integration import Office365Integration, EmailTicketParser


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.permanent_session_lifetime = timedelta(hours=24)
CORS(app)

# Initialize modules
db = TicketDatabase('data/tickets/tickets.db')
# Ensure reports directory uses absolute path
reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reports')
report_gen = ExcelReportGenerator(reports_dir)
ticket_assignment = TicketAssignment()
email_service = Office365Integration()

# Admin credentials (in production, use proper authentication)
ADMIN_CREDENTIALS = {
    'admin': generate_password_hash('admin123'),
    'support_manager': generate_password_hash('manager123')
}

# Support staff credentials (demo). In production use a proper user store.
SUPPORT_CREDENTIALS = {
    'tech1': generate_password_hash('techpass1'),
    'tech2': generate_password_hash('techpass2')
}

# Department admins for IT, HR, Sales
DEPT_ADMINS = {
    'IT': generate_password_hash('itadmin'),
    'HR': generate_password_hash('hradmin'),
    'Sales': generate_password_hash('salesadmin')
}


def login_required(f):
    """Decorator for protecting routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # If it's an API request, return JSON
            if request.path.startswith('/admin/api/'):
                return jsonify({'error': 'Not authenticated'}), 401
            # Otherwise redirect to login
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def support_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'support':
            return redirect(url_for('support_login'))
        return f(*args, **kwargs)
    return decorated_function


def dept_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'dept_admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== PUBLIC ROUTES =====

@app.route('/', methods=['GET'])
def index():
    """Home page with ticket form"""
    return render_template('index.html')


@app.route('/api/create-ticket', methods=['POST'])
def create_ticket():
    """Create a new support ticket"""
    try:
        data = request.get_json()
        
        # Extract form data
        user_name = data.get('user_name', '').strip()
        user_email = data.get('user_email', '').strip()
        department = data.get('department', '').strip()
        phone = data.get('phone', '').strip()
        asset_id = data.get('asset_id', '').strip()
        description = data.get('description', '').strip()

        # Validate required fields (asset_id is mandatory)
        if not all([user_name, user_email, description, asset_id]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all required fields (Name, Email, Description, Asset/System ID)'
            }), 400
        
        # Step 1: Spelling correction and normalization
        corrector = SpellingCorrector()
        corrected_data = corrector.process_ticket_description(description)
        
        # Step 2: Route ticket to appropriate team
        ticket_data = {
            'user_name': user_name,
            'user_email': user_email,
            'department': department,
            'phone': phone,
            'asset_id': asset_id,
            'original_description': corrected_data['original_description'],
            'corrected_description': corrected_data['corrected_description'],
            'category': corrected_data['category'],
            'priority': corrected_data['priority'],
            'metadata': {
                'spelling_corrections': corrected_data['spelling_corrections'],
                'correction_timestamp': corrected_data['timestamp']
            }
        }
        
        # Get assignment details
        assignment = ticket_assignment.assign_ticket(ticket_data)
        ticket_data['assigned_to'] = assignment['assigned_to']
        
        # Step 3: Store in database
        ticket_id = db.create_ticket(ticket_data)
        
        # Step 4: Update with assignment info
        db.update_ticket(ticket_id, {
            'assigned_to': assignment['assigned_to'],
            'status': 'Assigned'
        })
        
        # Step 5: Send notifications
        try:
            # Send confirmation to user
            email_service.send_ticket_confirmation(
                user_email,
                ticket_id,
                corrected_data['corrected_description'][:100],
                assignment['team_email']
            )
            
            # Send notification to team
            ticket_data['ticket_id'] = ticket_id
            email_service.send_team_notification(
                assignment['team_email'],
                ticket_id,
                ticket_data
            )
        except Exception as e:
            print(f"Email notification failed: {str(e)}")
            # Continue even if email fails
        
        return jsonify({
            'success': True,
            'message': 'Ticket created successfully!',
            'ticket_id': ticket_id,
            'ticket_data': {
                'id': ticket_id,
                'user': user_name,
                'email': user_email,
                'category': ticket_data['category'],
                'priority': ticket_data['priority'],
                'assigned_to': assignment['assigned_to'],
                'status': 'Assigned'
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating ticket: {str(e)}'
        }), 500


@app.route('/api/ticket/<ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    """Get ticket details with history"""
    try:
        # Get ticket from database
        ticket = db.get_ticket(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Get ticket history
        history = db.get_ticket_history(ticket_id) if hasattr(db, 'get_ticket_history') else []
        
        # Return detailed ticket info
        return jsonify({
            'success': True,
            'ticket': ticket,
            'history': history if history else []
        }), 200
    
    except Exception as e:
        print(f"Error fetching ticket: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch ticket'
        }), 500


@app.route('/api/search-tickets', methods=['GET'])
def search_tickets():
    """Search tickets by email address"""
    try:
        email = request.args.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required',
                'tickets': []
            }), 400
        
        # Get all tickets and filter by email
        all_tickets = db.get_all_tickets()
        matching_tickets = [
            t for t in all_tickets 
            if t.get('user_email', '').lower() == email
        ]
        
        if matching_tickets:
            return jsonify({
                'success': True,
                'tickets': matching_tickets,
                'total': len(matching_tickets)
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No tickets found for this email',
                'tickets': []
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching tickets: {str(e)}',
            'tickets': []
        }), 500


# ===== ADMIN ROUTES =====

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            # Validate credentials
            if not username or not password:
                return jsonify({
                    'success': False, 
                    'message': 'Username and password are required'
                }), 400
            
            # Check if user exists and password matches
            if username in ADMIN_CREDENTIALS and \
               check_password_hash(ADMIN_CREDENTIALS[username], password):
                session['user'] = username
                session['role'] = 'admin'
                session.permanent = True
                return jsonify({
                    'success': True, 
                    'message': 'Login successful',
                    'redirect': '/admin/'
                }), 200
            else:
                return jsonify({
                    'success': False, 
                    'message': 'Invalid username or password'
                }), 401
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({
                'success': False, 
                'message': 'Login error. Please try again.'
            }), 500
    
    return render_template('admin_login.html')


@app.route('/admin/logout', methods=['GET'])
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin/', methods=['GET'])
@login_required
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin_dashboard.html')


@app.route('/admin/api/tickets', methods=['GET'])
@login_required
def get_tickets():
    """Get all tickets with filters"""
    filters = {}
    
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('category'):
        filters['category'] = request.args.get('category')
    if request.args.get('priority'):
        filters['priority'] = request.args.get('priority')
    if request.args.get('date_from'):
        filters['date_from'] = request.args.get('date_from')
    if request.args.get('date_to'):
        filters['date_to'] = request.args.get('date_to')
    
    tickets = db.get_all_tickets(filters)
    # Convert sqlite3.Row objects to dictionaries for JSON serialization
    tickets_list = [dict(ticket) if isinstance(ticket, dict) else dict(ticket) for ticket in tickets] if tickets else []
    return jsonify(tickets_list)


@app.route('/admin/api/ticket/<ticket_id>', methods=['GET', 'PUT'])
@login_required
def manage_ticket(ticket_id):
    """Get or update ticket"""
    if request.method == 'GET':
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        history = db.get_ticket_history(ticket_id)
        return jsonify({'ticket': ticket, 'history': history})
    
    elif request.method == 'PUT':
        data = request.get_json()
        updates = {}
        
        if 'status' in data:
            updates['status'] = data['status']
        if 'assigned_to' in data:
            updates['assigned_to'] = data['assigned_to']
        if 'resolution_notes' in data:
            updates['resolution_notes'] = data['resolution_notes']
        if 'priority' in data:
            updates['priority'] = data['priority']
        
        if updates:
            # Record who performed the update
            updates['performed_by'] = session.get('user', 'System')
            db.update_ticket(ticket_id, updates)
            return jsonify({'success': True, 'message': 'Ticket updated'})
        
        return jsonify({'error': 'No valid updates provided'}), 400


@app.route('/admin/api/statistics', methods=['GET'])
@login_required
def get_statistics():
    """Get dashboard statistics"""
    all_tickets = db.get_all_tickets()
    
    stats = {
        'total_tickets': len(all_tickets),
        'open_tickets': len([t for t in all_tickets if t.get('status') == 'Open']),
        'assigned_tickets': len([t for t in all_tickets if t.get('status') == 'Assigned']),
        'resolved_tickets': len([t for t in all_tickets if t.get('status') == 'Resolved']),
        'closed_tickets': len([t for t in all_tickets if t.get('status') == 'Closed']),
        'critical_tickets': len([t for t in all_tickets if t.get('priority') == 'P1 - Critical']),
        'high_priority': len([t for t in all_tickets if t.get('priority') == 'P2 - High']),
    }
    
    # Category breakdown
    categories = {}
    for ticket in all_tickets:
        cat = ticket.get('category', 'General')
        categories[cat] = categories.get(cat, 0) + 1
    
    stats['by_category'] = categories
    
    return jsonify(stats)


@app.route('/admin/api/reports/download', methods=['GET'])
@login_required
def download_report():
    """Download report in Excel format"""
    report_type = request.args.get('type', 'all')
    
    all_tickets = db.get_all_tickets()
    
    try:
        filepath = None
        if report_type == 'category':
            filepath = report_gen.generate_category_report(all_tickets)
        elif report_type == 'date':
            filepath = report_gen.generate_date_wise_report(all_tickets)
        elif report_type == 'history':
            filepath = report_gen.generate_history_report(all_tickets)
        elif report_type == 'summary':
            filepath = report_gen.generate_summary_report(all_tickets)
        else:
            filepath = report_gen.generate_ticket_report(all_tickets, report_type='all')
        
        if filepath and os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            return jsonify({'error': 'Report generation failed - file not found'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/reports/types', methods=['GET'])
@login_required
def get_report_types():
    """Get available report types"""
    return jsonify({
        'types': [
            {'id': 'all', 'name': 'All Tickets', 'description': 'Complete ticket list with all details'},
            {'id': 'summary', 'name': 'Summary Report', 'description': 'High-level overview with statistics'},
            {'id': 'category', 'name': 'By Category', 'description': 'Tickets grouped by category'},
            {'id': 'date', 'name': 'By Date', 'description': 'Tickets grouped by creation date'},
            {'id': 'history', 'name': 'With History', 'description': 'Tickets with complete activity history'}
        ]
    })


@app.route('/admin/api/teams', methods=['GET'])
@login_required
def get_teams():
    """Get support teams information"""
    router = TicketRouter()
    teams = router.SUPPORT_TEAMS
    return jsonify(teams)


# ===== SUPPORT STAFF ROUTES =====
@app.route('/support/login', methods=['GET', 'POST'])
def support_login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            if not username or not password:
                return jsonify({'success': False, 'message': 'Username and password required'}), 400

            if username in SUPPORT_CREDENTIALS and check_password_hash(SUPPORT_CREDENTIALS[username], password):
                session['user'] = username
                session['role'] = 'support'
                session.permanent = True
                return jsonify({'success': True, 'redirect': '/support/'}), 200
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        except Exception as e:
            print('Support login error:', e)
            return jsonify({'success': False, 'message': 'Login failed'}), 500
    return render_template('support_login.html')


@app.route('/support/logout')
def support_logout():
    session.clear()
    return redirect(url_for('support_login'))


@app.route('/support/', methods=['GET'])
@support_required
def support_dashboard():
    return render_template('support_dashboard.html')


@app.route('/support/api/tickets', methods=['GET'])
@support_required
def support_get_tickets():
    username = session.get('user')
    filters = {'assigned_to': username}
    tickets = db.get_all_tickets(filters)
    return jsonify({'tickets': tickets})


@app.route('/support/api/ticket/<ticket_id>', methods=['PUT'])
@support_required
def support_update_ticket(ticket_id):
    username = session.get('user')
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    # Only assigned support can update
    if ticket.get('assigned_to') != username:
        return jsonify({'error': 'Not authorized to update this ticket'}), 403

    data = request.get_json()
    updates = {}
    if 'status' in data:
        updates['status'] = data['status']
    if 'resolution_notes' in data:
        updates['resolution_notes'] = data['resolution_notes']
    if updates:
        updates['performed_by'] = username
        db.update_ticket(ticket_id, updates)
        return jsonify({'success': True}), 200
    return jsonify({'error': 'No updates provided'}), 400


# ===== DEPARTMENT ADMIN ROUTES =====
@app.route('/department/<dept>/login', methods=['GET', 'POST'])
def department_login(dept):
    dept_key = dept.capitalize()
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if dept_key not in DEPT_ADMINS:
            return jsonify({'success': False, 'message': 'Unknown department'}), 400
        if check_password_hash(DEPT_ADMINS[dept_key], password):
            # department admin login - username can be any identifier
            session['user'] = username or f'{dept_key}_admin'
            session['role'] = 'dept_admin'
            session['department'] = dept_key
            session.permanent = True
            return jsonify({'success': True, 'redirect': f'/department/{dept_key}/'}), 200
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    return render_template('department_login.html', department=dept_key)


@app.route('/department/<dept>/', methods=['GET'])
@dept_admin_required
def department_dashboard(dept):
    dept_key = dept.capitalize()
    return render_template('department_dashboard.html', department=dept_key)


@app.route('/department/<dept>/api/tickets', methods=['GET'])
@dept_admin_required
def department_get_tickets(dept):
    dept_key = dept.capitalize()
    # Ensure the logged-in department admin matches the requested department
    if session.get('department') != dept_key:
        return jsonify({'error': 'Not authorized for this department'}), 403
    tickets = db.get_all_tickets({'department': dept_key})
    return jsonify({'tickets': tickets})


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
