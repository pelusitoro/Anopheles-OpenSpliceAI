FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

COPY docker/requirements-openspliceai.txt ./

# mappy is distributed as source and needs a compiler and zlib headers.
# Remove build tools after installation so the runtime image stays smaller.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential zlib1g-dev zlib1g libgomp1 \
    && python -m pip install --upgrade pip \
    && python -m pip install -r requirements-openspliceai.txt \
    && apt-get purge -y --auto-remove build-essential zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY docker/app.py ./
COPY AgamI_model_best.pt /models/AgamI_model_best.pt

ENV OPENSPLICEAI_MODEL=/models/AgamI_model_best.pt

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
