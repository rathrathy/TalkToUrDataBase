# Use lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else (your code lives in /venv)
COPY . .

# Expose Streamlit’s default port
EXPOSE 8501

# Run the Streamlit app inside the venv folder
CMD ["streamlit", "run", "venv/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
