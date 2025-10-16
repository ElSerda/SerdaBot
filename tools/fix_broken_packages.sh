#!/bin/bash
echo "🔍 Détection des problèmes de désinstallation de paquets (RECORD manquant)..."

# Lance pip install -e . et capture la sortie complète
pip install -e . 2>&1 | tee install_log.txt

# Recherche les lignes contenant le problème RECORD
grep "RECORD file was not found for" install_log.txt > fix_targets.txt

# Si aucun problème détecté
if [ ! -s fix_targets.txt ]; then
    echo "✅ Aucun paquet cassé détecté. Installation réussie."
    rm -f install_log.txt fix_targets.txt
    exit 0
fi

# Sinon, on tente de corriger
echo "⚠️ Paquets à corriger détectés :"
cat fix_targets.txt

# Extraction des noms de paquets cassés
packages=$(grep "RECORD file was not found for" fix_targets.txt | sed -E "s/.*for ([a-zA-Z0-9_\-]+)\.*/\1/" | sort | uniq)

# Réinstallation forcée de chaque paquet
for pkg in $packages; do
    echo "🔁 Tentative de correction via --force-reinstall sur : $pkg"
    pip install --force-reinstall --no-deps "$pkg"
done

# Relance install propre
echo "🔁 Nouvelle tentative d'installation avec pip install -e ."
pip install -e .

# Nettoyage
rm -f install_log.txt fix_targets.txt
