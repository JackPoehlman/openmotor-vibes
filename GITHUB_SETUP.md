# GitHub Setup Guide for openmotor-vibes

This document covers repository setup, upstream sync, and publishing built binaries (including the Windows installer) to GitHub Releases.

## ✅ What's Been Done Locally

The following changes have been committed to your git repository:

1. **README.md** - Added "Attribution" section crediting reilleya and linking to original openMotor
2. **setup.py** - Updated package name to `openmotor-vibes` and added upstream project URL
3. **CHANGELOG.md** - Created template for tracking modifications and upstream synchronization
4. **Git commit** - Created initial commit with all attribution changes (commit: `345653f`)

**Current branch:** `main`

---

## 🚀 Quick Start: Push to GitHub (3 Steps)

### Step 1: Create Repository on GitHub.com

1. Go to **https://github.com/new**
2. Enter repository name: **`openmotor-vibes`**
3. Choose **Public** (recommended for open-source alignment with GPLv3)
4. **Leave all checkboxes unchecked** (don't add README, .gitignore, or license - you have these already)
5. Click **Create repository**
6. You'll see setup instructions - **copy the HTTPS URL** (looks like: `https://github.com/YOUR_USERNAME/openmotor-vibes.git`)

### Step 2: Update Git Remote & Push

Replace `YOUR_USERNAME` with your actual GitHub username and run:

```powershell
cd c:\Openmotor
git remote set-url origin https://github.com/YOUR_USERNAME/openmotor-vibes.git
git branch -M main
git push -u origin main
```

### Step 3: Set Up Upstream Tracking (for periodic rebases)

```powershell
git remote add upstream https://github.com/reilleya/openMotor.git
git fetch upstream
git remote -v  # Verify you see both 'origin' and 'upstream'
```

**Done!** Your repository is now live at `https://github.com/YOUR_USERNAME/openmotor-vibes`

---

## 📦 Publish Built Binaries to GitHub Releases

This project keeps installer artifacts out of git and publishes them as GitHub Release assets.

### Prerequisites

1. You have already built and tested the installer locally.
2. The installer artifact exists in `installers/Output`.
3. You have push access to `JackPoehlman/openmotor-vibes`.

### Verify local installer artifact

```powershell
Get-ChildItem -Path installers\Output -File
```

Expected artifact example:

- `installers/Output/OpenMotorVibes-Setup.exe`

### Create and publish a release (GitHub Web UI)

1. Go to `https://github.com/JackPoehlman/openmotor-vibes/releases/new`
2. Create/select a new tag (for example: `v0.6.2`)
3. Set release title (for example: `OpenMotor Vibes v0.6.2`)
4. Drag and drop release assets:
	 - `installers/Output/OpenMotorVibes-Setup.exe`
	 - Optional: a zip of `dist/openMotorVibes` for a portable build
5. Add release notes and click **Publish release**

### Create and publish a release (GitHub CLI)

If GitHub CLI is installed and authenticated:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" release create v0.6.2 `
	"installers/Output/OpenMotorVibes-Setup.exe#Windows Installer" `
	--repo JackPoehlman/openmotor-vibes `
	--title "OpenMotor Vibes v0.6.2" `
	--notes "See CHANGELOG.md for details."
```

If the tag already exists and you only need to upload/replace assets:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" release upload v0.6.2 `
	"installers/Output/OpenMotorVibes-Setup.exe#Windows Installer" `
	--repo JackPoehlman/openmotor-vibes `
	--clobber
```

---

## 🔄 Periodic Rebase Workflow (When Upstream Updates)

### Checking for Upstream Updates

```powershell
cd c:\Openmotor
git fetch upstream
git log --oneline upstream/main -5  # See latest upstream commits
```

### Option A: Rebase (Cleaner History - Recommended)

This replays your changes on top of the latest upstream code:

```powershell
# Backup current state (just in case)
git checkout -b backup-before-rebase

# Switch to main and rebase
git checkout main
git fetch upstream
git rebase upstream/main

# If conflicts occur, edit the conflicted files, then:
# git add <conflicted-file>
# git rebase --continue

# Test the application thoroughly!
# python main.py

# Force push to your fork (safe after rebase)
git push origin main -f

# Clean up backup
git branch -D backup-before-rebase
```

### Option B: Merge (Simpler)

This keeps the upstream changes as a separate merge commit:

```powershell
git fetch upstream
git merge upstream/main

# Resolve any conflicts if they occur
# Then commit:
git commit -m "Merge upstream openMotor vX.X.X"
git push origin main
```

---

## 📋 Post-Push Customization

### Update setup.py with Your GitHub Username

Replace `YOUR_USERNAME` in [setup.py](setup.py):

```python
author='YOUR_USERNAME',  # Change this to your actual username
url='https://github.com/YOUR_USERNAME/openmotor-vibes',
```

### Complete CHANGELOG.md

Fill in the template sections in [CHANGELOG.md](CHANGELOG.md):
- Document your modifications
- Add contributor names
- Update upstream commit hash and sync date
- List which features you've added or changed

### Add GitHub Repository Topics

In your GitHub repository settings:
1. Go to **Settings** → **About** (or Repository name section)
2. Add topics: `openmotor`, `rocket`, `ballistics`, `internal-ballistics`, `simulator`

### Update Git User Globally (Optional)

If you want all future commits to use your real GitHub account info:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@github.com"
```

The local openmotor-vibes repo is currently configured with:
```powershell
git config user.name          # Shows: openmotor-vibes-dev
git config user.email         # Shows: dev@openmotor-vibes.local
```

---

## 📚 Repository URLs & References

After pushing, these will be your key URLs:

| Purpose | URL |
|---------|-----|
| Your fork | `https://github.com/YOUR_USERNAME/openmotor-vibes` |
| Original openMotor | `https://github.com/reilleya/openMotor` |
| Clone your fork | `git clone https://github.com/YOUR_USERNAME/openmotor-vibes.git` |
| Clone original | `git clone https://github.com/reilleya/openMotor.git` |

---

## ⚙️ Git Remotes Currently Configured

```powershell
git remote -v
```

After Step 3, you should see:

```
origin    https://github.com/YOUR_USERNAME/openmotor-vibes.git (fetch)
origin    https://github.com/YOUR_USERNAME/openmotor-vibes.git (push)
upstream  https://github.com/reilleya/openMotor.git (fetch)
upstream  https://github.com/reilleya/openMotor.git (push)
```

---

## 🆘 Troubleshooting

### "Everything up-to-date" when pushing?
- You might already have a remote configured. Check: `git remote -v`
- If it's pointing to the wrong repository, use `git remote set-url origin <new-url>`

### Rebase conflicts?
- Don't panic! Conflicts are normal when rebasing modified files
- Edit each conflicted file to keep the changes you want
- Mark resolved: `git add <file>`
- Continue: `git rebase --continue`
- **Test thoroughly** after rebase before pushing

### Can't push to main?
- Check you have push access to the repository
- If using HTTPS, you may need to use a Personal Access Token instead of password
- See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

### Want to switch branches?
Currently on: `main`
To switch branches: `git checkout <branch-name>`

---

## 📖 Next Steps

1. ✅ Local setup complete (you're here)
2. Create GitHub repository (Step 1 above)
3. Push code (Step 2 above)
4. Set up upstream tracking (Step 3 above)
5. Update setup.py with your GitHub username
6. Fill in CHANGELOG.md with your modifications
7. Share your fork! 🎉

---

## 📞 Questions?

- For Git/GitHub help: https://docs.github.com/
- For openMotor questions: https://github.com/reilleya/openMotor
- For rebase walkthroughs: https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase
