from numpy.ma.extras import column_stack, row_stack

from settings import *
from pygame_gui.core.interfaces import IUIElementInterface
from pygame_gui.core.ui_container import UIContainer
import pygame
import pygame_gui

# class UIAutoLayoutContainer(UIContainer):
#     def __init__(self, relative_rect: pygame.Rect, manager, layout, gap, hug : bool = False, **kwargs):
#         # Initialisation de la classe parente
#         super().__init__(relative_rect, manager, **kwargs)
#         self.rect = relative_rect
#         self.manager = manager
#         self.layout = layout  # 'row' ou 'column'
#         self.gap = gap       # Si gap est None, le mode auto gap est activé
#         self.hug = hug
#
#     def add_element(self, element: IUIElementInterface):
#         super().add_element(element)
#         self.do_layout()
#
#     def remove_element(self, element: IUIElementInterface):
#         super().remove_element(element)
#         self.do_layout()
#
#     def set_gap(self, gap):
#         self.gap = gap
#         self.do_layout()
#
#     # --- Fonctions pour le calcul des métriques ---
#
#     def _get_total_elements_height(self):
#         """Retourne la somme des hauteurs de tous les éléments."""
#         total_elements_height = 0
#         for element in self.elements:
#             total_elements_height += element.get_relative_rect().height
#
#         return total_elements_height
#
#     def _get_total_elements_width(self):
#         """Retourne la somme des largeurs de tous les éléments."""
#         total_elements_width = 0
#         for element in self.elements:
#             total_elements_width += element.get_relative_rect().width
#
#         return total_elements_width
#
#     def _get_max_width_element(self):
#         max_width = 0
#         for element in self.elements :
#             max_width = max(element.get_relative_rect().width, max_width)
#
#         return max_width
#
#     def _get_max_height_element(self):
#         max_height = 0
#         for element in self.elements:
#             max_height = max(element.get_relative_rect().height, max_height)
#
#         return max_height
#
#     def _get_auto_gap_column(self):
#         """Calcule le gap vertical automatique pour un layout en colonne."""
#         n = len(self.elements)
#         if n <= 1:
#             column_gap = 0
#         else :
#             total_height = self._get_total_elements_height()
#             available_height = self.relative_rect.height - total_height
#             column_gap = abs(available_height // (n - 1))
#
#         return column_gap
#
#     def _get_auto_gap_row(self):
#         """Calcule le gap horizontal automatique pour un layout en ligne."""
#         n = len(self.elements)
#         if n <= 1:
#             row_gap = 0
#         else :
#             total_width = self._get_total_elements_width()
#             available_width = self.relative_rect.width - total_width
#             row_gap = abs(available_width // (n - 1))
#
#         return row_gap
#
#     def _get_column_layout_metrics(self):
#         """
#         Retourne un tuple (total_content_height, gap_value) pour un layout en colonne.
#         """
#         n = len(self.elements)
#         total_elements_height = self._get_total_elements_height()
#         gap_value = self.gap if self.gap is not None else self._get_auto_gap_column()
#         total_content_height = total_elements_height + gap_value * max(n - 1, 0)
#         max_width = self._get_max_width_element()
#
#         return total_content_height, gap_value, max_width
#
#     def _get_row_layout_metrics(self):
#         """
#         Retourne un tuple (total_content_width, gap_value) pour un layout en ligne.
#         """
#         n = len(self.elements)
#         total_elements_width = self._get_total_elements_width()
#         gap_value = self.gap if self.gap is not None else self._get_auto_gap_row()
#         total_content_width = total_elements_width + gap_value * max(n - 1, 0)
#         max_height = self._get_max_height_element()
#
#         return total_content_width, gap_value, max_height
#
#     # --- Disposition des éléments ---
#     def _adjust_to_content(self, content_width, content_height):
#         if self.hug :
#             self.set_dimensions((content_width, content_height))
#
#     def do_layout(self):
#         if self.layout == 'row':
#             self._do_row_layout()
#         elif self.layout == 'column':
#             self._do_column_layout()
#
#     def _do_column_layout(self):
#         """Dispose les éléments verticalement avec un gap entre eux."""
#         n = len(self.elements)
#         if n == 0:
#             return
#         total_content_height, gap_value, max_width = self._get_column_layout_metrics()
#         start_y = (self.relative_rect.height - total_content_height) // 2
#         for i, element in enumerate(self.elements):
#             if i == 0:
#                 # Premier élément centré horizontalement et positionné au début vertical
#                 element.set_anchors({'centerx': 'centerx'})
#                 element.set_relative_position((0, start_y))
#             else:
#                 # Positionne l'élément en dessous du précédent avec le gap calculé
#                 anchors = {
#                     'top': 'top',
#                     'bottom': 'top',
#                     'centerx': 'centerx',
#                     'top_target': self.elements[i - 1]
#                 }
#                 element.set_anchors(anchors)
#                 element.set_relative_position((0, gap_value))
#
#         self._adjust_to_content(max_width, total_content_height)
#
#     def _do_row_layout(self):
#         """Dispose les éléments horizontalement avec un gap entre eux."""
#         n = len(self.elements)
#         if n == 0:
#             return
#         total_content_width, gap_value, max_height = self._get_row_layout_metrics()
#         start_x = (self.relative_rect.width - total_content_width) // 2
#         for i, element in enumerate(self.elements):
#             if i == 0:
#                 # Premier élément centré verticalement et positionné au début horizontal
#                 element.set_anchors({'centery': 'centery'})
#                 element.set_relative_position((start_x, 0))
#             else:
#                 # Positionne l'élément à droite du précédent avec le gap calculé
#                 anchors = {
#                     'left': 'left',
#                     'right': 'left',
#                     'centery': 'centery',
#                     'left_target': self.elements[i - 1]
#                 }
#                 element.set_anchors(anchors)
#                 element.set_relative_position((gap_value, 0))
#
#         self._adjust_to_content(total_content_width, max_height)

if __name__ == "__main__":
    pygame.init()

    pygame.display.set_caption('Layout Test')
    window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")

    # # Choisissez layout='column' ou 'row'
    # auto_layout = UIAutoLayoutContainer(
    #     relative_rect=pygame.Rect(-200, -200, 200, 300),
    #     manager=manager,
    #     layout='row',  # ou 'row'
    #     gap=20,  # gap automatique activé si None
    #     hug=True,
    #     anchors={
    #         'left': 'right',
    #         'top':'bottom',
    #     }
    # )

    main_menu_panel = pygame_gui.elements.UIPanel(
        relative_rect=DEFAULT_MENU_LAYOUT,
        manager=manager,
        margins={
            'top':50,
            'left': 50,
            'right': 50,
            'bottom': 50
        }
    )

    game_name_label = pygame_gui.elements.UILabel(
        text=GAME_NAME,
        manager=manager,
        container=main_menu_panel,
        relative_rect=pygame.Rect((0,0, -1, 30)),
        anchors={
            'centerx':'centerx',
        }
    )

    # Création de quelques boutons pour tester
    button1 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 20), (300, 50)),
        text='Say Hello',
        manager=manager,
        container=main_menu_panel,
        anchors={
            'top': 'top',
            'bottom': 'top',
            'centerx': 'centerx',
            'top_target': game_name_label
        }
    )

    button2 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 20), (300, 50)),
        text='Say Hello',
        manager=manager,
        container=main_menu_panel,
        anchors = {
            'top': 'top',
            'bottom': 'top',
            'centerx': 'centerx',
            'top_target': button1
        }
    )

    button3 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, 20), (300, 50)),
        text='Say Hi',
        manager=manager,
        container=main_menu_panel,
        anchors={
            'top': 'top',
            'bottom': 'top',
            'centerx': 'centerx',
            'top_target': button2
        }

    )

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            manager.process_events(event)

        manager.update(time_delta)
        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)
        pygame.display.update()
