# Step 1: Base image
FROM python:3.11-slim

# Step 2: Set working directory inside container
WORKDIR /app

# Step 3: Copy requirement file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the application code
COPY app.py .

# Step 5: Create a logs directory inside the container
RUN mkdir -p /app/logs

# Step 6: Run the script when container starts
CMD ["python","-u", "app.py"]