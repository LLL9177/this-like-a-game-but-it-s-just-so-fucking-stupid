import pygame as pg

class Note:
    def __init__(self, screen, text, font=None, title="Note", color=(20, 20, 20), panel_color=(245, 245, 220)):
        self.screen = screen
        # convert <br> to \n, preserve multiple <br>s
        self.text = text.replace("<br>", "\n")
        self.title = title
        self.is_open = False

        # Fonts
        self.title_font = pg.font.SysFont("Arial", 40)
        self.body_font = font if font else pg.font.SysFont("Arial", 28)
        self.color = color
        self.panel_color = panel_color

        # Panel settings
        self.panel_width = 800
        self.panel_height = 600
        self.panel_x = (screen.get_width() - self.panel_width) // 2
        self.panel_y = (screen.get_height() - self.panel_height) // 2
        self.padding = 24
        self.tab_width = 40  # pixels per tab

        # Pre-render wrapped text
        self.text_surfaces = self._wrap_text(self.text, self.body_font, self.panel_width - 2*self.padding)

    def _wrap_text(self, text, font, max_width):
        """Return list of (surface, rect) tuples for wrapped text, handling tabs and multiple line breaks"""
        surfaces = []
        y_offset = 0
        lines = text.split("\n")  # preserves multiple line breaks
        for line in lines:
            # handle tabulation
            indent = 0
            while line.startswith("\t"):
                indent += self.tab_width
                line = line[1:]  # remove leading tab

            words = line.split()
            cur_line = ""
            for word in words:
                test_line = f"{cur_line} {word}".strip()
                if font.size(test_line)[0] + indent <= max_width:
                    cur_line = test_line
                else:
                    surf = font.render(cur_line, True, self.color)
                    rect = surf.get_rect(topleft=(self.panel_x + self.padding + indent, self.panel_y + 80 + y_offset))
                    surfaces.append((surf, rect))
                    y_offset += 36
                    cur_line = word
            if cur_line:
                surf = font.render(cur_line, True, self.color)
                rect = surf.get_rect(topleft=(self.panel_x + self.padding + indent, self.panel_y + 80 + y_offset))
                surfaces.append((surf, rect))
                y_offset += 36

            # if line was empty (multiple \n), add spacing
            if not line.strip():
                y_offset += 36
        return surfaces

    def check_opened(self):
        return self.is_open

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def toggle(self):
        self.is_open = not self.is_open

    def draw(self):
        """Draw the note if it’s open"""
        if not self.is_open:
            return

        # Semi-transparent overlay
        overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Panel
        panel_rect = pg.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pg.draw.rect(self.screen, self.panel_color, panel_rect, border_radius=16)
        pg.draw.rect(self.screen, (50, 50, 50), panel_rect, width=4, border_radius=16)  # border

        # Title
        title_surf = self.title_font.render(self.title, True, (50, 50, 50))
        title_rect = title_surf.get_rect(midtop=(self.screen.get_width()//2, self.panel_y + 20))
        self.screen.blit(title_surf, title_rect)

        # Body text
        for surf, rect in self.text_surfaces:
            self.screen.blit(surf, rect)

        # Hint
        hint_font = pg.font.SysFont("Arial", 22)
        hint_surf = hint_font.render("Press E to close", True, (80, 80, 80))
        hint_rect = hint_surf.get_rect(midbottom=(self.screen.get_width()//2, self.panel_y + self.panel_height - 20))
        self.screen.blit(hint_surf, hint_rect)

# --- SpriteAnimator class ---

class SpriteAnimator:
    def __init__(self, sprite_sheet_path, rows, cols, scale=1, frame_delay=200, offset_x=0, offset_y=0):
        """
        offset_x, offset_y: manually shift the sprite when drawing to align different animations
        """
        self.sprite_sheet = pg.image.load(sprite_sheet_path).convert_alpha()
        self.rows = rows
        self.cols = cols
        self.scale = scale
        self.frame_delay = frame_delay
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.frames = self._load_frames()
        self.current_frame = 0
        self.timer = 0

        # --- Option 1: use first frame as reference for hitbox size ---
        self.base_rect = self.frames[0].get_rect()

    def draw(self, surface, x, y, flip_x=False):
        """Draw current frame, optionally flipped horizontally"""
        frame = self.get_frame()
        if flip_x:
            frame = pg.transform.flip(frame, True, False)
        surface.blit(frame, (x + self.offset_x, y + self.offset_y))

    def _load_frames(self):
        frames = []
        frame_width = self.sprite_sheet.get_width() // self.cols
        frame_height = self.sprite_sheet.get_height() // self.rows

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * frame_width
                y = row * frame_height
                frame = self.sprite_sheet.subsurface((x, y, frame_width, frame_height))
                rect = frame.get_bounding_rect()  # trim transparent edges
                frame = frame.subsurface(rect).copy()
                frame = pg.transform.scale(
                    frame, (int(frame.get_width()*self.scale), int(frame.get_height()*self.scale))
                )
                frames.append(frame)
        return frames

    def update(self, dt):
        """Call every frame with dt = clock.tick()"""
        self.timer += dt
        if self.timer >= self.frame_delay:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_frame(self):
        """Returns current frame surface to draw"""
        return self.frames[self.current_frame]

    def get_hitbox(self, x, y, shrink=0.2):
        """
        Returns a consistent hitbox based on first frame size,
        anchored to sprite's feet (bottom center).
        """
        rect = self.base_rect.copy()
        # Position it so feet are anchored at (x, y + height)
        rect.midbottom = (x + rect.width // 2, y + self.base_rect.height)
        return rect.inflate(-rect.width * shrink, -rect.height * shrink)

# --- Initialize Pygame ---
pg.init()
screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
clock = pg.time.Clock()

# --- Usage Tutorial ---
# Creating animations for the player:
#   player_anim = SpriteAnimator("sprites/player_idle.png", rows=3, cols=2, scale=5, frame_delay=300)
#
# Updating the animation each frame:
#   player_anim.update(dt)
#
# Drawing the current frame:
#   player_anim.draw(screen, player_x, player_y)
#
# Getting a smaller hitbox for collisions:
#   hitbox = player_anim.get_hitbox(player_x, player_y, shrink=0.2)
#
# Switching animations for different states:
#   player_idle = SpriteAnimator("sprites/player_idle.png", 3, 2, scale=5, frame_delay=300)
#   player_walk = SpriteAnimator("sprites/player_walk.png", 3, 2, scale=5, frame_delay=100)
#   current_player_anim = player_walk if moving else player_idle
#
# Building a level once into a surface:
#   level_surface, hitboxes = build_level()
#   ...
#   screen.blit(level_surface, (level_x, level_y))

# --- Create player animator ---
player_anim = SpriteAnimator("sprites/player_idle.png", rows=3, cols=2, scale=5, frame_delay=400)
player_walk_anim = SpriteAnimator("sprites/player_walk.png", rows=2, cols=2, scale=5, offset_x=17.5, frame_delay=400)

# open notes
def open_notes(surface, text: str):
    # translucent fullscreen overlay
    overlay = pg.Surface(surface.get_size(), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    # panel
    panel = pg.Rect(560, 140, 800, 800)  # centered-ish
    pg.draw.rect(overlay, (245, 245, 245, 255), panel, border_radius=16)
    pg.draw.rect(overlay, (25, 25, 25, 255), panel, width=3, border_radius=16)

    # title/text
    font = pg.font.Font(None, 48)
    body = pg.font.Font(None, 32)

    title_surf = font.render("Note", True, (20, 20, 20))
    overlay.blit(title_surf, (panel.x + 24, panel.y + 20))

    # simple word-wrap
    def wrap(txt, width):
        words, lines, line = txt.split(), [], ""
        for w in words:
            test = (line + " " + w).strip()
            if body.size(test)[0] <= width: line = test
            else: lines.append(line); line = w
        if line: lines.append(line)
        return lines

    lines = wrap(text, panel.width - 48)
    y = panel.y + 80
    for ln in lines:
        overlay.blit(body.render(ln, True, (30, 30, 30)), (panel.x + 24, y))
        y += 36

    # hint
    hint = pg.font.Font(None, 28).render("Press E again to close", True, (60, 60, 60))
    overlay.blit(hint, (panel.x + 24, panel.bottom - 40))

    surface.blit(overlay, (0, 0))

notes_open = False
toggled = False

# --- Load textures ---
current_level = 1
house_wall_texture = pg.image.load("sprites/house_wall_texture_exterior.png")
house_wall_texture = pg.transform.scale(house_wall_texture, (house_wall_texture.get_width()*6, house_wall_texture.get_height()*6))
interior_wall_texture = pg.image.load("sprites/interior_wall_texture.png")
interior_wall_texture = pg.transform.scale(interior_wall_texture, (interior_wall_texture.get_width()*6, interior_wall_texture.get_height()*6))
house_floor_texture = pg.image.load("sprites/house_floor_texture.png")
house_floor_texture = pg.transform.scale(house_floor_texture, (house_floor_texture.get_width()*6, house_floor_texture.get_height()*6))

# --- Build level into one surface ---
def build_level(current_level, current_direction):
    if current_level == 0:
        # size can be bigger if you want a larger map
        level_surface = pg.Surface((1920, 1080), pg.SRCALPHA)

        # draw all tiles onto this surface once
        level_surface.blit(interior_wall_texture, (929, 40))
        level_surface.blit(interior_wall_texture, (305, 40))

        level_surface.blit(house_floor_texture, (329, 424))
        level_surface.blit(house_floor_texture, (947, 424))
        level_surface.blit(house_floor_texture, (959, 424))
        level_surface.blit(house_floor_texture, (329, 635))
        level_surface.blit(house_floor_texture, (947, 635))
        level_surface.blit(house_floor_texture, (959, 635))

        # define hitboxes separately (world coordinates, not tied to drawing)
        hitboxes = {
            "walls": [
                pg.Rect(929, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                pg.Rect(305, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
            ]
        }
    elif current_level == 1:
        # size can be bigger if you want a larger map
        level_surface = pg.Surface((2200, 1080), pg.SRCALPHA)

        # draw all tiles onto this surface once
        level_surface.blit(interior_wall_texture, (305, 40))
        level_surface.blit(interior_wall_texture, (929, 40))
        level_surface.blit(interior_wall_texture, (1705, 40))

        level_surface.blit(house_floor_texture, (329, 424))
        level_surface.blit(house_floor_texture, (947, 424))
        level_surface.blit(house_floor_texture, (959, 424))
        level_surface.blit(house_floor_texture, (329, 635))
        level_surface.blit(house_floor_texture, (947, 635))
        level_surface.blit(house_floor_texture, (959, 635))
        level_surface.blit(house_floor_texture, (1729, 424))
        level_surface.blit(house_floor_texture, (1729, 635))

        # define hitboxes separately (world coordinates, not tied to drawing)
        hitboxes = {
            "walls": [
                pg.Rect(929, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                pg.Rect(305, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                pg.Rect(1553, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                pg.Rect(0, 850, 2200, 20),
                pg.Rect(310, 200, 20, 900),
                pg.Rect(1553, 300, 200, interior_wall_texture.get_height()+200)
            ]
        }

        if current_direction == 'd':
            level_surface.blit(house_floor_texture, (1400, 424))
            level_surface.blit(house_floor_texture, (1400, 635))

            hitboxes = {
                "walls": [
                    pg.Rect(929, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                    pg.Rect(305, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                    pg.Rect(1553, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                    pg.Rect(0, 850, 2200, 20),
                    pg.Rect(310, 200, 20, 900),
                ]
            }
    elif current_level == 2:
        level_surface = pg.Surface((1920, 1080))
        level_surface.blit(interior_wall_texture, (250, 40))
        level_surface.blit(interior_wall_texture, (624+250, 40))

        level_surface.blit(house_floor_texture, (274, 424))
        level_surface.blit(house_floor_texture, (878, 424))
        level_surface.blit(house_floor_texture, (904, 424))

        hitboxes = {
            "walls": [
                pg.Rect(250, 40, interior_wall_texture.get_width()*2, interior_wall_texture.get_height()-75),
                pg.Rect(210, 400, 50, house_floor_texture.get_height()*2),
                pg.Rect(1520, 400, 50, house_floor_texture.get_height()*2),
                pg.Rect(210, 640, 1600, 50)
            ]
        }
    elif current_level == 3:
        level_surface = pg.Surface((1920+2575, 1080))

        level_surface.blit(interior_wall_texture, (305+1000, 40))
        level_surface.blit(interior_wall_texture, (929+1000, 40))

        level_surface.blit(house_floor_texture, (329+1000, 424))
        level_surface.blit(house_floor_texture, (947+1000, 424))
        level_surface.blit(house_floor_texture, (959+1000, 424))
        level_surface.blit(house_floor_texture, (329+1000, 635))
        level_surface.blit(house_floor_texture, (947+1000, 635))
        level_surface.blit(house_floor_texture, (959+1000, 635))

        hitboxes = {
            "walls": [
                pg.Rect(929+1000, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                pg.Rect(305+1000, 40, interior_wall_texture.get_width(), interior_wall_texture.get_height()-75),
                pg.Rect(1000, 850, 2200, 20),
                pg.Rect(310+1000, 200, 20, 900),
                pg.Rect(1575+1000, 300, 200, interior_wall_texture.get_height()+200)
            ]
        }
    
    elif current_level == 4:
        level_surface = pg.Surface((3000, 1080))

        level_surface.blit(interior_wall_texture, (1605, 40))
        level_surface.blit(interior_wall_texture, (2229, 40))

        level_surface.blit(house_floor_texture, (329+1300, 424))
        level_surface.blit(house_floor_texture, (947+1300, 424))
        level_surface.blit(house_floor_texture, (959+1300, 424))
        level_surface.blit(house_floor_texture, (329+1300, 635))
        level_surface.blit(house_floor_texture, (947+1300, 635))
        level_surface.blit(house_floor_texture, (959+1300, 635))

        hitboxes = {"walls": []}
    
    return level_surface, hitboxes

level_surface, hitboxes = build_level(current_level, 'w')
level_x = 0
level_y = 0

# Build furniture
current_direction = 'w'

bedside_table_1_shelf = pg.image.load('sprites/bedside_table_1_shelf.png').convert_alpha()
bedside_table_1_shelf = pg.transform.scale(bedside_table_1_shelf, (bedside_table_1_shelf.get_width()*3, bedside_table_1_shelf.get_height()*3))
bedside_table_11_shelf = pg.image.load('sprites/bedside_table_11_shelf.png').convert_alpha()
bedside_table_11_shelf = pg.transform.scale(bedside_table_11_shelf, (bedside_table_11_shelf.get_width()*3, bedside_table_11_shelf.get_height()*3))
bedside_table_2_shelf = pg.image.load('sprites/bedside_table_2_shelf.png').convert_alpha()
bedside_table_2_shelf = pg.transform.scale(bedside_table_2_shelf, (bedside_table_2_shelf.get_width()*3, bedside_table_2_shelf.get_height()*3))
bedside_table_21_shelf = pg.image.load('sprites/bedside_table_21_shelf.png').convert_alpha()
bedside_table_21_shelf = pg.transform.scale(bedside_table_21_shelf, (bedside_table_21_shelf.get_width()*3, bedside_table_21_shelf.get_width()*3))
bedside_table_22_shelf = pg.image.load('sprites/bedside_table_22_shelf.png').convert_alpha()
bedside_table_22_shelf = pg.transform.scale(bedside_table_22_shelf, (bedside_table_22_shelf.get_width()*3, bedside_table_22_shelf.get_height()*3))
door_image = pg.image.load('sprites/door.png').convert_alpha()
door_image = pg.transform.scale(door_image, (door_image.get_width()*3, door_image.get_height()*3))
door_opened_image = pg.image.load('sprites/door_opened.png').convert_alpha()
door_opened_image = pg.transform.scale(door_opened_image, (door_opened_image.get_width()*3, door_opened_image.get_height()*3))
key_image = pg.image.load('sprites/key.png').convert_alpha()
lock = pg.image.load('sprites/lock.png').convert_alpha()
note = Note(screen, 'test note')
note_item = pg.image.load('sprites/note_item.png')

def build_furniture(direction, current_level):
    note_item = pg.image.load('sprites/note_item.png')
    note_item = pg.transform.rotate(note_item, 90.0)

    if current_level == 0:
        furniture_surface = pg.Surface((1920, 1080), pg.SRCALPHA)

        if direction == 'w':
            furniture_surface.blit(bedside_table_1_shelf, (500, 320))
            furniture_surface.blit(bedside_table_2_shelf, (900, 320))

            furniture_hitboxes = {
                'shelf': [
                    pg.Rect(500, 320, bedside_table_1_shelf.get_width(), bedside_table_1_shelf.get_height()-130),
                    pg.Rect(540, 415, 112, 40),
                    bedside_table_11_shelf,
                    (500, 320),
                    'key',
                    (580, 420),
                    '0',
                    True
                ],
                'shelf_1': [
                    pg.Rect(0, 0, 0, 0),
                    pg.Rect(0, 0, 0, 0),
                    bedside_table_11_shelf,
                    (-100, -100),
                    'key',
                    (-100, -100),
                    '1',
                    False,
                    'lock',
                    (-100, -100),
                    'shelf',
                    '0'
                ]
                # 'shelf_2': [
                #     pg.Rect(0, 320, bedside_table_1_shelf.get_width(), bedside_table_1_shelf.get_height()-130),
                #     pg.Rect(40, 415, 112, 40),
                #     bedside_table_11_shelf,
                #     (0, 320),
                #     'note',
                #     (80, 420),
                #     '1',
                #     True,
                #     'blank',
                #     'blank',
                #     'blank',
                #     'blank',
                #     'w',
                #     note_item
                # ] # This is how the note looks like
            }    
        elif direction == 'd':
            furniture_surface.blit(bedside_table_1_shelf, (700, 320))
            furniture_surface.blit(door_image, (1200, 230))

            furniture_hitboxes = {
                'shelf': [
                    pg.Rect(0, 0, 0, 0),
                    pg.Rect(0, 0, 0, 0),
                    bedside_table_11_shelf,
                    (-100, -100),
                    'none',
                    (-100, -100),
                    '0', # item id
                    True
                ],
                'shelf_1': [
                    pg.Rect(700, 320, bedside_table_1_shelf.get_width(), bedside_table_1_shelf.get_height()-130),
                    pg.Rect(740, 415, 112, 40),
                    bedside_table_11_shelf,
                    (700, 320),
                    'key',
                    (780, 420),
                    '1',
                    False,
                    'lock',
                    (790, 420),
                    'shelf',
                    '0'
                ],
                'door_locked1': [
                    pg.Rect(1150, 180, door_image.get_width()+100, door_image.get_height()+100),
                    door_opened_image,
                    (1200, 230),
                    False,
                    '2',
                    'door',
                    1,
                    'lock',
                    (1310, 325),
                    'shelf_1',
                    '1'
                ]
            }
        elif direction == 's':
            

            furniture_hitboxes = {
                
            }
        elif direction == 'a':
            furniture_surface.blit(bedside_table_1_shelf, (850, 320))

            furniture_hitboxes = {
                "shelf_3": [
                    pg.Rect(850, 320, bedside_table_11_shelf.get_width(), bedside_table_11_shelf.get_height()-130),
                    pg.Rect(890, 415, 112, 40),
                    bedside_table_11_shelf,
                    (850, 320),
                    'key',
                    (930, 420),
                    '9',
                    True # or idk, think about it
                ]
            }
    elif current_level == 1:
        furniture_surface = pg.Surface((2200, 1080), pg.SRCALPHA)
        furniture_hitboxes = {}

        if direction == 'w':
            furniture_surface.blit(door_image, (400, 230))
            furniture_surface.blit(door_image, (1100, 230))
            furniture_surface.blit(door_image, (1900, 230))
            furniture_surface.blit(bedside_table_1_shelf, (800, 320))

            furniture_hitboxes = {
                "door1": [
                    pg.Rect(350, 180, door_image.get_width()+100, door_image.get_height()+100),
                    door_opened_image,
                    (400, 230),
                    True,
                    '3',
                    'door',
                    0
                ],
                "door2": [
                    pg.Rect(1050, 180, door_image.get_width()+100, door_image.get_height()+100),
                    door_opened_image,
                    (1100, 230),
                    True,
                    '3',
                    'door',
                    2
                ],
                "shelf_2": [
                    pg.Rect(800, 320, bedside_table_1_shelf.get_width(), bedside_table_1_shelf.get_height()-130),
                    pg.Rect(840, 415, 112, 40),
                    bedside_table_11_shelf,
                    (800, 320),
                    'note',
                    (880, 420),
                    '2',
                    True,
                    'blank',
                    'blank',
                    'blank',
                    'blank',
                    'w',
                    note_item,
                    "hidden_note2"
                ],
                "door3": [
                    pg.Rect(1850, 180, door_image.get_width()+100, door_image.get_height()+100),
                    door_opened_image,
                    (1900, 230),
                    True,
                    '4',
                    'door',
                    3
                ]
            }    
        elif direction == 'd':
            furniture_surface.blit(door_image, (1900, 230))

            furniture_hitboxes = {
                "door_locked2": [
                    pg.Rect(1850, 180, door_image.get_width()+100, door_image.get_height()+100),
                    door_opened_image,
                    (1900, 230),
                    False,
                    '3',
                    'door',
                    4,
                    'lock',
                    (2010, 325),
                    "shelf_3",
                    '9'
                ],
                "shelf_3": [
                    pg.Rect(0, 0, 0, 0),
                    pg.Rect(0, 0, 0, 0),
                    bedside_table_11_shelf,
                    (-100, -100),
                    'key',
                    (-100, -100),
                    '9',
                    True # or idk, think about it
                ]
            }

    elif current_level == 2:
        furniture_surface = pg.Surface((1920, 1080), pg.SRCALPHA)
        furniture_hitboxes = {}

        if current_direction == 'w':
            furniture_surface.blit(bedside_table_1_shelf, (800, 320))
            furniture_surface.blit(door_image, (1100, 230))

            furniture_hitboxes = {
                "shelf_4": [
                    pg.Rect(800, 320, bedside_table_1_shelf.get_width(), bedside_table_1_shelf.get_height()-130),
                    pg.Rect(840, 415, 112, 40),
                    bedside_table_11_shelf,
                    (800, 320),
                    'note',
                    (880, 420),
                    '7',
                    True,
                    'none',
                    'none',
                    'none',
                    'none',
                    'w',
                    note_item,
                    'hidden_note7'
                ],
                "door5": [
                    pg.Rect(1050, 180, door_image.get_width()+100, door_image.get_height()+100),
                    opened_door_image,
                    (1100, 230),
                    True,
                    '8',
                    "door",
                    1
                ]
            }
        
        elif current_direction == 's':
            furniture_surface.blit(bedside_table_1_shelf, (800, 320))

            furniture_hitboxes = {
                "shelf_5": [
                    pg.Rect(800, 320, bedside_table_1_shelf.get_width(), bedside_table_1_shelf.get_height()-130),
                    pg.Rect(840, 415, 112, 40),
                    bedside_table_11_shelf,
                    (800, 320),
                    'key',
                    (880, 420),
                    '10',
                    True
                ]
            }

    elif current_level == 3:
        furniture_surface = pg.Surface((2000, 1080), pg.SRCALPHA)
        furniture_hitboxes = {}

        if direction == "w":
            furniture_surface.blit(door_image, (1659, 230))

            furniture_hitboxes = {
                "door5": [
                    pg.Rect(1609, 180, door_image.get_width()+100, door_image.get_height()+100),
                    opened_door_image,
                    (1659, 230),
                    True,
                    '5',
                    'door',
                    1
                ]
            }

        elif direction == 'd':
            furniture_surface.blit(door_image, (1800, 230))

            furniture_hitboxes = {
                "door_locked3": [
                    pg.Rect(1750, 180, door_image.get_width()+100, door_image.get_height()+100),
                    opened_door_image,
                    (1800, 230),
                    False,
                    '6',
                    'door',
                    4,
                    'lock',
                    (1910, 325),
                    "none",
                    "shelf_3",
                    '10' # key is in room id 2
                ]
            }

    elif current_level == 4:
        furniture_surface = pg.Surface((2000, 1080), pg.SRCALPHA)
        furniture_hitboxes = {}

    return furniture_surface, furniture_hitboxes

furniture_surface, furniture_hitboxes = build_furniture(current_direction, current_level)

def lock_logic(furniture_hitboxes, lock_name, key_name, binded_item_id):
    if lock_name == 'lock':
        locks_key = furniture_hitboxes[key_name][6]
        if locks_key == binded_item_id and locks_key in taken_items:
            taken_items.pop(taken_items.index(locks_key))
            lock_name = 'none'
            used_items.append(binded_item_id)

# load items

def build_items(direction, current_level):
    if current_level == 0:
        items_surface = pg.Surface((1920, 1080), pg.SRCALPHA)

        if direction == 'w':
            items_surface.blit(note_item, (600, 350))
            items_surface.blit(pg.transform.rotate(note_item, 36.0), (1000, 370))

            items_hitboxes = {
                'item_note': [pg.Rect(470, 230, 250, 200)],
                'item_note4': [pg.Rect(870, 230, 250, 200)]
            }
        elif direction == 'd':
            items_surface.blit(note_item, (800, 350))

            items_hitboxes = {
                'item_note1': [pg.Rect(670, 230, 250, 200)]
            }
        elif direction == 's':
            items_surface.blit(note_item, (700, 350))

            items_hitboxes = {
                'item_note2': [pg.Rect(570, 230, 250, 200)]
            }
        elif direction == 'a':


            items_hitboxes = {

            }

    elif current_level == 1:
        items_surface = pg.Surface((2200, 1080), pg.SRCALPHA)

        if direction == 'w':
            items_surface.blit(pg.transform.rotate(note_item, 56.0), (910, 695))

            items_hitboxes = {
                'item_note5': [pg.Rect(800, 600, 250, 200)]
            }
        elif direction == 'd':
            items_surface.blit(pg.transform.rotate(note_item, 234.0), (1200, 600))

            items_hitboxes = {
                "item_note6": [pg.Rect(1090, 505, 250, 200)]
            }
        elif direction == 's':

            items_hitboxes = {
                
            }
        elif direction == 'a':

            items_hitboxes = {
                
            }
    
    elif current_level == 2:
        items_surface = pg.Surface((1920, 1080), pg.SRCALPHA)

        if direction == 'w':
            
            items_hitboxes = {}
        if direction == 'a':
            
            items_hitboxes = {}
        if direction == 's':
            
            items_hitboxes = {}
        if direction == 'd':
            
            items_hitboxes = {}
    
    elif current_level == 3:
        items_surface = pg.Surface((3000, 1080), pg.SRCALPHA)

        if direction == 'w':
            items_surface.blit(note_item, (2500, 500))
            
            items_hitboxes = {
                "item_note6": [pg.Rect(2370, 420, 250, 200)]
            }
        if direction == 'a':
            
            items_hitboxes = {}
        if direction == 's':
            items_surface.blit(note_item, (1930, 700))
            
            items_hitboxes = {
                "item_note7": [pg.Rect(1800, 640, 250, 200)]
            }
        if direction == 'd':
            
            items_hitboxes = {}
    
    elif current_level == 4:
        items_surface = pg.Surface((3000, 1080), pg.SRCALPHA)
        items_hitboxes = {}

        if direction == 'w':
            
            items_hitboxes = {
                
            }
        elif direction == 'a':
            pass
        elif direction == 's':
            pass
        elif direction == 'd':
            pass

    return items_surface, items_hitboxes

items_surface, items_hitboxes = build_items(current_direction, current_level)


items_with_notesW = {
    "item_note": Note(screen, "Walking is a crazy proccess. <br>\tBut look at this guy. He just opened the game and already walks. <br> <br> Alr i'm kidding. Just leave the note and pess the right arrow."),
    "item_note4": Note(screen, "Well, at first, i wanted to make this thing work. But eventually this is shit idea cuz it takes too much RAM. So please play with that :("),
    "item_note5": Note(screen, "Ебать - Черный квадрат МаЛЕВичО!!<br>(ya znayu chto eto ne on)"),
    "hidden_note2": Note(screen, "Literally changed my UI to German everywhere."),
    "item_note6": Note(screen, "You got the dud hahahah :)\n\n\n\n\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\tQUICK"),
    "hidden_note7": Note(screen, "Only UP - is a game where while you are playing, you might just sell your pc to the window.") # FIRST DIRECTION
}

items_with_notesD = {
    "item_note1": Note(screen, "Congrats on reaching the right side of the room. Now you are in a trap. <br><br> Can you find a way to get back? <br><br><br><br><br> Maybe tho check the shelf?"),
    "hidden_note2": Note(screen, "Literally changed my UI to German everywhere."),
    "item_note6": Note(screen, "Monsters don't care about you changing dimensions."),
    "hidden_note7": Note(screen, "Only UP - is a game where while you are playing, you might just sell your pc to the window.")
}

items_with_notesS = {
    "item_note7": Note(screen, "00110111 01000001 00100000 00110110 01000110 00100000 00110110 00110111 00100000 00110110 00111000 00100000 00110010 00110000 00100000 00110010 01000100 00100000 00110010 00110000 00100000 00110110 00110110 00100000 00110111 00110111 00100000 00110111 00110101 00100000 00110111 00110110 00100000 00110110 00111000"),
    "hidden_note7": Note(screen, "Only UP - is a game where while you are playing, you might just sell your pc to the window.")
}

items_with_notesA = {
    "hidden_note7": Note(screen, "Only UP - is a game where while you are playing, you might just sell your pc to the window.")
}

# --- Debug: draw all hitboxes ---
def draw_debug_hitboxes():
    # walls = red
    for wall in hitboxes["walls"]:
        moved_wall = wall.move(level_x, level_y)
        pg.draw.rect(screen, (255, 0, 0), moved_wall, 2)

    # furniture = blue
    for obj_list in furniture_hitboxes.values():
        moved_obj = obj_list[0].move(level_x, level_y)
        if obj_list[5] != 'door':
            moved_obj1 = obj_list[1].move(level_x, level_y)
            pg.draw.rect(screen, (0, 0, 255), moved_obj1, 2)
        pg.draw.rect(screen, (0, 0, 255), moved_obj, 2)

    # items = green
    for obj_list in items_hitboxes.values():
        for obj in obj_list:
            moved_obj = obj.move(level_x, level_y)
            pg.draw.rect(screen, (0, 255, 0), moved_obj, 2)

    # player = yellow
    pg.draw.rect(screen, (255, 255, 0), player_hitbox, 2)

# Flags
dir_w_avail = True # default
dir_d_avail = True # default
dir_a_avail = True
dir_s_avail = True
checking_drawer = False
current_drawer = None
current_door_avail = False

# other stuff
taken_items = []
used_items = []
hidden_notes = [
    # ('hidden_note1', [pg.Rect(furniture_hitboxes['shelf_2'][5][0]-105, furniture_hitboxes['shelf_2'][5][1]-100, 250, 200)]) # And it's also has to be here.
    ("hidden_note2", [pg.Rect(775, 320, 250, 200)]),
    ("hidden_note7", [pg.Rect(775, 320, 250, 200)])
]
level_list = [0, 1, 2, 3, 4]

# --- Player state ---
player_x, player_y = 900, 480
player_speed = 300
player_upM = player_downM = player_leftM = player_rightM = False
player_flipped = False
reached_edge_up = reached_edge_left = reached_edge_down = reached_edge_right = False

# --- Game loop ---
running = True
while running:
    # print(current_level)
    # print(player_x)
    dt = clock.tick(60)
    items_surface, items_hitboxes = build_items(current_direction, current_level)
    furniture_surface, furniture_hitboxes = build_furniture(current_direction, current_level)
    level_surface, hitboxes = build_level(current_level, current_direction)
    mpos = pg.mouse.get_pos()

    # First, put all hidden notes into items_hitboxes
    for key, hitbox in hidden_notes:
        for obj in furniture_hitboxes.values():
            if obj[5] != 'door' and len(obj) > 12:
                if key == obj[14]:
                    if checking_drawer:
                        items_hitboxes[key] = hitbox
                    else:
                        items_hitboxes.pop(key, None)

    # Then handle the drawer check
    for key, obj in furniture_hitboxes.items():
        checking_drawer = False
        if not key.startswith("door"):
            m_collision = obj[1].move(level_x, level_y).collidepoint(mpos)

            # print(f"Debug in CCD logic:\n\tmouse collision: {m_collision}\n\tchecking_drawer: {checking_drawer}\n\tRect: {obj[1]}\n\tFurniture hitboxes length: {len(furniture_hitboxes)}\n\n\tWhole object: {obj}\n")

            if m_collision:
                checking_drawer = True
                # print(f"Current drawer: {key}")
                break

    # Set door availability for key E event
    for key, obj in furniture_hitboxes.items():
        if key.startswith("door"):
            door_availiability = obj[3]
            if not door_availiability and len(obj) > 7:
                binded_item_id = obj[10]

                # print(f"Debug in CDA:\n\tbinded_item_id: {binded_item_id}\n\tbinded_item_id in taken_items: {binded_item_id in taken_items}\n\ttaken_items: {taken_items}\n")

                if binded_item_id in taken_items:
                    # print("setting door_availiavility to true for the key event logic")
                    door_availability = True
                    current_door_avail = True
                    break

        # print(f"Current door: {key}")

    # --- Events ---
    for e in pg.event.get():
        if e.type == pg.QUIT:
            running = False

        if e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                running = False

            # movement keys should only be blocked if ANY note is open
            if current_direction == 'w':
                if not any(note.check_opened() for note in items_with_notesW.values()):
                    if e.key == pg.K_w: player_upM = True
                    if e.key == pg.K_a:
                        player_leftM = True
                        player_rightM = False
                        player_flipped = True
                    if e.key == pg.K_s: player_downM = True
                    if e.key == pg.K_d:
                        player_rightM = True
                        player_leftM = False
                        player_flipped = False
                    if e.key == pg.K_RIGHT:
                        current_direction = 'd'
                    if e.key == pg.K_DOWN and dir_s_avail:
                        current_direction = 's'
                    if e.key == pg.K_LEFT and dir_a_avail:
                        current_direction = 'a'
            elif current_direction == 'd':
                if not any(note.check_opened() for note in items_with_notesW.values()):
                    if e.key == pg.K_w: player_upM = True
                    if e.key == pg.K_a:
                        player_leftM = True
                        player_rightM = False
                        player_flipped = True
                    if e.key == pg.K_s: player_downM = True
                    if e.key == pg.K_d:
                        player_rightM = True
                        player_leftM = False
                        player_flipped = False
                    if e.key == pg.K_UP:
                        current_direction = 'w'
                    if e.key == pg.K_DOWN and dir_s_avail:
                        current_direction = 's'
                    if e.key == pg.K_LEFT and dir_a_avail:
                        current_direction = 'a'
            elif current_direction == 's':
                if not any(note.check_opened() for note in items_with_notesW.values()):
                    if e.key == pg.K_w: player_upM = True
                    if e.key == pg.K_a:
                        player_leftM = True
                        player_rightM = False
                        player_flipped = True
                    if e.key == pg.K_s: player_downM = True
                    if e.key == pg.K_d:
                        player_rightM = True
                        player_leftM = False
                        player_flipped = False
                    if e.key == pg.K_UP:
                        current_direction = 'w'
                    if e.key == pg.K_RIGHT:
                        current_direction = 'd'
                    if e.key == pg.K_LEFT and dir_a_avail:
                        current_direction = 'a'
            elif current_direction == 'a':
                if not any(note.check_opened() for note in items_with_notesW.values()):
                    if e.key == pg.K_w: player_upM = True
                    if e.key == pg.K_a:
                        player_leftM = True
                        player_rightM = False
                        player_flipped = True
                    if e.key == pg.K_s: player_downM = True
                    if e.key == pg.K_d:
                        player_rightM = True
                        player_leftM = False
                        player_flipped = False
                    if e.key == pg.K_UP:
                        current_direction = 'w'
                    if e.key == pg.K_RIGHT:
                        current_direction = 'd'
                    if e.key == pg.K_DOWN and dir_s_avail:
                        current_direction = 's'

            if e.key == pg.K_e:
                player_hitbox = player_anim.get_hitbox(player_x, player_y)

                for key, obj in furniture_hitboxes.items():
                    if key.startswith("door") and (obj[3] or current_door_avail): # and door_availibility
                        # print(f"Whole door obj for key {key}: {obj}")
                        door_hitbox = obj[0]
                        opened_door_image = obj[1]
                        opened_door_image_position = obj[2]
                        door_avail = obj[3]
                        door_id = obj[4]
                        going_to_level_id = obj[6]

                        # print(f"Debug in OPD:\n\tdoor_hitbox: {door_hitbox}\n\tdoor_avail: {door_avail}\n\t?hitbox: {player_hitbox.colliderect(door_hitbox.move(level_x, level_y))}\n\tgoing_to_level_id: {going_to_level_id}\n\tcurrent_level: {current_level}\n")

                        if player_hitbox.colliderect(door_hitbox.move(level_x, level_y)):
                            # print(f"teleporting to room: {going_to_level_id}")
                            current_level = going_to_level_id
                            break

                for key, obj_list in items_hitboxes.items():
                    if player_hitbox.colliderect(obj_list[0].move(level_x, level_y)):
                        if current_direction == 'w':
                            if key in items_with_notesW:
                                items_with_notesW[key].toggle()
                        elif current_direction == 'd':
                            if key in items_with_notesD:
                                items_with_notesD[key].toggle()
                        elif current_direction == 's':
                            if key in items_with_notesS:
                                items_with_notesS[key].toggle()
                        elif current_direction == 'a':
                            if key in items_with_notesA:
                                items_with_notesA[key].toggle()

                        break  # stop after first hit

        if e.type == pg.KEYUP:
            if e.key == pg.K_w: player_upM = False
            if e.key == pg.K_a: player_leftM = False
            if e.key == pg.K_s: player_downM = False
            if e.key == pg.K_d: player_rightM = False


    scroll_speed = 5

    # --- Edge checks and scrolling ---
    reached_edge_right = player_x >= 1460 - player_anim.get_frame().get_width()
    reached_edge_left  = player_x <= 460
    reached_edge_down  = player_y >= 470 + player_anim.get_frame().get_height()
    reached_edge_up    = player_y <= 240

    if reached_edge_right and player_rightM:
        level_x -= scroll_speed
    if reached_edge_left and player_leftM:
        level_x += scroll_speed
    if reached_edge_down and player_downM:
        level_y -= scroll_speed
    if reached_edge_up and player_upM:
        level_y += scroll_speed

    # --- Fix player position after scrolling ---
    player_hitbox = player_anim.get_hitbox(player_x, player_y)
    for wall in hitboxes["walls"]:
        moved_wall = wall.move(level_x, level_y)
        if player_hitbox.colliderect(moved_wall):
            # Push player out of wall (revert to previous position)
            # You can store prev_x, prev_y before scrolling for more accuracy
            # Here, just move player outside the wall on X and Y
            if player_hitbox.right > moved_wall.left and player_hitbox.left < moved_wall.left:
                player_x = moved_wall.left - player_hitbox.width
            elif player_hitbox.left < moved_wall.right and player_hitbox.right > moved_wall.right:
                player_x = moved_wall.right
            if player_hitbox.bottom > moved_wall.top and player_hitbox.top < moved_wall.top:
                player_y = moved_wall.top - player_hitbox.height
            elif player_hitbox.top < moved_wall.bottom and player_hitbox.bottom > moved_wall.bottom:
                player_y = moved_wall.bottom
            player_hitbox = player_anim.get_hitbox(player_x, player_y)

    # --- Movement ---
    dx = dy = 0
    if player_upM and not reached_edge_up: dy -= 1
    if player_downM and not reached_edge_down: dy += 1
    if player_leftM and not reached_edge_left: dx -= 1
    if player_rightM and not reached_edge_right: dx += 1
    if dx != 0 and dy != 0:
        dx *= 0.707
        dy *= 0.707

    # --- Collision-aware movement ---
    prev_x = player_x
    player_x += dx * player_speed * (dt / 1000)
    player_sprite = player_anim.get_frame()
    player_x = max(0, min(1920 - player_sprite.get_width(), player_x))
    player_hitbox = player_anim.get_hitbox(player_x, player_y)

    # check walls
    for wall in hitboxes["walls"]:
        moved_wall = wall.move(level_x, level_y)
        if player_hitbox.colliderect(moved_wall):
            if dx > 0:
                player_x = prev_x -10
            elif dx < 0:
                player_x = prev_x +10 

            break

    # check furniture
    # for obj_list in furniture_hitboxes.values():
    #     for obj in obj_list:
    #         moved_obj = obj.move(level_x, level_y)
    #         if player_hitbox.colliderect(moved_obj):
    #             player_x = prev_x
    #             break

    for obj_list in furniture_hitboxes.values():
        if obj_list[5] != 'door':
            moved_obj = obj_list[0].move(level_x, level_y)
            moved_obj1 = obj_list[1].move(level_x, level_y)
            if player_hitbox.colliderect(moved_obj):
                player_x = prev_x
                break

    prev_y = player_y
    player_y += dy * player_speed * (dt / 1000)
    player_y = max(0, min(1080 - player_sprite.get_height(), player_y))
    player_hitbox = player_anim.get_hitbox(player_x, player_y)

    # check walls
    for wall in hitboxes["walls"]:
        moved_wall = wall.move(level_x, level_y)
        if player_hitbox.colliderect(moved_wall):
            if dy > 0:
                player_y = prev_y -13
            elif dy < 0:
                player_y = prev_y

            break


    # check furniture
    # for obj_list in furniture_hitboxes.values():
    #     for obj in obj_list:
    #         moved_obj = obj.move(level_x, level_y)
    #         if player_hitbox.colliderect(moved_obj):
    #             player_y = prev_y
    #             break

    for obj_list in furniture_hitboxes.values():
        if obj_list[5] != 'door':
            moved_obj = obj_list[0].move(level_x, level_y)
            moved_obj1 = obj_list[1].move(level_x, level_y)
            if player_hitbox.colliderect(moved_obj):
                player_y = prev_y
                break

    # open up that drawer
    for obj in furniture_hitboxes.values():
        if obj[5] != 'door':
            # storing those objects for easier readability
            drawer_hitbox = obj[1]
            opened_image = obj[2]
            opened_image_pos = obj[3]
            item_name = obj[4]
            item_pos = obj[5]
            item_id = obj[6]
            item_availability = obj[7]

            obj_moved = drawer_hitbox.move(level_x, level_y)
            mouse_collision = obj_moved.collidepoint(mpos)

            # checking if the item is locked
            if len(obj) > 8:
                # storing some more objects for easier readability
                lock_name = obj[8]
                lock_pos = obj[9]
                key_name = obj[10]
                binded_item_id = obj[11]

                # print(f"Debug:\n\tlock_name: {lock_name}\n\tchecking_drawer: {checking_drawer}")
                
                # This just deletes the lock completely so it doesn't fucking draw it once and for all
                if checking_drawer and lock_name == 'lock':
                    lock_name = 'none'
                    # print("lock name setted to none")

                # That's like blitting the lock image if the item is not used
                if binded_item_id not in used_items and lock_name == 'lock':
                    # print('blitting the lock in drawer logic')
                    items_surface.blit(lock, lock_pos)

                # This one is checking if the item was taken, so the drawer can be opened.
                if binded_item_id in taken_items:
                    item_availability = True
            
            # uh don't even ask me what this is. It works, be glad.
            if mouse_collision and item_availability and item_id not in used_items:
                checking_drawer = True

                if item_id not in taken_items and item_name == 'key': items_surface.blit(key_image, item_pos)

                if item_name == 'note': 
                    direction = obj[12]
                    note_image = obj[13]
                    note_link = obj[14]

                    if not checking_drawer:
                        items_hitboxes.pop(f"hidden_note{item_id}")
                        hidden_notes.pop(f"hidden_note{item_id}")

                    if current_direction == 'w':
                        note_instance = items_with_notesW[f"hidden_note{item_id}"]
                    elif current_direction == 'a':
                        note_instance = items_with_notesA[f"hidden_note{item_id}"]
                    elif current_direction == 's':
                        note_instance = items_with_notesS[f"hidden_note{item_id}"]
                    elif current_direction == 'd':
                        note_instance = items_with_notesD[f"hidden_note{item_id}"]

                    for i in hidden_notes:
                        if i[0] == note_link:
                            note_hitbox = i[1]
                            
                    items_surface.blit(note_image, item_pos)

                    if direction == 'w' and f"hidden_note{item_id}" not in items_hitboxes:
                        items_with_notesW[f"hidden_note{item_id}"] = note_instance
                        hidden_notes.append((f"hidden_note{item_id}", note_hitbox))
                        items_hitboxes[f"hidden_note{item_id}"] = note_hitbox

                furniture_surface.blit(opened_image, opened_image_pos)
                if player_hitbox.colliderect(obj_moved):
                    if item_name == 'key' or item_name == 'lock':
                        if item_id not in taken_items:
                            taken_items.append(item_id)
                        else:
                            item_name = 'none'
                            
                    if len(obj) > 8:
                        lock_logic(furniture_hitboxes, lock_name, key_name, binded_item_id)
                    
        # open the dooooor
        for obj in furniture_hitboxes.values():
            if obj[5] == 'door':
                door_hitbox = obj[0]
                opened_door_image = obj[1]
                opened_door_pos = obj[2]
                door_availability = obj[3]
                door_id = obj[4]
                door_name = obj[5]
                level_to_travel = obj[6]

                if len(obj) > 7:
                    lock_name = obj[7]
                    lock_pos = obj[8]
                    binded_furniture_name = obj[9]
                    binded_item_id = obj[10]

                    if binded_item_id in taken_items:
                        door_availability = True

                    if binded_item_id not in taken_items and binded_item_id not in used_items and not door_availability:
                        items_surface.blit(lock, lock_pos)

                if player_hitbox.colliderect(door_hitbox.move(level_x, level_y)) and door_availability:
                    furniture_surface.blit(opened_door_image, opened_door_pos)

    # --- Update animation ---
    player_anim.update(dt)
    player_walk_anim.update(dt)

    # --- Draw ---
    screen.fill((0, 0, 0))
    screen.blit(level_surface, (level_x, level_y))
    screen.blit(furniture_surface, (level_x, level_y))
    screen.blit(items_surface, (level_x, level_y))
    current_anim = player_walk_anim if (player_upM or player_leftM or player_downM or player_rightM) else player_anim
    current_anim.draw(screen, player_x, player_y, flip_x=player_flipped)
    draw_debug_hitboxes()
    if current_direction == 'w':
        for note in items_with_notesW.values():
            if note.check_opened():
                note.draw()
    elif current_direction == 'd':
        for note in items_with_notesD.values():
            if note.check_opened():
                note.draw()
    elif current_direction == 's':
        for note in items_with_notesS.values():
            if note.check_opened():
                note.draw()
    elif current_direction == 'a':
        for note in items_with_notesA.values():
            if note.check_opened():
                note.draw()
    pg.display.flip()

pg.quit()
