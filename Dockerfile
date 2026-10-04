FROM python:3.11-slim

# Prevent Python from creating .pyc files
# and keep logs immediately visible.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Tesseract OCR required by pytesseract.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Application directory
WORKDIR /app

# Copy dependency file first so Docker can cache
# the dependency-installation layer.
COPY requirements.txt .

# Upgrade pip and install Python dependencies.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the project into the container.
COPY . .

# Render provides its own PORT environment variable.
# 8501 is used as the local/default Streamlit port.
EXPOSE 8501

# Start the existing VidyānVaya AI application.
CMD ["sh", "-c", "python -m streamlit run app/main.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true"]