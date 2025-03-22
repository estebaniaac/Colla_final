FROM python:3.11-slim

WORKDIR /app

COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Default command 
CMD ["python", "my_collaborative/send_to_speckle.py"]
