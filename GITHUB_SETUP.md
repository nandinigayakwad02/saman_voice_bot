# GitHub Setup Guide

## 📋 Quick Steps to Push Code to GitHub

### Step 1: Create GitHub Repository (if not created)
1. Go to https://github.com
2. Click "+" → "New repository"
3. Name: `Josh_voice_bot` (or any name)
4. **Don't** initialize with README (we already have files)
5. Click "Create repository"
6. Copy the repository URL (e.g., `https://github.com/yourusername/Josh_voice_bot.git`)

---

### Step 2: Configure Git (First Time Only)
```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"
```

---

### Step 3: Add Files to Git
```bash
# Add all files except those in .gitignore
git add .

# Check what will be committed
git status
```

---

### Step 4: Create Initial Commit
```bash
# Commit with a message
git commit -m "Initial commit: WhatsApp AI Voice Bot with ElevenLabs and OpenAI Realtime API"
```

---

### Step 5: Rename Branch to 'main' (Optional but Recommended)
```bash
# Rename master to main
git branch -M main
```

---

### Step 6: Connect to GitHub
```bash
# Add remote repository (replace with YOUR GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Example:
# git remote add origin https://github.com/johnsmith/Josh_voice_bot.git
```

---

### Step 7: Push to GitHub
```bash
# Push to GitHub
git push -u origin main
```

---

## 🔐 If You Get Authentication Error

### Option 1: Use Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Copy the token (save it somewhere safe!)
5. When pushing, use token as password:
   ```bash
   Username: your_github_username
   Password: [paste your token here]
   ```

### Option 2: Use SSH (Better for Long Term)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@gmail.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Then use SSH URL: git@github.com:username/repo.git
```

---

## 📝 Complete Flow (All Commands)

```bash
# 1. Configure git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"

# 2. Add files
git add .

# 3. Commit
git commit -m "Initial commit: WhatsApp AI Voice Bot"

# 4. Rename branch to main
git branch -M main

# 5. Add remote (replace with YOUR URL)
git remote add origin https://github.com/YOUR_USERNAME/Josh_voice_bot.git

# 6. Push to GitHub
git push -u origin main
```

---

## 🔄 After First Push (Future Updates)

```bash
# Add changes
git add .

# Commit
git commit -m "Your commit message"

# Push
git push
```

---

## ✅ Verify
After pushing, go to your GitHub repository URL in browser to see your code!

---

## 🚨 Common Issues

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin YOUR_URL
```

### "Updates were rejected"
```bash
git pull origin main --rebase
git push -u origin main
```

### "Authentication failed"
Use Personal Access Token instead of password (see above)
