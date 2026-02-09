# Deployment Guide

This document provides instructions for deploying the IT Support Service Desk system in different environments.

## 🏗️ Development Environment

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)
- Git (optional)

### Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Environment File**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize Database**
   ```bash
   mkdir -p data/tickets data/reports
   python -c "from modules.database import TicketDatabase; TicketDatabase('data/tickets/tickets.db')"
   ```

5. **Run Development Server**
   ```bash
   # From project root
   python app/app.py
   ```

6. **Access Application**
   - Home: http://localhost:5000
   - Admin: http://localhost:5000/admin/login

## 🏢 Production Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Nginx (reverse proxy)
- Gunicorn (WSGI server)
- Systemd (service management)
- SSL certificate

### Installation

1. **Clone Project**
   ```bash
   git clone <repository> /opt/service-desk
   cd /opt/service-desk
   ```

2. **Install System Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv nginx postgresql-client
   ```

3. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Configure Environment**
   ```bash
   sudo cp .env.example /etc/service-desk/.env
   sudo nano /etc/service-desk/.env
   ```

5. **Configure Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/service-desk.service
   ```

   ```ini
   [Unit]
   Description=IT Support Service Desk
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/opt/service-desk
   Environment="PATH=/opt/service-desk/venv/bin"
   ExecStart=/opt/service-desk/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app.app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Enable Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable service-desk
   sudo systemctl start service-desk
   ```

7. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/service-desk
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

8. **Enable SSL (Let's Encrypt)**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

9. **Test and Reload Nginx**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.app:app"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
      - DATABASE_PATH=/app/data/tickets/tickets.db
    restart: always

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: always
```

### Run with Docker
```bash
docker-compose up -d
```

## 🔄 Backup and Recovery

### Database Backup
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp -r /opt/service-desk/data $BACKUP_DIR/data_$DATE
tar -czf $BACKUP_DIR/service-desk_$DATE.tar.gz $BACKUP_DIR/data_$DATE
```

### Automated Backup (Cron)
```bash
# Add to crontab
0 2 * * * /opt/service-desk/backup.sh >> /var/log/service-desk-backup.log 2>&1
```

## 📊 Monitoring

### Application Logs
```bash
sudo journalctl -u service-desk -f
```

### Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Maintenance
```bash
# Check database size
ls -lh data/tickets/tickets.db

# Vacuum database (optimize)
python -c "
import sqlite3
conn = sqlite3.connect('data/tickets/tickets.db')
conn.execute('VACUUM')
conn.close()
print('Database optimized')
"
```

## 🔐 Security Hardening

### 1. Update System
```bash
sudo apt-get update && sudo apt-get upgrade
```

### 2. Configure Firewall
```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 3. Generate Strong Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Update in .env:
```
SECRET_KEY=<generated-key>
```

### 4. Database Encryption
```bash
# Use PostgreSQL with encrypted connection for production
```

### 5. Regular Updates
```bash
# Weekly security updates
sudo apt-get update
sudo apt-get install --only-upgrade
```

## 🚀 Performance Tuning

### Gunicorn Configuration
```ini
# /etc/service-desk/gunicorn.conf.py
workers = 4  # CPU cores * 2 + 1
worker_class = 'sync'
bind = '127.0.0.1:8000'
backlog = 2048
timeout = 30
```

### Nginx Configuration
```nginx
# Add to nginx.conf
worker_processes auto;
keepalive_timeout 65;
client_max_body_size 10M;

# Gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### Database Optimization
```python
# Add indexes for better performance
import sqlite3
conn = sqlite3.connect('data/tickets/tickets.db')
cursor = conn.cursor()

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tickets(status)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON tickets(category)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_created ON tickets(created_timestamp)')

conn.commit()
conn.close()
```

## 📈 Scaling Considerations

### For Single Server
- ✅ Gunicorn with 4-8 workers
- ✅ Nginx as reverse proxy
- ✅ SQLite database (up to 10,000 tickets)

### For Multiple Servers
- Consider PostgreSQL instead of SQLite
- Use load balancer (Nginx, HAProxy)
- Implement session replication
- Centralized logging (ELK stack)
- Shared file storage for reports

## 🔧 Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo journalctl -u service-desk -n 50

# Test manually
cd /opt/service-desk
source venv/bin/activate
python app/app.py
```

### Database Lock
```bash
# Check processes
lsof | grep "tickets.db"

# Kill blocking process
kill -9 <PID>
```

### High Memory Usage
```bash
# Restart service
sudo systemctl restart service-desk

# Check memory
free -h
```

### Nginx Upstream Timeout
```bash
# Increase timeout in nginx.conf
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

## 📋 Maintenance Schedule

### Daily
- Monitor application logs
- Check system resources
- Verify backups

### Weekly
- Review support ticket metrics
- Check for system updates
- Analyze error logs

### Monthly
- Database optimization
- Security audit
- Performance review
- Capacity planning

### Quarterly
- Major updates
- Full disaster recovery test
- Security vulnerability scan

## 📞 Support and Escalation

1. Check application logs
2. Review system resource usage
3. Test database connectivity
4. Verify email service
5. Contact system administrator

---

For additional help, refer to the main [README.md](README.md)
