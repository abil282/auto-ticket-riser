# IT Support Service Desk Automation System

A comprehensive, intelligent service desk automation solution with Python backend, responsive Bootstrap UI, automatic ticket categorization, and multi-channel integration.

## 🌟 Features

### **Intelligent Automation**
- ✅ **Auto Spelling Correction** - Automatically corrects IT-related spelling mistakes (network, connection, Windows, login, etc.)
- ✅ **Smart Categorization** - Automatically detects issue category and priority
- ✅ **Intelligent Routing** - Routes tickets to appropriate support teams based on rules
- ✅ **Priority Auto-Detection** - Sets urgency levels automatically based on keywords

### **Multi-Channel Support**
- ✅ **Web Form Submission** - Clean, responsive form for users to raise tickets
- ✅ **Office 365 Email Integration** - Create tickets from incoming support emails
- ✅ **Email Notifications** - Automatic confirmations and updates to users

### **Data Management**
- ✅ **SQLite Database** - Persistent storage of all ticket data
- ✅ **Excel Export** - Download reports in Excel format
- ✅ **Structured Storage** - Organized folder structure for documents and attachments
- ✅ **Audit Trail** - Complete history of ticket changes and actions

### **Admin Dashboard**
- ✅ **Real-time Statistics** - Dashboard with key metrics and charts
- ✅ **Ticket Management** - View, search, filter, and update tickets
- ✅ **Advanced Filtering** - Filter by status, category, priority, date range
- ✅ **Report Generation** - Generate date-wise and category-wise reports
- ✅ **Team Management** - View support teams and their expertise

### **Responsive UI**
- ✅ **Mobile-Friendly** - Works seamlessly on all devices
- ✅ **Bootstrap 5** - Modern, clean, professional design
- ✅ **Accessibility** - WCAG compliant interface
- ✅ **Dark Mode Ready** - Easy to extend for dark mode support

## 📋 Project Structure

```
auto ticket riser/
├── app/
│   ├── app.py                 # Main Flask application
│   ├── templates/
│   │   ├── index.html         # Home page with ticket form
│   │   ├── admin_dashboard.html   # Admin dashboard
│   │   └── admin_login.html   # Login page
│   └── static/
│       ├── css/
│       │   ├── style.css      # Main styles
│       │   └── admin.css      # Admin dashboard styles
│       └── js/
│           ├── main.js        # Home page JavaScript
│           └── admin.js       # Admin dashboard JavaScript
├── modules/
│   ├── __init__.py
│   ├── spelling_corrector.py  # AI-powered spelling & keywords
│   ├── database.py            # SQLite & Excel storage
│   ├── ticket_router.py       # Intelligent routing logic
│   └── email_integration.py   # Office 365 integration
├── data/
│   ├── tickets/
│   │   └── tickets.db         # SQLite database
│   └── reports/               # Generated Excel reports
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Office 365 account (optional, for email integration)

### Installation

1. **Clone or download the project**
   ```bash
   cd "auto ticket riser"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create data directories**
   ```bash
   mkdir -p data/tickets data/reports
   ```

4. **Run the application**
   ```bash
   python app/app.py
   ```

5. **Access the application**
   - **Home Page**: http://localhost:5000
   - **Admin Portal**: http://localhost:5000/admin/login
   - **Demo Credentials**: 
     - Username: `admin`
     - Password: `admin123`

## 📝 API Documentation

### Public APIs

#### Create Ticket
```
POST /api/create-ticket
Content-Type: application/json

{
  "user_name": "John Doe",
  "user_email": "john@company.com",
  "department": "Finance",
  "phone": "(123) 456-7890",
  "description": "Cannot connect to network. Network connection not working."
}

Response:
{
  "success": true,
  "message": "Ticket created successfully!",
  "ticket_id": "TKT-20240209-ABC123",
  "ticket_data": {...}
}
```

#### Get Ticket Details
```
GET /api/ticket/{ticket_id}

Response:
{
  "ticket": {...},
  "history": [...]
}
```

### Admin APIs (Require Authentication)

#### Get All Tickets
```
GET /admin/api/tickets?status=Open&category=Network&priority=P1%20-%20Critical
```

#### Get Ticket by ID
```
GET /admin/api/ticket/{ticket_id}
```

#### Update Ticket
```
PUT /admin/api/ticket/{ticket_id}
Content-Type: application/json

{
  "status": "In Progress",
  "assigned_to": "John Tech",
  "resolution_notes": "Working on the issue"
}
```

#### Get Statistics
```
GET /admin/api/statistics
```

#### Download Report
```
GET /admin/api/reports/download?type=all|date|category
```

## 🔧 Configuration

### Spelling Corrector
Edit `modules/spelling_corrector.py` to add/modify IT-related corrections:

```python
IT_CORRECTIONS = {
    'netwrok': 'network',
    'conection': 'connection',
    # Add more corrections...
}
```

### Support Teams
Edit `modules/ticket_router.py` to modify teams and routing rules:

```python
SUPPORT_TEAMS = {
    'Network Support': {
        'email': 'network-support@company.com',
        'members': ['John Tech', 'Sarah Net'],
        'expertise': ['network', 'connection', 'wifi', ...],
        'max_capacity': 20
    },
    # Add more teams...
}
```

### Email Integration
To enable Office 365 email integration:

```python
# In app/app.py
email_service = Office365Integration()
email_service.authenticate('your.email@company.com', 'your_password_or_app_password')
```

## 📊 Database Schema

### Tickets Table
```sql
CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    user_email TEXT NOT NULL,
    department TEXT,
    phone TEXT,
    original_description TEXT NOT NULL,
    corrected_description TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT DEFAULT 'Open',
    assigned_to TEXT,
    created_timestamp TEXT NOT NULL,
    updated_timestamp TEXT NOT NULL,
    resolved_timestamp TEXT,
    resolution_notes TEXT,
    attachments TEXT,
    metadata TEXT
);
```

### Ticket History Table
```sql
CREATE TABLE ticket_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL,
    action TEXT NOT NULL,
    performed_by TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT,
    FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
);
```

## 🎯 Workflow

1. **User Submits Ticket**
   - User fills out the form on the home page
   - System receives the request

2. **Automatic Processing**
   - Spelling corrector fixes IT-related mistakes
   - Smart categorization determines ticket type
   - Priority detection sets urgency level
   - Intelligent router assigns to appropriate team

3. **Ticket Creation**
   - Ticket stored in SQLite database
   - Assigned to support team member
   - Unique ticket ID generated (TKT-YYYYMMDD-XXXXXX)

4. **Notifications**
   - User receives confirmation email
   - Support team receives notification
   - Ticket status set to "Assigned"

5. **Admin Management**
   - Admin views tickets in dashboard
   - Filter and search by various criteria
   - Update ticket status and assign to team
   - Generate reports for auditing

6. **Ticket Resolution**
   - Team member works on ticket
   - Updates status to "In Progress"
   - Adds resolution notes
   - Marks as "Resolved" when complete
   - Final status "Closed" for archived tickets

## 🔐 Security

### Current Implementation
- Session-based authentication for admin portal
- Password hashing using werkzeug.security
- Input validation and sanitization
- HTML escaping to prevent XSS attacks
- CSRF protection with Flask-CORS

### Recommendations for Production
1. Use environment variables for sensitive data
2. Implement proper OAuth2/SSO integration
3. Enable HTTPS/SSL certificates
4. Use database encryption for sensitive data
5. Implement rate limiting
6. Add comprehensive audit logging
7. Use secrets management system
8. Regular security audits

## 📈 Performance Optimization

- Database indexing on frequently searched fields
- Pagination for large result sets
- Caching for support teams and common categorizations
- Async task processing for email notifications
- Client-side form validation to reduce server load

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📚 Common Use Cases

### Creating a Ticket for Network Issues
```
Name: John Smith
Email: john.smith@company.com
Department: Sales
Description: "Cannot conect to WiFi netwrok on my laptop"

System Processing:
- Corrects: "conect" → "connect", "netwrok" → "network"
- Category: Network
- Priority: P3 - Medium
- Assigned Team: Network Support
- Assigned To: John Tech
```

### Admin Filtering for Critical Issues
```
Filter: Status = Open, Priority = P1 - Critical, Category = Email
Result: Shows all unresolved critical email issues
Action: Admin can bulk update or individual ticket management
```

## 🔄 Updating and Maintaining

### Adding New Support Category
1. Add keywords to `CATEGORY_KEYWORDS` in `spelling_corrector.py`
2. Add routing rules to `ticket_router.py`
3. Create new support team in `SUPPORT_TEAMS`

### Modifying Email Templates
Edit the methods in `modules/email_integration.py`:
- `send_ticket_confirmation()`
- `send_ticket_update()`
- `send_team_notification()`

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
rm data/tickets/tickets.db

# Recreate on next run
python app/app.py
```

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)
```

### Email Not Sending
- Verify Office365 credentials
- Check if app password is used (not regular password)
- Verify SMTP settings
- Check firewall/network settings

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Check API documentation
4. Review code comments

## 📄 License

This project is provided as-is for internal business use.

## 🚀 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Automated escalation rules
- [ ] SLA tracking and alerts
- [ ] Integration with ticketing systems (Jira, ServiceNow)
- [ ] Mobile app
- [ ] Voice-based ticket creation
- [ ] AI chatbot for common issues
- [ ] Automated resolution suggestions
- [ ] Sentiment analysis for priority detection

## 📝 Changelog

### Version 1.0.0 (2024-02-09)
- Initial release
- Core functionality implemented
- Web UI with Bootstrap
- Admin dashboard
- Email integration
- Report generation

---

**Built with ❤️ for efficient IT support management**
# auto-ticket-riser
