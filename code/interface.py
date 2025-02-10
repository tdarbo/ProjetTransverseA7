from PIL import Image, ImageSequence
import tkinter as tk
from PIL import ImageTk

# Charger le GIF
gif_path = "Arbre fast.gif"
img = Image.open(gif_path)

# Création de la fenêtre Tkinter
root = tk.Tk()
frame = tk.Label(root)
frame.pack()


# Fonction pour mettre à jour l'affichage du GIF
def update(index):
    img.seek(index)  # Aller à la frame actuelle
    frame.img = ImageTk.PhotoImage(img)
    frame.config(image=frame.img)

    index += 1
    try:
        root.after(100, update, index)  # 100 ms entre chaque frame
    except EOFError:
        root.after(100, update, 0)  # Recommence depuis le début


update(0)
root.mainloop()