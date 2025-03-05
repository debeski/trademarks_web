# Use the pre-built Python base image
FROM debeski/trademarks-base:latest

# Set the working directory inside the container
WORKDIR /app

USER root

# Copy the entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
