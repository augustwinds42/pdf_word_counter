# Azure Web App Configuration Instructions

After creating your Azure Web App, follow these steps to configure it properly:

## 1. Application Settings

In the Azure Portal, go to your Web App > Settings > Configuration > Application settings:

Add these application settings:

- **WEBSITE_WEBDEPLOY_USE_SCM**: `false`
- **SCM_DO_BUILD_DURING_DEPLOYMENT**: `true`
- **FLASK_APP**: `app.py`

## 2. Startup Command

In the same Configuration page, go to the General settings tab:

Set the startup command to:
```
gunicorn --bind=0.0.0.0 --timeout 600 wsgi:application
```

## 3. Always On

If you're using a Basic tier or higher (not Free tier), enable "Always On" to keep your application responsive.

## 4. HTTPS Only

Enable "HTTPS Only" for better security.

## 5. Verify Deployment

After GitHub Actions deploys your application:

1. Go to your Web App URL (e.g., https://pdfwordcounter.azurewebsites.net)
2. Test uploading a PDF and searching for words
3. Check the logs if you encounter any issues: Web App > Monitoring > Log stream

Remember to save all your configuration changes before leaving the Azure Portal.
