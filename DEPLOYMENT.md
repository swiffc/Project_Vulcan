# Project Vulcan - Deployment

This document provides an overview of the deployment process for Project Vulcan.

## Render Deployment

For a detailed step-by-step guide on deploying to Render, please see the [Deployment Checklist](DEPLOYMENT_CHECKLIST.md).

## Docker Deployment

To deploy the application using Docker, you can use the `docker-compose.yml` file in the root of the project.

```bash
docker-compose up -d
```

This will start all the services defined in the `docker-compose.yml` file in the background.

## Monitoring

The application is configured to use Sentry for error and performance monitoring. To enable Sentry, you need to set the `SENTRY_DSN` and `NEXT_PUBLIC_SENTRY_DSN` environment variables.

## Backup and Restore

For information on how to back up and restore the application data, please see the [Backup and Restore Guide](docs/BACKUP_AND_RESTORE.md).
