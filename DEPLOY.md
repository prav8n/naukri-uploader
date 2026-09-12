# Deploying to Oracle Cloud (Ampere A1 / ARM64)

This runs the uploader 24/7 on your LedgerIQ Oracle VM so your laptop doesn't
have to be on. It fires **daily at 9:30 AM and 2:30 PM IST** and uses whatever PDF is sitting
at `resume/Praveen_Choudhary_Data_Scientist.pdf` on the VM at that moment.

> **Why the code changed:** Oracle Ampere A1 is ARM64. The old Dockerfile
> downloaded x86-64 Google Chrome, which cannot run on ARM. It now installs
> Debian's `chromium` + `chromium-driver`, which build for the host arch and work
> on both ARM64 and x86.

---

## A. One-time: push the project to GitHub (from your laptop)

Secrets and your resume are gitignored, so only code goes up. **Make the repo private anyway.**

```bash
cd ~/Desktop/naukri-uploader/naukri-uploader
git init
git add .
git commit -m "Naukri resume uploader (ARM64-ready)"

# Create a PRIVATE repo and push (using GitHub CLI):
gh repo create naukri-uploader --private --source=. --push
# ...or create it manually on github.com, then:
# git remote add origin git@github.com:<you>/naukri-uploader.git
# git push -u origin main
```

---

## B. One-time: set up the Oracle VM

SSH in (Ubuntu image → user is `ubuntu`; Oracle Linux → `opc`):

```bash
ssh ubuntu@<YOUR_VM_PUBLIC_IP>
```

### 1. Install Docker (skip if LedgerIQ already uses it)

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
sudo systemctl enable --now docker   # survives VM reboots
# log out and back in so the group change takes effect
exit
```

### 2. Clone the repo

```bash
ssh ubuntu@<YOUR_VM_PUBLIC_IP>
git clone git@github.com:<you>/naukri-uploader.git
cd naukri-uploader
```

### 3. Add credentials (not in git)

```bash
cp .env.example .env
nano .env    # fill NAUKRI_EMAIL and NAUKRI_PASSWORD
```

### 4. Add your resume (not in git — copy it from your laptop)

Run this **from your laptop**, in a second terminal:

```bash
scp ~/Desktop/naukri-uploader/naukri-uploader/resume/Praveen_Choudhary_Data_Scientist.pdf \
    ubuntu@<YOUR_VM_PUBLIC_IP>:~/naukri-uploader/resume/Praveen_Choudhary_Data_Scientist.pdf
```

### 5. Build and start

Back on the VM:

```bash
docker compose up -d --build
```

That's it. `restart: unless-stopped` + `systemctl enable docker` means it comes
back automatically after any reboot. **No inbound ports needed** — the uploader
only makes outbound connections, so you don't touch Oracle's security lists.

---

## C. Verify it's working

```bash
docker ps                                   # container should be "Up"
docker exec naukri-uploader crontab -l      # shows: 30 9,14 * * *  (CRON_TZ=Asia/Kolkata)
docker exec naukri-uploader date            # should print IST

# Force an upload right now instead of waiting for the next scheduled run:
docker exec naukri-uploader bash -c "source /etc/environment && python /app/upload_resume.py"

# Watch logs
docker logs -f naukri-uploader
tail -f logs/upload.log
```

---

## D. Updating your resume later (the everyday workflow)

Whenever you have a new/updated resume, run **one command from your laptop**:

```bash
scp /path/to/new_resume.pdf \
    ubuntu@<YOUR_VM_PUBLIC_IP>:~/naukri-uploader/resume/Praveen_Choudhary_Data_Scientist.pdf
```

The resume folder is volume-mounted into the container, so this **overwrites the
old file in place** — no rebuild, no restart. The next scheduled run (9:30 AM or
2:30 PM IST) uploads the new version automatically.

Want it live on Naukri immediately (don't wait for the next run)? Follow the scp with:

```bash
ssh ubuntu@<YOUR_VM_PUBLIC_IP> \
  "docker exec naukri-uploader bash -c 'source /etc/environment && python /app/upload_resume.py'"
```

---

## E. Pushing code changes later

```bash
# laptop
git commit -am "tweak"; git push
# VM
cd ~/naukri-uploader && git pull && docker compose up -d --build
```
