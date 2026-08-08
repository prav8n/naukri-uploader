#!/bin/bash
cd ~/Desktop/naukri-uploader/naukri-uploader

echo "=============================="
echo "🐳 CONTAINER STATUS"
echo "=============================="
docker ps | grep naukri

echo ""
echo "=============================="
echo "🔄 RESTART COUNT"
echo "=============================="
docker inspect naukri-uploader --format='Restarts: {{.RestartCount}}'

echo ""
echo "=============================="
echo "⏰ CRON JOB"
echo "=============================="
docker exec naukri-uploader cat /etc/cron.d/naukri-upload

echo ""
echo "=============================="
echo "🕐 CONTAINER TIME"
echo "=============================="
docker exec naukri-uploader date

echo ""
echo "=============================="
echo "📋 LAST 5 LOG ENTRIES"
echo "=============================="
grep -E "Started|Completed|failed|ERROR" logs/upload.log | tail -5

echo ""
echo "=============================="
echo "✅ SUCCESS COUNT"
echo "=============================="
echo -n "Total successful uploads: "
grep "Upload Completed Successfully" logs/upload.log | wc -l

echo ""
echo "=============================="
echo "💻 SYSTEM UPTIME"
echo "=============================="
uptime
