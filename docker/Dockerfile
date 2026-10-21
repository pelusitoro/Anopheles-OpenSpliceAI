FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Native OpenMP runtime used by scientific Python packages on Linux.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-openspliceai.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-openspliceai.txt

COPY app.py ./

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
