#!/bin/bash
set -e

echo "🔬 ScholarScope - Quick Setup"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
docker-compose up -d postgres
sleep 5
python scripts/init_db.py
python ingestion/ingest_arxiv.py --category cs.AI --max-papers 100
echo "✅ Setup Complete!"
