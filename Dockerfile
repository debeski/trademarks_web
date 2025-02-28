# Use the official Python image
FROM python:3.13

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app


RUN useradd -m vscode && \
    echo 'vscode:123456' | chpasswd && \
    adduser vscode sudo && \
    chown -R vscode:vscode /app

# Copy the entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER vscode

# Copy requirements and install dependencies
COPY --chown=vscode:vscode requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY --chown=vscode:vscode . .

# Expose port 8000 for Django
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
