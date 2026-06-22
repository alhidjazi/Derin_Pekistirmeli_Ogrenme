import pygame
import random
import heapq
import numpy as np
import math

WIDTH, HEIGHT = 1250, 780
GRID_SIZE = 20
CELL_SIZE = 32
MAP_OFFSET = (30, 70)
PANEL_X = 700
PANEL_W = WIDTH - PANEL_X


BG_COLOR      = (28, 32, 38)
ROAD_COLOR    = (38, 44, 52)
ROAD_LINE     = (48, 56, 66)
BUILD_DARK    = (42, 50, 62)
BUILD_MID     = (52, 62, 76)
BUILD_LIGHT   = (65, 78, 96)
BUILD_WINDOW  = (90, 130, 170)
PANEL_BG      = (24, 28, 36)
PANEL_BORDER  = (55, 68, 88)
ACCENT_BLUE   = (90, 160, 220)
ACCENT_CYAN   = (70, 190, 180)
ACCENT_GREEN  = (80, 185, 130)
ACCENT_ORANGE = (210, 145, 70)
ACCENT_RED    = (200, 90, 100)
ACCENT_PURPLE = (140, 105, 200)
TEXT_WHITE    = (215, 225, 235)
TEXT_DIM      = (140, 158, 178)
TEXT_BRIGHT   = (240, 246, 252)
GOLD          = (220, 185, 90)


LOCATION_DEFS = [
    ("Merkez AVM",      "mall",      (200, 140, 70)),
    ("Teknopark",       "tech",      (80, 155, 210)),
    ("Şehir Hastanesi", "hospital",  (190, 90, 100)),
    ("Liman Deposu",    "warehouse", (160, 135, 90)),
    ("Üniversite",      "edu",       (130, 100, 190)),
    ("Gıda Market",     "market",    (80, 170, 120)),
    ("Hava Limanı",     "airport",   (75, 160, 190)),
    ("Sanayi Bölgesi",  "factory",   (175, 140, 75)),
]

def draw_rounded_rect(surf, color, rect, radius=10, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

def draw_gradient_rect(surf, rect, color_top, color_bot):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * t)
        pygame.draw.line(surf, (r, g, b), (x, y + i), (x + w, y + i))


def draw_motor_icon(surf, cx, cy, size=14, heading_right=True):
    """Motosiklet görünümünde kurye ikonu."""
    s = size

    body_pts = [
        (cx - s, cy),
        (cx - s//2, cy - s//2),
        (cx + s//3, cy - s//2),
        (cx + s, cy - s//6),
        (cx + s, cy + s//4),
        (cx - s, cy + s//4),
    ]
    pygame.draw.polygon(surf, ACCENT_ORANGE, body_pts)
    pygame.draw.polygon(surf, GOLD, body_pts, 1)

    pygame.draw.circle(surf, (60, 60, 80), (cx + s - 2, cy + s//2), s//3 + 1)
    pygame.draw.circle(surf, ACCENT_ORANGE, (cx + s - 2, cy + s//2), s//3)
    pygame.draw.circle(surf, GOLD, (cx + s - 2, cy + s//2), s//3, 1)
    # Arka tekerlek
    pygame.draw.circle(surf, (60, 60, 80), (cx - s + 2, cy + s//2), s//3 + 1)
    pygame.draw.circle(surf, ACCENT_ORANGE, (cx - s + 2, cy + s//2), s//3)
    pygame.draw.circle(surf, GOLD, (cx - s + 2, cy + s//2), s//3, 1)

    pygame.draw.circle(surf, ACCENT_CYAN, (cx, cy - s//2 - 3), s//3)

    pygame.draw.circle(surf, (255, 255, 180), (cx + s, cy - s//8), 3)

def draw_building_icon(surf, cx, cy, icon_type, color, size=11, visited=False):
    """Her lokasyon tipi için ayrı vektör ikon."""
    alpha = 100 if visited else 255
    s = size

    if icon_type == "hospital":

        pygame.draw.rect(surf, color if not visited else (80, 80, 80),
                         (cx - s, cy - s, s*2, s*2), border_radius=2)
        pygame.draw.rect(surf, (255,255,255) if not visited else (150,150,150),
                         (cx - 2, cy - s + 2, 4, s*2 - 4))
        pygame.draw.rect(surf, (255,255,255) if not visited else (150,150,150),
                         (cx - s + 2, cy - 2, s*2 - 4, 4))

    elif icon_type == "mall":

        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - s, cy - s//2, s*2, s + s//2), border_radius=2)
        pygame.draw.polygon(surf, (color[0]//2, color[1]//2, color[2]//2) if not visited else (60,60,60),
                            [(cx - s, cy - s//2), (cx, cy - s - 4), (cx + s, cy - s//2)])

        for wx in [-s//2, s//2 - 2]:
            pygame.draw.rect(surf, BUILD_WINDOW if not visited else (60,60,80),
                             (cx + wx - 3, cy - 2, 6, 7), border_radius=1)

    elif icon_type == "tech":
        # Monitör
        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - s, cy - s, s*2, int(s*1.4)), border_radius=3)
        pygame.draw.rect(surf, BUILD_WINDOW if not visited else (40,50,70),
                         (cx - s + 3, cy - s + 3, s*2 - 6, int(s*1.4) - 8))
        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - 4, cy + s//2 - 2, 8, 5))

    elif icon_type == "warehouse":

        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - s, cy - s//3, s*2, s + s//3))
        pygame.draw.polygon(surf, (min(color[0]+40,255), color[1], color[2]) if not visited else (100,90,60),
                            [(cx - s - 2, cy - s//3), (cx, cy - s - 2), (cx + s + 2, cy - s//3)])

        pygame.draw.rect(surf, (20,20,35) if not visited else (50,50,50),
                         (cx - 4, cy + 2, 8, s//2 + 2))

    elif icon_type == "edu":

        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - s, cy - s//2, s*2, s + s//2))
        for col_x in [-s + 3, -s//3, s//3, s - 3]:
            pygame.draw.rect(surf, (min(color[0]+30,255), min(color[1]+30,255), min(color[2]+30,255)) if not visited else (100,100,100),
                             (cx + col_x - 2, cy - s//2 - 6, 4, s//2 + 6))
        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - s - 2, cy - s//2 - 8, s*2 + 4, 5))

    elif icon_type == "market":

        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - s, cy - s//2, s*2, s + s//2), border_radius=2)
        awning = color if not visited else (80,80,80)
        pygame.draw.polygon(surf, awning,
                            [(cx - s, cy - s//2), (cx - s, cy - s//2 + 5),
                             (cx + s, cy - s//2 + 5), (cx + s, cy - s//2)])
        pygame.draw.line(surf, (255,255,255) if not visited else (150,150,150),
                         (cx - s, cy - s//2), (cx + s, cy - s//2), 2)

    elif icon_type == "airport":

        pts = [
            (cx, cy - s), (cx + s//3, cy), (cx + s, cy + s//3),
            (cx + s//2, cy + s//2), (cx, cy + s//4),
            (cx - s//2, cy + s//2), (cx - s, cy + s//3), (cx - s//3, cy)
        ]
        pygame.draw.polygon(surf, color if not visited else (80,80,80), pts)
        pygame.draw.polygon(surf, TEXT_WHITE if not visited else (120,120,120), pts, 1)

    elif icon_type == "factory":

        pygame.draw.rect(surf, color if not visited else (80,80,80),
                         (cx - s, cy - s//3, s*2, s + s//3))
        pygame.draw.rect(surf, (min(color[0]+20,255), color[1], color[2]) if not visited else (100,90,50),
                         (cx - s//2 - 2, cy - s - 4, 7, s + 4))
        pygame.draw.rect(surf, (min(color[0]+20,255), color[1], color[2]) if not visited else (100,90,50),
                         (cx + s//4, cy - s + 2, 7, s + 2))

        if not visited:
            for i, bx in enumerate([-s//2 + 1, s//4 + 3]):
                pygame.draw.circle(surf, (150,150,150), (cx + bx, cy - s - 6 - i*2), 4)


class CyberDelivery:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Akıllı Lojistik Simülatörü")
        self.clock = pygame.time.Clock()
        self.tick_count = 0

        self.font_title  = pygame.font.SysFont("Consolas", 20, bold=True)
        self.font_main   = pygame.font.SysFont("Consolas", 15, bold=True)
        self.font_small  = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_bold   = pygame.font.SysFont("Consolas", 17, bold=True)
        self.font_big    = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_label  = pygame.font.SysFont("Consolas", 12, bold=True)

        self.num_targets = 6
        self.btn_start = pygame.Rect(0, 0, 0, 0)
        self.btn_reset = pygame.Rect(0, 0, 0, 0)
        self.btn_graph = pygame.Rect(0, 0, 0, 0)
        self.delivery_log = []
        self.speed_level = 2
        self.episode_done = False
        self.show_graph = False
        self.reset_env()


    def reset_env(self):
        self.grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.building_colors = {}
        self._gen_buildings()
        self.depot = (0, 0)

        chosen = random.sample(LOCATION_DEFS, min(self.num_targets, len(LOCATION_DEFS)))
        self.target_data = []
        while len(self.target_data) < self.num_targets:
            pos = (random.randint(1, 19), random.randint(1, 19))
            if self.grid[pos[0]][pos[1]] == 0 and pos != self.depot:
                if not any(t["pos"] == pos for t in self.target_data):
                    defn = chosen[len(self.target_data) % len(chosen)]
                    self.target_data.append({
                        "pos": pos, "name": defn[0],
                        "icon": defn[1], "color": defn[2],
                        "visited": False, "visit_time": None
                    })

        self.pos = list(self.depot)
        self.path = []
        self.trail = []
        self.time = 0
        self.elapsed_s = 0
        self.score = 0
        self.penalties = 0
        self.is_running = False
        self.current_target_name = "Bekleniyor..."
        self.current_target_icon = "mall"
        self.current_target_color = ACCENT_BLUE
        self.delivery_log = []
        self.heading = (0, 1)
        self.episode_done = False
        self.show_graph = False
        self._plan_smart_path()

    def _gen_buildings(self):
        palette = [
            (BUILD_DARK, BUILD_MID),
            (BUILD_MID, BUILD_LIGHT),
            ((15,18,42), (28,38,80)),
        ]
        for _ in range(15):
            r, c = random.randint(2, 17), random.randint(2, 17)
            w = random.randint(1, 3)
            h = random.randint(1, 2)
            clr = random.choice(palette)
            for i in range(r, min(r+h, GRID_SIZE-1)):
                for j in range(c, min(c+w, GRID_SIZE-1)):
                    self.grid[i][j] = -1
                    self.building_colors[(i, j)] = clr

    def _plan_smart_path(self):
        unvisited = [t for t in self.target_data if not t["visited"]]
        if unvisited:
            cp = np.array(self.pos)
            best = min(unvisited, key=lambda t: np.linalg.norm(cp - np.array(t["pos"])))
            self.current_target_name  = best["name"]
            self.current_target_icon  = best["icon"]
            self.current_target_color = best["color"]
            self.path = self.a_star(tuple(self.pos), best["pos"])
        else:
            self.current_target_name = "Tüm Teslimatlar Bitti!"
            self.is_running = False
            self.episode_done = True

    def a_star(self, start, goal):
        queue = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        while queue:
            current = heapq.heappop(queue)[1]
            if current == goal:
                p = []
                while current in came_from:
                    p.append(current); current = came_from[current]
                return p[::-1]
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nb = (current[0]+dx, current[1]+dy)
                if 0 <= nb[0] < GRID_SIZE and 0 <= nb[1] < GRID_SIZE and self.grid[nb[0]][nb[1]] != -1:
                    tg = g_score[current] + 1
                    if tg < g_score.get(nb, 9999):
                        came_from[nb] = current; g_score[nb] = tg
                        f = tg + abs(nb[0]-goal[0]) + abs(nb[1]-goal[1])
                        heapq.heappush(queue, (f, nb))
        return []


    def update_logic(self):
        if self.is_running and self.path:
            prev = tuple(self.pos)
            nxt = self.path.pop(0)
            self.heading = (nxt[0] - prev[0], nxt[1] - prev[1])
            self.pos = list(nxt)
            self.time += 1
            self.elapsed_s += 1
            pen = {1: 0.4, 2: 0.8, 3: 1.4}.get(self.speed_level, 0.8)
            self.penalties += pen

            self.trail.append(tuple(self.pos))
            if len(self.trail) > 30:
                self.trail.pop(0)

            for target in self.target_data:
                if not target["visited"] and tuple(self.pos) == target["pos"]:
                    target["visited"] = True
                    target["visit_time"] = self.elapsed_s
                    bonus = max(50, 300 - self.elapsed_s * 2)
                    self.score += bonus
                    self.delivery_log.append({
                        "name": target["name"],
                        "time": self.elapsed_s,
                        "bonus": bonus
                    })
                    self._plan_smart_path()
                    break


    def draw(self):
        self.tick_count += 1
        self.screen.fill(BG_COLOR)

        self._draw_map()
        self._draw_panel()
        if self.show_graph:
            self._draw_graph_overlay()
        pygame.display.flip()

    def _draw_map(self):
        # Başlık
        title_surf = self.font_big.render("AKILLI LOJİSTİK SİMÜLATÖRÜ", True, ACCENT_CYAN)
        self.screen.blit(title_surf, (MAP_OFFSET[0], 16))
        ver_surf = self.font_small.render("A* Rota Optimizasyonu  |  Akıllı Teslimat", True, TEXT_DIM)
        self.screen.blit(ver_surf, (MAP_OFFSET[0], 42))


        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = MAP_OFFSET[0] + c * CELL_SIZE
                y = MAP_OFFSET[1] + r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                if self.grid[r][c] == -1:
                    clr_pair = self.building_colors.get((r, c), (BUILD_DARK, BUILD_MID))
                    draw_gradient_rect(self.screen, rect, clr_pair[0], clr_pair[1])

                    for wy in range(4, CELL_SIZE - 4, 8):
                        for wx in range(4, CELL_SIZE - 4, 8):
                            if (r + c + wy + wx) % 5 != 0:
                                win_color = BUILD_WINDOW if random.random() > 0.4 else (30, 50, 90)
                                pygame.draw.rect(self.screen, win_color, (x + wx, y + wy, 4, 4))
                    pygame.draw.rect(self.screen, ROAD_LINE, rect, 1)
                else:
                    pygame.draw.rect(self.screen, ROAD_COLOR, rect)

                    pygame.draw.rect(self.screen, ROAD_LINE, rect, 1)


        for i, tp in enumerate(self.trail):
            alpha = int(255 * i / max(len(self.trail), 1))
            tx = MAP_OFFSET[0] + tp[1] * CELL_SIZE + CELL_SIZE // 2
            ty = MAP_OFFSET[1] + tp[0] * CELL_SIZE + CELL_SIZE // 2
            r_col = max(0, ACCENT_CYAN[0] - (255 - alpha)//2)
            g_col = max(0, ACCENT_CYAN[1] - (255 - alpha)//2)
            b_col = max(0, ACCENT_CYAN[2] - (255 - alpha)//2)
            pygame.draw.circle(self.screen, (r_col, g_col, b_col), (tx, ty), 3)


        if self.path:
            for i in range(len(self.path) - 1):
                p1 = self.path[i]; p2 = self.path[i+1]
                x1 = MAP_OFFSET[0] + p1[1]*CELL_SIZE + CELL_SIZE//2
                y1 = MAP_OFFSET[1] + p1[0]*CELL_SIZE + CELL_SIZE//2
                x2 = MAP_OFFSET[0] + p2[1]*CELL_SIZE + CELL_SIZE//2
                y2 = MAP_OFFSET[1] + p2[0]*CELL_SIZE + CELL_SIZE//2
                pygame.draw.line(self.screen, (0, 80, 120), (x1, y1), (x2, y2), 2)


        dx = MAP_OFFSET[0] + self.depot[1]*CELL_SIZE + CELL_SIZE//2
        dy = MAP_OFFSET[1] + self.depot[0]*CELL_SIZE + CELL_SIZE//2
        pulse = int(4 + 3 * math.sin(self.tick_count * 0.08))
        pygame.draw.circle(self.screen, ACCENT_GREEN, (dx, dy), pulse + 6, 2)
        pygame.draw.circle(self.screen, (20, 80, 40), (dx, dy), pulse + 4)
        dep_lbl = self.font_label.render("DEPO", True, ACCENT_GREEN)
        self.screen.blit(dep_lbl, (dx - dep_lbl.get_width()//2, dy - 22))


        for data in self.target_data:
            r, c = data["pos"]
            cx = MAP_OFFSET[0] + c*CELL_SIZE + CELL_SIZE//2
            cy = MAP_OFFSET[1] + r*CELL_SIZE + CELL_SIZE//2

            if not data["visited"]:

                pulse2 = int(3 * math.sin(self.tick_count * 0.07 + r + c))
                pygame.draw.circle(self.screen, data["color"], (cx, cy), 16 + pulse2, 2)
                pygame.draw.circle(self.screen, (data["color"][0]//4, data["color"][1]//4, data["color"][2]//4),
                                   (cx, cy), 14)
            else:
                pygame.draw.circle(self.screen, (50, 50, 50), (cx, cy), 14)

            draw_building_icon(self.screen, cx, cy, data["icon"], data["color"],
                               size=10, visited=data["visited"])

            name_color = TEXT_DIM if data["visited"] else data["color"]
            lbl = self.font_label.render(data["name"], True, name_color)
            self.screen.blit(lbl, (cx - lbl.get_width()//2, cy - 26))

            if data["visited"]:
                chk = self.font_label.render("✓", True, ACCENT_GREEN)
                self.screen.blit(chk, (cx + 12, cy - 6))

        mx = MAP_OFFSET[0] + self.pos[1]*CELL_SIZE + CELL_SIZE//2
        my = MAP_OFFSET[1] + self.pos[0]*CELL_SIZE + CELL_SIZE//2
        draw_motor_icon(self.screen, mx, my, size=12)


        map_rect = pygame.Rect(MAP_OFFSET[0] - 4, MAP_OFFSET[1] - 4,
                               GRID_SIZE*CELL_SIZE + 8, GRID_SIZE*CELL_SIZE + 8)
        pygame.draw.rect(self.screen, PANEL_BORDER, map_rect, 2, border_radius=4)


        map_bottom = MAP_OFFSET[1] + GRID_SIZE * CELL_SIZE + 10
        map_total_w = GRID_SIZE * CELL_SIZE
        btn_w = (map_total_w - 24) // 3
        btn_h = 44
        self.btn_start = pygame.Rect(MAP_OFFSET[0], map_bottom, btn_w, btn_h)
        self.btn_reset = pygame.Rect(MAP_OFFSET[0] + btn_w + 12, map_bottom, btn_w, btn_h)
        self.btn_graph = pygame.Rect(MAP_OFFSET[0] + (btn_w + 12) * 2, map_bottom, btn_w, btn_h)

        start_bg = (30, 70, 45) if not self.is_running else (70, 28, 28)
        start_br = ACCENT_GREEN if not self.is_running else ACCENT_RED
        start_txt = "▶  BAŞLAT" if not self.is_running else "⏸  DURDUR"
        draw_rounded_rect(self.screen, start_bg, self.btn_start, radius=8,
                          border=2, border_color=start_br)
        ss2 = self.font_bold.render(start_txt, True, TEXT_BRIGHT)
        self.screen.blit(ss2, (self.btn_start.x + self.btn_start.w//2 - ss2.get_width()//2,
                                self.btn_start.y + self.btn_start.h//2 - ss2.get_height()//2))
        hint1 = self.font_label.render("[S]", True, TEXT_DIM)
        self.screen.blit(hint1, (self.btn_start.right - 24, self.btn_start.y + 4))

        draw_rounded_rect(self.screen, (28, 38, 62), self.btn_reset, radius=8,
                          border=2, border_color=ACCENT_BLUE)
        rs2 = self.font_bold.render("↺  SIFIRLA", True, TEXT_BRIGHT)
        self.screen.blit(rs2, (self.btn_reset.x + self.btn_reset.w//2 - rs2.get_width()//2,
                                self.btn_reset.y + self.btn_reset.h//2 - rs2.get_height()//2))
        hint2 = self.font_label.render("[R]", True, TEXT_DIM)
        self.screen.blit(hint2, (self.btn_reset.right - 24, self.btn_reset.y + 4))

        graph_active = self.episode_done
        graph_bg  = (38, 28, 62) if graph_active else (28, 28, 38)
        graph_br  = ACCENT_PURPLE if graph_active else TEXT_DIM
        graph_txt_clr = TEXT_BRIGHT if graph_active else TEXT_DIM
        draw_rounded_rect(self.screen, graph_bg, self.btn_graph, radius=8,
                          border=2, border_color=graph_br)
        gs = self.font_bold.render("📊 GRAFİK", True, graph_txt_clr)
        self.screen.blit(gs, (self.btn_graph.x + self.btn_graph.w//2 - gs.get_width()//2,
                               self.btn_graph.y + self.btn_graph.h//2 - gs.get_height()//2))
        if not graph_active:
            lock = self.font_label.render("oyun bekleniyor", True, TEXT_DIM)
            self.screen.blit(lock, (self.btn_graph.x + self.btn_graph.w//2 - lock.get_width()//2,
                                    self.btn_graph.y + 4))

    def _draw_panel(self):
        px = PANEL_X

        panel_rect = pygame.Rect(px, 0, PANEL_W, HEIGHT)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, ACCENT_BLUE, (px, 0), (px, HEIGHT), 3)

        y = 18

        self._draw_section_header("KONTROL MERKEZİ", px + 20, y, PANEL_W - 40, ACCENT_BLUE)
        y += 38


        status_color = ACCENT_GREEN if self.is_running else ACCENT_ORANGE
        status_text = "● AKTİF" if self.is_running else "◼ BEKLEMEDE"
        status_rect = pygame.Rect(px + 15, y, PANEL_W - 30, 36)
        draw_rounded_rect(self.screen,
                          (0, 40, 20) if self.is_running else (40, 25, 0),
                          status_rect, radius=8,
                          border=2, border_color=status_color)
        st_surf = self.font_bold.render(status_text, True, status_color)
        self.screen.blit(st_surf, (px + PANEL_W//2 - st_surf.get_width()//2, y + 9))
        y += 50


        self._draw_section_header("MEVCUT HEDEF", px + 20, y, PANEL_W - 40, ACCENT_PURPLE)
        y += 30
        tgt_rect = pygame.Rect(px + 15, y, PANEL_W - 30, 52)
        draw_rounded_rect(self.screen, (18, 10, 35), tgt_rect, radius=8,
                          border=2, border_color=self.current_target_color)
        icon_cx = px + 36; icon_cy = y + 26
        draw_building_icon(self.screen, icon_cx, icon_cy,
                           self.current_target_icon, self.current_target_color, size=11)
        tgt_name = self.font_bold.render(self.current_target_name, True, TEXT_WHITE)
        self.screen.blit(tgt_name, (px + 55, y + 10))
        rem = sum(1 for t in self.target_data if not t["visited"])
        rem_surf = self.font_small.render(f"Kalan: {rem} teslimat", True, TEXT_DIM)
        self.screen.blit(rem_surf, (px + 55, y + 30))
        y += 66


        self._draw_section_header("PERFORMANS METRİKLERİ", px + 20, y, PANEL_W - 40, ACCENT_CYAN)
        y += 30

        metrics = [
            ("SÜRE", f"{self.elapsed_s}s", ACCENT_CYAN,   "clock"),
            ("MESAFE", f"{self.time} adım", ACCENT_BLUE,  "map"),
            ("ÖDÜL",  f"+{self.score}", ACCENT_GREEN,     "star"),
            ("CEZA",  f"-{int(self.penalties)}", ACCENT_RED, "warn"),
        ]
        card_w = (PANEL_W - 40) // 2
        card_h = 52
        for i, (label, value, color, _) in enumerate(metrics):
            col = i % 2; row = i // 2
            cx2 = px + 15 + col * (card_w + 8)
            cy2 = y + row * (card_h + 8)
            card_rect = pygame.Rect(cx2, cy2, card_w, card_h)
            draw_rounded_rect(self.screen, (12, 14, 30), card_rect, radius=7,
                              border=1, border_color=(40, 55, 100))
            lbl_s = self.font_label.render(label, True, TEXT_DIM)
            val_s = self.font_bold.render(value, True, color)
            self.screen.blit(lbl_s, (cx2 + 10, cy2 + 8))
            self.screen.blit(val_s, (cx2 + 10, cy2 + 25))

            pygame.draw.rect(self.screen, color, (cx2, cy2 + 12, 3, card_h - 24), border_radius=2)
        y += 2 * (card_h + 8) + 10


        net = int(self.score - self.penalties)
        net_color = ACCENT_GREEN if net >= 0 else ACCENT_RED
        net_rect = pygame.Rect(px + 15, y, PANEL_W - 30, 46)
        draw_gradient_rect(self.screen, net_rect,
                           (0, 30, 15) if net >= 0 else (30, 0, 0),
                           (5, 20, 10) if net >= 0 else (20, 0, 0))
        pygame.draw.rect(self.screen, net_color, net_rect, 2, border_radius=8)
        net_lbl = self.font_small.render("NET KÂR", True, TEXT_DIM)
        net_val = self.font_big.render(f"{'+'if net>=0 else ''}{net} puan", True, net_color)
        self.screen.blit(net_lbl, (px + PANEL_W//2 - net_lbl.get_width()//2, y + 5))
        self.screen.blit(net_val, (px + PANEL_W//2 - net_val.get_width()//2, y + 20))
        y += 60


        self._draw_section_header("TESLİMAT GEÇMİŞİ", px + 20, y, PANEL_W - 40, ACCENT_ORANGE)
        y += 30
        log_rect = pygame.Rect(px + 15, y, PANEL_W - 30, 110)
        draw_rounded_rect(self.screen, (10, 12, 26), log_rect, radius=6,
                          border=1, border_color=PANEL_BORDER)
        if not self.delivery_log:
            nd = self.font_small.render("Henüz teslimat yapılmadı", True, TEXT_DIM)
            self.screen.blit(nd, (px + 30, y + 14))
        for li, entry in enumerate(self.delivery_log[-4:]):
            ey = y + 8 + li * 24
            idx_s = self.font_label.render(f"#{li+1}", True, ACCENT_ORANGE)
            name_s = self.font_label.render(entry["name"][:16], True, TEXT_WHITE)
            bonus_s = self.font_label.render(f"+{entry['bonus']}p  @{entry['time']}s", True, ACCENT_GREEN)
            self.screen.blit(idx_s,  (px + 22, ey))
            self.screen.blit(name_s, (px + 48, ey))
            self.screen.blit(bonus_s,(px + 160, ey))
        y += 118


        self._draw_section_header("HIZ SEÇİCİ", px + 20, y, PANEL_W - 40, ACCENT_BLUE)
        y += 30
        speed_labels = ["YAVAŞ", "NORMAL", "HIZLI"]
        sw = (PANEL_W - 40) // 3
        for si, slbl in enumerate(speed_labels):
            sr = pygame.Rect(px + 15 + si*sw, y, sw - 6, 34)
            is_active = (si + 1) == self.speed_level
            bg_clr = ACCENT_BLUE if is_active else (18, 22, 45)
            brd_clr = ACCENT_CYAN if is_active else (40, 55, 100)
            draw_rounded_rect(self.screen, bg_clr, sr, radius=6, border=2, border_color=brd_clr)
            txt_clr = TEXT_BRIGHT if is_active else TEXT_DIM
            ss = self.font_small.render(slbl, True, txt_clr)
            self.screen.blit(ss, (sr.x + sr.w//2 - ss.get_width()//2, sr.y + 9))
        self.btn_speed = [
            pygame.Rect(px + 15 + si*(sw), y, sw - 6, 34) for si in range(3)
        ]
        y += 50


        self._draw_section_header("TESLİMAT LİSTESİ", px + 20, y, PANEL_W - 40, ACCENT_GREEN)
        y += 30
        for ti, t in enumerate(self.target_data):
            done = t["visited"]
            row_rect = pygame.Rect(px + 15, y + ti*26, PANEL_W - 30, 22)
            if not done:
                pygame.draw.rect(self.screen, (14, 18, 38), row_rect, border_radius=4)
            icon_x = px + 26; icon_y = y + ti*26 + 11
            draw_building_icon(self.screen, icon_x, icon_y, t["icon"], t["color"], size=7, visited=done)
            dot_c = ACCENT_GREEN if done else t["color"]
            name_c = TEXT_DIM if done else TEXT_WHITE
            ns = self.font_label.render(("✓ " if done else "• ") + t["name"], True, name_c)
            self.screen.blit(ns, (px + 38, y + ti*26 + 5))
            if done and t["visit_time"]:
                ts = self.font_label.render(f"@{t['visit_time']}s", True, TEXT_DIM)
                self.screen.blit(ts, (px + PANEL_W - 60, y + ti*26 + 5))
        y += len(self.target_data) * 26 + 10



    def _draw_graph_overlay(self):
        """Epizot sonu grafik ekranı — tüm ekranı kaplar, ESC veya tekrar tıkla kapatır."""
        ow, oh = 700, 500
        ox = (WIDTH - ow) // 2
        oy = (HEIGHT - oh) // 2


        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))


        draw_rounded_rect(self.screen, PANEL_BG, pygame.Rect(ox, oy, ow, oh),
                          radius=14, border=2, border_color=ACCENT_PURPLE)


        title = self.font_big.render("OYUN SONUÇ GRAFİĞİ", True, ACCENT_PURPLE)
        self.screen.blit(title, (ox + ow//2 - title.get_width()//2, oy + 16))
        pygame.draw.line(self.screen, ACCENT_PURPLE, (ox + 20, oy + 46), (ox + ow - 20, oy + 46), 1)

        if not self.delivery_log:
            nd = self.font_bold.render("Henüz tamamlanan teslimat yok.", True, TEXT_DIM)
            self.screen.blit(nd, (ox + ow//2 - nd.get_width()//2, oy + oh//2))
            close = self.font_label.render("Kapatmak için ESC veya tekrar GRAFİK butonuna bas", True, TEXT_DIM)
            self.screen.blit(close, (ox + ow//2 - close.get_width()//2, oy + oh - 30))
            return

        chart_x = ox + 50
        chart_y = oy + 60
        chart_w = ow - 100
        chart_h = 200
        logs = self.delivery_log

        max_bonus = max(e["bonus"] for e in logs) if logs else 1
        bar_count = len(logs)
        bar_w = min(60, (chart_w - (bar_count - 1) * 10) // bar_count)
        total_bar_area = bar_count * bar_w + (bar_count - 1) * 10
        bar_start_x = chart_x + (chart_w - total_bar_area) // 2


        pygame.draw.line(self.screen, PANEL_BORDER, (chart_x, chart_y),
                         (chart_x, chart_y + chart_h), 2)
        pygame.draw.line(self.screen, PANEL_BORDER, (chart_x, chart_y + chart_h),
                         (chart_x + chart_w, chart_y + chart_h), 2)


        for yi in range(0, 5):
            val = int(max_bonus * yi / 4)
            ypos = chart_y + chart_h - int(chart_h * yi / 4)
            pygame.draw.line(self.screen, (45, 55, 70), (chart_x, ypos),
                             (chart_x + chart_w, ypos), 1)
            lbl = self.font_label.render(str(val), True, TEXT_DIM)
            self.screen.blit(lbl, (chart_x - lbl.get_width() - 6, ypos - 6))

        bar_colors = [ACCENT_GREEN, ACCENT_CYAN, ACCENT_BLUE, ACCENT_ORANGE,
                      ACCENT_PURPLE, ACCENT_RED]
        for i, entry in enumerate(logs):
            bx = bar_start_x + i * (bar_w + 10)
            bh = int(chart_h * entry["bonus"] / max_bonus)
            by = chart_y + chart_h - bh
            color = bar_colors[i % len(bar_colors)]


            for bi in range(bh):
                t = bi / max(bh, 1)
                rc = int(color[0] * (1 - t * 0.5))
                gc = int(color[1] * (1 - t * 0.5))
                bc = int(color[2] * (1 - t * 0.5))
                pygame.draw.line(self.screen, (rc, gc, bc),
                                 (bx, by + bi), (bx + bar_w, by + bi))
            pygame.draw.rect(self.screen, color, (bx, by, bar_w, bh), 1, border_radius=3)


            val_s = self.font_label.render(f"+{entry['bonus']}", True, color)
            self.screen.blit(val_s, (bx + bar_w//2 - val_s.get_width()//2, by - 16))


            short_name = entry["name"][:9]
            name_s = self.font_label.render(short_name, True, TEXT_DIM)
            self.screen.blit(name_s, (bx + bar_w//2 - name_s.get_width()//2,
                                      chart_y + chart_h + 6))


            time_s = self.font_label.render(f"@{entry['time']}s", True, TEXT_DIM)
            self.screen.blit(time_s, (bx + bar_w//2 - time_s.get_width()//2,
                                      chart_y + chart_h + 20))


        sy = oy + 290
        pygame.draw.line(self.screen, PANEL_BORDER, (ox + 20, sy), (ox + ow - 20, sy), 1)
        sy += 12

        net = int(self.score - self.penalties)
        net_clr = ACCENT_GREEN if net >= 0 else ACCENT_RED
        summary_items = [
            (f"Toplam Teslimat: {len(logs)}", TEXT_WHITE),
            (f"Toplam Süre: {self.elapsed_s}s", ACCENT_CYAN),
            (f"Toplam Mesafe: {self.time} adım", ACCENT_BLUE),
            (f"Toplam Ödül: +{self.score}", ACCENT_GREEN),
            (f"Toplam Ceza: -{int(self.penalties)}", ACCENT_RED),
            (f"NET KÂR: {'+' if net>=0 else ''}{net}", net_clr),
        ]
        col_w = (ow - 40) // 2
        for i, (txt, clr) in enumerate(summary_items):
            col = i % 2; row = i // 2
            sx = ox + 30 + col * col_w
            sy2 = sy + row * 26
            draw_rounded_rect(self.screen, (18, 22, 38),
                              pygame.Rect(sx - 6, sy2 - 2, col_w - 8, 22), radius=4)
            s = self.font_small.render(txt, True, clr)
            self.screen.blit(s, (sx, sy2))


        tl_y = oy + 390
        pygame.draw.line(self.screen, PANEL_BORDER, (ox + 20, tl_y), (ox + ow - 20, tl_y), 1)
        tl_label = self.font_label.render("ZAMAN ÇİZGİSİ (kümülatif ödül)", True, TEXT_DIM)
        self.screen.blit(tl_label, (ox + 20, tl_y + 4))
        if len(logs) >= 2:
            cumulative = []
            running_total = 0
            for e in logs:
                running_total += e["bonus"]
                cumulative.append((e["time"], running_total))
            max_t = max(c[0] for c in cumulative)
            max_v = max(c[1] for c in cumulative)
            spx = ox + 20; spy = tl_y + 22
            spw = ow - 40; sph = 50
            pts = []
            for t, v in cumulative:
                px2 = spx + int(spw * t / max(max_t, 1))
                py2 = spy + sph - int(sph * v / max(max_v, 1))
                pts.append((px2, py2))
            if len(pts) >= 2:
                pygame.draw.lines(self.screen, ACCENT_CYAN, False, pts, 2)
            for pt in pts:
                pygame.draw.circle(self.screen, ACCENT_CYAN, pt, 4)
                pygame.draw.circle(self.screen, PANEL_BG, pt, 2)

        close = self.font_label.render("Kapatmak için ESC veya tekrar GRAFİK butonuna bas", True, TEXT_DIM)
        self.screen.blit(close, (ox + ow//2 - close.get_width()//2, oy + oh - 22))

    def _draw_section_header(self, text, x, y, w, color):
        surf = self.font_label.render(text, True, color)
        self.screen.blit(surf, (x, y))
        lx = x + surf.get_width() + 8
        pygame.draw.line(self.screen, color, (lx, y + 6), (x + w, y + 6), 1)


    def run(self):
        running = True
        move_timer = 0
        speed_map = {1: 280, 2: 140, 3: 55}
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.is_running = not self.is_running
                    if event.key == pygame.K_r:
                        self.reset_env()
                    if event.key == pygame.K_ESCAPE:
                        self.show_graph = False
                    if event.key == pygame.K_1: self.speed_level = 1
                    if event.key == pygame.K_2: self.speed_level = 2
                    if event.key == pygame.K_3: self.speed_level = 3
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.show_graph:
                        self.show_graph = False
                    elif self.btn_start.collidepoint(event.pos):
                        self.is_running = not self.is_running
                    elif self.btn_reset.collidepoint(event.pos):
                        self.reset_env()
                    elif self.btn_graph.collidepoint(event.pos) and self.episode_done:
                        self.show_graph = True
                    else:
                        for si, sr in enumerate(self.btn_speed):
                            if sr.collidepoint(event.pos):
                                self.speed_level = si + 1

            if self.is_running:
                move_timer += dt
                delay = speed_map.get(self.speed_level, 140)
                if move_timer > delay:
                    self.update_logic()
                    move_timer = 0
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    CyberDelivery().run()
