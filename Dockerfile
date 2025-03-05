# Use the pre-built Python base image
FROM debeski/trademarks-base:latest

# Create a new user for security and add to sudoers (granting superuser privileges)
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN addgroup --gid $GROUP_ID vscode && \
    adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Ensure /app directory is owned by vscode user and group
RUN mkdir -p /app && chown -R vscode:vscode /app

# Create user with specific UID/GID matching host user
USER vscode

# Set the working directory inside the container
WORKDIR /app

# Create directories and set permissions
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Copy the application files and set ownership
COPY --chown=vscode:vscode . .

USER root

# Copy entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER vscode

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
