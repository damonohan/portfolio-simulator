FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure the entrypoint script is executable
RUN chmod +x run_gui.py

# The GUI needs to be able to connect to the X server for display
CMD ["python", "run_gui.py"] 