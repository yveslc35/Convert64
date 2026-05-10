#!/bin/bash
# Installation de l'appli Convert64  v1.0
# --- Gestion du terminal ---
if [[ ! -t 1 ]]; then
  for term in x-terminal-emulator gnome-terminal konsole xterm; do
    if command -v "$term" >/dev/null 2>&1; then
      exec "$term" -e "$0"
      exit
    fi
  done
fi

# --- On se place là où est le script ---
# C'est la clé : maintenant "." désigne le dossier d'installation, peu importe où il est.
cd "$(dirname "$0")"

# --- Chemins SOURCES (Relatifs au script) ---
# On assume que ces fichiers sont dans le même dossier que ce script d'installation
FICHEXE="./Convert64" 
ICONE="./Conv64.png"
# --- Chemins DESTINATIONS (Toujours absolus car dans le système) ---
DESTEXE="$HOME/Applications"
DESTICONE="$HOME/.local/share/icons"
DESTLANCEUR="$HOME/.local/share/applications"

# === Couleurs ===
GREEN="\e[32m"
YELLOW="\e[33m"
NC="\e[0m"

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}   Installation de Convert64 v1.0 ${NC}"
echo -e "${YELLOW}==============================================${NC}"

# === Création des dossiers de destination ===
mkdir -p "$DESTEXE"
mkdir -p "$DESTICONE"
mkdir -p "$DESTLANCEUR"

# === Copie des fichiers ===
# On vérifie si le source existe avant de copier pour éviter un messages d'erreur
if [ -f "$FICHEXE" ]; then
    cp -f "$FICHEXE" "$DESTEXE/"
    # On rend l'exécutable... exécutable !
    chmod +x "$DESTEXE/$(basename "$FICHEXE")"
    echo -e "Exécutable : ${GREEN}Installé${NC}"
else
    echo -e "Exécutable : ${RED}Source introuvable !${NC}"
fi

[ -f "$ICONE" ] && cp -f "$ICONE" "$DESTICONE/" && echo -e "Icône application : ${GREEN}Installée${NC}"

cat <<EOF > "$DESTLANCEUR/convert64.desktop"
## === Création du lanceur de l'exécutable' ===
[Desktop Entry]
Type=Application
Name=convert64
Comment=Lanceur créé par l'installateur
Exec=$HOME/Applications/Convert64
Icon=$HOME/.local/share/icons/Conv64.png
Terminal=false
Categories=Utility;
EOF

# === Finalisation des droits et rafraîchissement ===
# 1. On rend l'exécutable bien... exécutable
chmod +x "$DESTEXE/Convert64"
# 2. On donne les droits au lanceur .desktop
chmod +x "$DESTLANCEUR/convert64.desktop"
# 3. On force le système à voir la nouvelle application immédiatement
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESTLANCEUR" >/dev/null 2>&1
fi

echo -e "\n${GREEN}  Installation terminée ${NC}"
echo ""
read -p "Appuyez sur Entrée pour quitter..."



