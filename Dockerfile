#Build stage
FROM python:3.14-slim AS build

WORKDIR /app

#Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

#Copy the build stage
COPY /src /app/src
RUN chown -R appuser:appuser /app

#Switch to non-root user
USER appuser

#Expose
EXPOSE 8000

#Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]