# Deployment Guide - Render

This guide provides detailed instructions for deploying your portfolio site to Render.

## Understanding Render's Free vs Paid Tiers

### Free Tier Limitations ⚠️
- **SQLite database gets wiped** on every deploy or service restart
- **No persistent disk storage** - uploaded files are lost
- Services spin down after 15 minutes of inactivity
- **Admin credentials are lost** after each deploy/restart

### Paid Tier Benefits ✅
- **PostgreSQL database** with persistent storage
- Database persists across deploys
- Admin credentials and data are saved permanently
- No spin-down - always available
- Better performance and uptime

**Recommendation**: For a production portfolio site with admin functionality, upgrade to a paid plan ($7/month for web service + $7/month for PostgreSQL = $14/month total).

---

## Deployment Options

### Option 1: Free Tier (For Testing Only)

If you're on the free tier, you'll need to recreate the admin user after every deploy.

#### Quick Admin Reset (Free Tier)

1. After each deploy, go to your Render dashboard: https://dashboard.render.com
2. Open your web service
3. Click the **Shell** tab on the left
4. Run the reset script:
   ```bash
   cd backend
   python reset_admin.py
   ```

This will create/reset your admin user with:
- **Email**: `admin@mackenzie-dev.com`
- **Password**: `admin123`

**⚠️ IMPORTANT: Change the password immediately after logging in!**

---

### Option 2: Paid Tier with PostgreSQL (Recommended for Production)

This is the proper production setup where your data persists permanently.

#### Step 1: Upgrade Your Web Service to Paid Plan

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your web service (e.g., "mackenzie-dev-backend")
3. Navigate to **Settings** → **Instance Type**
4. Upgrade to **Starter** plan ($7/month)
5. Click **Save Changes**

#### Step 2: Create PostgreSQL Database

1. In Render dashboard, click **New +** → **PostgreSQL**
2. Configure database:
   - **Name**: `mackenzie-dev-db` (or your preferred name)
   - **Database**: `mackenzie_dev`
   - **User**: Auto-generated (keep default)
   - **Region**: **Same region as your web service** (important!)
   - **Instance Type**: Select **Starter** ($7/month)
   - **PostgreSQL Version**: 16 (recommended)
3. Click **Create Database**
4. Wait for database to provision (~2-3 minutes)

#### Step 3: Get Database Connection String

1. Go to your PostgreSQL database in Render dashboard
2. Scroll down to the **Connections** section
3. **Copy the "Internal Database URL"** (starts with `postgres://`)

   Example format:
   ```
   postgres://user:password@dpg-xxxxx/database
   ```

   **Important:** Use the **Internal URL**, not the External URL (Internal is faster and free)

#### Step 4: Update Environment Variables

1. Go to your **web service** in Render dashboard
2. Click **Environment** in the left sidebar
3. Find the `DATABASE_URL` variable (or add it if missing)
4. **Update/Add these variables:**

```bash
DATABASE_URL=postgres://user:password@dpg-xxxxx/database
```
(Paste your actual Internal Database URL from Step 3)

```bash
SECRET_KEY=<generate-secure-key-see-below>
```

```bash
ENVIRONMENT=production
```

**To generate a secure SECRET_KEY**, run this locally:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as your SECRET_KEY value.

5. Click **Save Changes**
6. Your service will automatically redeploy (takes ~2-3 minutes)

#### Step 5: Run Database Migrations

After the redeploy completes:

1. Go to your web service in Render dashboard
2. Click **Shell** in the left sidebar (wait for it to connect)
3. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> 123abc, initial migration
INFO  [alembic.runtime.migration] Running upgrade 123abc -> 456def, add projects
```

If you see these messages, migrations ran successfully! ✅

#### Step 6: Create Admin User (One-Time Setup)

Now create your admin user in the persistent PostgreSQL database.

**Method 1: Using Python Shell in Render (Recommended)**

In the Render Shell (make sure you're still in `/backend`):

```bash
python
```

Then paste this Python code (update the password to your own secure password):

```python
from app.db import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()

# Check if admin already exists
existing_admin = db.query(User).filter(User.email == "admin@mackenzie-dev.com").first()

if not existing_admin:
    admin = User(
        email="admin@mackenzie-dev.com",
        hashed_password=get_password_hash("YourSecurePassword123!"),
        full_name="Craig Mackenzie",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("✅ Admin user created successfully!")
    print(f"Email: {admin.email}")
else:
    print("⚠️ Admin user already exists")
    print(f"Email: {existing_admin.email}")

db.close()
exit()
```

**Method 2: Using Reset Script (Quick but less secure)**

```bash
cd backend
python reset_admin.py
```

This creates admin with default password `admin123`. **Change it immediately after logging in!**

---

## Verifying Your Deployment

### 1. Check Service Health

Visit in your browser or use curl:
```bash
https://your-app-name.onrender.com/health
```

**Expected response:**
```json
{"status": "healthy"}
```

### 2. Test Admin Login

1. Visit: `https://your-app-name.onrender.com/admin/login`
2. Enter your admin credentials
3. You should see the admin dashboard
4. Try creating a test project to verify database persistence

### 3. Verify PostgreSQL Connection

In Render Shell:
```bash
cd backend
python -c "from app.db import engine; print(engine.url)"
```

Should show your PostgreSQL URL (password will be hidden).

### 4. Test Data Persistence

1. Create a project in the admin panel
2. Trigger a manual redeploy: Dashboard → Deploy → Deploy latest commit
3. After redeploy, check if your project still exists
4. ✅ If it persists, you're successfully using PostgreSQL!

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError" after deploy

**Cause:** requirements.txt is missing a dependency

**Solution:**
```bash
# Locally, regenerate requirements:
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements.txt"
git push
```

### Issue: "relation 'users' does not exist" or similar SQL errors

**Cause:** Database migrations haven't been run

**Solution:** Run migrations in Render Shell:
```bash
cd backend
alembic upgrade head
```

### Issue: Admin user not found after deploy (Free Tier)

**Cause:** This is expected on free tier - SQLite database resets

**Solution:** Either:
- Upgrade to paid tier with PostgreSQL ($14/month)
- OR run `python reset_admin.py` after each deploy

### Issue: "Connection to server failed"

**Cause:** DATABASE_URL is incorrect or database is in different region

**Solution:**
1. Verify DATABASE_URL in Environment variables
2. Use **Internal Database URL**, not External
3. Ensure database and web service are in the **same region**
4. Check database status (should say "Available")

### Issue: Uploaded images disappear

**Cause:** On free tier, disk storage is not persistent

**Solution:**
- Upgrade to paid tier
- OR implement cloud storage (AWS S3, Cloudinary, etc.)

### Issue: Service keeps spinning down

**Cause:** Free tier services spin down after 15 minutes of inactivity

**Solution:**
- Upgrade to paid tier ($7/month) for always-on service
- OR accept the spin-down behavior for testing

---

## Environment Variables Reference

### Required Variables

```bash
# Database (PostgreSQL for paid tier)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Security
SECRET_KEY=your-super-secure-secret-key-here

# Environment
ENVIRONMENT=production
```

### Optional Variables (for future features)

```bash
# CORS (if you add a separate frontend)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (for contact form notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
NOTIFICATION_EMAIL=your-email@gmail.com
```

---

## Updating Your Deployed Site

### Standard Updates (No Database Changes)

1. **Make changes locally**
2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your update description"
   git push origin main
   ```
3. **Render auto-deploys** from your GitHub repository
4. Monitor deploy logs in Render dashboard

### Updates with Database Schema Changes

1. **Create migration locally:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of schema changes"
   ```

2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add database migration: description"
   git push origin main
   ```

3. **After Render deploys, run migration in Shell:**
   ```bash
   cd backend
   alembic upgrade head
   ```

---

## Cost Breakdown

### Free Tier (Testing Only)
| Service | Cost |
|---------|------|
| Web Service (Free) | $0/month |
| Database | None (SQLite, resets) |
| **Total** | **$0/month** |
| **Limitation** | Data doesn't persist |

### Paid Tier (Production)
| Service | Plan | Cost |
|---------|------|------|
| Web Service | Starter | $7/month |
| PostgreSQL | Starter | $7/month |
| **Total** | | **$14/month** |
| **Benefit** | Persistent data, always-on |

---

## Production Checklist

Before going live with real data:

- [ ] ✅ Upgrade web service to Starter ($7/month)
- [ ] ✅ Create PostgreSQL database ($7/month)
- [ ] ✅ Update `DATABASE_URL` environment variable
- [ ] ✅ Generate and set secure `SECRET_KEY`
- [ ] ✅ Run database migrations (`alembic upgrade head`)
- [ ] ✅ Create admin user with **strong, unique password**
- [ ] ✅ Test admin login
- [ ] ✅ Create test project and verify it persists after redeploy
- [ ] ✅ Upload test images
- [ ] ✅ Test contact form (if implemented)
- [ ] ✅ Verify site loads on mobile
- [ ] ✅ Set up custom domain (optional)
- [ ] ✅ Enable HTTPS (automatic on Render)

---

## Quick Reference Commands (Render Shell)

```bash
# Navigate to backend
cd backend

# Check Python version
python --version

# Run migrations
alembic upgrade head

# Check current migration status
alembic current

# View migration history
alembic history

# Reset admin user (creates default admin)
python reset_admin.py

# Open Python shell
python

# Check database connection
python -c "from app.db import engine; print(engine.url)"

# List all database users
python -c "from app.db import SessionLocal; from app.models.user import User; db = SessionLocal(); users = db.query(User).all(); [print(f'{u.email} - {u.role}') for u in users]; db.close()"

# Check if PostgreSQL is being used
python -c "from app.db import engine; print('PostgreSQL' if 'postgresql' in str(engine.url) else 'SQLite')"
```

---

## Connecting to PostgreSQL Locally (Optional)

If you want to connect to your Render PostgreSQL from your local machine:

1. Get **External Database URL** from Render dashboard (PostgreSQL → Connections)
2. Install PostgreSQL client:
   ```bash
   # Windows: Download from postgresql.org
   # Mac: brew install postgresql
   ```
3. Connect:
   ```bash
   psql "postgresql://user:pass@host:port/database"
   ```

---

## Support & Troubleshooting Resources

### Render Dashboard Sections

- **Logs**: View application logs and errors
- **Metrics**: CPU, memory, request statistics
- **Events**: Deploy history and status
- **Shell**: Interactive terminal access
- **Environment**: Manage environment variables

### Useful Links

- Render Documentation: https://docs.render.com/
- Render Status: https://status.render.com/
- Render Community: https://community.render.com/

### Debugging Steps

1. **Check Logs first**: Dashboard → Your Service → Logs
2. **Check Database status**: Dashboard → PostgreSQL → Status
3. **Verify environment variables**: Dashboard → Service → Environment
4. **Test locally** with same config to isolate issues
5. **Check Render Status page** for platform issues

---

## Next Steps After Successful Deployment

1. ✅ **Secure your admin account**
   - Change password from default if used
   - Use strong, unique password
   - Enable 2FA on your Render account

2. 📝 **Add content**
   - Create your project portfolio entries
   - Upload project images
   - Write case studies

3. 🌐 **Set up custom domain** (Optional)
   - Add domain in Render dashboard
   - Update DNS records at your registrar
   - SSL is automatic

4. 📊 **Monitor your site**
   - Check logs regularly
   - Monitor database size
   - Set up uptime monitoring (e.g., UptimeRobot)

5. 🔄 **Plan backups**
   - Render PostgreSQL includes daily backups
   - Export data periodically
   - Keep code in GitHub

---

**Last Updated**: January 2025
**For**: Render Deployment (PostgreSQL + FastAPI)

