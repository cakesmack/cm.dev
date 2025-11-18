# PythonAnywhere Deployment Guide

## Pre-Deployment Checklist
- [x] Email notifications working locally
- [x] Updated SMTP to use port 587 (TLS) for PythonAnywhere compatibility
- [ ] Push code to GitHub (recommended)
- [ ] Test email with TLS locally
- [ ] Backup old PythonAnywhere app

---

## Step 1: Remove Old App from PythonAnywhere

1. Log in to your PythonAnywhere account
2. Go to **Web** tab
3. Click on your existing web app
4. Scroll down and click **"Delete web app"** (or disable it if you want to keep it)
5. Optional: Backup any important data from the old app first

---

## Step 2: Upload Your Code

### Option A: Using Git (Recommended)

1. **Push your code to GitHub:**
   ```bash
   cd C:\Users\Craig\Desktop\projects\cm.dev
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **On PythonAnywhere console:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cm.dev.git
   cd cm.dev
   ```

### Option B: Using Zip File

1. Zip the entire `cm.dev` folder
2. Upload to PythonAnywhere using **Files** tab
3. Extract the zip file in your home directory

---

## Step 3: Set Up Virtual Environment

In PythonAnywhere **Bash console**:

```bash
cd ~/cm.dev/backend
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If `weasyprint` fails, you can remove it from requirements.txt (it's for PDF generation).

---

## Step 4: Set Up Environment Variables

Create `.env` file in PythonAnywhere:

```bash
cd ~/cm.dev/backend
nano .env
```

Paste this content (update values as needed):

```env
# Database Configuration
DATABASE_URL=sqlite:///./mackenzie_dev.db

# Security
SECRET_KEY=CHANGE-THIS-TO-A-LONG-RANDOM-STRING-IN-PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
PROJECT_NAME=Craig Mackenzie Portfolio
VERSION=1.0.0
API_PREFIX=/api/v1
ENVIRONMENT=production

# Email Configuration (Hostinger SMTP)
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=587
SMTP_USER=craig@cmack.dev
SMTP_PASSWORD=your-email-password-here
SMTP_FROM_EMAIL=craig@cmack.dev
SMTP_FROM_NAME=Craig Mackenzie Portfolio
NOTIFICATION_EMAIL=craig@cmack.dev
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

**IMPORTANT:** Generate a new SECRET_KEY for production:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Step 5: Initialize Database

```bash
cd ~/cm.dev/backend
source venv/bin/activate
python -c "from app.db import init_db; init_db()"
```

---

## Step 6: Create Web App

1. Go to **Web** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Choose **Manual configuration** (not Flask/Django)
4. Select **Python 3.10**

---

## Step 7: Configure WSGI File

1. In the **Web** tab, find the **"Code"** section
2. Click on the WSGI configuration file link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. **Delete everything** in the file
4. Replace with this:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/cm.dev/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.chdir(project_home)

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/cm.dev/backend/venv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Import FastAPI app
from app.main import app as application
```

**Replace `YOUR_USERNAME` with your actual PythonAnywhere username!**

---

## Step 8: Configure Virtual Environment

In the **Web** tab, find **"Virtualenv"** section:

1. Enter the path to your virtual environment:
   ```
   /home/YOUR_USERNAME/cm.dev/backend/venv
   ```

---

## Step 9: Configure Static Files

In the **Web** tab, scroll to **"Static files"** section:

Add these mappings:

| URL                    | Directory                                           |
|------------------------|-----------------------------------------------------|
| `/static`              | `/home/YOUR_USERNAME/cm.dev/backend/static`         |
| `/uploads`             | `/home/YOUR_USERNAME/cm.dev/backend/static/uploads` |

---

## Step 10: Set Up Custom Domain (cmack.dev)

### On PythonAnywhere:

1. Go to **Web** tab
2. In **"Web app domain"** section, add custom domain:
   - `cmack.dev`
   - `www.cmack.dev`

### On Hostinger (or your domain registrar):

1. Go to DNS settings for cmack.dev
2. Add these DNS records:

**For bare domain (cmack.dev):**
- Type: `A`
- Name: `@`
- Value: Get IP from PythonAnywhere Web tab (shown when you add custom domain)
- TTL: `3600`

**For www subdomain:**
- Type: `CNAME`
- Name: `www`
- Value: `YOUR_USERNAME.pythonanywhere.com`
- TTL: `3600`

**Note:** DNS propagation can take 24-48 hours.

---

## Step 11: Reload Web App

1. Go back to **Web** tab
2. Click the big green **"Reload"** button
3. Wait for it to reload

---

## Step 12: Test Your Site

1. Visit: `https://YOUR_USERNAME.pythonanywhere.com`
2. Test the contact form
3. Check if email notifications arrive at craig@cmack.dev
4. Test admin login
5. Upload a test project with images

---

## Step 13: SSL Certificate (HTTPS)

PythonAnywhere provides free HTTPS for custom domains:

1. In **Web** tab, scroll to **"Security"** section
2. Click **"Force HTTPS"** to redirect HTTP to HTTPS
3. SSL certificates are automatic for custom domains

---

## Troubleshooting

### Error: Module not found
- Check virtual environment path is correct
- Make sure you activated venv before pip install
- Check WSGI file paths

### Email not sending
- Check error logs in PythonAnywhere **"Log files"** section
- Verify SMTP credentials in .env
- Port 587 should work (port 465 is blocked)
- Test SMTP manually:
  ```python
  python3 -c "from app.services import email_service; print(email_service.send_contact_form_notification('Test', 'test@example.com', 'Test message'))"
  ```

### Static files not loading
- Check static file paths in Web tab
- Make sure `/static` directory exists
- Check file permissions

### Database errors
- Make sure database file has write permissions
- Run database initialization again
- Check DATABASE_URL in .env

### 502 Bad Gateway
- Check error log for Python errors
- Verify WSGI file is correct
- Make sure all imports work

---

## Important Notes

1. **Free Account Limitations:**
   - Port 465 (SSL SMTP) is blocked - we use 587 (TLS) ✓
   - Limited CPU time per day
   - App goes to sleep after inactivity (wakes on request)

2. **Database:**
   - Currently using SQLite (fine for portfolio site)
   - For production with high traffic, consider upgrading to PostgreSQL

3. **File Uploads:**
   - Uploaded media is stored in `/static/uploads`
   - Make sure this directory exists and is writable
   - Consider using cloud storage (S3/Cloudinary) for scalability

4. **Backups:**
   - Regularly backup your database file
   - Keep your code in GitHub
   - Export environment variables securely

---

## Quick Commands Reference

```bash
# Activate virtual environment
source ~/cm.dev/backend/venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Check app logs
tail -f ~/cm.dev/backend/logs/app.log

# Run database migrations (if using Alembic)
cd ~/cm.dev/backend
alembic upgrade head

# Test email
python3 -c "from app.services import email_service; email_service.send_contact_form_notification('Test', 'test@example.com', 'Test')"
```

---

## Next Steps After Deployment

- [ ] Set up Google Analytics
- [ ] Add meta tags for SEO
- [ ] Set up sitemap.xml
- [ ] Test on mobile devices
- [ ] Add favicon
- [ ] Set up database backups
- [ ] Monitor error logs regularly
