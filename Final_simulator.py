import pygame
import random
import heapq
import numpy as np
import math

WIDTH, HEIGHT = 1250, 1000
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
ACCENT_YELLOW = (225, 200, 90)
TEXT_WHITE    = (215, 225, 235)
TEXT_DIM      = (140, 158, 178)
TEXT_BRIGHT   = (240, 246, 252)
GOLD          = (220, 185, 90)
TRAFFIC_COLOR = (90, 60, 30)


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

# --- Araç tipleri: hız çarpanı (yüksek = daha hızlı hareket) ve batarya tüketim çarpanı ---
VEHICLES = {
    "motor":    {"name": "Motosiklet", "speed_mult": 1.0, "drain": 1.0, "color": ACCENT_ORANGE},
    "bisiklet": {"name": "Bisiklet",   "speed_mult": 0.65, "drain": 0.5, "color": ACCENT_GREEN},
    "araba":    {"name": "Araba",      "speed_mult": 1.6, "drain": 1.8, "color": ACCENT_BLUE},
}
VEHICLE_KEYS = list(VEHICLES.keys())

BATTERY_OPTIONS = [60, 100, 160]
AGENT_COLORS = [ACCENT_ORANGE, ACCENT_CYAN, ACCENT_PURPLE]
RL_ACTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


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


def draw_motor_icon(surf, cx, cy, size=14, heading_right=True, body_color=None, wheel_color=GOLD):
    """Motosiklet/araç görünümünde kurye ikonu. body_color verilirse araca göre renklenir."""
    s = size
    if body_color is None:
        body_color = ACCENT_ORANGE

    body_pts = [
        (cx - s, cy),
        (cx - s//2, cy - s//2),
        (cx + s//3, cy - s//2),
        (cx + s, cy - s//6),
        (cx + s, cy + s//4),
        (cx - s, cy + s//4),
    ]
    pygame.draw.polygon(surf, body_color, body_pts)
    pygame.draw.polygon(surf, wheel_color, body_pts, 1)

    pygame.draw.circle(surf, (60, 60, 80), (cx + s - 2, cy + s//2), s//3 + 1)
    pygame.draw.circle(surf, body_color, (cx + s - 2, cy + s//2), s//3)
    pygame.draw.circle(surf, wheel_color, (cx + s - 2, cy + s//2), s//3, 1)
    # Arka tekerlek
    pygame.draw.circle(surf, (60, 60, 80), (cx - s + 2, cy + s//2), s//3 + 1)
    pygame.draw.circle(surf, body_color, (cx - s + 2, cy + s//2), s//3)
    pygame.draw.circle(surf, wheel_color, (cx - s + 2, cy + s//2), s//3, 1)

    pygame.draw.circle(surf, ACCENT_CYAN, (cx, cy - s//2 - 3), s//3)

    pygame.draw.circle(surf, (255, 255, 180), (cx + s, cy - s//8), 3)


def draw_charge_icon(surf, cx, cy, size=12, pulse=0):
    """Şarj istasyonu ikonu (yıldırım)."""
    s = size
    pygame.draw.circle(surf, (30, 60, 30), (cx, cy), s + 4 + pulse, 2)
    pygame.draw.circle(surf, (15, 35, 15), (cx, cy), s + 2)
    pts = [
        (cx + 2, cy - s), (cx - 4, cy + 1), (cx, cy + 1),
        (cx - 2, cy + s), (cx + 4, cy - 1), (cx, cy - 1),
    ]
    pygame.draw.polygon(surf, ACCENT_YELLOW, pts)
    pygame.draw.polygon(surf, (255, 255, 255), pts, 1)


def draw_flag_icon(surf, cx, cy, color, size=11, visited=False):
    """Bitiş noktası bayrağı."""
    s = size
    clr = color if not visited else (90, 90, 90)
    pygame.draw.line(surf, (200, 200, 200) if not visited else (110, 110, 110),
                      (cx - s//2, cy + s), (cx - s//2, cy - s), 3)
    pts = [(cx - s//2, cy - s), (cx + s, cy - s//2), (cx - s//2, cy)]
    pygame.draw.polygon(surf, clr, pts)
    pygame.draw.polygon(surf, (255, 255, 255) if not visited else (140, 140, 140), pts, 1)


def draw_building_icon(surf, cx, cy, icon_type, color, size=11, visited=False):
    """Her lokasyon tipi için ayrı vektör ikon."""
    s = size

    if icon_type == "flag":
        draw_flag_icon(surf, cx, cy, color, size=size, visited=visited)
        return
    if icon_type == "charge":
        draw_charge_icon(surf, cx, cy, size=size)
        return

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
        self.btn_speed = []
        self.delivery_log = []
        self.speed_level = 2
        self.episode_done = False
        self.show_graph = False

        self.depot = (0, 0)
        self.end_point = None
        self.click_mode = None

        self.vehicle_key = "motor"
        self.battery_idx = 1

        self.mode_rl = False
        self.q_table = {}
        self.episode_count = 0

        self.num_agents = 1

        self.btn_vehicle = pygame.Rect(0, 0, 0, 0)
        self.btn_battery = pygame.Rect(0, 0, 0, 0)
        self.btn_mode = pygame.Rect(0, 0, 0, 0)
        self.btn_agents = pygame.Rect(0, 0, 0, 0)
        self.btn_set_depot = pygame.Rect(0, 0, 0, 0)
        self.btn_set_end = pygame.Rect(0, 0, 0, 0)

        self.reset_env()

    def reset_env(self):
        self.grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.building_colors = {}
        self._gen_buildings()

        self.grid[self.depot[0]][self.depot[1]] = 0
        if self.end_point is not None:
            self.grid[self.end_point[0]][self.end_point[1]] = 0

        occupied = {self.depot}
        if self.end_point is not None:
            occupied.add(tuple(self.end_point))

        chosen = random.sample(LOCATION_DEFS, min(self.num_targets, len(LOCATION_DEFS)))
        self.target_data = []
        while len(self.target_data) < self.num_targets:
            pos = (random.randint(1, 19), random.randint(1, 19))
            if self.grid[pos[0]][pos[1]] == 0 and pos not in occupied:
                if not any(t["pos"] == pos for t in self.target_data):
                    defn = chosen[len(self.target_data) % len(chosen)]
                    self.target_data.append({
                        "pos": pos, "name": defn[0],
                        "icon": defn[1], "color": defn[2],
                        "visited": False, "visit_time": None,
                        "claimed_by": None
                    })
                    occupied.add(pos)

        self.charge_stations = []
        attempts = 0
        while len(self.charge_stations) < 3 and attempts < 400:
            attempts += 1
            pos = (random.randint(0, 19), random.randint(0, 19))
            if self.grid[pos[0]][pos[1]] == 0 and pos not in occupied and pos not in self.charge_stations:
                self.charge_stations.append(pos)

        self.traffic = {}
        attempts = 0
        while len(self.traffic) < 16 and attempts < 400:
            attempts += 1
            pos = (random.randint(0, 19), random.randint(0, 19))
            if (self.grid[pos[0]][pos[1]] == 0 and pos not in occupied
                    and pos not in self.charge_stations and pos not in self.traffic):
                self.traffic[pos] = random.choice([2.0, 2.5, 3.0])

        self.agents = []
        veh = VEHICLES[self.vehicle_key]
        cap = BATTERY_OPTIONS[self.battery_idx]
        for i in range(self.num_agents):
            self.agents.append({
                "id": i,
                "pos": list(self.depot),
                "path": [],
                "trail": [],
                "heading": (0, 1),
                "battery": float(cap),
                "battery_capacity": float(cap),
                "vehicle_key": self.vehicle_key,
                "color": AGENT_COLORS[i % len(AGENT_COLORS)],
                "status": "idle",
                "target": None,
            })

        self.time = 0
        self.elapsed_s = 0
        self.score = 0
        self.penalties = 0
        self.is_running = False
        self.delivery_log = []
        self.episode_done = False
        self.show_graph = False
        self.click_mode = None
        self.episode_count += 1

        for agent in self.agents:
            self._plan_agent_target(agent)
        self._refresh_status_label()

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

    def _is_walkable(self, p):
        return 0 <= p[0] < GRID_SIZE and 0 <= p[1] < GRID_SIZE and self.grid[p[0]][p[1]] != -1

    def _plan_agent_target(self, agent):
        unvisited = [t for t in self.target_data
                     if not t["visited"] and t["claimed_by"] in (None, agent["id"])]
        if unvisited:
            cp = np.array(agent["pos"])
            best = min(unvisited, key=lambda t: np.linalg.norm(cp - np.array(t["pos"])))
            best["claimed_by"] = agent["id"]
            agent["target"] = best
            agent["status"] = "moving"
            if not self.mode_rl:
                agent["path"] = self.a_star(tuple(agent["pos"]), best["pos"])
            else:
                agent["path"] = []
        elif self.end_point is not None and tuple(agent["pos"]) != tuple(self.end_point):
            agent["target"] = {"pos": tuple(self.end_point), "name": "Bitiş Noktası",
                                "icon": "flag", "is_end": True}
            agent["status"] = "to_end"
            if not self.mode_rl:
                agent["path"] = self.a_star(tuple(agent["pos"]), tuple(self.end_point))
            else:
                agent["path"] = []
        else:
            agent["target"] = None
            agent["path"] = []
            agent["status"] = "done"

    def _refresh_status_label(self):
        active = [a for a in self.agents if a["target"]]
        if active:
            t = active[0]["target"]
            self.current_target_name = t["name"]
            self.current_target_icon = t["icon"]
            self.current_target_color = t.get("color", ACCENT_GREEN if t.get("is_end") else ACCENT_BLUE)
        else:
            self.current_target_name = "Tüm Teslimatlar Bitti!"
            self.current_target_icon = "flag"
            self.current_target_color = ACCENT_GREEN

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
            for dx, dy in RL_ACTIONS:
                nb = (current[0]+dx, current[1]+dy)
                if self._is_walkable(nb):
                    cost = self.traffic.get(nb, 1.0)
                    tg = g_score[current] + cost
                    if tg < g_score.get(nb, 9999):
                        came_from[nb] = current; g_score[nb] = tg
                        f = tg + abs(nb[0]-goal[0]) + abs(nb[1]-goal[1])
                        heapq.heappush(queue, (f, nb))
        return []

    def _rl_step(self, agent):
        tgt = agent["target"]
        if not tgt:
            return None
        target_pos = tuple(tgt["pos"])
        pos = tuple(agent["pos"])
        if pos == target_pos:
            return None
        valid = [a for a in RL_ACTIONS if self._is_walkable((pos[0]+a[0], pos[1]+a[1]))]
        if not valid:
            return None
        epsilon = max(0.05, 0.6 - self.episode_count * 0.03)
        if random.random() < epsilon:
            action = random.choice(valid)
        else:
            qvals = [(self.q_table.get((pos, target_pos, a), 0.0), a) for a in valid]
            action = max(qvals, key=lambda x: x[0])[1]
        nxt = (pos[0] + action[0], pos[1] + action[1])
        old_dist = abs(pos[0]-target_pos[0]) + abs(pos[1]-target_pos[1])
        new_dist = abs(nxt[0]-target_pos[0]) + abs(nxt[1]-target_pos[1])
        traffic_pen = (self.traffic.get(nxt, 1.0) - 1.0) * 2.0
        reward = 10.0 if nxt == target_pos else (0.3 if new_dist < old_dist else -0.6) - traffic_pen
        old_q = self.q_table.get((pos, target_pos, action), 0.0)
        future_qs = [self.q_table.get((nxt, target_pos, a2), 0.0) for a2 in RL_ACTIONS]
        max_future = max(future_qs) if future_qs else 0.0
        new_q = old_q + 0.3 * (reward + 0.9 * max_future - old_q)
        self.q_table[(pos, target_pos, action)] = new_q
        return nxt

    def update_logic(self):
        if not self.is_running:
            return
        veh = VEHICLES[self.vehicle_key]
        active_count = 0

        for agent in self.agents:
            if agent["status"] == "done":
                continue
            if agent["battery"] <= 0:
                if agent["status"] != "stranded" and agent["target"] and not agent["target"].get("is_end"):
                    agent["target"]["claimed_by"] = None
                agent["status"] = "stranded"
                continue

            if agent["target"] is None:
                self._plan_agent_target(agent)
                if agent["target"] is None:
                    continue

            if self.mode_rl:
                nxt = self._rl_step(agent)
                if nxt is None:
                    continue
            else:
                if not agent["path"]:
                    self._plan_agent_target(agent)
                    if not agent["path"]:
                        continue
                nxt = tuple(agent["path"].pop(0))

            active_count += 1
            prev = tuple(agent["pos"])
            agent["heading"] = (nxt[0]-prev[0], nxt[1]-prev[1])
            agent["pos"] = list(nxt)

            traffic_mult = self.traffic.get(nxt, 1.0)
            drain = veh["drain"] * traffic_mult
            agent["battery"] = max(0.0, agent["battery"] - drain)

            self.time += 1
            self.elapsed_s += 1
            pen = {1: 0.4, 2: 0.8, 3: 1.4}.get(self.speed_level, 0.8) * traffic_mult
            self.penalties += pen

            agent["trail"].append(tuple(agent["pos"]))
            if len(agent["trail"]) > 30:
                agent["trail"].pop(0)

            if tuple(agent["pos"]) in self.charge_stations:
                agent["battery"] = min(agent["battery_capacity"], agent["battery"] + 9)

            tgt = agent["target"]
            if tgt and tuple(agent["pos"]) == tuple(tgt["pos"]):
                if tgt.get("is_end"):
                    agent["status"] = "done"
                    agent["target"] = None
                else:
                    for t in self.target_data:
                        if t is tgt and not t["visited"]:
                            t["visited"] = True
                            t["visit_time"] = self.elapsed_s
                            bonus = max(50, 300 - self.elapsed_s * 2)
                            self.score += bonus
                            self.delivery_log.append({
                                "name": t["name"], "time": self.elapsed_s,
                                "bonus": bonus, "agent": agent["id"]
                            })
                    self._plan_agent_target(agent)

        self._refresh_status_label()

        all_targets_done = all(t["visited"] for t in self.target_data)
        all_agents_finished = all(a["status"] in ("done", "stranded") for a in self.agents)
        end_reached = (self.end_point is None) or all(
            tuple(a["pos"]) == tuple(self.end_point) or a["status"] == "stranded"
            for a in self.agents
        )
        if all_agents_finished and all_targets_done and end_reached:
            self.is_running = False
            self.episode_done = True

    def draw(self):
        self.tick_count += 1
        self.screen.fill(BG_COLOR)

        self._draw_map()
        self._draw_panel()
        if self.show_graph:
            self._draw_graph_overlay()
        pygame.display.flip()

    def _draw_map(self):
        title_surf = self.font_big.render("AKILLI LOJİSTİK SİMÜLATÖRÜ", True, ACCENT_CYAN)
        self.screen.blit(title_surf, (MAP_OFFSET[0], 16))
        ver_surf = self.font_small.render("A* / RL Rota Optimizasyonu  |  Akıllı Teslimat", True, TEXT_DIM)
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
                    if (r, c) in self.traffic:
                        overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        overlay.fill((*TRAFFIC_COLOR, 110))
                        self.screen.blit(overlay, (x, y))
                        for hy in range(0, CELL_SIZE, 6):
                            pygame.draw.line(self.screen, ACCENT_ORANGE,
                                              (x, y + hy), (x + 6, y + hy - 6), 1)
                    pygame.draw.rect(self.screen, ROAD_LINE, rect, 1)

        if self.click_mode:
            hint_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.grid[r][c] == 0:
                        x = MAP_OFFSET[0] + c * CELL_SIZE
                        y = MAP_OFFSET[1] + r * CELL_SIZE
                        ov = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        ov.fill((90, 200, 255, 28))
                        self.screen.blit(ov, (x, y))

        for (cr, cc) in self.charge_stations:
            cx = MAP_OFFSET[0] + cc*CELL_SIZE + CELL_SIZE//2
            cy = MAP_OFFSET[1] + cr*CELL_SIZE + CELL_SIZE//2
            pulse = int(2 * math.sin(self.tick_count * 0.1))
            draw_charge_icon(self.screen, cx, cy, size=10, pulse=pulse)

        for agent in self.agents:
            for i, tp in enumerate(agent["trail"]):
                alpha = int(255 * i / max(len(agent["trail"]), 1))
                tx = MAP_OFFSET[0] + tp[1] * CELL_SIZE + CELL_SIZE // 2
                ty = MAP_OFFSET[1] + tp[0] * CELL_SIZE + CELL_SIZE // 2
                base = agent["color"]
                r_col = max(0, base[0] - (255 - alpha)//2)
                g_col = max(0, base[1] - (255 - alpha)//2)
                b_col = max(0, base[2] - (255 - alpha)//2)
                pygame.draw.circle(self.screen, (r_col, g_col, b_col), (tx, ty), 3)

            if agent["path"]:
                full_path = [tuple(agent["pos"])] + agent["path"]
                for i in range(len(full_path) - 1):
                    p1 = full_path[i]; p2 = full_path[i+1]
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


        if self.end_point is not None:
            ex = MAP_OFFSET[0] + self.end_point[1]*CELL_SIZE + CELL_SIZE//2
            ey = MAP_OFFSET[1] + self.end_point[0]*CELL_SIZE + CELL_SIZE//2
            all_done = all(t["visited"] for t in self.target_data)
            draw_flag_icon(self.screen, ex, ey, ACCENT_PURPLE, size=12, visited=False)
            end_lbl = self.font_label.render("BİTİŞ", True, ACCENT_PURPLE)
            self.screen.blit(end_lbl, (ex - end_lbl.get_width()//2, ey - 28))

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

        for agent in self.agents:
            mx = MAP_OFFSET[0] + agent["pos"][1]*CELL_SIZE + CELL_SIZE//2
            my = MAP_OFFSET[1] + agent["pos"][0]*CELL_SIZE + CELL_SIZE//2
            draw_motor_icon(self.screen, mx, my, size=12, body_color=agent["color"])

            pct = agent["battery"] / max(agent["battery_capacity"], 1)
            bar_w = 22
            bx = mx - bar_w // 2
            by = my - 22
            pygame.draw.rect(self.screen, (20, 20, 25), (bx, by, bar_w, 4), border_radius=2)
            bcol = ACCENT_GREEN if pct > 0.5 else (ACCENT_ORANGE if pct > 0.2 else ACCENT_RED)
            pygame.draw.rect(self.screen, bcol, (bx, by, max(2, int(bar_w*pct)), 4), border_radius=2)
            if agent["status"] == "stranded":
                sl = self.font_label.render("PİL BİTTİ", True, ACCENT_RED)
                self.screen.blit(sl, (mx - sl.get_width()//2, my + 14))

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

        legend_y = map_bottom + btn_h + 18
        if self.click_mode == "set_depot":
            hint = "Yeni DEPO konumu için yol üzerinde bir hücreye tıklayın (ESC: vazgeç)"
            hs = self.font_small.render(hint, True, ACCENT_GREEN)
            self.screen.blit(hs, (MAP_OFFSET[0], legend_y))
            legend_y += 22
        elif self.click_mode == "set_end":
            hint = "Yeni BİTİŞ konumu için yol üzerinde bir hücreye tıklayın (ESC: vazgeç)"
            hs = self.font_small.render(hint, True, ACCENT_PURPLE)
            self.screen.blit(hs, (MAP_OFFSET[0], legend_y))
            legend_y += 22

        legend_items = [
            ("⚡", "Şarj İstasyonu", ACCENT_YELLOW),
            ("🚧", "Trafik (yavaş/pahalı)", ACCENT_ORANGE),
            ("🏁", "Bitiş Noktası", ACCENT_PURPLE),
            ("🔋", "Batarya Durumu", ACCENT_GREEN),
        ]
        for i, (sym, txt, clr) in enumerate(legend_items):
            ly = legend_y + i * 20
            ls = self.font_small.render(f"{sym}  {txt}", True, clr)
            self.screen.blit(ls, (MAP_OFFSET[0], ly))

        mode_lbl = self.font_main.render(
            f"MOD: {'RL (öğrenen kurye)' if self.mode_rl else 'A* (optimal rota)'}",
            True, ACCENT_CYAN if not self.mode_rl else ACCENT_PURPLE)
        self.screen.blit(mode_lbl, (MAP_OFFSET[0], legend_y + len(legend_items)*20 + 8))

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
        y += 28

        metrics = [
            ("SÜRE", f"{self.elapsed_s}s", ACCENT_CYAN,   "clock"),
            ("MESAFE", f"{self.time} adım", ACCENT_BLUE,  "map"),
            ("ÖDÜL",  f"+{self.score}", ACCENT_GREEN,     "star"),
            ("CEZA",  f"-{int(self.penalties)}", ACCENT_RED, "warn"),
        ]
        card_w = (PANEL_W - 40) // 2
        card_h = 46
        for i, (label, value, color, _) in enumerate(metrics):
            col = i % 2; row = i // 2
            cx2 = px + 15 + col * (card_w + 8)
            cy2 = y + row * (card_h + 6)
            card_rect = pygame.Rect(cx2, cy2, card_w, card_h)
            draw_rounded_rect(self.screen, (12, 14, 30), card_rect, radius=7,
                              border=1, border_color=(40, 55, 100))
            lbl_s = self.font_label.render(label, True, TEXT_DIM)
            val_s = self.font_bold.render(value, True, color)
            self.screen.blit(lbl_s, (cx2 + 10, cy2 + 6))
            self.screen.blit(val_s, (cx2 + 10, cy2 + 22))
            pygame.draw.rect(self.screen, color, (cx2, cy2 + 10, 3, card_h - 20), border_radius=2)
        y += 2 * (card_h + 6) + 8

        net = int(self.score - self.penalties)
        net_color = ACCENT_GREEN if net >= 0 else ACCENT_RED
        net_rect = pygame.Rect(px + 15, y, PANEL_W - 30, 40)
        draw_gradient_rect(self.screen, net_rect,
                           (0, 30, 15) if net >= 0 else (30, 0, 0),
                           (5, 20, 10) if net >= 0 else (20, 0, 0))
        pygame.draw.rect(self.screen, net_color, net_rect, 2, border_radius=8)
        net_lbl = self.font_small.render("NET KÂR", True, TEXT_DIM)
        net_val = self.font_bold.render(f"{'+'if net>=0 else ''}{net} puan", True, net_color)
        self.screen.blit(net_lbl, (px + PANEL_W//2 - net_lbl.get_width()//2, y + 3))
        self.screen.blit(net_val, (px + PANEL_W//2 - net_val.get_width()//2, y + 17))
        y += 50

        # --- Ajan / batarya / araç durumu ---
        self._draw_section_header("AJAN & PİL DURUMU", px + 20, y, PANEL_W - 40, ACCENT_GREEN)
        y += 26
        for agent in self.agents:
            row_rect = pygame.Rect(px + 15, y, PANEL_W - 30, 24)
            draw_rounded_rect(self.screen, (12, 16, 28), row_rect, radius=5,
                              border=1, border_color=PANEL_BORDER)
            veh_name = VEHICLES[agent["vehicle_key"]]["name"]
            lbl = self.font_label.render(f"Ajan {agent['id']+1} ({veh_name})", True, TEXT_WHITE)
            self.screen.blit(lbl, (px + 22, y + 5))
            pct = agent["battery"] / max(agent["battery_capacity"], 1)
            bar_x = px + PANEL_W - 30 - 80
            bar_w = 70
            pygame.draw.rect(self.screen, (20, 20, 25), (bar_x, y + 7, bar_w, 10), border_radius=3)
            bcol = ACCENT_GREEN if pct > 0.5 else (ACCENT_ORANGE if pct > 0.2 else ACCENT_RED)
            pygame.draw.rect(self.screen, bcol, (bar_x, y + 7, max(2, int(bar_w*pct)), 10), border_radius=3)
            status_clr = {"moving": ACCENT_CYAN, "to_end": ACCENT_PURPLE,
                          "done": ACCENT_GREEN, "stranded": ACCENT_RED,
                          "idle": TEXT_DIM}.get(agent["status"], TEXT_DIM)
            pygame.draw.circle(self.screen, status_clr, (px + 18, y + 12), 3)
            y += 28
        y += 6

        self._draw_section_header("TESLİMAT GEÇMİŞİ", px + 20, y, PANEL_W - 40, ACCENT_ORANGE)
        y += 26
        log_rect = pygame.Rect(px + 15, y, PANEL_W - 30, 78)
        draw_rounded_rect(self.screen, (10, 12, 26), log_rect, radius=6,
                          border=1, border_color=PANEL_BORDER)
        if not self.delivery_log:
            nd = self.font_small.render("Henüz teslimat yapılmadı", True, TEXT_DIM)
            self.screen.blit(nd, (px + 30, y + 14))
        for li, entry in enumerate(self.delivery_log[-3:]):
            ey = y + 8 + li * 22
            idx_s = self.font_label.render(f"#{li+1}", True, ACCENT_ORANGE)
            name_s = self.font_label.render(entry["name"][:14], True, TEXT_WHITE)
            bonus_s = self.font_label.render(f"+{entry['bonus']}p @{entry['time']}s", True, ACCENT_GREEN)
            self.screen.blit(idx_s,  (px + 22, ey))
            self.screen.blit(name_s, (px + 48, ey))
            self.screen.blit(bonus_s,(px + 170, ey))
        y += 86

        self._draw_section_header("HIZ SEÇİCİ", px + 20, y, PANEL_W - 40, ACCENT_BLUE)
        y += 28
        speed_labels = ["YAVAŞ", "NORMAL", "HIZLI"]
        sw = (PANEL_W - 40) // 3
        for si, slbl in enumerate(speed_labels):
            sr = pygame.Rect(px + 15 + si*sw, y, sw - 6, 30)
            is_active = (si + 1) == self.speed_level
            bg_clr = ACCENT_BLUE if is_active else (18, 22, 45)
            brd_clr = ACCENT_CYAN if is_active else (40, 55, 100)
            draw_rounded_rect(self.screen, bg_clr, sr, radius=6, border=2, border_color=brd_clr)
            txt_clr = TEXT_BRIGHT if is_active else TEXT_DIM
            ss = self.font_small.render(slbl, True, txt_clr)
            self.screen.blit(ss, (sr.x + sr.w//2 - ss.get_width()//2, sr.y + 7))
        self.btn_speed = [
            pygame.Rect(px + 15 + si*(sw), y, sw - 6, 30) for si in range(3)
        ]
        y += 44

        self._draw_section_header("TESLİMAT LİSTESİ", px + 20, y, PANEL_W - 40, ACCENT_GREEN)
        y += 26
        for ti, t in enumerate(self.target_data):
            done = t["visited"]
            row_rect = pygame.Rect(px + 15, y + ti*22, PANEL_W - 30, 20)
            if not done:
                pygame.draw.rect(self.screen, (14, 18, 38), row_rect, border_radius=4)
            icon_x = px + 26; icon_y = y + ti*22 + 10
            draw_building_icon(self.screen, icon_x, icon_y, t["icon"], t["color"], size=7, visited=done)
            name_c = TEXT_DIM if done else TEXT_WHITE
            ns = self.font_label.render(("✓ " if done else "• ") + t["name"], True, name_c)
            self.screen.blit(ns, (px + 38, y + ti*22 + 4))
            if done and t["visit_time"]:
                ts = self.font_label.render(f"@{t['visit_time']}s", True, TEXT_DIM)
                self.screen.blit(ts, (px + PANEL_W - 60, y + ti*22 + 4))
        y += len(self.target_data) * 22 + 14


        self._draw_section_header("GELİŞMİŞ AYARLAR", px + 20, y, PANEL_W - 40, ACCENT_PURPLE)
        y += 28
        bw = (PANEL_W - 40 - 16) // 3
        bh = 34
        gap = 8

        self.btn_vehicle = pygame.Rect(px + 15, y, bw, bh)
        self.btn_battery = pygame.Rect(px + 15 + bw + gap, y, bw, bh)
        self.btn_mode = pygame.Rect(px + 15 + 2*(bw + gap), y, bw, bh)
        row2_y = y + bh + gap
        self.btn_agents = pygame.Rect(px + 15, row2_y, bw, bh)
        self.btn_set_depot = pygame.Rect(px + 15 + bw + gap, row2_y, bw, bh)
        self.btn_set_end = pygame.Rect(px + 15 + 2*(bw + gap), row2_y, bw, bh)

        veh = VEHICLES[self.vehicle_key]
        self._draw_mini_button(self.btn_vehicle, f"ARAÇ", veh["name"][:8], veh["color"])
        cap = BATTERY_OPTIONS[self.battery_idx]
        self._draw_mini_button(self.btn_battery, "PİL", f"{cap}", ACCENT_YELLOW)
        self._draw_mini_button(self.btn_mode, "MOD", "RL" if self.mode_rl else "A*",
                                ACCENT_PURPLE if self.mode_rl else ACCENT_CYAN)
        self._draw_mini_button(self.btn_agents, "AJAN", f"{self.num_agents}", ACCENT_GREEN)
        depot_active = self.click_mode == "set_depot"
        end_active = self.click_mode == "set_end"
        self._draw_mini_button(self.btn_set_depot, "DEPO", "SEÇİYOR.." if depot_active else "SEÇ",
                                ACCENT_GREEN, active=depot_active)
        self._draw_mini_button(self.btn_set_end, "BİTİŞ", "SEÇİYOR.." if end_active else "EKLE/SEÇ",
                                ACCENT_PURPLE, active=end_active)
        y = row2_y + bh + 10

    def _draw_mini_button(self, rect, label, value, color, active=False):
        bg = (30, 24, 46) if not active else (color[0]//3, color[1]//3, color[2]//3)
        draw_rounded_rect(self.screen, bg, rect, radius=7, border=2, border_color=color)
        lbl_s = self.font_label.render(label, True, TEXT_DIM)
        val_s = self.font_small.render(value, True, TEXT_BRIGHT if not active else color)
        self.screen.blit(lbl_s, (rect.x + rect.w//2 - lbl_s.get_width()//2, rect.y + 4))
        self.screen.blit(val_s, (rect.x + rect.w//2 - val_s.get_width()//2, rect.y + 17))

    def _draw_graph_overlay(self):
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


    def _grid_pos_from_mouse(self, mx, my):
        gx = mx - MAP_OFFSET[0]
        gy = my - MAP_OFFSET[1]
        if gx < 0 or gy < 0:
            return None
        c = gx // CELL_SIZE
        r = gy // CELL_SIZE
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            return (int(r), int(c))
        return None

    def _handle_map_click(self, mpos):
        if not self.click_mode:
            return False
        cell = self._grid_pos_from_mouse(*mpos)
        if cell is None:
            return False
        if self.grid[cell[0]][cell[1]] == -1:
            return True
        if any(t["pos"] == cell for t in self.target_data):
            return True
        if self.click_mode == "set_depot":
            self.depot = cell
        elif self.click_mode == "set_end":
            self.end_point = cell
        self.click_mode = None
        self.reset_env()
        return True

    def _cycle_vehicle(self):
        idx = VEHICLE_KEYS.index(self.vehicle_key)
        self.vehicle_key = VEHICLE_KEYS[(idx + 1) % len(VEHICLE_KEYS)]
        self.reset_env()

    def _cycle_battery(self):
        self.battery_idx = (self.battery_idx + 1) % len(BATTERY_OPTIONS)
        self.reset_env()

    def _toggle_mode(self):
        self.mode_rl = not self.mode_rl
        self.reset_env()

    def _cycle_agents(self):
        self.num_agents = (self.num_agents % 3) + 1
        self.reset_env()

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
                        self.click_mode = None
                    if event.key == pygame.K_1: self.speed_level = 1
                    if event.key == pygame.K_2: self.speed_level = 2
                    if event.key == pygame.K_3: self.speed_level = 3
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.show_graph:
                        self.show_graph = False
                    elif self.click_mode and self._handle_map_click(event.pos):
                        pass
                    elif self.btn_start.collidepoint(event.pos):
                        self.is_running = not self.is_running
                    elif self.btn_reset.collidepoint(event.pos):
                        self.reset_env()
                    elif self.btn_graph.collidepoint(event.pos) and self.episode_done:
                        self.show_graph = True
                    elif self.btn_vehicle.collidepoint(event.pos):
                        self._cycle_vehicle()
                    elif self.btn_battery.collidepoint(event.pos):
                        self._cycle_battery()
                    elif self.btn_mode.collidepoint(event.pos):
                        self._toggle_mode()
                    elif self.btn_agents.collidepoint(event.pos):
                        self._cycle_agents()
                    elif self.btn_set_depot.collidepoint(event.pos):
                        self.click_mode = None if self.click_mode == "set_depot" else "set_depot"
                    elif self.btn_set_end.collidepoint(event.pos):
                        self.click_mode = None if self.click_mode == "set_end" else "set_end"
                    else:
                        for si, sr in enumerate(self.btn_speed):
                            if sr.collidepoint(event.pos):
                                self.speed_level = si + 1

            if self.is_running:
                move_timer += dt
                base_delay = speed_map.get(self.speed_level, 140)
                veh_mult = VEHICLES[self.vehicle_key]["speed_mult"]
                delay = base_delay / max(veh_mult, 0.1)
                if move_timer > delay:
                    self.update_logic()
                    move_timer = 0
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    CyberDelivery().run()