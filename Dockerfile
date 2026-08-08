FROM python:3.11-slim

# ── Timezone (so cron + logs are in IST) ────────────────────────────────────────
ENV TZ=Asia/Kolkata

# ── System deps ────────────────────────────────────────────────────────────────
# chromium + chromium-driver come from Debian and are built for the host arch,
# so this image works on both ARM64 (Oracle Ampere A1) and x86-64.
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron tzdata ca-certificates \
    chromium chromium-driver \
    fonts-liberation \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/* \
    # Smoke test — fail the build early if the browser/driver are missing
    && chromium --version \
    && chromedriver --version

# ── Python deps ────────────────────────────────────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── App files ──────────────────────────────────────────────────────────────────
COPY upload_resume.py .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Directories (also provided via volume mounts at runtime)
RUN mkdir -p /app/logs /app/resume

CMD ["/entrypoint.sh"]
