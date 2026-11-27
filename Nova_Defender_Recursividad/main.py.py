
import math, random, sys, array
import pygame

W, H = 480, 800                    
FPS = 60
RATE = 22050

C = {"ship": (61, 245, 224), "enemy": (255, 77, 141), "boss": (255, 182, 39), "eb": (255, 107, 107),
     "life": (255, 77, 109), "missile": (255, 182, 39), "spread": (125, 211, 252), "shield": (163, 230, 53)}
SKINS = [("Cian clásica", (14, 127, 120), (201, 255, 248), (61, 245, 224)),
         ("Fénix rojo", (130, 20, 30), (255, 200, 170), (255, 90, 60)),
         ("Rayo dorado", (140, 100, 0), (255, 245, 180), (255, 200, 40)),
         ("Sombra violeta", (60, 20, 110), (220, 190, 255), (170, 110, 255)),
         ("Hielo blanco", (90, 110, 140), (255, 255, 255), (190, 230, 255))]
JEFES = [{"body": (255, 210, 63), "dark": (166, 124, 0), "glow": (255, 224, 102), "eye": (58, 42, 0)},
         {"body": (255, 59, 59), "dark": (122, 0, 16), "glow": (255, 92, 92), "eye": (255, 224, 102)},
         {"body": (21, 21, 28), "dark": (0, 0, 0), "glow": (255, 26, 26), "eye": (255, 26, 26)}]
DIFS = [("facil", "BÁSICO", dict(enemy_hp=0.85, boss_hp=0.88, speed=0.85, enemy_fire=0.75, boss_fire=0.85)),
        ("normal", "INTERMEDIO", dict(enemy_hp=1, boss_hp=1, speed=1, enemy_fire=1, boss_fire=1)),
        ("dificil", "DIFÍCIL", dict(enemy_hp=1.25, boss_hp=1.25, speed=1.2, enemy_fire=1.3, boss_fire=1.25))]
MAX_LEVEL, MAX_METEORS = 3, 6
LEVEL_SPEED = {1: 1.6, 2: 2.6, 3: 2.6}
NOMBRE_NIVEL = ["Básico", "Intermedio", "Difícil"]


def onda(freq, dur, vol=0.4, tipo="sq", slide=0.0, ruido=False):
    n = int(RATE * dur); buf = array.array("h"); fase = 0.0
    for i in range(n):
        t = i / n
        fr = freq * (1 + slide * t)
        fase += fr / RATE
        if ruido: v = random.uniform(-1, 1)
        elif tipo == "sq": v = 1.0 if (fase % 1) < 0.5 else -1.0
        elif tipo == "tri": v = 4 * abs((fase % 1) - 0.5) - 1
        else: v = math.sin(fase * 2 * math.pi)
        env = min(1.0, i / 200) * (1 - t) ** 1.5
        buf.append(int(v * env * vol * 32767))
    return buf

def nota_hz(n): return 440 * 2 ** ((n - 69) / 12)



MIN, MAJ = (0, 3, 7), (0, 4, 7)

def _lista(compases):
    """compases[bar] = [(paso, nota MIDI, duración en pasos), ...]"""
    return lambda bar, st: next(((n, d) for s, n, d in compases[bar] if s == st), None)

def _jefe_lead(bar, st):
    if st % 2: return None
    r = [52, 53, 52, 53, 52, 58, 53, 59][bar]
    return (r + 24 + [0, 1, 0, 1, 7, 8, 7, 3][st >> 1], 2)

TEMAS = {
  
    "menu": dict(
        bpm=100, eco=True,
        compases=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ), (57, MIN), (53, MAJ), (55, MAJ), (52, MAJ)],
        lead=_lista([
            [(0, 76, 6), (6, 79, 2), (8, 81, 8)],
            [(0, 77, 6), (6, 81, 2), (8, 84, 8)],
            [(0, 79, 6), (6, 76, 2), (8, 72, 8)],
            [(0, 74, 6), (6, 79, 2), (8, 83, 4), (12, 81, 4)],
            [(0, 81, 4), (4, 79, 4), (8, 76, 8)],
            [(0, 77, 4), (4, 81, 4), (8, 84, 4), (12, 81, 4)],
            [(0, 83, 6), (6, 79, 2), (8, 74, 8)],
            [(0, 76, 4), (4, 80, 4), (8, 83, 4), (12, 80, 4)]]),
        bajo=lambda r, st: (r - 24, 6) if st % 8 == 0 else None,
        arp=lambda st: [0, 1, 2, 1][(st >> 1) % 4] if st % 2 == 0 else None,
        v_lead=0.07, v_arp=0.05, v_bajo=0.24, t_bajo="tri",
        bombo=lambda st: st in (0, 8), caja=lambda st: False, hat=lambda st: st % 4 == 2, v_bat=0.5),
    
    "battle": dict(
        bpm=148, eco=True,
        compases=[(57, MIN), (57, MIN), (53, MAJ), (55, MAJ), (57, MIN), (57, MIN), (53, MAJ), (52, MAJ)],
        lead=_lista([
            [(0, 81, 3), (3, 79, 1), (4, 76, 4), (8, 79, 3), (11, 76, 1), (12, 72, 4)],
            [(0, 81, 3), (3, 83, 1), (4, 84, 4), (8, 83, 2), (10, 81, 2), (12, 79, 4)],
            [(0, 77, 3), (3, 81, 1), (4, 84, 4), (8, 81, 3), (11, 77, 1), (12, 81, 4)],
            [(0, 79, 3), (3, 83, 1), (4, 86, 4), (8, 83, 2), (10, 79, 2), (12, 74, 4)],
            [(0, 81, 3), (3, 79, 1), (4, 76, 4), (8, 79, 3), (11, 76, 1), (12, 72, 4)],
            [(0, 84, 2), (2, 83, 2), (4, 81, 2), (6, 79, 2), (8, 76, 4), (12, 79, 4)],
            [(0, 81, 3), (3, 84, 1), (4, 89, 4), (8, 84, 2), (10, 81, 2), (12, 77, 4)],
            [(0, 83, 2), (2, 80, 2), (4, 76, 2), (6, 80, 2), (8, 83, 4), (12, 88, 4)]]),
        bajo=lambda r, st: (r - 24 + (12 if st % 4 == 2 else 0), 2) if st % 2 == 0 else None,
        arp=lambda st: [0, 2, 1, 5][st % 4],
        v_lead=0.07, v_arp=0.04, v_bajo=0.28, t_bajo="tri",
        bombo=lambda st: st % 4 == 0, caja=lambda st: st in (4, 12), hat=lambda st: st % 2 == 0, v_bat=1.0),
    
    "boss": dict(
        bpm=168, eco=False,
        compases=[(52, MIN), (53, MAJ), (52, MIN), (53, MAJ), (52, MIN), (58, MAJ), (53, MAJ), (59, MAJ)],
        lead=_jefe_lead,
        bajo=lambda r, st: (r - 24 + (12 if st % 8 >= 6 else 0), 1),
        arp=lambda st: 2 if st % 4 == 1 else 4 if st % 4 == 3 else None,
        v_lead=0.06, v_arp=0.045, v_bajo=0.1, t_bajo="sq",
        bombo=lambda st: st % 4 == 0 or st == 14, caja=lambda st: st in (4, 12), hat=lambda st: True, v_bat=1.1),
}

_cache = {}
def _tono(f, dur, tipo, vol):
    k = (round(f, 2), round(dur, 4), tipo, vol)
    if k not in _cache: _cache[k] = onda(f, dur, vol, tipo)
    return _cache[k]

def _bombo(vol):
    k = ("bombo", vol)
    if k not in _cache:
        n = int(RATE * 0.14); buf = array.array("h"); fase = 0.0
        for i in range(n):
            t = i / n; fase += 150 * (40 / 150) ** t / RATE
            buf.append(int(math.sin(fase * 2 * math.pi) * (1 - t) ** 2 * 0.32 * vol * 32767))
        _cache[k] = buf
    return _cache[k]

def _ruido_agudo(dur, vol):
    
    k = ("ruido", dur, vol)
    if k not in _cache:
        n = int(RATE * dur); buf = array.array("h"); prev = 0.0
        for i in range(n):
            v = random.uniform(-1, 1); h = (v - prev) * 0.5; prev = v
            buf.append(int(h * (1 - i / n) ** 2 * vol * 32767))
        _cache[k] = buf
    return _cache[k]

def componer(tr):
   
    paso = 60 / tr["bpm"] / 4; n = int(RATE * paso); nb = len(tr["compases"])
    total = [0] * (n * 16 * nb)

    def mezclar(seg, base, g=1.0):
        fin = min(len(seg), len(total) - base)
        if g == 1.0:
            for i in range(fin): total[base + i] += seg[i]
        else:
            for i in range(fin): total[base + i] += int(seg[i] * g)

    vb = tr["v_bat"]
    for bar in range(nb):
        raiz, q = tr["compases"][bar]
        for st in range(16):
            base = (bar * 16 + st) * n
            l = tr["lead"](bar, st)
            if l:
                seg = _tono(nota_hz(l[0]), l[1] * paso * 0.95, "sq", tr["v_lead"])
                mezclar(seg, base)
                if tr["eco"]:                       # eco espacial: copias retrasadas y más suaves
                    mezclar(seg, base + 3 * n, 0.45); mezclar(seg, base + 6 * n, 0.2)
            b = tr["bajo"](raiz, st)
            if b: mezclar(_tono(nota_hz(b[0]), b[1] * paso * 0.95, tr["t_bajo"], tr["v_bajo"]), base)
            a = tr["arp"](st)
            if a is not None:
                nt = raiz + q[a % 3] + 12 + (12 if a >= 3 else 0)
                mezclar(_tono(nota_hz(nt), paso * 0.8, "sq", tr["v_arp"]), base)
            if tr["bombo"](st): mezclar(_bombo(vb), base)
            if tr["caja"](st): mezclar(_ruido_agudo(0.11, 0.11 * vb), base)
            if tr["hat"](st): mezclar(_ruido_agudo(0.035, 0.045 * vb), base)
    return array.array("h", [max(-32767, min(32767, s)) for s in total])

class Audio:
    def __init__(self):
        self.ok = True; self.on = True; self.actual = None
        try:
            pygame.mixer.pre_init(RATE, -16, 1, 512); pygame.mixer.init(RATE, -16, 1, 512)
        except Exception:
            self.ok = False; return
        S = lambda b: pygame.mixer.Sound(buffer=b.tobytes())
        self.sfx = {
            "shot": S(onda(880, 0.07, 0.18, "sq", -0.5)),
            "missile": S(onda(220, 0.35, 0.25, "sq", 1.5)),
            "hit": S(onda(300, 0.05, 0.2, "sq", -0.6)),
            "boom": S(onda(0, 0.35, 0.35, ruido=True)),
            "bigboom": S(onda(0, 1.0, 0.5, ruido=True)),
            "power": S(onda(523, 0.25, 0.25, "sin", 1.0)),
            "hurt": S(onda(160, 0.4, 0.35, "sq", -0.7)),
            "alert": S(onda(440, 0.6, 0.25, "sq", 0.5)),
            "select": S(onda(660, 0.06, 0.2, "sq")),
            "start": S(onda(392, 0.4, 0.25, "sq", 1.0)),
        }
        
        self.musica = {nombre: S(componer(tr)) for nombre, tr in TEMAS.items()}
        self.canal = pygame.mixer.Channel(0)
        pygame.mixer.set_reserved(1)

    def play(self, nombre):
        if self.ok and self.on: self.sfx[nombre].play()

    def tema(self, nombre):
        if not self.ok or nombre == self.actual: return
        self.actual = nombre
        self.canal.stop()
        if self.on and nombre: self.canal.play(self.musica[nombre], loops=-1)

    def pausar(self, p):
       
        if not self.ok: return
        if p: self.canal.pause()
        else: self.canal.unpause()

    def alternar(self):
        if not self.ok: return
        self.on = not self.on
        t = self.actual; self.actual = None
        if self.on: self.tema(t)
        else: self.canal.stop(); self.actual = t

def formacion(x0, x1, y, prof, out, nivel, dif):
    
    if prof == 0 or x1 - x0 < 50:
        hp = max(1, math.ceil((1 + nivel // 3) * dif["enemy_hp"]))
        out.append(dict(x=(x0 + x1) / 2, y=y, hp=hp, max=hp, r=15, t=random.random() * 6, kind=prof, boss=False))
        return
    mid = (x0 + x1) / 2
    formacion(x0, mid, y + 38, prof - 1, out, nivel, dif)
    formacion(mid, x1, y + 38, prof - 1, out, nivel, dif)
    if prof % 2 == 0:
        hp = max(1, math.ceil((2 + nivel) * dif["enemy_hp"]))
        out.append(dict(x=mid, y=y, hp=hp, max=hp, r=17, t=0, kind=9, boss=False))

def disparo_fractal(x, y, ang, abre, prof, out, vel):
   
    if prof == 0:
        out.append(dict(x=x, y=y, vx=math.cos(ang) * vel, vy=math.sin(ang) * vel, dmg=1, enemy=True)); return
    disparo_fractal(x, y, ang - abre, abre / 2, prof - 1, out, vel)
    disparo_fractal(x, y, ang + abre, abre / 2, prof - 1, out, vel)

def explosion(x, y, c, n, out):
    if n <= 0: return
    a = random.random() * math.tau; s = random.random() * 4 + 1
    out.append(dict(x=x, y=y, vx=math.cos(a) * s, vy=math.sin(a) * s, life=40, c=c))
    explosion(x, y, c, n - 1, out)

R_STEP, R_MOVE, R_DEPTH, R_HARD, R_MAX = 5, 30, 6, 1000, 350
class Ruta: nodos = 0; obs = []; y = 0; meta = W / 2

def peligro(x, paso):
    f = paso * R_STEP; c = 0
    for (ox, oy, vx, vy, r) in Ruta.obs:
        if abs(ox + vx * f - x) < r + 22 and abs(oy + vy * f - Ruta.y) < r + 26: c += R_HARD
    return c

def buscar_ruta(x, paso, prof, limite):
  
    Ruta.nodos += 1
    if prof == 0 or Ruta.nodos > R_MAX: return abs(x - Ruta.meta) * 0.01, []
    mejor = (math.inf, [])
    for dx in (0, -1, 1):
        nx = max(25, min(W - 25, x + dx * R_MOVE))
        c = peligro(nx, paso + 1) + abs(dx) * 0.6
        if c >= min(mejor[0], limite): continue
        sc, sp = buscar_ruta(nx, paso + 1, prof - 1, min(mejor[0], limite) - c)
        if c + sc < mejor[0]: mejor = (c + sc, [nx] + sp)
    return mejor


_glow = {}
def brillo(surf, color, x, y, r, fuerza=1.0):
    key = (color, int(r), round(fuerza, 1))
    if key not in _glow:
        s = pygame.Surface((r * 2, r * 2))
        for i in range(int(r), 0, -2):
            k = (1 - i / r) ** 2 * fuerza
            pygame.draw.circle(s, tuple(min(255, int(ch * k)) for ch in color), (r, r), i)
        _glow[key] = s
    surf.blit(_glow[key], (x - r, y - r), special_flags=pygame.BLEND_RGB_ADD)

def corazon(s, x, y, tam, col):
    r = tam * 0.3
    pygame.draw.circle(s, col, (int(x - r), int(y - r * 0.4)), int(r) + 1)
    pygame.draw.circle(s, col, (int(x + r), int(y - r * 0.4)), int(r) + 1)
    pygame.draw.polygon(s, col, [(x - tam * 0.58, y - r * 0.1), (x + tam * 0.58, y - r * 0.1), (x, y + tam * 0.6)])

def icono(s, tipo, x, y, col=(7, 10, 26)):
    if tipo == "life": corazon(s, x, y, 15, col)
    elif tipo == "missile":
        pygame.draw.polygon(s, col, [(x, y - 9), (x + 3, y - 4), (x + 3, y + 4), (x + 6, y + 7), (x - 6, y + 7), (x - 3, y + 4), (x - 3, y - 4)])
        pygame.draw.polygon(s, (255, 90, 0), [(x - 2, y + 7), (x + 2, y + 7), (x, y + 11)])
    elif tipo == "spread":
        for a in (-0.45, 0, 0.45):
            tx, ty = x + math.sin(a) * 10, y + 5 - math.cos(a) * 12
            pygame.draw.line(s, col, (x, y + 5), (tx, ty), 2); pygame.draw.circle(s, col, (int(tx), int(ty)), 2)
    else:
        pygame.draw.polygon(s, col, [(x, y - 8), (x + 7, y - 5), (x + 6, y + 3), (x, y + 8), (x - 6, y + 3), (x - 7, y - 5)])
        pygame.draw.line(s, (255, 255, 255), (x, y - 5), (x, y + 5), 1)

def crear_misil():
    
    s = pygame.Surface((16, 34), pygame.SRCALPHA)
    pygame.draw.polygon(s, (200, 30, 30), [(8, 0), (11, 7), (5, 7)])             
    pygame.draw.rect(s, (225, 230, 240), (5, 7, 6, 18))                          
    pygame.draw.rect(s, (150, 160, 175), (9, 7, 2, 18))                          
    pygame.draw.rect(s, (255, 182, 39), (5, 13, 6, 3))                           
    pygame.draw.polygon(s, (200, 30, 30), [(5, 19), (0, 27), (5, 25)])           
    pygame.draw.polygon(s, (200, 30, 30), [(11, 19), (16, 27), (11, 25)])
    pygame.draw.rect(s, (70, 70, 80), (6, 25, 4, 3))                             
    return s

def dibujar_nave(s, x, y, sk, llama=True, escala=1.0):
    _, dark, light, glow = sk
    P = lambda pts: [(x + px * escala, y + py * escala) for px, py in pts]
    if llama:
        fl = 10 + random.random() * 8
        brillo(s, (255, 140, 40), x, y + 16 * escala, 14 * escala, 0.8)
        pygame.draw.polygon(s, (255, 157, 46), P([(-6, 10), (0, 14 + fl), (6, 10)]))
        pygame.draw.polygon(s, (255, 247, 194), P([(-3, 10), (0, 10 + fl * 0.6), (3, 10)]))
    brillo(s, glow, x, y, 30 * escala, 0.6)
    pygame.draw.polygon(s, dark, P([(0, -22), (6, -6), (18, 12), (6, 8), (0, 12), (-6, 8), (-18, 12), (-6, -6)]))
    pygame.draw.polygon(s, light, P([(0, -22), (4, -6), (8, 8), (0, 12), (-8, 8), (-4, -6)]))
    pygame.draw.ellipse(s, (27, 42, 107), pygame.Rect(x - 3.5 * escala, y - 13 * escala, 7 * escala, 14 * escala))
    pygame.draw.ellipse(s, (230, 240, 255), pygame.Rect(x - 2 * escala, y - 12 * escala, 2 * escala, 6 * escala))


class Juego:
    def __init__(self):
        pygame.init()
        self.audio = Audio()
        self.pantalla = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Nova Defender")
        self.reloj = pygame.time.Clock()
        fuente = "orbitron,consolas,arial"
        self.f_big = pygame.font.SysFont(fuente, 44, bold=True)
        self.f_mid = pygame.font.SysFont(fuente, 26, bold=True)
        self.f = pygame.font.SysFont(fuente, 17, bold=True)
        self.f_s = pygame.font.SysFont(fuente, 13)
        self.misil_img = crear_misil()
        self.fondo = pygame.Surface((W, H))
        for yy in range(H):
            t = yy / H
            self.fondo.fill((int(2 + 9 * t), int(3 + 12 * t), int(12 + 30 * t)), (0, yy, W, 1))
        self.stars = [[random.random() * W, random.random() * H, random.random() * 2 + 0.5] for _ in range(140)]
        self.estado = "menu"; self.pausa = False; self.skin = 0; self.dif = 1
        self.sel = 0; self.f_count = 0; self.ver_perf = False; self.plan_ms = 0.0
        self.mouse = dict(x=W / 2, y=H - 80, activo=False, down=False)
        self.g = self.nuevo()
        self.audio.tema("menu")

    def d(self): return DIFS[self.dif][2]

    def nuevo(self):
        return dict(px=W / 2, py=H - 80, lives=3, score=0, level=1, cd=0, inv=0, shield=0, missiles=0,
                    spread=0, bullets=[], enemies=[], items=[], parts=[], meteors=[], auto=False, route=[],
                    boss_phase=False, banner=120, tx=None)

   
    def empezar(self):
        self.g = self.nuevo(); self.estado = "play"; self.pausa = False; self.sel = 0
        self.audio.play("start"); self.iniciar_nivel()

    def iniciar_nivel(self):
        g = self.g
        g["enemies"] = []; g["meteors"] = []; g["boss_phase"] = False; g["banner"] = 120
        formacion(40, W - 40, 50, min(2 + math.ceil(g["level"] / 2), 4), g["enemies"], g["level"], self.d())
        self.audio.tema("battle")

    def aparecer_jefe(self):
        g = self.g; g["boss_phase"] = True; g["banner"] = 120
        hp = math.ceil([60, 90, 130][g["level"] - 1] * self.d()["boss_hp"])
        g["enemies"].append(dict(x=W / 2, y=-60, hp=hp, max=hp, r=46, t=0, boss=True, kind=g["level"]))
        self.audio.play("alert"); self.audio.tema("boss")

    def soltar(self, x, y, jefe):
        tipos = ["life", "missile", "spread", "shield"]
        if jefe:
            self.g["items"] += [dict(x=x - 20, y=y, type="life"), dict(x=x + 20, y=y, type=random.choice(tipos[1:]))]
        elif random.random() < 0.12:
            self.g["items"].append(dict(x=x, y=y, type=random.choice(tipos)))

    def herir(self):
        g = self.g
        if g["inv"] > 0: return
        if g["shield"] > 0: g["shield"] = 0; g["inv"] = 60; self.audio.play("hit"); return
        g["lives"] -= 1; g["inv"] = 120; explosion(g["px"], g["py"], C["ship"], 30, g["parts"])
        self.audio.play("hurt")
        if g["lives"] <= 0: self.terminar("over")

    def terminar(self, est):
        self.estado = est; self.pausa = False; self.sel = 0
        self.audio.play("bigboom" if est == "over" else "start"); self.audio.tema("menu")

    def planear(self):
        g = self.g; Ruta.obs = []; Ruta.y = g["py"]; look = R_STEP * R_DEPTH
        def add(x, y, vx, vy, r):
            if not (vy >= 0 and y < Ruta.y - 400) and y + vy * look > Ruta.y - 60 and y < Ruta.y + 60:
                Ruta.obs.append((x, y, vx, vy, r))
        for e in g["enemies"]: add(e["x"], e["y"], 0, 0 if e["boss"] else 0.15 * LEVEL_SPEED[g["level"]], e["r"])
        for m in g["meteors"]: add(m["x"], m["y"], m["vx"], m["vy"], 24)
        for b in g["bullets"]:
            if b.get("enemy"): add(b["x"], b["y"], b["vx"], b["vy"], 5)
        Ruta.meta = W / 2; by = -1
        for e in g["enemies"]:
            if by < e["y"] < g["py"]: Ruta.meta = e["x"]; by = e["y"]
        Ruta.nodos = 0
        _, path = buscar_ruta(g["px"], 0, R_DEPTH, math.inf)
        g["route"] = path
        return path[0] if path else g["px"]

    
    def actualizar(self, k):
        g = self.g; d = self.d(); m = self.mouse
        disparar = k[pygame.K_SPACE] or m["down"]
        if g["auto"]:
            if self.f_count % 2 == 0:
                t0 = pygame.time.get_ticks(); g["tx"] = self.planear(); self.plan_ms = pygame.time.get_ticks() - t0
            g["px"] += max(-6, min(6, (g["tx"] or g["px"]) - g["px"]))
            g["py"] += max(-2, min(2, (H - 80) - g["py"])); disparar = True
        else:
            iz = k[pygame.K_LEFT] or k[pygame.K_a]; de = k[pygame.K_RIGHT] or k[pygame.K_d]
            ar = k[pygame.K_UP] or k[pygame.K_w]; ab = k[pygame.K_DOWN] or k[pygame.K_s]
            if iz or de or ar or ab: m["activo"] = False
            if m["activo"]:
                g["px"] += max(-12, min(12, m["x"] - g["px"])); g["py"] += max(-12, min(12, m["y"] - g["py"]))
            else:
                g["px"] += (de - iz) * 6; g["py"] += (ab - ar) * 5
        g["px"] = max(20, min(W - 20, g["px"])); g["py"] = max(H * 0.45, min(H - 30, g["py"]))
        g["cd"] -= 1; g["inv"] -= 1
        if g["shield"] > 0: g["shield"] -= 1
        if g["spread"] > 0: g["spread"] -= 1

        if disparar and g["cd"] <= 0:
            g["cd"] = 10; self.audio.play("shot")
            g["bullets"].append(dict(x=g["px"], y=g["py"] - 20, vx=0, vy=-10, dmg=1))
            if g["spread"] > 0:
                for vx in (-2, 2): g["bullets"].append(dict(x=g["px"], y=g["py"] - 20, vx=vx, vy=-9, dmg=1))
            if g["missiles"] > 0 and random.random() < 0.35:
                g["missiles"] -= 1; self.audio.play("missile")
                g["bullets"].append(dict(x=g["px"], y=g["py"], vx=0, vy=-4, dmg=5, homing=True))
        for s in self.stars:
            s[1] += s[2]
            if s[1] > H: s[1] = 0; s[0] = random.random() * W

        for b in g["bullets"]:
            if b.get("homing") and g["enemies"]:
                t = g["enemies"][0]; a = math.atan2(t["y"] - b["y"], t["x"] - b["x"])
                b["vx"] += math.cos(a) * 0.6; b["vy"] += math.sin(a) * 0.6
                mg = math.hypot(b["vx"], b["vy"]) or 1; b["vx"] = b["vx"] / mg * 8; b["vy"] = b["vy"] / mg * 8
                if self.f_count % 2 == 0:
                    g["parts"].append(dict(x=b["x"] - b["vx"] * 2, y=b["y"] - b["vy"] * 2, vx=random.uniform(-.5, .5), vy=random.uniform(-.5, .5), life=18, c=(255, 140, 40)))
            b["x"] += b["vx"]; b["y"] += b["vy"]

        if g["level"] == 3 and not g["boss_phase"] and len(g["meteors"]) < MAX_METEORS and random.random() < 0.016:
            g["meteors"].append(dict(x=random.random() * (W - 60) + 30, y=-40, vx=random.choice([-2, -1, 1, 2]), vy=4 + random.random() * 4, rot=random.random() * 6))
        for mt in g["meteors"]:
            mt["x"] += mt["vx"]; mt["y"] += mt["vy"]; mt["rot"] += 0.04
            if math.hypot(mt["x"] - g["px"], mt["y"] - g["py"]) < 38: self.herir(); mt["y"] = 9999
        g["meteors"] = [mt for mt in g["meteors"] if mt["y"] < H + 40 and -60 < mt["x"] < W + 60]

        vel = LEVEL_SPEED[g["level"]] * d["speed"]
        for e in g["enemies"]:
            e["t"] += 0.03
            if e["boss"]:
                if e["y"] < 130: e["y"] += 1
                e["x"] = W / 2 + math.sin(e["t"]) * (W / 2 - 70)
                if random.random() < (0.012 + e["kind"] * 0.008) * d["boss_fire"]:
                    disparo_fractal(e["x"], e["y"] + 40, math.pi / 2, 0.5, e["kind"] + 1, g["bullets"], 3 + e["kind"])
                if random.random() < 0.03 * d["boss_fire"]:
                    a = math.atan2(g["py"] - e["y"], g["px"] - e["x"])
                    g["bullets"].append(dict(x=e["x"], y=e["y"], vx=math.cos(a) * 5, vy=math.sin(a) * 5, dmg=1, enemy=True))
            else:
                e["x"] += math.sin(e["t"]) * vel; e["y"] += 0.15 * vel
                if random.random() < 0.0025 * g["level"] * d["enemy_fire"] and len(g["bullets"]) < 110:
                    g["bullets"].append(dict(x=e["x"], y=e["y"], vx=0, vy=3.5 + g["level"] * 0.7, dmg=1, enemy=True))
                if e["y"] > H: e["hp"] = 0
            if math.hypot(e["x"] - g["px"], e["y"] - g["py"]) < e["r"] + 14:
                self.herir()
                if not e["boss"]: e["hp"] = 0

        jefe_caido = False
        for b in g["bullets"]:
            if b.get("enemy"):
                if math.hypot(b["x"] - g["px"], b["y"] - g["py"]) < 14: b["y"] = 9999; self.herir()
                continue
            for e in g["enemies"]:
                if e["hp"] > 0 and math.hypot(b["x"] - e["x"], b["y"] - e["y"]) < e["r"]:
                    e["hp"] -= b["dmg"]; b["y"] = -9999
                    if e["hp"] <= 0:
                        g["score"] += 1000 * g["level"] if e["boss"] else 50
                        explosion(e["x"], e["y"], C["boss"] if e["boss"] else C["enemy"], 80 if e["boss"] else 15, g["parts"])
                        self.soltar(e["x"], e["y"], e["boss"])
                        self.audio.play("bigboom" if e["boss"] else "boom")
                        if e["boss"]: jefe_caido = True
                    else: self.audio.play("hit")
                    break
        if jefe_caido:
            g["bullets"] = [b for b in g["bullets"] if not b.get("enemy")]; g["meteors"] = []
            self.audio.tema("battle")
        g["bullets"] = [b for b in g["bullets"] if -50 < b["y"] < H + 50 and -50 < b["x"] < W + 50]
        g["enemies"] = [e for e in g["enemies"] if e["hp"] > 0]

        for it in g["items"]:
            it["y"] += 2
            if math.hypot(it["x"] - g["px"], it["y"] - g["py"]) < 24:
                t = it["type"]
                if t == "life": g["lives"] = min(g["lives"] + 1, 3)
                if t == "missile": g["missiles"] += 10
                if t == "spread": g["spread"] = 900
                if t == "shield": g["shield"] = 600
                it["y"] = 9999; self.audio.play("power")
        g["items"] = [i for i in g["items"] if i["y"] < H + 20]
        for p in g["parts"]: p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
        g["parts"] = [p for p in g["parts"] if p["life"] > 0]
        if g["banner"] > 0: g["banner"] -= 1

        if not g["enemies"] and self.estado == "play":
            if not g["boss_phase"]: self.aparecer_jefe()
            elif g["level"] >= MAX_LEVEL: self.terminar("win")
            else: g["level"] += 1; g["score"] += 200; self.iniciar_nivel()

   
    def texto(self, t, fuente, col, x, y, centro=True, glow=None):
        img = fuente.render(t, True, col)
        r = img.get_rect(center=(x, y)) if centro else img.get_rect(topleft=(x, y))
        if glow: brillo(self.pantalla, glow, r.centerx, r.centery, max(r.w, r.h) // 2 + 10, 0.35)
        self.pantalla.blit(img, r)

    def fondo_espacial(self):
        s = self.pantalla; s.blit(self.fondo, (0, 0)); f = self.f_count
        brillo(s, (120, 40, 200), 120, (f * 0.2) % (H + 400) - 200, 220, 0.35)
        brillo(s, (0, 180, 200), 360, (f * 0.15 + 300) % (H + 400) - 200, 190, 0.3)
        for x, y, sz in self.stars:
            a = 0.5 + 0.5 * abs(math.sin(f * 0.05 + x))
            col = (int(191 * a), int(233 * a), 255) if sz > 2 else (int(255 * a),) * 3
            pygame.draw.circle(s, col, (int(x), int(y)), max(1, int(sz * 0.7)))

    def dibujar_jefe(self, e):
        s = self.pantalla; b = JEFES[min(2, max(0, e["kind"] - 1))]; r = e["r"]; x, y = e["x"], e["y"]; f = self.f_count
        brillo(s, b["glow"], x, y, r * 2, 0.55)
        pygame.draw.polygon(s, b["dark"], [(x - r * 1.1, y), (x - r * 1.5, y + r * .7), (x - r * .7, y + r * .3)])
        pygame.draw.polygon(s, b["dark"], [(x + r * 1.1, y), (x + r * 1.5, y + r * .7), (x + r * .7, y + r * .3)])
        pygame.draw.ellipse(s, b["dark"], pygame.Rect(x - r * 1.15, y - r * .5, r * 2.3, r))
        pygame.draw.ellipse(s, b["body"], pygame.Rect(x - r * 1.05, y - r * .45, r * 2.1, r * .8))
        if e["kind"] == 3: pygame.draw.ellipse(s, (255, 26, 26), pygame.Rect(x - r * 1.15, y - r * .5, r * 2.3, r), 2)
        dome = (90, 10, 10) if e["kind"] == 3 else (150, 210, 255)
        pygame.draw.ellipse(s, dome, pygame.Rect(x - r * .55, y - r * .75, r * 1.1, r * .9))
        pygame.draw.ellipse(s, (255, 255, 255), pygame.Rect(x - r * .3, y - r * .65, r * .2, r * .25))
        for i in range(8):
            a = f * 0.05 + i / 8 * math.tau
            col = b["glow"] if i % 2 else (255, 255, 255)
            pygame.draw.circle(s, col, (int(x + math.cos(a) * r * .95), int(y + math.sin(a) * r * .25 + 6)), 3)
        pulso = 1 + 0.25 * math.sin(f * 0.2) if e["kind"] == 3 else 1
        for sx in (-1, 1):
            pts = [(x + sx * 8, y - 2), (x + sx * 24 * pulso, y - 8), (x + sx * 22, y + 4)]
            if e["kind"] == 3: brillo(s, (255, 26, 26), x + sx * 16, y - 2, 18, 0.9)
            pygame.draw.polygon(s, b["eye"], pts)
        pygame.draw.rect(s, (40, 40, 50), (60, 14, W - 120, 10))
        pygame.draw.rect(s, b["glow"], (60, 14, (W - 120) * e["hp"] / e["max"], 10))
        pygame.draw.rect(s, b["glow"], (60, 14, W - 120, 10), 1)
        self.texto(f"JEFE {NOMBRE_NIVEL[self.g['level'] - 1].upper()}", self.f_s, (255, 255, 255), W / 2, 36)

    def dibujar_enemigo(self, e):
        s = self.pantalla; col = (192, 132, 252) if e["kind"] == 9 else C["enemy"]; r = e["r"]; x, y = e["x"], e["y"]
        brillo(s, col, x, y, r * 1.8, 0.4)
        for sx in (-0.6, 0, 0.6):
            pygame.draw.line(s, col, (x + sx * r, y + 6), (x + sx * r + math.sin(self.f_count * .15 + e["t"] + sx) * 4, y + 14), 2)
        pygame.draw.ellipse(s, col, pygame.Rect(x - r, y + 2 - r * .42, r * 2, r * .84))
        pygame.draw.circle(s, tuple(min(255, c + 60) for c in col), (int(x), int(y - 2)), int(r * .55), draw_top_left=True, draw_top_right=True)
        for ex in (-5, 5):
            pygame.draw.circle(s, (10, 10, 20), (int(x + ex), int(y - 4)), 3)
            pygame.draw.circle(s, (255, 255, 255), (int(x + ex - 1), int(y - 5)), 1)
        if e["hp"] < e["max"]:
            pygame.draw.rect(s, (60, 60, 70), (x - r, y - r, r * 2, 3))
            pygame.draw.rect(s, col, (x - r, y - r, r * 2 * e["hp"] / e["max"], 3))

    def dibujar_misil(self, b):
        ang = math.degrees(math.atan2(-b["vx"], -b["vy"]))
        img = pygame.transform.rotate(self.misil_img, ang)
        mg = math.hypot(b["vx"], b["vy"]) or 1; ux, uy = b["vx"] / mg, b["vy"] / mg
        cola = (b["x"] - ux * 17, b["y"] - uy * 17)
        brillo(self.pantalla, (255, 120, 30), cola[0], cola[1], 12 + random.random() * 4, 0.9)
        pygame.draw.circle(self.pantalla, (255, 240, 180), (int(cola[0]), int(cola[1])), 3)
        self.pantalla.blit(img, img.get_rect(center=(b["x"], b["y"])))

    def dibujar_juego(self):
        s = self.pantalla; g = self.g; f = self.f_count
        for mt in g["meteors"]:
            pygame.draw.circle(s, (105, 115, 140), (int(mt["x"]), int(mt["y"])), 23)
            for dx, dy, rr in ((-9, -9, 7), (9, 7, 6)):
                ca, sa = math.cos(mt["rot"]), math.sin(mt["rot"])
                pygame.draw.circle(s, (55, 60, 80), (int(mt["x"] + dx * ca - dy * sa), int(mt["y"] + dx * sa + dy * ca)), rr)
        for e in g["enemies"]: (self.dibujar_jefe if e["boss"] else self.dibujar_enemigo)(e)
        if g["auto"] and g["route"]:
            pts = [(g["px"], g["py"] - 26)] + [(x, g["py"] - 26 - (i + 1) * 12) for i, x in enumerate(g["route"])]
            pygame.draw.lines(s, (61, 245, 224), False, pts, 2)
        for b in g["bullets"]:
            if b.get("homing"): self.dibujar_misil(b)
            elif b.get("enemy"):
                brillo(s, C["eb"], b["x"], b["y"], 10, 0.9); pygame.draw.circle(s, (255, 230, 230), (int(b["x"]), int(b["y"])), 3)
            else:
                brillo(s, C["ship"], b["x"], b["y"], 10, 0.8); pygame.draw.rect(s, (230, 255, 250), (b["x"] - 2, b["y"] - 8, 4, 16))
        for p in g["parts"]:
            k = p["life"] / 40
            pygame.draw.circle(s, tuple(int(c * min(1, k + .2)) for c in p["c"]), (int(p["x"]), int(p["y"])), max(1, int(1 + k * 3)))
        for it in g["items"]:
            bob = math.sin(f * 0.1 + it["x"]) * 2; col = C[it["type"]]
            brillo(s, col, it["x"], it["y"] + bob, 24, 0.7)
            pygame.draw.circle(s, col, (int(it["x"]), int(it["y"] + bob)), 13)
            icono(s, it["type"], it["x"], it["y"] + bob)
        if g["inv"] <= 0 or (g["inv"] // 5) % 2:
            dibujar_nave(s, g["px"], g["py"], SKINS[self.skin])
            if g["shield"] > 0:
                brillo(s, C["shield"], g["px"], g["py"], 32, 0.4)
                pygame.draw.circle(s, C["shield"], (int(g["px"]), int(g["py"])), 29, 2)
     
        self.texto(f"NIVEL {g['level']} · {NOMBRE_NIVEL[g['level'] - 1]}", self.f_s, (232, 255, 251), 12, 50, False)
        for i in range(max(0, g["lives"])): corazon(s, 22 + i * 24, 82, 16, C["life"])
        self.texto(f"PUNTOS {g['score']}", self.f, (232, 255, 251), 12, H - 30, False)
        extra = f"MISILES {g['missiles']}" + (" · TRIPLE" if g["spread"] > 0 else "") + (" · ESCUDO" if g["shield"] > 0 else "")
        img = self.f_s.render(extra, True, C["missile"]); s.blit(img, (W - img.get_width() - 12, H - 28))
        if g["auto"]: self.texto("AUTOPILOTO", self.f_s, C["shield"], 12, 100, False)
        if self.ver_perf:
            self.texto(f"FPS {self.reloj.get_fps():.0f} · RUTA {self.plan_ms} ms", self.f_s, (163, 230, 53), 12, H - 52, False)
        if g["banner"] > 0:
            col = JEFES[min(2, g["level"] - 1)]["glow"] if g["boss_phase"] else C["ship"]
            self.texto("¡ALERTA: JEFE!" if g["boss_phase"] else f"NIVEL {g['level']}", self.f_mid, col, W / 2, H / 2, glow=col)
        pygame.draw.rect(s, (61, 245, 224), (W - 44, 44, 30, 30), 1, border_radius=6)
        pygame.draw.rect(s, (61, 245, 224), (W - 35, 51, 4, 16)); pygame.draw.rect(s, (61, 245, 224), (W - 27, 51, 4, 16))

    
    def opciones(self):
        if self.estado == "menu":
            return ["START", f"DIFICULTAD: ‹ {DIFS[self.dif][1]} ›", f"NAVE: ‹ {SKINS[self.skin][0]} ›",
                    f"SONIDO: {'SÍ' if self.audio.on else 'NO'}", "SALIR DEL JUEGO"]
        if self.pausa:
            return ["CONTINUAR", f"NAVE: ‹ {SKINS[self.skin][0]} ›", f"SONIDO: {'SÍ' if self.audio.on else 'NO'}",
                    "SALIR AL INICIO", "SALIR DEL JUEGO"]
        return ["REINTENTAR", "MENÚ DE INICIO", "SALIR DEL JUEGO"]

    def rects_opciones(self, y0):
        return [pygame.Rect(W / 2 - 170, y0 + i * 52, 340, 42) for i in range(len(self.opciones()))]

    def dibujar_menu(self):
        s = self.pantalla; velo = pygame.Surface((W, H), pygame.SRCALPHA); velo.fill((2, 3, 12, 160)); s.blit(velo, (0, 0))
        if self.estado == "menu":
            self.texto("NOVA", self.f_big, C["ship"], W / 2, 110, glow=C["ship"])
            self.texto("DEFENDER", self.f_big, C["missile"], W / 2, 160, glow=C["missile"])
            dibujar_nave(s, W / 2, 270, SKINS[self.skin], True, 2.0)
            y0 = 360
        elif self.pausa:
            self.texto("PAUSA", self.f_big, C["ship"], W / 2, 150, glow=C["ship"])
            dibujar_nave(s, W / 2, 250, SKINS[self.skin], True, 1.6); y0 = 330
        else:
            t = "¡GALAXIA SALVADA!" if self.estado == "win" else "FIN DEL JUEGO"
            self.texto(t, self.f_mid, C["missile"] if self.estado == "win" else C["eb"], W / 2, 200, glow=C["eb"])
            self.texto(f"Puntos: {self.g['score']} · Nivel {self.g['level']}", self.f, (232, 255, 251), W / 2, 250); y0 = 330
        for i, (r, t) in enumerate(zip(self.rects_opciones(y0), self.opciones())):
            on = i == self.sel
            if on: brillo(s, C["ship"], r.centerx, r.centery, 120, 0.25)
            pygame.draw.rect(s, C["ship"] if on else (20, 30, 50), r, 0, border_radius=8)
            pygame.draw.rect(s, C["ship"], r, 1, border_radius=8)
            self.texto(t, self.f, (7, 10, 26) if on else (232, 255, 251), r.centerx, r.centery)
        if self.estado == "menu":
            yl = H - 120
            for i, (t, n) in enumerate((("life", "Vida"), ("missile", "Misiles"), ("spread", "Triple"), ("shield", "Escudo"))):
                x = 60 + i * 110
                pygame.draw.circle(s, C[t], (x, yl), 13); icono(s, t, x, yl)
                self.texto(n, self.f_s, (200, 220, 230), x, yl + 26)
            self.texto("↑↓ elegir · ←→ cambiar · Enter aceptar · mouse también", self.f_s, (150, 170, 190), W / 2, H - 50)
            self.texto("Mueve: flechas/WASD/mouse · Dispara: Espacio/clic", self.f_s, (150, 170, 190), W / 2, H - 30)
        self._y0 = y0

    def accion(self, i, d=0):
        op = self.opciones()[i]; self.audio.play("select")
        if op.startswith("DIFICULTAD"): self.dif = (self.dif + (d or 1)) % 3
        elif op.startswith("NAVE"): self.skin = (self.skin + (d or 1)) % len(SKINS)
        elif op.startswith("SONIDO"): self.audio.alternar()
        elif d: return
        elif op in ("START", "REINTENTAR"): self.empezar()
        elif op == "CONTINUAR": self.pausa = False
        elif op in ("SALIR AL INICIO", "MENÚ DE INICIO"):
            self.estado = "menu"; self.pausa = False; self.sel = 0; self.audio.tema("menu")
        elif op == "SALIR DEL JUEGO": pygame.quit(); sys.exit()

   
    def en_menu(self): return self.estado != "play" or self.pausa

    def run(self):
        self._y0 = 360
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    k = ev.key
                    if k == pygame.K_m: self.audio.alternar()
                    if k == pygame.K_f: self.ver_perf = not self.ver_perf
                    if self.estado == "play" and k in (pygame.K_ESCAPE, pygame.K_p):
                        self.pausa = not self.pausa; self.sel = 0; self.audio.play("select"); continue
                    if self.estado == "play" and not self.pausa and k == pygame.K_t:
                        self.g["auto"] = not self.g["auto"]; self.g["route"] = []
                    if self.en_menu():
                        n = len(self.opciones())
                        if k in (pygame.K_UP, pygame.K_w): self.sel = (self.sel - 1) % n; self.audio.play("select")
                        if k in (pygame.K_DOWN, pygame.K_s): self.sel = (self.sel + 1) % n; self.audio.play("select")
                        if k in (pygame.K_LEFT, pygame.K_a): self.accion(self.sel, -1)
                        if k in (pygame.K_RIGHT, pygame.K_d): self.accion(self.sel, 1)
                        if k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE): self.accion(self.sel)
                if ev.type == pygame.MOUSEMOTION:
                    self.mouse["x"], self.mouse["y"] = ev.pos
                    if self.en_menu():
                        for i, r in enumerate(self.rects_opciones(self._y0)):
                            if r.collidepoint(ev.pos): self.sel = i
                    else: self.mouse["activo"] = True
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.en_menu():
                        for i, r in enumerate(self.rects_opciones(self._y0)):
                            if r.collidepoint(ev.pos): self.accion(i)
                    elif pygame.Rect(W - 44, 44, 30, 30).collidepoint(ev.pos): self.pausa = True; self.sel = 0
                    else: self.mouse["activo"] = True; self.mouse["down"] = True
                if ev.type == pygame.MOUSEBUTTONUP: self.mouse["down"] = False
            self.f_count += 1
            pausado = self.estado == "play" and self.pausa
            if pausado != getattr(self, "_mus_pausada", False):
                self._mus_pausada = pausado; self.audio.pausar(pausado)
            if self.estado == "play" and not self.pausa: self.actualizar(pygame.key.get_pressed())
            self.fondo_espacial()
            if self.estado == "play": self.dibujar_juego()
            if self.en_menu(): self.dibujar_menu()
            pygame.display.flip()
            self.reloj.tick(FPS)

if __name__ == "__main__":
    Juego().run()
