# Use the official Python base image
FROM python:3.10.13-slim

# Set the working directory in the container
WORKDIR /frontend

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend application files to the working directory
COPY . .

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]

# Expose the port Streamlit runs on
EXPOSE 8501

