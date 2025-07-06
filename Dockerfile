FROM python:3.10.18-bookworm

RUN mkdir -p /app/cctv-app
WORKDIR /app/cctv-app
COPY requirements.txt /app/cctv-app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
RUN chmod +x /app/cctv-app/start.sh
CMD ["/app/cctv-app/start.sh"]
