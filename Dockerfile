# Use official Python image as base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot source code
#COPY ./src ./src

#COPY ./data ./data

# Run the bot
CMD ["python", "src/main.py"]
