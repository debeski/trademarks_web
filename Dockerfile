# Use the pre-built Python base image
FROM debeski/trademarks-base:latest

# Create user with specific UID/GID matching host user
USER vscode

# Create directories and set permissions
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Set the working directory inside the container
WORKDIR /app

# Copy the application files and set ownership
COPY --chown=vscode:vscode . .

# Switch to root for the entrypoint script
USER root

# Copy entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch back to the vscode user
USER vscode

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
