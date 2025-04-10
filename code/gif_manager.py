
from PIL import Image
import pygame


class GifManager:
    def __init__(self):
        self.gifs = []

    def add_gif(self, path:str, x:int ,y:int, map_anchored:bool, hide:bool) -> None:
        gif = Gif(path,x,y,map_anchored,hide)
        self.gifs.append(gif)

    def update_map(self, map_surf:pygame.Surface) -> None:
        for gif in self.gifs:
            if gif.map_anchored:
                gif.update(map_surf)

    def update_overlay(self, overlay_surf:pygame.Surface) -> None:
        for gif in self.gifs:
            if not gif.map_anchored:
                gif.update(overlay_surf)

    def update_all(self, map_surf:pygame.Surface, overlay_surf:pygame.Surface) -> None:
        self.update_map(map_surf)
        self.update_overlay(overlay_surf)

    def hide_all(self):
        for gif in self.gifs:
            gif.hide = True

    def show_all(self):
        for gif in self.gifs:
            gif.hide = False

    def reset_all(self):
        for gif in self.gifs:
            gif.reset()

class Gif:
    def __init__(self, gif_path:str,x:int,y:int, map_anchored:bool, hide:bool) -> None:
        self.frames = get_gif_frames(gif_path)

        self.current_frame = 0
        self.max_frame = len(self.frames)

        self.x, self.y = x,y

        self.map_anchored = map_anchored

        self.hide = hide


    def update(self,surface:pygame.Surface):

        if self.hide:
            return

        frame = self.frames[self.current_frame]

        surface.blit(frame,(self.x,self.y))

        self.current_frame += 1
        if self.current_frame >= self.max_frame:
            self.current_frame = 0

    def reset(self):
        self.current_frame = 0


def get_gif_frames(path):
    gif = Image.open(path)
    frames = []

    try:
        while True:
            frame = gif.convert("RGBA")
            pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
            frames.append(pygame_image)
            gif.seek(gif.tell() + 1)
    except:
        pass
    return frames
