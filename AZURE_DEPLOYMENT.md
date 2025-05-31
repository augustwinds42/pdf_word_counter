# Deploying to Azure Web App

This guide explains how to deploy the PDF Word Counter Web Application to Azure using Azure Web App Service, which is a cost-effective option for hosting web applications.

## Prerequisites

1. An Azure account (create one at [https://azure.microsoft.com/](https://azure.microsoft.com/) if you don't have one)
2. Azure CLI installed (optional, but helpful)
3. Git installed on your local machine

## Option 1: Deploy using Azure Portal (Easiest)

1. **Create a Web App in Azure Portal**:
   - Go to [Azure Portal](https://portal.azure.com/)
   - Click "Create a resource" > "Web App"
   - Fill in the details:
     - Resource Group: Create new or use existing
     - Name: Choose a unique name (e.g., pdf-word-counter)
     - Publish: Code
     - Runtime stack: Python 3.9 or later
     - Operating System: Linux
     - Region: Choose the closest to your users
     - App Service Plan: Create new (Basic B1 is a good balance of price and performance, or Free tier for testing)
   - Click "Review + create", then "Create"

2. **Set up GitHub Actions (or other deployment method)**:
   - In the Azure Portal, go to your newly created Web App
   - In the left menu, under "Deployment", click "Deployment Center"
   - Select your source control system (GitHub, Azure Repos, etc.)
   - Follow the prompts to connect to your repository and set up continuous deployment

3. **Configure Application Settings**:
   - In the Azure Portal, go to your Web App
   - In the left menu, under "Settings", click "Configuration"
   - Add the following application settings:
     - Key: `WEBSITE_WEBDEPLOY_USE_SCM` Value: `false`
     - Key: `SCM_DO_BUILD_DURING_DEPLOYMENT` Value: `true`
     - Key: `FLASK_APP` Value: `app.py`

4. **Add a startup command**:
   - In the same Configuration page, go to "General settings"
   - Set the startup command to: `gunicorn --bind=0.0.0.0 --timeout 600 wsgi:application`

## Option 2: Deploy using Azure CLI

1. **Create a Web App using Azure CLI**:
   ```bash
   # Login to Azure
   az login

   # Create a resource group
   az group create --name pdf-word-counter-rg --location eastus

   # Create an App Service Plan (Basic B1 tier)
   az appservice plan create --name pdf-word-counter-plan --resource-group pdf-word-counter-rg --sku B1 --is-linux

   # Create a Web App
   az webapp create --resource-group pdf-word-counter-rg --plan pdf-word-counter-plan --name your-unique-app-name --runtime "PYTHON:3.9"

   # Configure the deployment source (local Git)
   az webapp deployment source config-local-git --name your-unique-app-name --resource-group pdf-word-counter-rg
   ```

2. **Configure Application Settings**:
   ```bash
   # Set application settings
   az webapp config appsettings set --resource-group pdf-word-counter-rg --name your-unique-app-name --settings FLASK_APP=app.py SCM_DO_BUILD_DURING_DEPLOYMENT=true

   # Set the startup command
   az webapp config set --resource-group pdf-word-counter-rg --name your-unique-app-name --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 wsgi:application"
   ```

3. **Deploy your code**:
   ```bash
   # Add the Azure remote to your git repository
   git remote add azure <git-url-from-previous-step>

   # Push your code to Azure
   git push azure main
   ```

## Option 3: Deploy using GitHub Actions (Recommended)

This approach automates your deployment process with continuous integration and testing.

1. **Create a Web App in Azure Portal**:
   - Follow the steps in Option 1 to create a Web App

2. **Get your Web App Publish Profile**:
   - In the Azure Portal, go to your Web App
   - Click on "Get publish profile" and download the file
   - This file contains credentials needed for GitHub Actions

3. **Configure GitHub Secrets**:
   - In your GitHub repository, go to Settings > Secrets and Variables > Actions
   - Add the following secrets:
     - Name: `AZURE_WEBAPP_NAME` Value: Your web app name (e.g., pdf-word-counter)
     - Name: `AZURE_WEBAPP_PUBLISH_PROFILE` Value: The entire contents of the publish profile file you downloaded

4. **Use the existing GitHub Actions workflow**:
   - The repository already contains a workflow file at `.github/workflows/azure-deploy.yml`
   - This workflow:
     - Runs on pushes to the main branch
     - Sets up Python
     - Installs dependencies
     - Runs tests with coverage
     - Deploys to Azure if tests pass

5. **Push to GitHub**:
   - Commit your changes and push to the main branch
   - GitHub Actions will automatically deploy your application to Azure

6. **Configure Application Settings in Azure**:
   - Set the startup command to: `gunicorn --bind=0.0.0.0 --timeout 600 wsgi:application`
   - Add any additional environment variables your application needs

## Troubleshooting

- **Application Error or 500 Server Error**:
  - Check the application logs in Azure Portal: Go to your Web App > Monitoring > Log stream
  - Ensure all dependencies are listed in `requirements.txt`

- **Slow Uploads or Timeouts**:
  - You may need to increase the timeout settings in your App Service configuration
  - For larger PDFs, consider upgrading to a higher tier App Service Plan

## Cost Optimization

- For the cheapest option, use the **Free** tier for development/testing (limited to 60 minutes of CPU time per day)
- For production with low traffic, **Basic B1** (~$13/month) is sufficient
- Enable auto-scaling if your application sees variable traffic
- Consider turning off the Web App when not in use to save costs

## Monitoring

- Set up Azure Application Insights for monitoring your application
- Configure alerts for errors or performance issues

Remember to test your application thoroughly before deploying to production!
