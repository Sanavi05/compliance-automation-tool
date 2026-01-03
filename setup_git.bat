@echo off
echo Setting up Git repository and pushing to remote...

REM Initialize git if not already initialized
git init

REM Add remote repository
git remote add origin https://github.com/Sanavi05/compliance-automation-tool.git

REM Check current remotes (in case it already exists)
git remote -v

REM Create and switch to a new branch (replace 'your-feature-branch' with your desired branch name)
git checkout -b aml-model-api

REM Add all files
git add .

REM Commit changes
git commit -m "Add AML model API endpoints with FastAPI"

REM Push to the new branch
git push -u origin aml-model-api

echo Done! Your code has been pushed to the 'aml-model-api' branch.
pause

