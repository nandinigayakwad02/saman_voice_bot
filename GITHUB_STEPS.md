# GitHub Par Code Push Karne Ke Steps

## ✅ Step 1: Git Config (Agar pehli baar kar rahe ho)
```bash
git config --global user.name "nandinigayakwad02
"
git config --global user.email "nandani.gayakwad@vkaps.com"
```

## ✅ Step 2: Files Add Karo
```bash
git add .
```

## ✅ Step 3: Commit Karo
```bash
git commit -m "Initial commit: WhatsApp AI Voice Bot"
```

## ✅ Step 4: Branch Name Change Karo (master → main)
```bash
git branch -M main
```

## ✅ Step 5: GitHub Repo URL Add Karo
**Pehle GitHub par repo banana:**
- https://github.com par jao
- "+" click karo → "New repository"
- Naam do (jaise: Josh_voice_bot)
- "Create repository" click karo
- URL copy karo

**Phir terminal mein:**
```bash
git remote add origin https://github.com/TUMHARA_USERNAME/REPO_NAME.git
```

**Example:**
```bash
git remote add origin https://github.com/john/Josh_voice_bot.git
```

## ✅ Step 6: Push Karo GitHub Par
```bash
git push -u origin main
```

---

## 🔐 Agar Password Maange

GitHub ab password nahi, **Personal Access Token** maangta hai:

1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. "Generate new token" click karo
4. `repo` ko select karo
5. Token copy karo
6. Push karte waqt password ki jagah token use karo

---

## 🎯 Quick Commands (All in One)

```bash
# 1. Configure (first time only)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 2. Add, commit, push
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```
