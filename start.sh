#!/bin/bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_URL=http://localhost:8000 uv run streamlit run ui/app.py --server.port 7860 --server.address 0.0.0.0 --server.headless true
