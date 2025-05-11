# ⛳ GOAT (Golf Overkill Annihilation Tournament)

***GOAT*** est un jeu de golf en 2D en tour par tour et jouable jusqu'à 5. Dans ce jeu, votre réfléxion sera mise à l'épreuve, à vous d'éviter les obstacles, de récupérer les bonus, et surtout, d'atteindre le trou en faisant le moins de coup possible !

## 🏌🏻Notre projet

**L'objectif :**
- Développer un jeu 2D en **Python** avec *Pygame* incluant des **notions de physique**
- Travailler en groupe de 5 grâce à Github

### 👤 Qui sommes-nous ?
- Thomas Darbo
- Louis Lemonnier
- Mathias Leroy
- Bastien Pommard
- Mattéo Spindler

## ⚪ Fonctionnalités du jeu
- Mode solo ou multijoueur jusqu'à **5** joueurs
- Bonus et Malus

## ⛳Comment installer et lancer le jeu

### 1. Cloner le dépôt
Pour récupérer le code du jeu, ouvrez votre terminal et exécutez la commande suivante :

```bash
git clone https://github.com/tdarbo/ProjetTransverseA7.git
cd GOAT
```

### 2. Installer les dépendances
Le jeu utilise plusieurs bibliothèques Python, notamment Pygame pour le rendu graphique. Pour installer toutes les dépendances nécessaires, exécutez :

```bash
pip install -r requirements.txt
```

Les dépendances principales incluent :
- pygame (pour le rendu graphique 2D)
- pygamegui (pour les interfaces et les boutons)
- PyTMX (pour les cartes)
- numpy (pour les calculs de physique)
- pillow (pour le traitement d'images, notamment les GIFs)
- pygamegui (pour les interfaces et les boutons)

### 3. Lancer le jeu
Une fois les dépendances installées, vous pouvez lancer le jeu avec la commande suivante :

```bash
python main.py
```

Vous pouvez maintenant profiter du jeu GOAT et défier vos amis dans des parties de golf endiablées !

## ❔Comment jouer 
- Jouer un coup *Clic gauche*
- Déplacer la caméra *Clic droit*
- Régler le zoom *Molette*
- Activer les bonus *E*

## 💻 Organisation du code
Notre code est composé de **18** classes différentes.
Il y a :
- ```bonus_manager``` qui permet de gérer les bonus et les malus.
- ```broadcast``` qui permet d'afficher des messages dans le jeu.
- ```camera``` qui gère le déplacement de la caméra sur le joueur dont c'est le tour et qui permet de déplacer librement la caméra sur la carte.
- ```engine``` qui gère la physique du jeu.
- ```game``` qui est la classe principale qui contient la boucle Pygame.
- ```gif_manager``` qui récupère les fichiers GIF et les transforme dans un format exploitable. 
- ```interface_manager``` qui gère les différentes interfaces du jeu.
- ```level``` qui gère le tour des joueurs.
- ```map``` qui contient tous les éléments de la carte : surface, bonus, gifs.
- ```player``` qui s'occupe de la gestion des joueurs tout au long du jeu.
- ```scene_config``` qui gère les interfaces pour le paramétrage du jeu.
- ```scene_manager``` qui gère les différentes scènes du jeu : menu, configuration, jeu.
- ```scene_play``` qui permet de gérer les niveaux.
- ```scene_start_menu``` qui s'occupe de l'affichage du menu d'accueil.
- ```score``` qui gère le tableau des scores tout au long de la partie.
- ```sound``` qui permet d'avoir de la musique et différents bruitages tout au long du jeu.
- ```tile``` qui permet de représenter les différentes surfaces comme l'herbe, le sable ou la glace.
- ```ui_text``` qui permet la création des textes.

### Configuration requise
- Python 3.7 ou supérieur
- Les bibliothèques mentionnées ci-dessus
- Un système d'exploitation compatible avec Pygame (Windows, macOS, Linux)

Bon jeu !
