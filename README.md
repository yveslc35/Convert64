Cette application permet de transformer des images pour pouvoir les stocker directement dans le code d'un programme.
A partir de n'importe quelle image PNG on transforme celle-ci en base 64 et on l'enregistre dans un dossier qui 
pourra servir par la suite à tous les programmes pour illustrer des icônes ou des boutons par exemple.

# Installation de Convert64 sous Linux

## Procédure automatique : 

1 Dézipper le dossier "Release_Github_Linux.tar.gz " et conservez-le.

(https://github.com/yveslc35/Convert64/releases/tag/v.1.0)

2 Lancer le script "Script_install.sh" (double-clic puis lancer)

(Cela va installer l'exécutable dans le menu Linux)

                         ==================================

## Compatibilité Linux
Cet exécutable est fourni au format binaire autonome. Il a été compilé sous Docker pour garantir une compatibilité maximale entre les différentes distributions.

• Systèmes testés et supportés :
◦ Ubuntu : 20.04 LTS, 22.04 LTS, 24.04 LTS et versions ultérieures.
◦ Linux Mint : 20, 21, 22 et versions ultérieures.
◦ Debian : 11 (Bullseye), 12 (Bookworm) et versions ultérieures.
◦ Autres : Compatible avec la majorité des distributions utilisant GLIBC 2.31 ou supérieure.

    • Prérequis système : Aucune installation de Python n'est requise. Cependant, si l'interface ne s'affiche pas, assurez-vous que les bibliothèques graphiques de base sont présentes (généralement déjà installées sur les versions "Desktop") : libx11-6, libglib2.0-0.

                       =============================

>Pour en savoir plus sur le fonctionnement et l'usage de ce programme,
>consulter le guide proposé dans la barre de menu du programme.

                       =============================

Si vous deviez recompiler le programme, voici les procédures de compilations que j'ai pu faire sous Linux Mint 22.3 - Cinnamon 64-bit :

# Compil Linux / Docker :

(pour être compatible avec anciennes versions Ubuntu, Mint, Debian)
```bash
cd ~/DOCUMENTS/Python/Conv64/Compil_Docker
```
```bash
docker run --rm -v "$(pwd):/src" -w /src python:3.10-slim-bullseye /bin/bash -c "apt-get update && apt-get install -y binutils python3-tk && pip install --upgrade pip && pip install -r requirements.txt pyinstaller && pyinstaller --onefile --windowed --icon=Conv64.png Convert64.py"
```
```bash
sudo chown -R $USER:$USER dist build 
```
                       =============================

# Installation d'EncapsArduino sous Windows

1 Téléchargez le fichier `Release_Github_Windows.zip` dans les [Releases]

https://github.com/yveslc35/Convert64/releases/tag/v.1.0

2 Décompressez l'archive.

3 Double-cliquez sur `Convert64.exe`.


Si vous deviez recompiler le programme sous windows, voici la procédure de compilation que j'ai exécutée sous Windows 11 :

## Compil Windows / PyInstaller :

Dans une fenêtre terminal : 

1 Se placer dans le dossier où  se trouve le prog (cd C:\.....etc)
	
2 Installer PyInstaller et Pillow
```powershell
pip3 install pyinstaller
pip3 install pillow	
```		
3 Lancer la compilation :
```powershell
python -m PyInstaller --clean --onefile --noconsole --collect-all customtkinter --collect-all CTkMessagebox --add-data "Conv64.ico;." --icon="Conv64.ico" Convert64.py
``` 
		



