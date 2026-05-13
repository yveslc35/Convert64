import FreeSimpleGUI as sg
from PIL import Image, ImageOps
import io
from io import BytesIO
import base64
import os
from pathlib import Path
import subprocess
import sys

sg.theme('BluePurple')
MAX_SIZE = 370
versionC64 = "V_1.0 du 09 Mai 2026"    #  <========= à maintenir si modifs
dossstock = ""

# --------Fonction d'ouverture de dossier indépendant du compilateur--------
def safe_open_path(path):     
    # A utiliser si compilation avec Docker pour appel proces ou lien url
    # Lance une commande ou ouvre un chemin en nettoyant l'environnement.
    # 'commande' peut être un simple chemin (string) ou une liste [prog, arg]
    new_env = os.environ.copy()    # préparation d'un environnement propre
    if sys.platform.startswith('linux'):
        for var in ['LD_LIBRARY_PATH', 'PYTHONPATH', 'PYTHONHOME']:
            new_env.pop(var, None)
    try:
        if isinstance(path, str):   # C'est une chaîne de caractères (Dossier ou URL)
            if sys.platform == "win32":
                os.startfile(path)  # Sous Windows, on utilise 'os.startfile'
            else:
                subprocess.Popen(['xdg-open', path], env=new_env) # Sous Linux, on utilise 'xdg-open' avec l'environnement propre
        else:     # Sinon c'est une liste (p.ex. Lancement de l'IDE Arduino avec arguments)
            subprocess.Popen(path, env=new_env)  # Popen fonctionne sur Windows et Linux         
    except Exception as e:
        print(f"Erreur avec {path} : {e}")
        
# Fonction d'affichage popup de sélection de dossier
def selecteur(titre, message):
    bouton_parcourir = sg.FolderBrowse("Parcourir")
    layout_popup = [
        [sg.Text(titre, font=("Helvetica", 12, "bold"))],
        [sg.Text(message)],
        [sg.Input(key="-PATH-", size=(60, 1), expand_x=True), bouton_parcourir],
        [sg.Button("OK", button_color=('black','lightgreen'), pad=((10,0),(20,10))),
            sg.Push(),
            sg.Button("Nouveau dossier",key="-NOUV-", button_color=('black','orange')),
            sg.Push(),
            sg.Button("Quitter",button_color=('black','red'),
                pad=((10, 0),(20, 10)), bind_return_key=True)
        ]
    ]
    pop_win = sg.Window(titre, layout_popup, modal=True)
    resultat = None
    while True:
        event, values = pop_win.read()
        if event in (sg.WIN_CLOSED,"Quitter"):
            break
        if event == "OK":
            resultat = values["-PATH-"]
            break
        if event == "-NOUV-":
            base = values["-PATH-"]
            if base and os.path.isdir(base):
                new_folder = sg.popup_get_text("Nom du nouveau dossier :",keep_on_top=True)
                if new_folder:
                    path = os.path.join(base, new_folder)
                    try:
                        os.mkdir(path)
                        sg.popup("Dossier créé :", path, background_color="Green",
                                 text_color="black",keep_on_top=True)
                        resultat = path
                        break
                    except Exception as e:
                        sg.popup("Erreur :",e,background_color="red",
                                 text_color="white",keep_on_top=True)
            else:
                sg.popup("Choisir d'abord le répertoire où créer le dossier",keep_on_top=True)

    pop_win.close()
    return resultat

# --------Recherche dossier de stockage des images converties ------------
def chercher_param():
    # On définit un dossier spécifique à l'application dans le HOME de l'utilisateur
    # Windows : C:\Users\Nom\.Convert64    Linux : /home/nom/.Convert64
    dossier_config = Path.home() / ".Convert64"  
    # On s'assure que le dossier existe (on le crée si besoin)
    dossier_config.mkdir(exist_ok=True) 
    fiparam = dossier_config / "param64.txt"   
    if fiparam.exists():
        dossstock = fiparam.read_text(encoding='utf-8').strip()
    else:
        dossstock = selecteur("Dossier de stockage des images en base 64",
                              "Où voulez-vous enregistrer les images lors de leur conversion en base 64 ?")      
        # Sécurité : on n'écrit que si l'utilisateur a choisi un dossier
        if dossstock:
            fiparam.write_text(dossstock, encoding='utf-8')           
    return dossstock

# -------LECTURE IMAGE SOURCE --------
def charger_image(path):
    img = Image.open(path)

    # taille originale (AVANT modification)
    original_w, original_h = img.size

    # image pour affichage (modifiée uniquement pour rendu)
    img.thumbnail((MAX_SIZE, MAX_SIZE))

    bio = io.BytesIO()
    img.save(bio, format="PNG")

    return bio.getvalue(), original_w, original_h

# -------CONVERSION EN BASE 64 ----------
def convertir_image(path, width, height, border, optimize):
    img = Image.open(path)

    # resize exact (non carré obligatoire)
    img = img.resize((width, height), Image.LANCZOS)

    # bordure si besoin
    if border > 0:
        img = ImageOps.expand(img, border=border, fill="black")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=optimize)

    b64 = base64.b64encode(buffer.getvalue()).decode()

    return buffer.getvalue(), b64

# Fonction d'affichage de l'à propos
def afficher_apropos(window_parent):   
    window_parent.refresh()
    desc_apropos =  """
             Convert64 
        Programme développé
       sous Python3+FreeSimpleGUI
       et compilé avec Docker
       pour rétro-compatibilité.

       Auteur : Yves Le Chevalier
       Pour :  My Human Kit
       {version}"""
    desc_apropos = desc_apropos.format(version=versionC64)
    layout = [
        [sg.Frame('', [
            [sg.Multiline(desc_apropos, size=(30,11), no_scrollbar=True)],
            [sg.Push(), sg.Button("Fermer", key="-CLOSE_AP-"), sg.Push()],
            ], border_width=1)
        ]
    ]
    return sg.Window("À propos", layout,keep_on_top=True, finalize=True)

# Fonction d'affichage de l'aide
def afficher_aide(window_parent):
    window_parent.refresh()
    desc_aide = """
         Programme de redimensionnement et de conversion en base64 d'une image PNG.

    Cette opération permettra ensuite d'intégrer facilement cette image dans le code d'un
    programme pour, par exemple, décorer un bouton ou afficher un logo.
    
    A la première utilisation, le programme demande de choisir le dossier de stockage des images
    converties en base 64. 
    Un bouton permet de créer à cette occasion un nouveau dossier réservé à cet usage, mais il
    faut, bien entendu, avoir choisi au préalable le répertoire dans lequel mettre ce dossier.
    Le chemin d'accès à ce dossier est alors mémorisé dans le fichier 'param64.txt.
    L'emplacement de ce dossier de stockage est affiché lorsqu'on lance le [Visualiseur]. 
    
    Si vous désirez par la suite déplacer le dossier de stockage, il faut le copier à son
    nouvel emplacement puis supprimer ensuite le fichier 'param64.txt' qui se trouve dans
    le répertoire  C:\\Users\\nom-utilisateur\\.Convert64  pour Windows et dans le répertoire
    /home/nom-utilisateur/.Convert64  pour Linux.
    Ceci déclenchera une nouvelle demande d'emplacement du dossier des images en base 64
    au prochain lancement de ce programme.
    
    [Convertisseur] : Ce bouton déclenche la fonction de conversion d'une image.
    
    Il faut choisir une image PNG, de préférence en mode indexé afin de réduire son volume.
    La transparence du fond de l'image, si tel est le cas, sera conservée.
    Les paramètres de conversion permettent de fixer les dimensions de l'image convertie et de
    lui affecter éventuellement une bordure. (0 = pas de bordure, valeur par défaut)
    La taille de l'image convertie est initialisée par défaut à 32x32 mais on peut choisir
    une autre taille, carrée ou rectangulaire selon sa destination (forme d'un bouton p.ex.).
    Lorsqu'on modifie la largeur, celle-ci est reportée automatiquement dans la hauteur pour
    conserver par défaut un ratio carré.
    Mais on peut ensuite modifer la hauteur sans impacter la largeur précédemment saisie.
    
    L'image source est affichée dans sa taille d'origine dans la mesure où elle peut entrer
    dans la fenêtre d'affichage. Au-delà, son affichage sera limité à la fenêtre d'affichage.
    
    L'image convertie sera visualisée dans sa taille réelle quelle que soit sa taille,
    mais si elle est trop grande, seul le coin supérieur gauche de l'image sera affiché.
    
    Il faut choisir un nom d'image pour pouvoir enregistrer celle-ci dans le dossier de stockage.
    Ce n'est qu'après avoir cliqué sur le bouton [Convertir] que l'on pourra enregistrer l'image.
    A noter que le nom de l'image saisi sera automatiquement suffixé par ses dimensions lors de
    l'enregistrement ainsi que par l'épaisseur de son cadre éventuel. 
    Ainsi une image dont le nom est  AAAAAA  sera enregistrée sous le nom  AAAAAA_75x55_0
    où 75x55 indique sa largeur x hauteur et 0 l'épaisseur de son cadre (0 = pas de cadre).
    
    [Visualiseur] :  Ce bouton déclenche l'affichage de la liste triée des images en base64.
    Il est alors possible, en cliquant sur le nom, de visualiser l'image dans sa taille réelle.
    Cela affiche un re-calcul de ses dimensions et son poids en nombre de caractères.
    Un bouton permet de supprimer de façon définitive cette image en base64.
    Un autre bouton propose d'afficher le contenu intégral du fichier image en base 64.
    Ce contenu s'affiche dans une petite fenêtre et un bouton permet d'en faire la copie.
    Il suffit ensuite de coller les données dans le programme destinataire en nommant
    l'image : NomImage = b'xxxxxxxxx' (où xxxxxxx est le contenu du fichier en base 64).
    
    [Aide] :   Bouton permettant l'affichage de ce texte explicatif.
"""
    layout = [
        [sg.Frame('', [
            [sg.Multiline(desc_aide, size=(80, 25), no_scrollbar=False,
                          border_width=4, disabled=True, font=("Arial", 11),text_color = "blue4")],
            [sg.Push(), sg.Button("Fermer", key="-CLOSE_HELP-"), sg.Push()],
            ], border_width=1)
        ]
    ]
    return sg.Window("Aide Conv64", layout, finalize=True)

# ----FONCTION DE VISUALISATION--------
def get_image_info(b64_string):
    img_bytes = base64.b64decode(b64_string)
    img = Image.open(BytesIO(img_bytes))
    return img.size  # (x, y)

def open_b64_viewer(dossier):
    dossier = Path(dossier)
    files = sorted([f.name for f in dossier.iterdir() if f.is_file()])  # Images triées par nom
    layout = [
        [sg.Text("Images stockées dans"),
         sg.Text(f"{dossier}")],
        [
            sg.Listbox(
                values=files,
                size=(35, 15),
                key="-FILES-",
                enable_events=True
            ),
            sg.VSeperator(),
            sg.Column([
                [sg.Button("Afficher les données base64 de l'image", key="-SHOW-",visible=False)],
                [sg.Text("")],
                [sg.Button("Supprimer ce fichier image", key="-SUPP-",
                           visible=False, size=(20, 2))],
                [sg.Text("")],
                [sg.HorizontalSeparator(color="gray")],
                [sg.Text("", key="-INFO-")],
                [sg.Text("", key="-SIZEFILE-")],
                [sg.Image(key="-IMG-")]
            ])
        ],
        [sg.Button("Fermer"),sg.Push(),sg.Text("",key="-MESS-")]
    ]
    window = sg.Window("Visionneuse images en base64", layout, modal=True,keep_on_top=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Fermer"):
            break
        if event == "-FILES-" and values["-FILES-"]:
            filename = values["-FILES-"][0]
            filepath = dossier / filename
            try:
                # lecture base64 texte
                b64 = filepath.read_text(encoding="utf-8").strip()
                size_file = len(b64)  # taille fichier base64
                img_bytes = base64.b64decode(b64)  # décodage image
                x, y = get_image_info(b64)   # taille image
                window["-SUPP-"].update(visible=True)
                window["-SHOW-"].update(visible=True)
                window["-IMG-"].update(data=img_bytes)
                window["-INFO-"].update(f"Taille image : {x} x {y} pixels")
                window["-SIZEFILE-"].update(f"Taille base64 : {size_file} caractères")
                window["-MESS-"].update("")    

            except Exception as e:
                sg.popup_error("Erreur lecture image base64 :", e)

        if event == "-SUPP-":
            try:
                os.remove(filepath)   
                files.remove(filename)      # pour supprimer l'entrée dans la Listbox
                window["-FILES-"].update(values=files)
                window["-IMG-"].update(data=None)
                window["-INFO-"].update("")
                window["-SIZEFILE-"].update("")
                window["-SUPP-"].update(visible=False)
                window["-SHOW-"].update(visible=False)
                window["-MESS-"].update(f"{filename} supprimé")
                print(f"Fichier '{filepath}' supprimé")
            except FileNotFoundError: print(f"Fichier '{filepath}' non trouvé")

        if event == "-SHOW-" and values["-FILES-"]:
            filename = values["-FILES-"][0]
            filepath = dossier / filename
            print("filepath ",filepath)
            try:
                content = filepath.read_text(encoding="utf-8")
                show_content_popup(content, title=filename)
            except Exception as e:
                sg.popup_error("Erreur lecture fichier :", e)           
    window.close()

# -----------AFFICHAGE DES DONNEES IMAGE EN BASE 64 ---------
def show_content_popup(content, title="Données à copier dans un programme"):
    layout = [
        [sg.Text(title)],
        [sg.Multiline(
            content,
            size=(80, 3),
            font=("Courier", 9),
            disabled=True,
            horizontal_scroll=True,
            key="-POP_CONTENT-"
        )],
        [sg.Button("Copier", key="-POP_COPY-"), sg.Button("Fermer")]
    ]
    win = sg.Window(title, layout, modal=True, keep_on_top=True)
    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, "Fermer"):
            break
        if event == "-POP_COPY-":
            win.TKroot.clipboard_clear()
            win.TKroot.clipboard_append(content)
            sg.popup("Contenu copié ✔",background_color="Green",text_color="white", keep_on_top=True)
            break
    win.close()

# ---------------- MENU ----------------

def construire_menu():
    return [
        ["Fichier",
            ["Quitter",]
        ],
        ["Aide",
            ["A_propos",
             "Guide",] 
        ], 
        [' '*60, []],
        ['MHK', ["My Human Kit"]],
    ]
 
# ---------------- COLONNE GAUCHE ----------------
colg_conv = [
    
    [
        sg.Button("Convertisseur", key="-OPEN-", size=(18,1)),
        sg.Text(" "*15),
        sg.Button("Visualiseur", key="-VIEW-", size=(10,1)),
    ],
    [sg.Frame('Image source', [
        [sg.Image(key="-IMAGE-")],
        ], border_width=5,key="-CADRE-",visible=False)
    ],
    [sg.Text("", key="-INFO-")],
    [sg.Text("", key="-SIZE-")]
]

# ---------------- COLONNE DROITE ----------------
cold_conv = [
    [sg.Text("Paramètres de l'image en base64",expand_x=True,justification="center",
             text_color = "blue3",font=("Ubuntu Sans, semibold",14))],
    [sg.HorizontalSeparator(color="gray")],
    [
        sg.Text("Largeur (px) :"),
        sg.Input("32", key="-WIDTH-", size=(4, 1), enable_events=True),
        sg.Push(),
        sg.Text("Bordure (px) :"),
        sg.Input("0", key="-BORDER-", size=(3, 1)),
    ],
    [
        sg.Text("Hauteur (px) :"),
        sg.Input("32", key="-HEIGHT-", size=(4, 1), enable_events=True),
    ],
    [sg.HorizontalSeparator(color="gray")],
    [
        sg.Text("Dossier :"),
        sg.Text(dossstock, size=(60, 1)),
    ],
    [
        sg.Text("Nom du fichier :"),
        sg.Input(key="-FILENAME-", size=(25, 1)),
    ],
    [sg.HorizontalSeparator(color="gray")],
    [
        sg.Button("Convertir", key="-CONV-",size=(12,1)),
        sg.Push(),
        sg.Button("Enregistrer", key="-ENRE-", button_color=("white", "green"),visible=False),
    ],
    [sg.Text("Visualisation en taille réelle :", key="-VOIR-",visible=False)],
    [sg.Image(key="-PREVIEW-")], 
]

# ------- CREATION FENETRE PRINCIPALE ---------
def creer_fenetre_principale():
    menu_def = construire_menu()
    layout = [
        [sg.Menu(menu_def, key="-MENU_BAR-")],
        [
            sg.Column(colg_conv, size=(400, 520)),
            sg.VSeperator(color="black"),
            sg.Column(cold_conv,key="-COLD-",visible=False,
                expand_x=True,expand_y=True)
        ]
    ]
    return sg.Window("Convertisseur image en base 64",layout,size=(950, 520),resizable=True)

# ----------DEBUT DE PROGRAMME -------------------
dossstock = chercher_param()    # trouver si Param64 déjà créé
current_file = None
current_b64 = None
window_main = creer_fenetre_principale()
window_aide = None
window_apropos = None
window_main.finalize()    # pour forcer un premier affichage propre
menu_def = construire_menu()
window_main["-MENU_BAR-"].update(menu_definition=menu_def)
height_locked = True  # verrouillage du ratio carré

while True:
    window, event, values = sg.read_all_windows(timeout=100)

    if window_apropos is not None and window == window_apropos:  # traitement des évènements de la fenêtre a propos
        if event in (sg.WIN_CLOSED, "-CLOSE_AP-"):
            window_apropos.close()
            window_apropos = None

    if window_aide is not None and window == window_aide:   # traitement des évènements de la fenêtre aide
        if event in (sg.WIN_CLOSED, "-CLOSE_HELP-"):
            window_aide.close()
            window_aide = None
            
    if window == window_main :          # traitement des évènements de la fenêtre principale     
        if event in (sg.WIN_CLOSED, "Quitter"):
            window_main.close()
            if window_aide is not None:
                window_aide.close()
                window_aide = None
            if window_apropos is not None:
                window_apropos.close()
                window_apropos = None
            break

        # -------- OUVRIR IMAGE SOURCE --------
        if event == "-OPEN-":
            fichier = sg.popup_get_file("Ouvrir une image", file_types=(("PNG", "*.png"),), keep_on_top=True)
            if fichier:
                current_file = fichier
                img = Image.open(fichier)
                img.thumbnail((MAX_SIZE, MAX_SIZE))
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                nom = os.path.basename(fichier)
                image_data, w, h = charger_image(fichier)
                window["-CADRE-"].update(visible=True)
                window["-IMAGE-"].update(data=image_data)
                window["-INFO-"].update(visible=True)
                window["-INFO-"].update(f"nom: {nom}")
                window["-SIZE-"].update(visible=True)
                window["-SIZE-"].update(f"taille originale: {w} x {h}")
                window["-COLD-"].update(visible=True)
                window["-FILENAME-"].update("")
                window["-WIDTH-"].update("32")
                window["-HEIGHT-"].update("32")
                window["-BORDER-"].update("0")
                window["-PREVIEW-"].update(data=b"")  # effacer l'affichage de l'image convertie
                window["-ENRE-"].update(visible=False)
                height_locked = True   # verrouillage du ratio carré

        if event == "-WIDTH-" and height_locked:
            window["-HEIGHT-"].update(values["-WIDTH-"])
        elif event == "-HEIGHT-":      
            height_locked = False  # modif de la hauteur désactive le ratio carré
        filename = values["-FILENAME-"].strip()
        
        # -------- CONVERSION --------
        if event == "-CONV-" and current_file:
            try:
                width = int(values["-WIDTH-"])
                height = int(values["-HEIGHT-"])
                border = int(values["-BORDER-"])
                optimize = True
                img_bytes, b64 = convertir_image(current_file,width,height,border,optimize)
                current_b64 = b64
                window["-VOIR-"].update(visible=True)
                window["-PREVIEW-"].update(data=img_bytes)
                if filename:
                    nomfich = Path(dossstock) / f"{filename}_{width}x{height}_{border}.txt"
                    print("nomfich = ", nomfich)
                    if nomfich.exists() :
                        sg.popup(f"Erreur : Ce nom existe déjà",background_color="red",
                            text_color="white",keep_on_top=True)
                        window["-ENRE-"].update(visible=False)
                        window.refresh()
                    else :
                        window["-ENRE-"].update(visible=True)
                        window.refresh()
            except Exception as e:
                sg.popup_error(f"Erreur : {e}")

        # -------- ENREGISTREMENT --------
        if event == "-ENRE-":
            if not current_b64:
                sg.popup_error("Aucune image convertie")
                continue
            if not dossstock:
                sg.popup_error("Aucun dossier sélectionné")
                continue
            if not filename:
                sg.popup_error("Nom de fichier manquant")
                continue
            path = os.path.join(dossstock,filename+"_"+str(width)+"x"+str(height)+"_"+str(border)+".txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(current_b64)
            sg.popup("Sauvegardé",background_color="Green",text_color="white", keep_on_top=True)

        # -------- A PROPOS --------
        if event == "A_propos":
            if window_apropos is None :
                window_apropos = afficher_apropos(window_main)
            else:
                window_apropos.bring_to_front()

        # -------- AIDE --------
        if event == "Guide":
            if window_aide is None :
                window_aide = afficher_aide(window_main)
            else:
                window_aide.bring_to_front()     # remonte au devant la fenêtre déjà ouverte

        # -------- VISUALISATION --------
        if event == "-VIEW-":
            window["-COLD-"].update(visible=False)
            window["-CADRE-"].update(visible=False)
            window["-INFO-"].update(visible=False)
            window["-SIZE-"].update(visible=False)
            open_b64_viewer(dossstock)

        # -------- Appel MHK --------
        if event == "My Human Kit" :
            safe_open_path("https://myhumankit.org/")
        

window.close()
