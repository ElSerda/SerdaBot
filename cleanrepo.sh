# 1. Supprime le dossier .git (⚠️ ce n'est PAS GitHub, c'est juste ton dossier local)
rm -rf .git

# 2. Réinitialise Git
git init
git branch -m main
git add .
git commit -m "🔥 Clean reboot - SerdaBot v0.1.0 final public-ready"

# 3. Reconnecte à GitHub
git remote add origin https://github.com/ElSerda/SerdaBot.git

# 4. Push en force
git push -f -u origin main
