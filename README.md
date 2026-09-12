# Naukri Resume Auto-Uploader 🤖

Uploads your resume to Naukri twice daily at **9:30 AM and 2:30 PM IST** automatically using Selenium + Docker.

---

## Project Structure

```
naukri-uploader/
├── upload_resume.py      # Selenium script
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── .env.example
├── resume/               # ← place your resume PDF here
│   └── resume.pdf
└── logs/                 # ← auto-created; logs land here
```

---

## Setup (One-Time)

### 1. Clone / copy this folder

### 2. Add your resume
```bash
mkdir -p resume
cp /path/to/your/resume.pdf resume/resume.pdf
```

### 3. Create `.env` with your Naukri credentials
```bash
cp .env.example .env
nano .env   # fill in NAUKRI_EMAIL and NAUKRI_PASSWORD
```

### 4. Build and start
```bash
docker compose up -d --build
```

That's it. The container will stay alive and upload every day at 9:30 AM and 2:30 PM IST.

---

## Verify It's Working

```bash
# Check container is running
docker ps

# Watch live logs
docker logs -f naukri-uploader

# Check upload log on host
tail -f logs/upload.log

# Trigger a manual upload right now (without waiting for cron)
docker exec naukri-uploader \
  bash -c "source /etc/environment && python /app/upload_resume.py"
```

---

## Replace Resume

Just overwrite the file — no rebuild needed:
```bash
cp /path/to/new_resume.pdf resume/resume.pdf
```

---

## Stop / Remove

```bash
docker compose down        # stop
docker compose down --rmi all   # stop + remove image
```

---

## Cron Schedule Reference

The cron entry is `30 9,14 * * *` with `CRON_TZ=Asia/Kolkata` — i.e. **9:30 AM and 2:30 PM IST**
(04:00 and 09:00 UTC).

If you're in a different timezone, edit the cron line in `entrypoint.sh`:
```
30 9,14 * * *    →  MM HH[,HH] * * *   (interpreted in CRON_TZ)
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Login fails | Check credentials in `.env`; Naukri may prompt a CAPTCHA |
| Resume not found | Ensure `resume/resume.pdf` exists on the host |
| Chrome crashes | Increase Docker memory limit (`--memory=2g`) |
| Error screenshot | Check `logs/error_screenshot.png` for a visual snapshot |
| Cron not firing | Run `docker exec naukri-uploader crontab -l` to verify |
