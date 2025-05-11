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

## ⛳Comment lancer le jeu
(à faire)
