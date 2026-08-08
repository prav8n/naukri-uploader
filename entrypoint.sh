#!/bin/bash
set -e

echo "=== Naukri Resume Uploader Starting ==="
echo "Timezone: $(date)"

# ── Export env vars so cron can access them ───────────────────────────────────
# Cron runs in a bare environment; we persist env to a file sourced at runtime.
printenv | grep -E "^(NAUKRI_EMAIL|NAUKRI_PASSWORD|RESUME_PATH)" > /etc/environment

# Patch the cron job to source env first
cat > /etc/cron.d/naukri-upload << 'EOF'
CRON_TZ=Asia/Kolkata
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Daily at 8:08 AM IST
8 8 * * * root source /etc/environment && /usr/local/bin/python /app/upload_resume.py >> /app/logs/cron.log 2>&1
EOF

chmod 0644 /etc/cron.d/naukri-upload
crontab /etc/cron.d/naukri-upload

echo "Cron job registered. Next run: 08:08 AM IST daily."
echo "Logs will be written to /app/logs/upload.log and /app/logs/cron.log"

# Run once immediately on container start (optional — comment out if not needed)
if [ "${RUN_ON_START:-false}" = "true" ]; then
    echo "RUN_ON_START=true → running upload now..."
    source /etc/environment
    /usr/local/bin/python /app/upload_resume.py
fi

# Start cron in foreground to keep container alive
echo "Starting cron daemon..."
cron -f
