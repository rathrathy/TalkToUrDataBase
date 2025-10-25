# Use official Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else into the container
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app (adjust path if needed)
CMD ["streamlit", "run", "venv/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
