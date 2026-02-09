# Quick Start Guide

Get the IT Support Service Desk running in 5 minutes!

## 🚀 Installation (Windows)

### Step 1: Install Python
- Download Python 3.8+ from https://www.python.org/downloads/
- During installation, **CHECK** "Add Python to PATH"

### Step 2: Navigate to Project
```cmd
cd "C:\Users\moham\OneDrive\Documents\auto ticket riser"
```

### Step 3: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 4: Create Data Folders
```cmd
mkdir data\tickets
mkdir data\reports
```

### Step 5: Run the Application
```cmd
python app/app.py
```

### Step 6: Open in Browser
- **Home Page**: http://localhost:5000
- **Admin Portal**: http://localhost:5000/admin/login
- **Admin Credentials**: 
  - Username: `admin`
  - Password: `admin123`

That's it! 🎉

---

## 🚀 Installation (macOS/Linux)

### Step 1: Open Terminal

### Step 2: Navigate to Project
```bash
cd ~/OneDrive/Documents/auto\ ticket\ riser
```

### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Create Data Folders
```bash
mkdir -p data/tickets data/reports
```

### Step 6: Run the Application
```bash
python app/app.py
```

### Step 7: Open in Browser
- **Home Page**: http://localhost:5000
- **Admin Portal**: http://localhost:5000/admin/login
- **Admin Credentials**: 
  - Username: `admin`
  - Password: `admin123`

---

## 📝 First Ticket

### Creating Your First Support Ticket

1. Go to http://localhost:5000
2. Fill in the form:
   - **Name**: Your Name
   - **Email**: your.email@company.com
   - **Department**: Your Department
   - **Description**: "I have a problem conecting to the WiFi"
3. Click **Submit Ticket**
4. You'll see your ticket ID (e.g., TKT-20240209-ABC123)

### What Happens Automatically:
✅ Spelling corrected: "conecting WiFi" → "connecting WiFi"  
✅ Category detected: Network  
✅ Priority set: Medium  
✅ Team assigned: Network Support  
✅ Confirmation email sent  

---

## 👨‍💼 Admin Dashboard

### Login
1. Go to http://localhost:5000/admin/login
2. Use: `admin` / `admin123`

### Dashboard Features

#### View Statistics
- Total tickets
- Open vs Resolved
- Category breakdown
- Priority distribution

#### Manage Tickets
1. Click "All Tickets"
2. Use filters to find specific tickets
3. Click ticket to view details
4. Update status and notes
5. Save changes

#### Download Reports
1. Click "Reports"
2. Choose report type:
   - **All Tickets**: Complete list
   - **Date-Wise**: Grouped by date
   - **Category-Wise**: Grouped by category
3. Click "Download Excel"

#### View Teams
- Click "Support Teams"
- See each team's expertise and capacity

---

## 🔧 Stopping the Application

### Windows
- Press `Ctrl + C` in the command prompt

### macOS/Linux
- Press `Ctrl + C` in the terminal

---

## ❓ Common Questions

### Q: Port 5000 already in use?
**A**: Edit `app/app.py` line at the bottom:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Q: How do I add more support teams?
**A**: Edit `modules/ticket_router.py` and add to `SUPPORT_TEAMS` dictionary.

### Q: How do I enable email notifications?
**A**: Edit `app/app.py` around line 150:
```python
email_service = Office365Integration()
email_service.authenticate('your.email@company.com', 'your_password')
```

### Q: Database file location?
**A**: `data/tickets/tickets.db`

### Q: Where are reports saved?
**A**: `data/reports/` directory

### Q: How do I backup the database?
**A**: Simply copy `data/tickets/tickets.db` to a safe location.

---

## 📚 Next Steps

1. **Configure Email Integration** 
   - See `modules/email_integration.py`

2. **Add More Spelling Corrections**
   - Edit `modules/spelling_corrector.py`

3. **Customize Support Teams**
   - Edit `modules/ticket_router.py`

4. **Deploy to Production**
   - See `DEPLOYMENT.md` for production setup

5. **Customize UI**
   - Edit HTML in `app/templates/`
   - Modify CSS in `app/static/css/`

---

## 📞 Need Help?

1. Check the main [README.md](README.md)
2. Review [DEPLOYMENT.md](DEPLOYMENT.md)
3. Check application console for errors
4. Look in `data/tickets/` for database
5. Review code comments in modules

---

## 🎯 Key Files to Know

| File | Purpose |
|------|---------|
| `app/app.py` | Main Flask application |
| `modules/spelling_corrector.py` | Auto-correct IT terms |
| `modules/ticket_router.py` | Auto-assign to teams |
| `modules/database.py` | Store tickets in database |
| `app/templates/index.html` | User ticket form |
| `app/templates/admin_dashboard.html` | Admin panel |
| `app/static/css/style.css` | Main styles |
| `data/tickets/tickets.db` | SQLite database |

---

## 🎓 Learning Resources

- **Python Flask**: https://flask.palletsprojects.com/
- **Bootstrap 5**: https://getbootstrap.com/
- **SQLite**: https://www.sqlite.org/
- **Openpyxl**: https://openpyxl.readthedocs.io/

---

**Enjoy your IT Support Service Desk! 🚀**

Last updated: February 2024
