#!/bin/bash
# run_scheduler.sh — Jalankan scheduler di background
# chmod +x run_scheduler.sh && ./run_scheduler.sh

echo "════════════════════════════════════════"
echo "  Run AbsensiChecker Scheduler"
echo "════════════════════════════════════════"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment tidak ditemukan!"
    echo "   Jalankan setup.sh terlebih dahulu:"
    echo "   bash setup.sh"
    exit 1
fi

# Activate venv
echo "[1/3] Activate virtual environment..."
source venv/bin/activate

# Create logs directory if not exists
echo "[2/3] Create logs directory..."
mkdir -p logs

# Run scheduler in background
echo "[3/3] Run scheduler in background..."
nohup python scheduler.py > logs/scheduler_background.log 2>&1 &
PID=$!

echo ""
echo "✅ Scheduler running in background!"
echo ""
echo "Process ID (PID): $PID"
echo "Log file: logs/scheduler_background.log"
echo ""
echo "════════════════════════════════════════"
echo ""
echo "📝 Lihat log real-time:"
echo "   tail -f logs/scheduler.log"
echo ""
echo "⛔ Stop scheduler:"
echo "   kill $PID"
echo ""
