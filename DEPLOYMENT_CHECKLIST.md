# Azure Deployment Checklist

Use this checklist to ensure your deployment to Azure is successful:

## Local Repository Setup ✓
- [x] Initialize Git repository
- [x] Create .gitignore file
- [x] Configure uploads folder with .gitkeep
- [x] Ensure all dependencies are in requirements.txt
- [x] Create GitHub Actions workflow file
- [x] Commit all files to Git
- [x] Rename default branch to 'main'

## GitHub Setup ☐
- [ ] Create GitHub repository
- [ ] Push local repository to GitHub:
  ```bash
  git remote add origin https://github.com/YOUR-USERNAME/pdftest.git
  git push -u origin main
  ```

## Azure Web App Setup ☐
- [ ] Create Azure Web App (see AZURE_DEPLOYMENT.md)
- [ ] Download publish profile
- [ ] Set up GitHub Secrets:
  - [ ] AZURE_WEBAPP_NAME
  - [ ] AZURE_WEBAPP_PUBLISH_PROFILE
- [ ] Configure Web App settings (see AZURE_CONFIGURATION.md):
  - [ ] Application settings
  - [ ] Startup command
  - [ ] Always On (if using Basic tier or higher)
  - [ ] HTTPS Only

## Post-Deployment Verification ☐
- [ ] Verify the application URL works
- [ ] Test PDF upload functionality
- [ ] Test word search functionality
- [ ] Check application logs if there are issues
- [ ] Verify test coverage meets targets (≥85%)

## Maintenance ☐
- [ ] Set up monitoring alerts
- [ ] Configure auto-scaling (if needed)
- [ ] Set up backup policies
- [ ] Document regular maintenance procedures

## Security ☐
- [ ] Enable HTTPS Only
- [ ] Set up authentication (if needed)
- [ ] Configure firewall rules (if needed)
- [ ] Set up rate limiting for uploads

This checklist ensures you've completed all necessary steps for a successful Azure deployment using GitHub Actions.
