
from PIL import Image
import pygame
from PIL.ImageOps import scale


class GifManager:
    def __init__(self):
        self.gifs = {}

    def show_gif(self,path:str, x:int, y:int, scale_factor:float, map_anchored:bool):
        s_gif = self.gifs[path]
        if isinstance(s_gif,Gif):
            s_gif.hide = False
            s_gif.x = x
            s_gif.y = y
            s_gif.scale = scale_factor
        else:
            n_gif = Gif(path, x, y, scale_factor, map_anchored, False)
            self.gifs[path] = n_gif

    def hide_gif(self,path:str):
        s_gif = self.gifs[path]
        if isinstance(s_gif,Gif):
            s_gif.hide = True
        else:
            raise Exception(f"Gif {path} not found in gifs list")

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
    def __init__(self, gif_path:str,x:int,y:int, scale:float, map_anchored:bool, hide:bool) -> None:
        self.frames = get_gif_frames(gif_path)

        self.current_frame = 0
        self.max_frame = len(self.frames)

        self.x, self.y, self.scale = x,y,scale

        self.map_anchored = map_anchored
        self.last_update = 0
        self.hide = hide


    def update(self,surface:pygame.Surface):


        if self.hide:
            return

        frame = self.frames[self.current_frame]

        final_frame = pygame.transform.scale_by(frame, self.scale)

        surface.blit(final_frame,(self.x,self.y))

        if abs(self.last_update - pygame.time.get_ticks()) < 500:
            return

        self.last_update = pygame.time.get_ticks()

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
