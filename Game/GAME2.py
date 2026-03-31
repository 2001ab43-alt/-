import pygame
import json
import os
import time
import random

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

coin_icon = pygame.image.load("coin_icon.png").convert_alpha()

def get_coin_icon(size):
    return pygame.transform.smoothscale(coin_icon, (size, size))

pygame.display.set_caption("Кликер — Рублёвый Мастер")

FONT = pygame.font.SysFont("Segoe UI", 34)
FONT_MED = pygame.font.SysFont("Segoe UI", 26)
FONT_SMALL = pygame.font.SysFont("Segoe UI", 20)
CLOCK = pygame.time.Clock()

SAVE_FILE = "save.json"
AUTOSAVE_INTERVAL = 10

# ЗАГРУЗКА / СОХРАНЕНИЕ
def load_save():
    default = {
        "score": 0,
        "per_click": 1,
        "passive": 0,
        "elite_click": 0.0,
        "elite_passive": 0.0,
        "rebirths": 0,
    }
    if not os.path.exists(SAVE_FILE):
        return default
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items():
            if k not in data:
                data[k] = v
        return data
    except:
        return default


def save_game(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)

# ЦВЕТНОЙ ФОН
def draw_gradient_bg():
    top = (242, 242, 247)
    bottom = (225, 235, 255)
    for i in range(HEIGHT):
        t = i / HEIGHT
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))


# ПАНЕЛИ И КНОПКИ
def draw_panel(x, y, w, h, r=16):
    shadow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 25), (0, 6, w, h - 6), border_radius=r)
    screen.blit(shadow, (x, y))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), border_radius=r)


def draw_button(x, y, w, h, text, enabled=True, accent=False):
    mx, my = pygame.mouse.get_pos()
    hover = x <= mx <= x + w and y <= my <= y + h

    if not enabled:
        color = (170, 170, 180)
        text_c = (40, 40, 40)
    else:
        if accent:
            color = (80, 150, 255) if not hover else (60, 130, 240)
            text_c = (255, 255, 255)
        else:
            color = (230, 230, 235) if not hover else (210, 210, 220)
            text_c = (30, 30, 30)

    pygame.draw.rect(screen, (0, 0, 0, 35), (x, y + 6, w, h - 6), border_radius=12)
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=12)

    lines = text.split("\n")

    for i, line in enumerate(lines):
        txt = FONT_MED.render(line, True, text_c)
        screen.blit(
            txt,
            (
                x + w // 2 - txt.get_width() // 2,
                y + h // 2 - txt.get_height() // 2 + i * 25
            )
        )

    return pygame.Rect(x, y, w, h)

# ЛЕТАЮЩИЕ МОНЕТКИ
class Coin:
    def __init__(self, x, y):
        self.x = x + random.uniform(-40, 40)
        self.y = y + random.uniform(-20, 20)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-4, -2)
        self.life = 70

    def update(self):
        self.vy += 0.2
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, (255, 220, 0), (int(self.x), int(self.y)), 10)
        pygame.draw.circle(screen, (180, 150, 0), (int(self.x), int(self.y)), 7)


coins = []

# ДОСТИЖЕНИЯ
achievements = [
    {"id": "first_click", "name": "Первый рубль", "desc": "Сделать первый клик", "done": False},
    {"id": "score_100", "name": "Сотка", "desc": "Накопить 100 р", "done": False},
    {"id": "score_1000", "name": "Косарь", "desc": "Накопить 1000 р", "done": False},
    {"id": "passive_10", "name": "Доходчик", "desc": "Пассивный доход 10 р/сек", "done": False},
    {"id": "click_10", "name": "Щёлк-мастер", "desc": "10 р за клик", "done": False},
]

achievement_popup = ""
achievement_timer = 0


# УЛУЧШЕНИЯ
click_upgrades = [
    {"name": "Монетка (+1)", "val": 1, "cost": 50},
    {"name": "Копилка (+2)", "val": 2, "cost": 120},
    {"name": "Монетный двор (+3)", "val": 3, "cost": 240},
    {"name": "Золотой запас (+4)", "val": 4, "cost": 400},
]

passive_upgrades = [
    {"name": "Касса (+1/сек)", "val": 1, "cost": 100},
    {"name": "Банк (+2/сек)", "val": 2, "cost": 250},
    {"name": "Инвестфонд (+3/сек)", "val": 3, "cost": 500},
    {"name": "ЦБ РФ (+4/сек)", "val": 4, "cost": 900},
]

elite_click = [
    {"name": "VIP-Печать (+5%)", "percent": 0.05, "cost": 2000, "bought": False},
    {"name": "Платиновая Чеканка (+10%)", "percent": 0.10, "cost": 6000, "bought": False},
    {"name": "Императорский Литейный (+15%)", "percent": 0.15, "cost": 12000, "bought": False},
]

elite_passive = [
    {"name": "Офшорный Рай (+5%)", "percent": 0.05, "cost": 3000, "bought": False},
    {"name": "Олигарх Инвест (+10%)", "percent": 0.10, "cost": 9000, "bought": False},
    {"name": "Газпром Премиум (+20%)", "percent": 0.20, "cost": 20000, "bought": False},
]
BASE_REBIRTH_PRICE = 10_000
REBIRTH_BONUS = 0.10

state = load_save()

score = state["score"]
per_click = state["per_click"]
passive = state["passive"]
elite_click_bonus = state["elite_click"]
elite_passive_bonus = state["elite_passive"]
rebirths = state.get("rebirths", 0)

rebirth_price = int(BASE_REBIRTH_PRICE * (1.4 ** rebirths))

last_autosave = time.time()
save_msg_timer = 0

shop_open = False
shop_section = 0
passive_timer = 0
achievements_open = False
click_pressed = False
combo_count = 0
combo_timer = 0
combo_multiplier = 1.0

# СЛУЧАЙНЫЕ СОБЫТИЯ
event_timer = 40
event_active = None
event_active_timer = 0
event_multiplier = 1.0
event_text = ""
event_popup_timer = 0

#КВЕСТЫ
random_quest_templates = [
    {"text": " Сделай 20 кликов за 8 сек",  "target": 20,  "time": 8,  "reward_percent": 0.15},
    {"text": " Сделай 30 кликов за 10 сек", "target": 30,  "time": 10, "reward_percent": 0.30},
    {"text": " Сделай 60 кликов за 20 сек", "target": 60,  "time": 20, "reward_percent": 0.45},
    {"text": " Сделай 100 кликов за 30 сек","target": 100, "time": 30, "reward_percent": 0.60},
]

active_random_quest = None
random_quest_timer = random.randint(25, 50)

def do_save():
    global save_msg_timer
    data = {
        "score": score,
        "per_click": per_click,
        "passive": passive,
        "elite_click": elite_click_bonus,
        "elite_passive": elite_passive_bonus,
        "rebirths": rebirths,
    }
    save_game(data)
    save_msg_timer = 140

# ГЛАВНЫЙ ЦИКЛ
running = True
while running:
    dt = CLOCK.tick(60)
    mx, my = pygame.mouse.get_pos()

    combo_timer -= dt / 1000
    if combo_timer <= 0:
        combo_count = 0
        combo_multiplier = 1.0

    for e in pygame.event.get():

        # ВЫХОД
        if e.type == pygame.QUIT:
            do_save()
            running = False

        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            click_pressed = False

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:

            if achievements_open:
                if back_btn.collidepoint(mx, my):
                    achievements_open = False

            if not shop_open:
                if click_btn.collidepoint(mx, my) and not click_pressed:
                    click_pressed = True
                    rebirth_bonus = 1 + rebirths * REBIRTH_BONUS
                    combo_count += 1
                    combo_timer = 1.0

                    if combo_count >= 15:
                        combo_multiplier = 2.0
                    elif combo_count >= 10:
                        combo_multiplier = 1.5
                    elif combo_count >= 5:
                        combo_multiplier = 1.2

                    score += (
                            (per_click + per_click * elite_click_bonus)
                            * rebirth_bonus
                            * event_multiplier
                            * combo_multiplier
                    )
                    if active_random_quest:
                        active_random_quest["progress"] += 1

                    for _ in range(5):
                        coins.append(Coin(WIDTH // 2, HEIGHT // 2 - 140))

                if ach_btn.collidepoint(mx, my):
                    achievements_open = True

                if shop_btn.collidepoint(mx, my):
                    shop_open = True

                if rebirth_btn.collidepoint(mx, my) and score >= rebirth_price:
                    score = 0
                    per_click = 1
                    passive = 0
                    elite_click_bonus = 0
                    elite_passive_bonus = 0

                    rebirths += 1
                    rebirth_price = int(BASE_REBIRTH_PRICE * (1.4 ** rebirths))

                    do_save()

            else:
                if back_btn.collidepoint(mx, my):
                    shop_open = False

                if sec1.collidepoint(mx, my): shop_section = 0
                if sec2.collidepoint(mx, my): shop_section = 1
                if sec3.collidepoint(mx, my): shop_section = 2
                if sec4.collidepoint(mx, my): shop_section = 3

                y = 260
                if shop_section == 0: ITEMS = click_upgrades
                elif shop_section == 1: ITEMS = passive_upgrades
                elif shop_section == 2: ITEMS = elite_click
                else: ITEMS = elite_passive

                for u in ITEMS:
                    buy_btn_rect = pygame.Rect(WIDTH - 240, y + 5, 160, 70)

                    if buy_btn_rect.collidepoint(mx, my) and score >= u["cost"] and not u.get("bought", False):
                        score -= u["cost"]

                        if shop_section == 0:
                            per_click += u["val"]
                            u["cost"] = int(u["cost"] * 1.4)
                        elif shop_section == 1:
                            passive += u["val"]
                            u["cost"] = int(u["cost"] * 1.4)
                        elif shop_section == 2:
                            elite_click_bonus += u["percent"]
                            u["bought"] = True
                        elif shop_section == 3:
                            elite_passive_bonus += u["percent"]
                            u["bought"] = True

                        do_save()
                    y += 100

    # Пассивный доход
    passive_timer += dt / 1000
    if passive_timer >= 1:
        rebirth_bonus = 1 + rebirths * REBIRTH_BONUS
        score += (passive + passive * elite_passive_bonus) * rebirth_bonus * event_multiplier
        passive_timer -= 1

    # ВНЕЗАПНЫЕ КВЕСТЫ
    random_quest_timer -= dt / 1000

    if random_quest_timer <= 0 and active_random_quest is None:
        q = random.choice(random_quest_templates)
        active_random_quest = {
            "text": q["text"],
            "target": q["target"],
            "progress": 0,
            "time_left": q["time"],
            "reward_percent": q["reward_percent"]
        }
        event_text = " ВНЕЗАПНЫЙ КВЕСТ!"
        event_popup_timer = 180

    if active_random_quest:
        active_random_quest["time_left"] -= dt / 1000
        if active_random_quest["time_left"] <= 0:
            active_random_quest = None
            random_quest_timer = random.randint(30, 60)

    # ЗАВЕРШЕНИЕ ВРЕМЕННОГО СОБЫТИЯ
    if event_active == "boost":
        event_active_timer -= dt / 1000
        if event_active_timer <= 0:
            event_active = None
            event_multiplier = 1.0
            event_text = ""

    # ОБРАБОТКА СЛУЧАЙНЫХ СОБЫТИЙ
    event_timer -= dt / 1000

    if event_timer <= 0 and event_active is None:
        event_type = random.choice(["bonus", "boost", "loss"])

        if event_type == "bonus":
            gain = int(score * 0.2 + 100)
            score += gain
            event_text = f" Бонус! +{gain} р"
            event_popup_timer = 180

        elif event_type == "boost":
            event_multiplier = 2.0
            event_active_timer = 20
            event_active = "boost"
            event_text = " Доход x2 на 20 сек!"
            event_popup_timer = 180

        elif event_type == "loss":
            loss = int(score * 0.1)
            score = max(0, score - loss)
            event_text = f" Потеря! -{loss} р"
            event_popup_timer = 180

        event_timer = 40

    # Обновление монет
    for c in coins[:]:
        c.update()
        if c.life <= 0:
            coins.remove(c)

    # ПРОВЕРКА ДОСТИЖЕНИЙ
    def unlock_achievement(a):
        global achievement_popup, achievement_timer
        a["done"] = True
        achievement_popup = f"Достижение: {a['name']}!"
        achievement_timer = 180


    for a in achievements:
        if a["done"]:
            continue

        if a["id"] == "first_click" and score > 0:
            unlock_achievement(a)

        elif a["id"] == "score_100" and score >= 100:
            unlock_achievement(a)

        elif a["id"] == "score_1000" and score >= 1000:
            unlock_achievement(a)

        elif a["id"] == "passive_10" and passive >= 10:
            unlock_achievement(a)

        elif a["id"] == "click_10" and per_click >= 10:
            unlock_achievement(a)

    # Рендер интерфейса
    draw_gradient_bg()

    # Верхняя панель
    draw_panel(20, 20, WIDTH - 40, 80)
    screen.blit(FONT.render("Кликер — Рублёвый Мастер", True, (30, 30, 40)),
                (40, 28))

    # Левая панель
    draw_panel(20, 120, 300, 150)
    screen.blit(FONT_MED.render(f"Баланс: {round(score,2)} р",
                                True, (20, 20, 30)), (40, 135))
    screen.blit(FONT_MED.render(
        f"За клик: {round(per_click + per_click * elite_click_bonus, 2)} р",
        True, (20, 20, 30)), (40, 165))
    screen.blit(FONT_MED.render(
        f"Пассив: {round(passive + passive * elite_passive_bonus, 2)} р/сек",
        True, (20, 20, 30)), (40, 195))
    screen.blit(
        FONT_SMALL.render(f"Перерождений: {rebirths}", True, (80, 80, 120)),
        (40, 225)
    )
    screen.blit(
        FONT_SMALL.render(f"Бонус: +{rebirths * 10}%", True, (80, 120, 80)),
        (40, 245)
    )
    if save_msg_timer > 0:
        save_msg_timer -= 1
        screen.blit(FONT_SMALL.render("Сохранено!", True, (0, 120, 0)),
                    (20, HEIGHT - 30))

    if combo_count > 0:
        screen.blit(
            FONT_SMALL.render(
                f"Комбо: x{combo_multiplier} ({combo_count})",
                True, (180, 120, 20)
            ),
            (40, 255)
        )
    # ВСПЛЫВАЮЩЕЕ ДОСТИЖЕНИЕ
    if achievement_timer > 0:
        achievement_timer -= 1
        draw_panel(WIDTH // 2 - 250, 90, 500, 60)
        screen.blit(
            FONT_MED.render(achievement_popup, True, (20, 120, 20)),
            (WIDTH // 2 - 230, 105)
        )

    # Игровой экран
    if not shop_open and not achievements_open:
        size = 300
        offset = 0

        if click_pressed:
            size = 270
            offset = 15

        click_btn = pygame.Rect(
            WIDTH // 2 - size // 2,
            HEIGHT // 2 - size // 2,
            size,
            size
        )

        coin_x = click_btn.centerx
        coin_y = click_btn.centery

        pygame.draw.circle(screen, (255, 220, 0), (coin_x, coin_y), size // 3)
        pygame.draw.circle(screen, (180, 150, 0), (coin_x, coin_y), size // 3 - 6)

        icon_size = size // 2
        coin_icon_scaled = get_coin_icon(icon_size)

        screen.blit(
            coin_icon_scaled,
            (
                coin_x - icon_size // 2,
                coin_y - icon_size // 2
            )
        )

        shop_btn = draw_button(WIDTH - 200, 20, 180, 60, "МАГАЗИН")
        ach_btn = draw_button(WIDTH - 200, 90, 180, 60, "ДОСТИЖЕНИЯ")
        rebirth_btn = draw_button(WIDTH - 200, 160, 180, 70, f"Перерождение\n{rebirth_price}р", accent=True)

    if active_random_quest and not shop_open and not achievements_open:
        draw_panel(WIDTH // 2 - 260, HEIGHT - 200, 520, 90)
        screen.blit(
            FONT_MED.render(active_random_quest["text"], True, (120, 80, 20)),
            (WIDTH // 2 - 240, HEIGHT - 185)
        )
        screen.blit(
            FONT_SMALL.render(
                f"{active_random_quest['progress']}/{active_random_quest['target']} | "
                f"Осталось: {int(active_random_quest['time_left'])} сек",
                True, (60, 60, 60)
            ),
            (WIDTH // 2 - 240, HEIGHT - 155)
        )

    # ЭКРАН ДОСТИЖЕНИЙ
    if achievements_open:
        draw_panel(40, 120, WIDTH - 80, HEIGHT - 160)
        screen.blit(FONT.render("ДОСТИЖЕНИЯ", True, (20, 20, 30)),
                    (WIDTH // 2 - 130, 130))

        back_btn = draw_button(WIDTH - 200, 20, 180, 60, "НАЗАД")

        y = 200
        for a in achievements:
            draw_panel(80, y, WIDTH - 160, 70)

            name_color = (20, 120, 20) if a["done"] else (120, 120, 120)
            status = "✔ Выполнено" if a["done"] else "✖ Не выполнено"

            screen.blit(FONT_MED.render(a["name"], True, name_color), (100, y + 8))
            screen.blit(FONT_SMALL.render(a["desc"], True, (60, 60, 60)), (100, y + 38))
            screen.blit(FONT_SMALL.render(status, True, name_color),
                        (WIDTH - 260, y + 25))

            y += 90

    # Магазин
    if shop_open:
        draw_panel(40, 120, WIDTH - 80, HEIGHT - 160)
        screen.blit(FONT.render("МАГАЗИН", True, (20, 20, 30)),
                    (WIDTH // 2 - 80, 130))

        back_btn = draw_button(WIDTH - 200, 20, 180, 60, "НАЗАД")

        sec1 = draw_button(70, 180, 250, 60, "За клик", accent=(shop_section == 0))
        sec2 = draw_button(330, 180, 250, 60, "Пассив", accent=(shop_section == 1))
        sec3 = draw_button(590, 180, 250, 60, "VIP Клик", accent=(shop_section == 2))
        sec4 = draw_button(850, 180, 250, 60, "VIP Пассив", accent=(shop_section == 3))

        y = 260
        if shop_section == 0:
            ITEMS = click_upgrades
        elif shop_section == 1:
            ITEMS = passive_upgrades
        elif shop_section == 2:
            ITEMS = elite_click
        else:
            ITEMS = elite_passive

        for u in ITEMS:
            draw_panel(80, y, WIDTH - 160, 80)
            screen.blit(FONT_MED.render(u["name"], True, (30, 30, 30)), (100, y + 5))

            price_text = "" if u.get("bought") else f"{u['cost']}р"
            screen.blit(FONT_SMALL.render(price_text, True, (50, 50, 60)),
                        (WIDTH - 320, y + 5))

            if u.get("bought"):
                draw_button(WIDTH - 240, y + 5, 160, 70, "КУПЛЕНО", enabled=False)
            else:
                draw_button(WIDTH - 240, y + 5, 160, 70, "КУПИТЬ", enabled=(score >= u["cost"]))

            y += 100

    # монетки поверх всего
    for c in coins:
        c.draw()

    # ОКНО СЛУЧАЙНОГО СОБЫТИЯ
    if event_popup_timer > 0:
        draw_panel(WIDTH // 2 - 260, HEIGHT - 120, 520, 60)
        screen.blit(
            FONT_MED.render(event_text, True, (120, 80, 20)),
            (WIDTH // 2 - 240, HEIGHT - 105)
        )
        event_popup_timer -= 1

    if active_random_quest:
        if active_random_quest["progress"] >= active_random_quest["target"]:
            reward = int(score * active_random_quest["reward_percent"])
            score += reward
            event_text = f" Квест выполнен! +{reward} р"
            event_popup_timer = 180
            active_random_quest = None
            random_quest_timer = random.randint(40, 80)

    pygame.display.flip()

pygame.quit()
