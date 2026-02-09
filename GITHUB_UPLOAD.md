# GitHub Upload Instructions

Follow these steps to upload this project to GitHub from VS Code:

## Prerequisites
- Git installed on your system (https://git-scm.com/download/win)
- GitHub account (https://github.com)

## Step 1: Install Git (if not already installed)
Download and install Git for Windows from: https://git-scm.com/download/win

## Step 2: Initialize Git Repository
Open VS Code integrated terminal (`Ctrl + ```) and run:

```powershell
cd "c:\Users\moham\OneDrive\Documents\auto ticket riser"
git init
git add .
git commit -m "Initial commit: IT Service Desk Automation System

- Complete ticket management system
- Admin dashboard with statistics
- Support staff and department admin logins
- Excel report generation (5 report types)
- Ticket tracking by ID
- Asset ID field enforcement
- Activity history and audit trail"
```

## Step 3: Create Repository on GitHub
1. Go to https://github.com/new
2. **Repository name**: `auto-ticket-riser` (or your preferred name)
3. **Description**: "IT Service Desk Automation System with Flask, SQLite, and Bootstrap"
4. **Visibility**: Choose Public or Private
5. Click **Create Repository**

## Step 4: Add Remote and Push
In VS Code terminal, run:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/auto-ticket-riser.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Step 5: Authenticate with GitHub
When prompted, choose:
- **HTTPS**: Enter your GitHub PAT (Personal Access Token)
  - Go to GitHub Settings > Developer settings > Personal access tokens
  - Click "Generate new token"
  - Select scopes: `repo`, `workflow`, `admin:public_key`
  - Copy and paste the token in VS Code

OR

- **SSH**: Set up SSH key authentication (recommended)
  - Follow: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

## Step 6: Verify Upload
1. Go to your GitHub repository URL
2. Verify all files are present
3. Check commits: Click commits tab to see your initial commit

## Future Updates
To push updates to GitHub:

```powershell
git add .
git commit -m "Your commit message"
git push
```

## Project Structure in GitHub
Your uploaded project will have this structure:

```
auto-ticket-riser/
├── app/
│   ├── app.py                 # Main Flask application
│   ├── templates/             # HTML templates
│   └── static/
│       ├── css/               # Stylesheets
│       └── js/                # JavaScript
├── modules/
│   ├── database.py            # Database management
│   ├── email_integration.py   # Email handling
│   ├── spelling_corrector.py  # Spell checker
│   └── ticket_router.py       # Ticket routing
├── data/
│   ├── reports/               # Generated Excel files
│   └── tickets/               # SQLite database
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
└── [other docs]
```

## Important Notes
- `.gitignore` is configured to exclude:
  - Virtual environment (`.venv/`)
  - Generated Excel reports
  - Database files (*.db)
  - IDE settings
  - Python cache files
  
- Sensitive information (.env files) are NOT pushed to GitHub (security best practice)
- The repository size should be manageable (~2-3 MB)

## Troubleshooting

**"git command not found"**
- Install Git from https://git-scm.com/download/win
- Restart VS Code after installation

**"fatal: remote origin already exists"**
- Run: `git remote remove origin`
- Then run the `git remote add origin` command again

**"Authentication failed"**
- Use GitHub Personal Access Token instead of password
- Or set up SSH keys (more secure for repeated pushes)

**Files not appearing on GitHub**
- Check `.gitignore` isn't excluding them unintentionally
- Run: `git status` to see what's staged
- Run: `git add .` and `git push` again

## References
- Git Documentation: https://git-scm.com/doc
- GitHub Help: https://docs.github.com/en
- VS Code Git Guide: https://code.visualstudio.com/docs/sourcecontrol/overview
