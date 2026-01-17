# 🚀 ProInvestiX v5.1.2 ULTIMATE - Deployment Guide

## Deployment Options

### Option 1: Local Development

```bash
# Clone/Extract project
cd proinvestix

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

Access at: `http://localhost:8501`

---

### Option 2: Streamlit Cloud (Recommended for Demo)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "ProInvestiX v5.1.2 ULTIMATE"
   git remote add origin https://github.com/YOUR_USERNAME/proinvestix.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Main file: `app.py`
   - Click "Deploy"

3. **Set Environment Variables** (in Streamlit Cloud settings)
   ```
   PROINVESTIX_ENV=PRODUCTION
   TICKETCHAIN_SECRET=your-secret-key-here
   ```

---

### Option 3: Docker Deployment

1. **Create Dockerfile** (already included if present)
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY . .
   
   # Expose port
   EXPOSE 8501
   
   # Health check
   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
   
   # Run
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Run**
   ```bash
   docker build -t proinvestix:v5.1.2 .
   docker run -d -p 8501:8501 --name proinvestix \
     -e PROINVESTIX_ENV=PRODUCTION \
     -e TICKETCHAIN_SECRET=your-secret-key \
     proinvestix:v5.1.2
   ```

---

### Option 4: Production Server (Ubuntu/Debian)

1. **System Setup**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3-pip nginx
   ```

2. **Application Setup**
   ```bash
   # Create app directory
   sudo mkdir -p /opt/proinvestix
   sudo chown $USER:$USER /opt/proinvestix
   
   # Extract application
   cd /opt/proinvestix
   unzip proinvestix_v5.1.2_FINAL.zip
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/proinvestix.service
   ```
   
   ```ini
   [Unit]
   Description=ProInvestiX Streamlit Application
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/proinvestix/proinvestix
   Environment="PROINVESTIX_ENV=PRODUCTION"
   Environment="TICKETCHAIN_SECRET=your-secret-key"
   ExecStart=/opt/proinvestix/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
   Restart=always
   RestartSec=3
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable proinvestix
   sudo systemctl start proinvestix
   ```

5. **Nginx Reverse Proxy**
   ```bash
   sudo nano /etc/nginx/sites-available/proinvestix
   ```
   
   ```nginx
   server {
       listen 80;
       server_name proinvestix.ma www.proinvestix.ma;
       
       location / {
           proxy_pass http://127.0.0.1:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 86400;
       }
   }
   ```
   
   ```bash
   sudo ln -s /etc/nginx/sites-available/proinvestix /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d proinvestix.ma -d www.proinvestix.ma
   ```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROINVESTIX_ENV` | No | DEVELOPMENT | Set to PRODUCTION for production |
| `TICKETCHAIN_SECRET` | Yes (prod) | Random | Secret key for blockchain operations |
| `DB_FILE` | No | proinvestix_ultimate.db | SQLite database file path |
| `DB_TYPE` | No | sqlite | Database type (sqlite/postgres) |
| `POSTGRES_HOST` | No | localhost | PostgreSQL host (if using postgres) |
| `POSTGRES_PORT` | No | 5432 | PostgreSQL port |
| `POSTGRES_DB` | No | proinvestix | PostgreSQL database name |
| `POSTGRES_USER` | No | proinvestix | PostgreSQL username |
| `POSTGRES_PASSWORD` | No | - | PostgreSQL password |

---

## Production Checklist

### Security
- [ ] Set `PROINVESTIX_ENV=PRODUCTION`
- [ ] Set strong `TICKETCHAIN_SECRET`
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow 80, 443)
- [ ] Set up backup strategy
- [ ] Review access permissions

### Performance
- [ ] Configure Nginx caching
- [ ] Set up monitoring (e.g., Prometheus, Grafana)
- [ ] Configure log rotation
- [ ] Set resource limits

### Database
- [ ] Backup existing data
- [ ] Consider PostgreSQL for production scale
- [ ] Set up automated backups
- [ ] Test restore procedure

### Monitoring
- [ ] Set up health checks
- [ ] Configure alerting
- [ ] Monitor disk space
- [ ] Track error rates

---

## Demo Credentials

For testing and demonstration:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **IMPORTANT:** Change these credentials in production!

---

## Database Migration

### Reset Database (Development)
```bash
rm proinvestix_ultimate.db
python -c "from database.setup import init_db; init_db()"
python database/generate_demo_data.py
```

### Backup Database
```bash
cp proinvestix_ultimate.db proinvestix_backup_$(date +%Y%m%d).db
```

---

## Troubleshooting

### Application won't start
```bash
# Check logs
journalctl -u proinvestix -f

# Check if port is in use
lsof -i :8501
```

### Database errors
```bash
# Check database integrity
sqlite3 proinvestix_ultimate.db "PRAGMA integrity_check;"

# Verify tables
sqlite3 proinvestix_ultimate.db ".tables"
```

### Permission issues
```bash
# Fix permissions
sudo chown -R www-data:www-data /opt/proinvestix
sudo chmod -R 755 /opt/proinvestix
```

---

## Support

- 📧 tech@proinvestix.ma
- 📧 support@proinvestix.ma
- 📍 Casablanca, Morocco 🇲🇦

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v5.1.2 | Jan 2026 | ULTIMATE release with all features |
| v5.1.1 | Dec 2025 | Bug fixes |
| v5.1.0 | Dec 2025 | Initial release |

---

*ProInvestiX - "We work FOR Morocco, WITH Morocco"*
