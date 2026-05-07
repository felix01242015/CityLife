import pygame
import sys
import random
import math as math
import time

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 
pygame.display.set_caption("CityLife Platformer")

# Colorssussyba
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
SKIN_COLOR = (255, 218, 185)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)
SUN_YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
MENU_BG = (245, 245, 220)  # Beige
BUTTON_COLOR = (169, 169, 169)
BUTTON_HOVER = (192, 192, 192)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)
PURPLE_DARK = (100, 0, 128)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)

# UI polish helpers
_font_cache = {}

def get_font(size: int, bold: bool = False):
    key = (size, bool(bold))
    f = _font_cache.get(key)
    if f is None:
        f = pygame.font.SysFont(None, size, bold=bold)
        _font_cache[key] = f
    return f

def draw_panel(rect: pygame.Rect, border_color, title: str | None = None, title_color=None):
    """Draw a modern panel with shadow + rounded corners."""
    # shadow
    shadow = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 120), (10, 10, rect.width, rect.height), border_radius=14)
    screen.blit(shadow, (rect.x - 10, rect.y - 10))

    # body
    body = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(body, (*MENU_BG, 245), (0, 0, rect.width, rect.height), border_radius=14)
    # subtle highlight band
    pygame.draw.rect(body, (255, 255, 255, 70), (0, 0, rect.width, 56), border_radius=14)
    # border
    pygame.draw.rect(body, (*border_color, 255), (0, 0, rect.width, rect.height), 4, border_radius=14)
    screen.blit(body, rect.topleft)

    if title:
        tf = get_font(48, bold=True)
        tcol = title_color if title_color is not None else border_color
        ts = tf.render(title, True, tcol)
        screen.blit(ts, (rect.x + 20, rect.y + 14))

def wrap_text_lines(font: pygame.font.Font, text: str, max_width: int) -> list[str]:
    """Simple word-wrap for UI labels."""
    s = str(text).replace("\n", " ").strip()
    if not s:
        return [""]
    words = s.split(" ")
    lines: list[str] = []
    cur = ""
    for w in words:
        if not w:
            continue
        test = w if not cur else (cur + " " + w)
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines if lines else [s]

def blit_wrapped(font: pygame.font.Font, text: str, color, x: int, y: int, max_width: int, line_gap: int = 4) -> int:
    """Draw wrapped text and return y after it."""
    for ln in wrap_text_lines(font, text, max_width):
        surf = font.render(ln, True, color)
        screen.blit(surf, (x, y))
        y += surf.get_height() + int(line_gap)
    return y

def draw_button(rect: pygame.Rect, fill, border, hover=False, radius=10):
    """Button with depth + hover glow."""
    # base
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 2, border_radius=radius)
    # shine
    hi = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(hi, (255, 255, 255, 38), (2, 2, rect.width - 4, rect.height // 2), border_radius=radius)
    screen.blit(hi, rect.topleft)
    if hover:
        glow = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*border, 70), (0, 0, rect.width + 10, rect.height + 10), border_radius=radius + 4)
        screen.blit(glow, (rect.x - 5, rect.y - 5))


def truncate_text(font: pygame.font.Font, text: str, max_width: int) -> str:
    """Truncate with ellipsis to fit within max_width pixels."""
    s = str(text)
    if font.size(s)[0] <= max_width:
        return s
    ell = "…"
    if font.size(ell)[0] > max_width:
        return ""
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi) // 2
        cand = s[:mid].rstrip() + ell
        if font.size(cand)[0] <= max_width:
            lo = mid + 1
        else:
            hi = mid
    return s[: max(0, lo - 1)].rstrip() + ell

# Add after other color definitions
SKIN_COLORS = [(255, 218, 185), (210, 180, 140), (169, 132, 103), (139, 69, 19)]
HAIR_COLORS = [(0, 0, 0), (139, 69, 19), (255, 215, 0), (211, 211, 211)]
CLOTHES_COLORS = [RED, BLUE, GREEN, PURPLE, ORANGE, PINK, CYAN, YELLOW]

# Shop and inventory items
BREAD_PRICE = 5
CROISSANT_PRICE = 8
CAKE_PRICE = 15

# Add these constants after the shop price definitions
XP_MULTIPLIER = 1.5  # XP gained is 1.5x the money spent
XP_PER_LEVEL = 300  # XP needed for each level (level 1 -> 2 starts at 300)

class ShopItem:
    def __init__(self, name, price, hunger_restore, item_type="food"):
        self.name = name
        self.price = price
        self.hunger_restore = hunger_restore
        self.item_type = item_type

# Player properties (move these outside the class)
player_x = 100
player_y = 400
player_width = 40
player_height = 60
player_speed = 5
player_jump = -15
player_velocity = 0
gravity = 0.8

# Movement feel (polish)
player_vx = 0.0
facing_dir = 1  # -1 left, +1 right
on_ground = False
was_on_ground = False
walk_phase = 0.0
COYOTE_FRAMES = 8          # small grace after leaving ground
JUMP_BUFFER_FRAMES = 8     # small grace before landing
coyote_timer = 0
jump_buffer_timer = 0
MOVE_ACCEL = 0.55
MOVE_FRICTION = 0.80
MOVE_AIR_ACCEL = 0.40
MOVE_AIR_FRICTION = 0.92


# Camera class
class Camera:
    def __init__(self):
        self.offset = 0
        
    def apply(self, x):
        return x - self.offset
    
    def update(self, target_x):
        # Keep player centered horizontally
        self.offset = target_x - WINDOW_WIDTH // 2

# Modify the Cloud class to preserve cloud positions
class Cloud:
    def __init__(self):
        # Create clouds in a wider area initially
        self.x = random.randint(-WINDOW_WIDTH * 2, WINDOW_WIDTH * 2)
        self.y = random.randint(50, 200)
        # Store original position to maintain cloud pattern
        self.original_x = self.x
        
    def draw(self, camera):
        screen_x = camera.apply(self.x)
        # Only draw if cloud is visible on screen
        if -100 < screen_x < WINDOW_WIDTH + 100:
            draw_cloud(screen_x, self.y)
            
        # Instead of removing clouds, we'll create a repeating pattern
        # If player moves too far in either direction, wrap the cloud around
        if screen_x < -WINDOW_WIDTH:
            self.x = self.x + WINDOW_WIDTH * 4
        elif screen_x > WINDOW_WIDTH * 2:
            self.x = self.x - WINDOW_WIDTH * 4

# Platform class
class Platform:
    def __init__(self):
        self.segments = []
        self.segment_width = WINDOW_WIDTH
        self.generate_initial_segments()
        
    def generate_initial_segments(self):
        # Create initial platform segments
        for i in range(-2, 3):  # Create 5 segments to start
            self.segments.append(pygame.Rect(
                i * self.segment_width, 500, 
                self.segment_width, 40
            ))

    def reset_for_window(self, center_x: float):
        """Rebuild platform segments using current WINDOW_WIDTH."""
        self.segment_width = WINDOW_WIDTH
        self.segments = []
        base = int(math.floor(float(center_x) / float(max(1, self.segment_width))))
        for i in range(base - 3, base + 4):
            self.segments.append(
                pygame.Rect(i * self.segment_width, 500, self.segment_width, 40)
            )
    
    def update(self, camera):
        # Generate new segments as needed
        rightmost = max(seg.x for seg in self.segments)
        leftmost = min(seg.x for seg in self.segments)
        
        # Add new segment on right if needed
        if camera.apply(rightmost) < WINDOW_WIDTH:
            self.segments.append(pygame.Rect(
                rightmost + self.segment_width, 500,
                self.segment_width, 40
            ))
            
        # Add new segment on left if needed
        if camera.apply(leftmost) > -self.segment_width:
            self.segments.append(pygame.Rect(
                leftmost - self.segment_width, 500,
                self.segment_width, 40
            ))
            
        # Remove segments that are too far away
        self.segments = [seg for seg in self.segments 
                        if -self.segment_width < camera.apply(seg.x) < WINDOW_WIDTH + self.segment_width]
    
    def draw(self, camera):
        for segment in self.segments:
            pygame.draw.rect(screen, GRAY, 
                           (camera.apply(segment.x), segment.y, 
                            segment.width, segment.height))
    
    def check_collision(self, x, y, width, height):
        for segment in self.segments:
            if (y + height >= segment.top and 
                y + height <= segment.top + 10 and  # Only check top collision
                x + width > segment.x and 
                x < segment.x + segment.width):
                return segment.top
        return None

# Stats
BASE_MAX_HEALTH = 100
MAX_HEALTH = BASE_MAX_HEALTH  # can increase via skills
health = BASE_MAX_HEALTH
BASE_MAX_HUNGER = 100
MAX_HUNGER = BASE_MAX_HUNGER  # can increase via skills
hunger = BASE_MAX_HUNGER
xp = 0
level = 1
max_xp = int(math.ceil(XP_PER_LEVEL * (1.5 ** (level - 1))))  # +50% XP required per level, rounded up
money = 300  # Add money variable
cheat_code_buffer = ""  # last typed letters for hidden codes

# Money -> XP (only when gaining money)
MONEY_XP_RATE = 1.0  # 1 XP per $ earned

def add_money(amount: int, grant_xp: bool = True):
    """Add money; optionally grant XP from earnings (e.g. bistro passive uses grant_xp=False)."""
    global money, xp
    if amount <= 0:
        return
    money += int(amount)
    if grant_xp:
        xp += int(math.ceil(int(amount) * MONEY_XP_RATE))
        check_level_up()

# Add after the stats section
HUNGER_DECREASE_RATE = 0.02  # How fast hunger decreases

# Shop and inventory
shop_items = {
    'Bread': ShopItem('Bread', BREAD_PRICE, 20),
    'Croissant': ShopItem('Croissant', CROISSANT_PRICE, 30),
    'Cake': ShopItem('Cake', CAKE_PRICE, 50)
}

# Supermarket ingredients (go in inventory; used for microwave recipes)
SUPERMARKET_ITEMS = {
    # Small hunger restore so they feel like "snacks"/raw ingredients
    "Cheese": ShopItem("Cheese", 6, 2, item_type="ingredient"),
    "Egg": ShopItem("Egg", 4, 1, item_type="ingredient"),
    "Rice": ShopItem("Rice", 5, 1, item_type="ingredient"),
    "Noodles": ShopItem("Noodles", 7, 2, item_type="ingredient"),
    "Veggies": ShopItem("Veggies", 6, 2, item_type="ingredient"),
    "Beef": ShopItem("Beef", 14, 2, item_type="ingredient"),
    "Seasoning": ShopItem("Seasoning", 3, 0, item_type="ingredient"),
    "Bottle of Water": ShopItem("Bottle of Water", 6, 2, item_type="drink"),
}
SUPERMARKET_ITEMS["Bottle of Water"].quick_drink = True
SUPERMARKET_ITEMS["Bottle of Water"].stamina_restore_drink = 60

# Microwave recipes: $5 fee + ingredients -> cooked food item
MICROWAVE_FEE = 5
MICROWAVE_RECIPES_BASE = [
    {
        "name": "Cheesy Rice",
        "ingredients": {"Rice": 1, "Cheese": 1},
        "result": ShopItem("Cheesy Rice", 0, 35, item_type="food"),
    },
    {
        "name": "Veggie Noodles",
        "ingredients": {"Noodles": 1, "Veggies": 1},
        "result": ShopItem("Veggie Noodles", 0, 40, item_type="food"),
    },
    {
        "name": "Egg Bowl",
        "ingredients": {"Egg": 2, "Rice": 1},
        "result": ShopItem("Egg Bowl", 0, 45, item_type="food"),
    },
]

MICROWAVE_RECIPES_CHEF = [
    {
        "name": "Loaded Noodles",
        "ingredients": {"Noodles": 1, "Cheese": 1, "Egg": 1},
        "result": ShopItem("Loaded Noodles", 0, 70, item_type="food"),
    },
    {
        "name": "Mega Veg Bowl",
        "ingredients": {"Rice": 1, "Veggies": 2, "Egg": 1},
        "result": ShopItem("Mega Veg Bowl", 0, 80, item_type="food"),
    },
]

STOVE_FEE = 10
MICROWAVE_COOK_FRAMES = 180  # 3s @ 60 FPS
STOVE_COOK_FRAMES = 300  # 5s
GRILL_FEE = 3
GRILL_COOK_FRAMES = STOVE_COOK_FRAMES + 180  # 3s longer than stove
STOVE_RECIPES = [
    {
        "name": "Chef's Feast",
        "ingredients": {"Rice": 2, "Veggies": 2, "Cheese": 1, "Egg": 1},
        "result": ShopItem("Chef's Feast", 0, 100, item_type="food"),
    },
    {
        "name": "Stove Noodle Tower",
        "ingredients": {"Noodles": 2, "Cheese": 1, "Egg": 2},
        "result": ShopItem("Stove Noodle Tower", 0, 90, item_type="food"),
    },
    {
        "name": "Steak Plate",
        "ingredients": {"Beef": 1, "Seasoning": 1},
        "result": ShopItem("Steak Plate", 0, 80, item_type="food"),
    },
    {
        "name": "Pepper Steak",
        "ingredients": {"Beef": 1, "Seasoning": 2},
        "result": ShopItem("Pepper Steak", 0, 95, item_type="food"),
    },
]
# Grill: low fee, longer cook; menu mixes "miss" plates and premium cuts at once.
GRILL_RECIPES = [
    {
        "name": "Charred Scraps",
        "ingredients": {"Beef": 1},
        "result": ShopItem("Charred Scraps", 0, 30, item_type="food"),
    },
    {
        "name": "Dry Patty",
        "ingredients": {"Beef": 1, "Rice": 1},
        "result": ShopItem("Dry Patty", 0, 42, item_type="food"),
    },
    {
        "name": "Smokehouse Burger",
        "ingredients": {"Beef": 1, "Veggies": 1},
        "result": ShopItem("Smokehouse Burger", 0, 62, item_type="food"),
    },
    {
        "name": "Backyard Ribeye",
        "ingredients": {"Beef": 1, "Seasoning": 1},
        "result": ShopItem("Backyard Ribeye", 0, 92, item_type="food"),
    },
    {
        "name": "Crown Tomahawk",
        "ingredients": {"Beef": 2, "Seasoning": 1},
        "result": ShopItem("Crown Tomahawk", 0, 115, item_type="food"),
    },
]
clothing_items = {
    'Red Shirt': {'color': RED, 'price': 0, 'owned': True, 'equipped': True},
    'Blue Shirt': {'color': BLUE, 'price': 50, 'owned': False, 'equipped': False},
    'Green Shirt': {'color': GREEN, 'price': 50, 'owned': False, 'equipped': False},
    'Purple Shirt': {'color': PURPLE, 'price': 50, 'owned': False, 'equipped': False},
    'Orange Shirt': {'color': ORANGE, 'price': 50, 'owned': False, 'equipped': False},
    'Pink Shirt': {'color': PINK, 'price': 50, 'owned': False, 'equipped': False},
    'Cyan Shirt': {'color': CYAN, 'price': 50, 'owned': False, 'equipped': False},
    'Yellow Shirt': {'color': YELLOW, 'price': 50, 'owned': False, 'equipped': False}
}
MAX_INVENTORY = 5  # hotbar slots (Minecraft-style stacks below)
MAX_STACK_SIZE = 10
inventory = [None] * MAX_INVENTORY  # each entry: None or {"item": ShopItem, "count": int}


def player_net_worth() -> int:
    """Cash plus inventory at listed item prices (includes all income paths that update `money`)."""
    inv_val = 0
    for slot in inventory:
        if not slot:
            continue
        it = slot["item"]
        pr = int(getattr(it, "price", 0) or 0)
        inv_val += pr * max(1, int(slot.get("count", 1)))
    return int(money) + inv_val


selected_slot = 0
eating_timer = 0
is_eating = False

# Initialize shop state variables
shop_open = False  # Track if shop menu is open
clothing_shop_open = False  # Track if clothing shop menu is open
arcade_shop_open = False  # Track if arcade shop menu is open
mission_center_open = False  # Track if mission center menu is open
supermarket_open = False  # Track if supermarket menu is open
seafood_market_open = False  # Sell fish from Sun Reef
# Seafood daily offer (increases sale price by +50% for one random fish per in-game day)
seafood_daily_offer_fish = None  # fish name str
seafood_daily_offer_day = -1  # day index last rolled

# Utility cart (appears starting Day 10, never disappears)
utility_cart_open = False
fish_upgrade_reel_zone = 0       # widens blue zone
fish_upgrade_hook_window = 0     # longer hookset window
fish_upgrade_reel_power = 0      # faster reel progress
fish_upgrade_luck = 0            # better rare odds
cheat_panel_open = False

# Black Market (opens every 3 in-game days)
black_market_open = False
black_market_day = -1
black_market_offers = []  # list of dict offers (rolled on open days)
clothing_coupon_uses = 0  # next N clothing purchases are 50% off
hotel_lobby_open = False  # Track if hotel lobby menu is open
cafe_open = False  # Track if cafe menu is open
in_hotel_room = False  # In-room scene flag
sleep_cutscene_timer = 0
microwave_open = False
hotel_notice_timer = 0
hotel_notice_text = ""
room_player_x = 200
ROOM_PLAYER_Y = 430
ROOM_PLAYER_SPEED = 4
stove_open = False
grill_open = False
hotel_room_owned = False

# --- Sun Reef ferry & fishing island ---
FERRY_FARE = 12
FERRY_CROSSING_FRAMES = 140
on_fishing_island = False
ferry_anim_timer = 0
ferry_anim_to_island = True
island_player_x = 220.0
ISLAND_FEET_Y = 458  # beach stand line (screen coords)
island_ambient_frame = 0
# Fishing minigame (only active on island)
fish_phase = "idle"  # idle | cast | wait | hookset | reel | win | lose
fish_cast_power = 0.0
fish_wait_until_tick = 0
fish_hook_deadline_tick = 0
fish_reel_progress = 0.0
fish_pos = 0.5
fish_vel = 0.0
fish_player_center = 0.5
fish_struggle_phase = 0.0
fish_pending_roll = None  # (name, price, hunger) or None
fish_splash = []  # (x, y, vy, life) particles

# Player house + Coffee Guy mission flag (set when drinking coffee during an active coffee buff)
mission_coffee_guy_done = False
house_owned = False
house_lobby_open = False
in_house_room = False
house_expansion_level = 0  # 0 hotel-sized, 1 wider + camera scroll, 2 second floor + ladder
house_player_x = 520.0
house_player_floor = 0
house_cam_offset = 0.0
house_buildings = []  # {"kind": str, "cx": float, "floor": int}
house_build_menu_open = False
house_build_scroll = 0
house_place_pick = None  # kind str while placing from catalog
house_notice_timer = 0
house_notice_text = ""
house_sink_ready_ms = 0  # pygame time.get_ticks() when sink may dispense again


def notify_coffee_guy_mission():
    global mission_coffee_guy_done
    mission_coffee_guy_done = True


# Player-owned bistro (side of town; repair + stock with cooked food only)
restaurant_open = False
restaurant_repaired = False
restaurant_business_open = True  # when False: no customers, chefs idle, runners won't supply (repaired bistro only)
restaurant_stock_units = []  # list of {"name": str, "cost": int} per plate (FIFO via random pop on sale)
RESTAURANT_REPAIR_COST = 550
restaurant_menu_scroll = 0
restaurant_menu_tab = "main"  # "main" | "upgrades"
restaurant_upgrades_scroll = 0
bistro_chef_dropdown_chef_idx = None  # which chef's dish dropdown is open (Upgrades tab)
# Lifetime bistro bookkeeping (sales vs. repair, payroll, upgrades, runner supply buys)
bistro_stats_earned = 0
bistro_stats_spent = 0
# Passive bistro income: only while guests are inside; base $/min at tier 0 (×1.25/tier), then ×(1 + 0.05 per patron)
restaurant_passive_income_acc = 0.0
RESTAURANT_PASSIVE_DOLLARS_PER_MIN = 40
RESTAURANT_PASSIVE_TIER_FACTOR = 1.25
RESTAURANT_PASSIVE_BONUS_PER_PATRON = 0.05  # +5% passive rate per customer seated inside

# Building expansion (facade tier 0–3): capacity, pricing, world footprint
restaurant_tier = 0
restaurant_patrons_inside = 0
RESTAURANT_BASE_CAPACITY = 10
RESTAURANT_EXTRA_SEATS_PER_TIER = 4
# Wandering NPC door-check: tier 1+ uses fixed entry rates (tier 0 uses base + ad)
RESTAURANT_ENTRY_BY_TIER = (0.35, 0.60, 0.80)  # tier 1, 2, 3
RESTAURANT_TIER_COSTS = (500, 1000, 3000)
RESTAURANT_PRICE_BONUS_PER_TIER = 0.06
RESTAURANT_GEOM_BASE_W = 155
RESTAURANT_GEOM_BASE_H = 132
RESTAURANT_GEOM_TOP_Y = 366

# --- Bistro automation (chefs + restockers) ---
BISTRO_UPGRADE_COST_ADV_AD = 450
BISTRO_UPGRADE_COST_BETTER_QUALITY = 580
BISTRO_UPGRADE_COST_DELICIOUS_SMELL = 400
BISTRO_UPGRADE_COST_AUTO_SEASON = 520
# Dedicated patrons (Better Quality): target rates requested.
# - No upgrade: ~20 patrons per 2.5 minutes => ~1 every 7.5s
# - With upgrade: ~23 patrons per 2 minutes => ~1 every 5.22s
BISTRO_SEEKER_SPAWN_MIN_FRAMES = int(60 * 4.8)   # ~4.8s
BISTRO_SEEKER_SPAWN_MAX_FRAMES = int(60 * 7.8)   # ~7.8s
BISTRO_SEEKER_MAX_CONCURRENT = 14

bistro_upgrade_advanced_advertising = False
bistro_upgrade_better_quality = False
bistro_upgrade_delicious_smell = False
bistro_upgrade_auto_seasoning = False
bistro_seeker_spawn_timer = random.randint(BISTRO_SEEKER_SPAWN_MIN_FRAMES, BISTRO_SEEKER_SPAWN_MAX_FRAMES)

BISTRO_PANTRY_MAX = 15
CHEF_MAX = 3
RESTOCKER_MAX = 2
CHEF_HIRE_COST = 280
RESTOCKER_HIRE_COST = 340
CHEF_XP_PER_PLATE = 28
RESTOCKER_XP_PER_RUN = 11  # was 22 — runners level up more slowly per supply trip
CHEF_LEVEL_XP = [0, 90, 220, 400, 620]  # min total XP to be at level 1..5 (level = bisect)
RESTOCKER_LEVEL_XP = [0, 80, 200, 360, 560]

bistro_pantry = {}  # ingredient name -> count (sum capped at BISTRO_PANTRY_MAX)
bistro_chefs = []  # {recipe_idx, xp, level, timer}
bistro_restockers = []  # {xp, level} per hired slot (parallel to restocker_workers)
restocker_workers = []  # RestockerWorker instances
ALL_BISTRO_RECIPES = []  # filled after recipe lists defined
# Parallel to ALL_BISTRO_RECIPES: minimum chef level (1–5) to assign this dish
BISTRO_RECIPE_MIN_LEVEL = []


def _rebuild_all_bistro_recipes():
    global ALL_BISTRO_RECIPES, BISTRO_RECIPE_MIN_LEVEL
    ALL_BISTRO_RECIPES = []
    for r in MICROWAVE_RECIPES_BASE + MICROWAVE_RECIPES_CHEF:
        ALL_BISTRO_RECIPES.append((r, "microwave"))
    for r in STOVE_RECIPES:
        ALL_BISTRO_RECIPES.append((r, "stove"))
    n_micro = len(MICROWAVE_RECIPES_BASE) + len(MICROWAVE_RECIPES_CHEF)
    BISTRO_RECIPE_MIN_LEVEL = []
    for i in range(len(ALL_BISTRO_RECIPES)):
        if i < 2:
            BISTRO_RECIPE_MIN_LEVEL.append(1)
        elif i == 2:
            BISTRO_RECIPE_MIN_LEVEL.append(2)
        elif i < n_micro:
            BISTRO_RECIPE_MIN_LEVEL.append(3)
        elif i == n_micro:
            BISTRO_RECIPE_MIN_LEVEL.append(4)
        else:
            BISTRO_RECIPE_MIN_LEVEL.append(5)


_rebuild_all_bistro_recipes()


def chef_unlocked_recipe_indices(level: int):
    return [i for i, ml in enumerate(BISTRO_RECIPE_MIN_LEVEL) if ml <= level]


def clamp_chef_recipe_to_unlocks(chef):
    opts = chef_unlocked_recipe_indices(chef.get("level", 1))
    if not opts:
        return
    if chef.get("recipe_idx", 0) not in opts:
        chef["recipe_idx"] = opts[0]


def restaurant_entry_probability():
    """Chance per frame-check that a wandering NPC near the door enters the bistro."""
    if restaurant_tier >= 1:
        return RESTAURANT_ENTRY_BY_TIER[min(restaurant_tier, 3) - 1]
    p = 0.14
    if bistro_upgrade_advanced_advertising:
        p = min(0.52, p + 0.28)
    return p


def restaurant_max_capacity() -> int:
    return RESTAURANT_BASE_CAPACITY + RESTAURANT_EXTRA_SEATS_PER_TIER * restaurant_tier


def restaurant_sale_price_multiplier() -> float:
    return 1.0 + RESTAURANT_PRICE_BONUS_PER_TIER * restaurant_tier


def restaurant_has_seating_available() -> bool:
    return restaurant_patrons_inside < restaurant_max_capacity()


def restaurant_register_patron_arrival():
    global restaurant_patrons_inside
    restaurant_patrons_inside += 1


def restaurant_register_patron_departure():
    global restaurant_patrons_inside
    restaurant_patrons_inside = max(0, restaurant_patrons_inside - 1)


def sync_restaurant_building_geometry():
    tw = restaurant_tier
    restaurant.width = RESTAURANT_GEOM_BASE_W + tw * 30
    restaurant.height = RESTAURANT_GEOM_BASE_H + tw * 14
    bottom = RESTAURANT_GEOM_TOP_Y + RESTAURANT_GEOM_BASE_H
    restaurant.y = bottom - restaurant.height


def restaurant_order_plate_count(stock_len: int) -> int:
    """How many plates one customer buys (1–3), capped by stock."""
    if stock_len <= 0:
        return 0
    cap = min(3, stock_len)
    if cap == 1:
        return 1
    if not bistro_upgrade_delicious_smell:
        return random.randint(1, cap)
    r = random.random()
    if r < 0.12:
        n = 1
    elif r < 0.50:
        n = 2
    else:
        n = 3
    return min(n, cap)


def pantry_total() -> int:
    return sum(bistro_pantry.values())


def chef_level_from_xp(xp: int, table) -> int:
    lv = 1
    for i in range(1, 5):
        if xp >= table[i]:
            lv = i + 1
    return min(5, lv)


def chef_cook_frames(level: int, source: str) -> int:
    base = MICROWAVE_COOK_FRAMES if source == "microwave" else STOVE_COOK_FRAMES
    # Each level above 1: 10% faster (duration * 0.9^(level-1))
    mult = 0.9 ** max(0, level - 1)
    return max(45, int(base * mult))


def ingredients_union_for_chefs():
    need = set()
    for c in bistro_chefs:
        recipe, _ = ALL_BISTRO_RECIPES[c["recipe_idx"]]
        need.update(recipe["ingredients"].keys())
    # If auto-seasoning is enabled, keep seasoning stocked even for recipes
    # that don't strictly require it (chefs will consume it to boost value).
    if bistro_upgrade_auto_seasoning:
        need.add("Seasoning")
    return need


def restock_trigger_needed() -> bool:
    if not bistro_restockers:
        return False
    need = ingredients_union_for_chefs()
    if not need:
        return False
    for ing in need:
        if bistro_pantry.get(ing, 0) < 5:
            return True
    return False


def compute_restock_delivery():
    """Return (list[(ingredient, qty)], total_cost) or (None, 0). Max 2 ingredient types, 5 each, respect pantry cap."""
    space = BISTRO_PANTRY_MAX - pantry_total()
    if space <= 0:
        return None, 0
    candidates = []
    for ing in sorted(ingredients_union_for_chefs(), key=lambda x: bistro_pantry.get(x, 0)):
        cur = bistro_pantry.get(ing, 0)
        if cur < 5:
            deficit = min(5, 5 - cur)
            candidates.append((ing, deficit))
    if not candidates:
        return None, 0
    order = []
    cost = 0
    for ing, want in candidates[:2]:
        if space <= 0:
            break
        q = min(want, 5, space)
        if q <= 0:
            continue
        if ing not in SUPERMARKET_ITEMS:
            continue
        price = get_effective_price(SUPERMARKET_ITEMS[ing].price)
        order.append((ing, q))
        cost += price * q
        space -= q
    if not order:
        return None, 0
    return order, cost


def try_consume_pantry_for_recipe(recipe: dict) -> bool:
    global bistro_pantry
    for ing, q in recipe["ingredients"].items():
        if bistro_pantry.get(ing, 0) < q:
            return False
    for ing, q in recipe["ingredients"].items():
        bistro_pantry[ing] = bistro_pantry.get(ing, 0) - q
        if bistro_pantry[ing] <= 0:
            del bistro_pantry[ing]
    return True


def add_to_bistro_pantry(name: str, qty: int) -> int:
    """Add up to qty; returns amount actually added (respects cap)."""
    global bistro_pantry
    added = 0
    for _ in range(qty):
        if pantry_total() >= BISTRO_PANTRY_MAX:
            break
        bistro_pantry[name] = bistro_pantry.get(name, 0) + 1
        added += 1
    return added


def tick_restaurant_passive_income():
    """Passive drip only with patrons inside; rate scales tier + (1 + bonus per patron). No XP."""
    global bistro_stats_earned, restaurant_passive_income_acc
    if not restaurant_repaired or not restaurant_business_open:
        return
    if restaurant_patrons_inside <= 0:
        return
    base = RESTAURANT_PASSIVE_DOLLARS_PER_MIN * (RESTAURANT_PASSIVE_TIER_FACTOR ** restaurant_tier)
    patron_mult = 1.0 + RESTAURANT_PASSIVE_BONUS_PER_PATRON * float(restaurant_patrons_inside)
    per_min = base * patron_mult
    restaurant_passive_income_acc += per_min / 3600.0
    if restaurant_passive_income_acc >= 1.0:
        payout = int(restaurant_passive_income_acc)
        restaurant_passive_income_acc -= payout
        add_money(payout, grant_xp=False)
        bistro_stats_earned += payout


def update_bistro_chefs():
    global bistro_chefs, restaurant_stock_units
    if not restaurant_repaired or not restaurant_business_open or not bistro_chefs:
        return
    for c in bistro_chefs:
        c["level"] = chef_level_from_xp(c["xp"], CHEF_LEVEL_XP)
        clamp_chef_recipe_to_unlocks(c)
        recipe, source = ALL_BISTRO_RECIPES[c["recipe_idx"]]
        if c.get("timer", 0) > 0:
            c["timer"] -= 1
            if c["timer"] == 0:
                dish = build_cooked_result(recipe, source)
                cst = int(getattr(dish, "cooked_cost_basis", 0) or MICROWAVE_FEE)
                # Auto-seasoning upgrade: consume pantry seasoning to boost dish value.
                if bistro_upgrade_auto_seasoning and bistro_pantry.get("Seasoning", 0) > 0:
                    bistro_pantry["Seasoning"] = int(bistro_pantry.get("Seasoning", 0)) - 1
                    if bistro_pantry.get("Seasoning", 0) <= 0:
                        bistro_pantry.pop("Seasoning", None)
                    cst = int(math.ceil(cst * 1.5))
                restaurant_stock_units.append({"name": dish.name, "cost": max(1, cst)})
                c["xp"] += CHEF_XP_PER_PLATE
                c["level"] = chef_level_from_xp(c["xp"], CHEF_LEVEL_XP)
                clamp_chef_recipe_to_unlocks(c)
            else:
                continue
        if try_consume_pantry_for_recipe(recipe):
            c["timer"] = chef_cook_frames(c["level"], source)


class RestockerWorker:
    """NPC runner: bistro -> market -> bistro with pantry goods."""

    BUYING_FRAMES = 72
    # Bistro uniform (awning red + white trim — matches Riverside Bistro)
    RESTAURANT_SHIRT = (220, 82, 72)
    RESTAURANT_SHIRT_TRIM = (245, 245, 245)

    def __init__(self, slot_index: int):
        self.slot_index = slot_index
        self.original_x = shop_entrance_cx(restaurant)
        self.y = 440
        self.width = 30
        self.height = 50
        self.speed = 5.5
        self.direction = 1
        self.state = "idle"
        self.timer = 0
        self.pending = []
        self.cost = 0
        self.skin_color = random.choice(SKIN_COLORS)
        self.hair_color = random.choice(HAIR_COLORS)
        self.current_dialog = ""
        self.dialog_timer = 0
        self.show_dialog = False
        self.can_talk = False

    def market_x(self):
        return shop_entrance_cx(supermarket)

    def bistro_x(self):
        return shop_entrance_cx(restaurant)

    def check_player_collision(self, player_x, player_width):
        return abs(self.original_x - player_x) < (player_width + self.width)

    def start_custom_dialog(self, text: str):
        self.current_dialog = text
        self.show_dialog = True
        self.dialog_timer = 180

    def update_dialog(self):
        if self.show_dialog:
            self.dialog_timer -= 1
            if self.dialog_timer <= 0:
                self.show_dialog = False

    def draw_dialog(self, screen, camera):
        if self.show_dialog:
            screen_x = camera.apply(self.original_x)
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.current_dialog, True, WHITE)
            text_rect = text.get_rect()
            padding = 20
            bubble_width = text_rect.width + padding
            bubble_height = text_rect.height + padding
            dialog_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
            pygame.draw.rect(
                dialog_surface, (0, 0, 0, 128), (0, 0, bubble_width, bubble_height), border_radius=10
            )
            text_rect.center = (bubble_width // 2, bubble_height // 2)
            dialog_surface.blit(text, text_rect)
            screen.blit(
                dialog_surface,
                (screen_x + self.width // 2 - bubble_width // 2, self.y - bubble_height - 20),
            )
            pointer_points = [
                (screen_x + self.width // 2 - 10, self.y - 20),
                (screen_x + self.width // 2 + 10, self.y - 20),
                (screen_x + self.width // 2, self.y - 10),
            ]
            pygame.draw.polygon(screen, (0, 0, 0, 128), pointer_points)

    def update(self):
        global money, money_spent, bistro_restockers, bistro_stats_spent
        if not restaurant_repaired or self.slot_index >= len(bistro_restockers):
            return
        # When closed, don't start new supply runs; finish any trip already in progress.
        if self.state == "idle" and not restaurant_business_open:
            return
        self.update_dialog()
        mx = self.market_x()
        bx = self.bistro_x()
        rs = bistro_restockers[self.slot_index]

        def gain_restock_xp():
            rs["xp"] = rs.get("xp", 0) + RESTOCKER_XP_PER_RUN
            rs["level"] = chef_level_from_xp(rs["xp"], RESTOCKER_LEVEL_XP)

        if self.state == "idle":
            if not restock_trigger_needed():
                return
            if any(w.state != "idle" for w in restocker_workers):
                return
            pack, cost = compute_restock_delivery()
            if not pack or cost <= 0:
                return
            if money < cost:
                return
            self.pending = pack
            self.cost = cost
            self.state = "to_market"
            self.direction = 1 if mx > self.original_x else -1
            return

        if self.state == "to_market":
            if abs(self.original_x - mx) < 14:
                self.state = "buying"
                self.timer = RestockerWorker.BUYING_FRAMES
            else:
                self.original_x += self.speed * self.direction
            return

        if self.state == "buying":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "to_bistro"
                self.direction = 1 if bx > self.original_x else -1
            return

        if self.state == "to_bistro":
            if abs(self.original_x - bx) < 14:
                money -= self.cost
                money_spent += self.cost
                bistro_stats_spent += self.cost
                for name, q in self.pending:
                    add_to_bistro_pantry(name, q)
                gain_restock_xp()
                show_success_toast(f"Supply run #{self.slot_index + 1}: pantry restocked (−${self.cost}).")
                self.pending = []
                self.cost = 0
                self.state = "idle"
                self.original_x = bx
            else:
                self.original_x += self.speed * self.direction
            return

    def draw(self, camera):
        screen_x = camera.apply(self.original_x)
        if not (-self.width < screen_x < WINDOW_WIDTH + self.width):
            return
        y0 = self.y
        y_offset = 0
        # Same silhouette as NPC.draw, bistro uniform shirt
        pygame.draw.rect(
            screen,
            RestockerWorker.RESTAURANT_SHIRT,
            (screen_x, y0 + 20 + y_offset, self.width, self.height - 20),
        )
        pygame.draw.rect(
            screen,
            RestockerWorker.RESTAURANT_SHIRT_TRIM,
            (screen_x + 2, y0 + 22 + y_offset, self.width - 4, 7),
            border_radius=2,
        )
        pygame.draw.line(
            screen,
            (180, 60, 55),
            (screen_x + 2, y0 + 36 + y_offset),
            (screen_x + self.width - 2, y0 + 36 + y_offset),
            1,
        )
        pygame.draw.circle(
            screen, self.skin_color, (screen_x + self.width // 2, y0 + 15 + y_offset), 12
        )
        pygame.draw.arc(
            screen,
            self.hair_color,
            (screen_x + self.width // 2 - 12, y0 + y_offset, 24, 24),
            0,
            3.14,
            3,
        )
        eye_offset = 3 if self.direction > 0 else -3
        pygame.draw.circle(
            screen,
            BLACK,
            (screen_x + self.width // 2 + eye_offset, y0 + 13 + y_offset),
            2,
        )

        if self.can_talk:
            prompt_font = pygame.font.SysFont(None, 20)
            prompt_text = prompt_font.render("Press T to talk", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(screen_x + self.width // 2, y0 - 30))
            pygame.draw.rect(screen, BLACK, prompt_rect.inflate(20, 10))
            screen.blit(prompt_text, prompt_rect)

        self.draw_dialog(screen, camera)


def sync_restocker_workers():
    """Ensure worker objects match hire count."""
    global restocker_workers
    while len(restocker_workers) < len(bistro_restockers):
        restocker_workers.append(RestockerWorker(len(restocker_workers)))
    while len(restocker_workers) > len(bistro_restockers):
        restocker_workers.pop()


# Cooking progress (time-based)
cooking_in_progress = False
cooking_timer = 0
cooking_timer_max = 0
cooking_pending_item = None  # ShopItem to add when done
cooking_pending_source = ""  # "microwave" | "stove" | "grill"
cooking_cost_basis = 0  # cost used for selling profit calc

def clone_item(item: ShopItem) -> ShopItem:
    n = ShopItem(item.name, item.price, item.hunger_restore, item.item_type)
    if getattr(item, "cooked_by_player", False):
        n.cooked_by_player = True
        n.cooked_cost_basis = int(getattr(item, "cooked_cost_basis", 0) or 0)
    if getattr(item, "coffee_source", False):
        n.coffee_source = True
        n.coffee_mult = float(getattr(item, "coffee_mult", 1.0))
        n.coffee_duration_ms = int(getattr(item, "coffee_duration_ms", 0))
    if getattr(item, "max_carry_one", False):
        n.max_carry_one = True
    if getattr(item, "quick_drink", False):
        n.quick_drink = True
    if getattr(item, "stamina_restore_drink", None) is not None:
        n.stamina_restore_drink = int(getattr(item, "stamina_restore_drink", 0))
    if getattr(item, "seasonable", False):
        n.seasonable = True
        n.seasoned = bool(getattr(item, "seasoned", False))
    if getattr(item, "caught_fish", False):
        n.caught_fish = True
    return n


def cooking_fee_for_source(source: str) -> int:
    if source == "microwave":
        return MICROWAVE_FEE
    if source == "grill":
        return GRILL_FEE
    return STOVE_FEE


def compute_recipe_cost_basis(recipe: dict, source: str) -> int:
    fee = cooking_fee_for_source(source)
    basis = fee
    for name, qty in recipe["ingredients"].items():
        if name in SUPERMARKET_ITEMS:
            basis += get_effective_price(SUPERMARKET_ITEMS[name].price) * int(qty)
    return int(basis)


def build_cooked_result(recipe: dict, source: str) -> ShopItem:
    basis = compute_recipe_cost_basis(recipe, source)
    result = clone_item(recipe["result"])
    result.cooked_by_player = True
    result.cooked_cost_basis = basis
    # Seasoner can buff cooked meals once.
    result.seasonable = True
    result.seasoned = False
    return result


def items_stackable(a: ShopItem, b: ShopItem) -> bool:
    if a.name != b.name or a.item_type != b.item_type:
        return False
    if getattr(a, "cooked_by_player", False) != getattr(b, "cooked_by_player", False):
        return False
    if getattr(a, "cooked_by_player", False):
        if int(getattr(a, "cooked_cost_basis", 0) or 0) != int(getattr(b, "cooked_cost_basis", 0) or 0):
            return False
    ca = getattr(a, "coffee_source", False)
    cb = getattr(b, "coffee_source", False)
    if ca or cb:
        if not (ca and cb):
            return False
        if getattr(a, "coffee_mult", None) != getattr(b, "coffee_mult", None):
            return False
        if getattr(a, "coffee_duration_ms", None) != getattr(b, "coffee_duration_ms", None):
            return False
    if getattr(a, "max_carry_one", False) or getattr(b, "max_carry_one", False):
        return False
    return True


def inventory_can_accept(item: ShopItem) -> bool:
    if getattr(item, "max_carry_one", False):
        for i in range(MAX_INVENTORY):
            slot = inventory[i]
            if slot and slot["item"].name == item.name:
                return False
    for i in range(MAX_INVENTORY):
        slot = inventory[i]
        if slot is None:
            return True
        if items_stackable(slot["item"], item) and slot["count"] < MAX_STACK_SIZE:
            return True
    return False


def try_add_inventory(item: ShopItem) -> bool:
    global inventory
    for i in range(MAX_INVENTORY):
        slot = inventory[i]
        if slot is None:
            continue
        if items_stackable(slot["item"], item) and slot["count"] < MAX_STACK_SIZE:
            slot["count"] += 1
            return True
    for i in range(MAX_INVENTORY):
        if inventory[i] is None:
            inventory[i] = {"item": clone_item(item), "count": 1}
            return True
    return False


def remove_one_from_slot(slot_idx: int):
    """Remove one item from stack at slot; clear slot if empty. Returns ShopItem template or None."""
    global inventory
    if slot_idx < 0 or slot_idx >= MAX_INVENTORY:
        return None
    slot = inventory[slot_idx]
    if slot is None:
        return None
    it = slot["item"]
    slot["count"] -= 1
    if slot["count"] <= 0:
        inventory[slot_idx] = None
    return it


def start_cooking(recipe: dict, source: str):
    """Start a timed cooking action; deduct fee + ingredients up front."""
    global money, cooking_in_progress, cooking_timer, cooking_timer_max
    global cooking_pending_item, cooking_pending_source, cooking_cost_basis

    fee = cooking_fee_for_source(source)
    if source == "microwave":
        duration = MICROWAVE_COOK_FRAMES
    elif source == "grill":
        duration = GRILL_COOK_FRAMES
    else:
        duration = STOVE_COOK_FRAMES

    basis = compute_recipe_cost_basis(recipe, source)

    if money < fee:
        show_failure_toast("Not enough money for the cooking fee.")
        return False

    money -= fee
    consume_ingredients(recipe["ingredients"])

    result = build_cooked_result(recipe, source)

    cooking_in_progress = True
    cooking_timer_max = duration
    cooking_timer = duration
    cooking_pending_item = result
    cooking_pending_source = source
    cooking_cost_basis = basis
    return True

def draw_cooking_progress():
    if not cooking_in_progress or cooking_timer_max <= 0:
        return
    progress = 1.0 - (cooking_timer / cooking_timer_max)
    bar_w = 260
    bar_h = 14
    x = (WINDOW_WIDTH - bar_w) // 2
    y = 42
    pygame.draw.rect(screen, BLACK, (x - 2, y - 2, bar_w + 4, bar_h + 4))
    pygame.draw.rect(screen, WHITE, (x, y, bar_w, bar_h))
    pygame.draw.rect(screen, GREEN, (x, y, int(bar_w * progress), bar_h))
    label = pygame.font.SysFont(None, 24).render("Cooking...", True, WHITE)
    screen.blit(label, (x, y - 24))

def time_of_day():
    return current_time / DAY_LENGTH

def can_sleep_now():
    # Allow sleep during sunset + night
    t = time_of_day()
    return (t >= 0.65) or (t < 0.25)

# Add to global variables
money_spent = 0  # Track total money spent for achievements

# Modify the draw_player function to use equipped color
def draw_player(x, y):
    # Get equipped color
    equipped_color = RED  # Default red
    for item_data in clothing_items.values():
        if item_data['equipped']:
            equipped_color = item_data['color']
            break

    # No walk animation (no bob, no limbs)
    sx = int(x)
    sy = int(y)

    # Shadow
    pygame.draw.ellipse(screen, (0, 0, 0, 90), (sx + 6, sy + player_height - 6, player_width - 12, 10))

    # Head (skin colored circle)
    pygame.draw.circle(screen, SKIN_COLOR, (sx + player_width // 2, sy + 15), 15)
    # Body
    body_rect = pygame.Rect(sx + 6, sy + 24, player_width - 12, player_height - 26)
    pygame.draw.rect(screen, equipped_color, body_rect, border_radius=6)
    # No limbs (clean silhouette)

# Modify the draw_status_bars function
def draw_status_bars():
    # Health bar (red)
    pygame.draw.rect(screen, BLACK, (20, 20, 204, 24))
    health_fill = (health / MAX_HEALTH) * 200
    pygame.draw.rect(screen, RED, (22, 22, health_fill, 20))
    health_text = pygame.font.SysFont(None, 24).render(f"Health: {int(health)}/{int(MAX_HEALTH)}", True, WHITE)
    screen.blit(health_text, (230, 22))

    # Hunger bar (green)
    pygame.draw.rect(screen, BLACK, (20, 50, 204, 24))
    hunger_fill = (hunger / MAX_HUNGER) * 200
    pygame.draw.rect(screen, GREEN, (22, 52, hunger_fill, 20))
    hunger_text = pygame.font.SysFont(None, 24).render(f"Hunger: {int(hunger)}/{int(MAX_HUNGER)}", True, WHITE)
    screen.blit(hunger_text, (230, 52))

    # XP bar (blue) with level
    pygame.draw.rect(screen, BLACK, (20, 80, 304, 14))
    pygame.draw.rect(screen, BLUE, (22, 82, (xp / max_xp) * 300, 10))
    xp_font = pygame.font.SysFont(None, 20)
    xp_text = xp_font.render(f"Level {level} - XP: {xp}/{max_xp}", True, WHITE)
    # Keep label on a clear row below the bar so it never crosses the blue fill
    screen.blit(xp_text, (24, 96))

    # Time + weather — below XP text, above stamina bar (see draw_stamina_bar y)
    time_font = pygame.font.SysFont(None, 18)
    tod = current_time / DAY_LENGTH
    if tod < 0.25:
        tod_label = "Sunrise"
    elif tod < 0.5:
        tod_label = "Day"
    elif tod < 0.75:
        tod_label = "Sunset"
    else:
        tod_label = "Night"
    weather_label = current_weather.capitalize()
    mini = time_font.render(f"{tod_label}  |  {weather_label}", True, WHITE)
    screen.blit(mini, (24, 118))

    # Day counter (place on the right to avoid stamina bar overlap)
    day_s = time_font.render(f"Day {int(day_index) + 1}", True, (235, 245, 255))
    day_r = day_s.get_rect()
    day_r.topright = (WINDOW_WIDTH - 20, 72)
    sh = time_font.render(f"Day {int(day_index) + 1}", True, BLACK)
    sh_r = sh.get_rect()
    sh_r.topright = (day_r.right + 1, day_r.top + 1)
    screen.blit(sh, sh_r)
    screen.blit(day_s, day_r)
    
    # Money counter (yellow text with $ symbol)
    money_font = pygame.font.SysFont(None, 32)
    money_text = money_font.render(f"$ {money}", True, SUN_YELLOW)
    money_rect = money_text.get_rect()
    money_rect.topright = (WINDOW_WIDTH - 20, 20)  # Position in top-right corner
    
    # Add slight shadow effect for better visibility
    shadow_text = money_font.render(f"$ {money}", True, BLACK)
    screen.blit(shadow_text, (money_rect.x + 2, money_rect.y + 2))
    screen.blit(money_text, money_rect)
    nw = player_net_worth()
    nw_font = pygame.font.SysFont(None, 20)
    nw_text = nw_font.render(f"Net worth: ${nw}", True, (255, 248, 200))
    nw_rect = nw_text.get_rect()
    nw_rect.topright = (WINDOW_WIDTH - 20, money_rect.bottom + 2)
    nw_shadow = nw_font.render(f"Net worth: ${nw}", True, BLACK)
    screen.blit(nw_shadow, (nw_rect.x + 1, nw_rect.y + 1))
    screen.blit(nw_text, nw_rect)

def draw_sun():
    # soft glow
    glow = pygame.Surface((160, 160), pygame.SRCALPHA)
    for r, a in ((70, 18), (58, 26), (48, 38)):
        pygame.draw.circle(glow, (255, 230, 120, a), (80, 80), r)
    screen.blit(glow, (700 - 80, 100 - 80))
    pygame.draw.circle(screen, SUN_YELLOW, (700, 100), 40)
    
def draw_cloud(x, y):
    # Draw multiple white circles to form a cloud
    pygame.draw.circle(screen, WHITE, (x, y), 20)
    pygame.draw.circle(screen, WHITE, (x + 15, y - 10), 20)
    pygame.draw.circle(screen, WHITE, (x + 30, y), 20)
    pygame.draw.circle(screen, WHITE, (x + 15, y + 10), 20)

# First, modify the Shop class to use absolute world coordinates
class Shop:
    def __init__(self):
        self.original_x = 200  # Store original world position
        self.width = 120
        self.height = 120
        self.y = 380
        
    def check_collision(self, player_x, player_width):
        return (self.original_x < player_x + player_width and 
                player_x < self.original_x + self.width)
        
    def draw(self, camera):
        shop_x = camera.apply(self.original_x)  # Use original_x for camera transformation
        
        # Only draw if shop is potentially visible
        if -self.width < shop_x < WINDOW_WIDTH + self.width:
            # Draw main building
            pygame.draw.rect(screen, BROWN, (shop_x, self.y, self.width, self.height))
            
            # Draw shop windows
            window_color = (173, 216, 230)  # Light blue
            pygame.draw.rect(screen, window_color, (shop_x + 20, self.y + 30, 30, 30))
            pygame.draw.rect(screen, window_color, (shop_x + 70, self.y + 30, 30, 30))
            
            # Draw door
            pygame.draw.rect(screen, LIGHT_BROWN, (shop_x + 45, self.y + 60, 30, 60))
            pygame.draw.circle(screen, BLACK, (shop_x + 50, self.y + 90), 3)  # Door handle
            
            # Draw roof
            roof_points = [
                (shop_x - 10, self.y),
                (shop_x + self.width//2, self.y - 50),
                (shop_x + self.width + 10, self.y)
            ]
            pygame.draw.polygon(screen, (165, 42, 42), roof_points)  # Dark red roof
            
            # Draw bakery sign
            sign_y = self.y - 30
            sign_width = 100
            sign_height = 25
            sign_x = shop_x + (self.width - sign_width) // 2
            
            # Sign background
            pygame.draw.rect(screen, WHITE, (sign_x, sign_y, sign_width, sign_height))
            pygame.draw.rect(screen, BROWN, (sign_x, sign_y, sign_width, sign_height), 2)
            
            # Sign text
            sign_font = pygame.font.SysFont(None, 30)
            sign_text = sign_font.render("BAKERY", True, BROWN)
            text_rect = sign_text.get_rect(center=(sign_x + sign_width//2, sign_y + sign_height//2))
            screen.blit(sign_text, text_rect)
            
            # Draw display window with pastries
            display_y = self.y + 20
            pygame.draw.rect(screen, WHITE, (shop_x + 10, display_y, 100, 30))
            # Draw small pastries in display
            for i in range(4):
                draw_item_icon(screen, shop_x + 15 + i*25, display_y + 5, 
                              list(shop_items.keys())[i % len(shop_items)])

# Add a new class for the clothing shop
class ClothingShop:
    def __init__(self):
        self.original_x = 400  # Position it after the bakery
        self.width = 120
        self.height = 120
        self.y = 380
        
    def check_collision(self, player_x, player_width):
        return (self.original_x < player_x + player_width and 
                player_x < self.original_x + self.width)
        
    def draw(self, camera):
        shop_x = camera.apply(self.original_x)
        
        if -self.width < shop_x < WINDOW_WIDTH + self.width:
            # Main building
            pygame.draw.rect(screen, BLUE, (shop_x, self.y, self.width, self.height))
            
            # Windows
            pygame.draw.rect(screen, WHITE, (shop_x + 20, self.y + 30, 30, 50))
            pygame.draw.rect(screen, WHITE, (shop_x + 70, self.y + 30, 30, 50))
            
            # Door
            pygame.draw.rect(screen, LIGHT_BROWN, (shop_x + 45, self.y + 60, 30, 60))
            pygame.draw.circle(screen, BLACK, (shop_x + 50, self.y + 90), 3)
            
            # Roof
            roof_points = [
                (shop_x - 10, self.y),
                (shop_x + self.width//2, self.y - 50),
                (shop_x + self.width + 10, self.y)
            ]
            pygame.draw.polygon(screen, (70, 70, 70), roof_points)
            
            # Shop sign
            sign_y = self.y - 30
            sign_width = 100
            sign_height = 25
            sign_x = shop_x + (self.width - sign_width) // 2
            
            pygame.draw.rect(screen, WHITE, (sign_x, sign_y, sign_width, sign_height))
            pygame.draw.rect(screen, BLUE, (sign_x, sign_y, sign_width, sign_height), 2)
            
            sign_font = pygame.font.SysFont(None, 30)
            sign_text = sign_font.render("CLOTHING", True, BLUE)
            text_rect = sign_text.get_rect(center=(sign_x + sign_width//2, sign_y + sign_height//2))
            screen.blit(sign_text, text_rect)
            
            # Display window with clothes
            display_y = self.y + 20
            pygame.draw.rect(screen, WHITE, (shop_x + 10, display_y, 100, 30))
            # Draw sample colored shirts
            for i, color in enumerate([RED, BLUE, GREEN, PURPLE]):
                pygame.draw.rect(screen, color, (shop_x + 15 + i*25, display_y + 5, 20, 20))

# Add this class for the Flappy Bird game
class FlappyBird:
    def __init__(self):
        self.bird_y = WINDOW_HEIGHT // 2
        self.bird_velocity = 0
        self.score = 0
        self.game_over = False
        self.pipes = []
        self.pipe_spawn_timer = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.pipe_speed = 3
        self.pipe_gap = 150
        self.playing = False
        # Allow multiple inputs for jumping
        self.jump_keys = (pygame.K_UP, pygame.K_SPACE)
        self.jump_key = pygame.K_UP  # legacy alias used elsewhere
        
    def reset(self):
        self.bird_y = WINDOW_HEIGHT // 2
        self.bird_velocity = 0
        self.score = 0
        self.game_over = False
        self.pipes = []
        self.pipe_spawn_timer = 0
        self.playing = True  # Make sure game stays in playing state 
        
    def update(self):
        if not self.game_over:
            # Bird physics
            self.bird_velocity += self.gravity
            self.bird_y += self.bird_velocity
            
            # Spawn pipes
            self.pipe_spawn_timer += 1
            if self.pipe_spawn_timer >= 90:  # Spawn pipe every 1.5 seconds
                self.pipe_spawn_timer = 0
                pipe_y = random.randint(100, WINDOW_HEIGHT - 200)
                self.pipes.append({'x': WINDOW_WIDTH, 'y': pipe_y})
            
            # Update pipes
            for pipe in self.pipes[:]:
                pipe['x'] -= self.pipe_speed
                if pipe['x'] < -50:
                    self.pipes.remove(pipe)
                    self.score += 1
                    # Add XP reward for each point scored
                    global xp
                    xp += 100
                    check_level_up()
            
            # Check collisions
            bird_rect = pygame.Rect(100, self.bird_y, 30, 30)
            for pipe in self.pipes:
                top_pipe = pygame.Rect(pipe['x'], 0, 50, pipe['y'])
                bottom_pipe = pygame.Rect(pipe['x'], pipe['y'] + self.pipe_gap, 
                                        50, WINDOW_HEIGHT)
                if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
                    self.game_over = True
            
            # Check boundaries
            if self.bird_y < 0 or self.bird_y > WINDOW_HEIGHT:
                self.game_over = True

    def draw_exit_button(self):
        exit_rect = pygame.Rect(WINDOW_WIDTH - 100, 20, 80, 30)
        pygame.draw.rect(screen, RED, exit_rect)
        exit_text = pygame.font.SysFont(None, 24).render("Exit", True, WHITE)
        text_rect = exit_text.get_rect(center=exit_rect.center)
        screen.blit(exit_text, text_rect)
        return exit_rect


class ArcadeSnake:
    """Grid snake; score = apples eaten in current run."""

    def __init__(self):
        self.grid_w = 20
        self.grid_h = 15
        self.cell = 22
        self.offset_x = (WINDOW_WIDTH - self.grid_w * self.cell) // 2
        self.offset_y = 72
        self.playing = False
        self.game_over = False
        self.score = 0
        self.snake = []
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.food = (10, 7)
        self.move_delay = 11
        self.move_timer = 0

    def reset(self):
        self.playing = True
        self.game_over = False
        self.score = 0
        hx, hy = self.grid_w // 2, self.grid_h // 2
        self.snake = [(hx, hy), (hx - 1, hy), (hx - 2, hy)]
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.move_timer = 0
        self._spawn_food()

    def _spawn_food(self):
        occupied = set(self.snake)
        for _ in range(400):
            fx = random.randint(0, self.grid_w - 1)
            fy = random.randint(0, self.grid_h - 1)
            if (fx, fy) not in occupied:
                self.food = (fx, fy)
                return
        self.food = None

    def draw_exit_button(self):
        exit_rect = pygame.Rect(WINDOW_WIDTH - 100, 20, 80, 30)
        pygame.draw.rect(screen, RED, exit_rect)
        exit_text = pygame.font.SysFont(None, 24).render("Exit", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))
        return exit_rect

    def try_set_direction(self, nd):
        """Avoid instant 180° turns."""
        od = self.direction
        if nd[0] + od[0] == 0 and nd[1] + od[1] == 0:
            return
        self.pending_direction = nd

    def update(self):
        global xp
        if self.game_over:
            return
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return
        self.move_timer = 0
        self.direction = self.pending_direction
        hx, hy = self.snake[0]
        dx, dy = self.direction
        nx, ny = hx + dx, hy + dy
        if nx < 0 or nx >= self.grid_w or ny < 0 or ny >= self.grid_h:
            self.game_over = True
            return
        new_head = (nx, ny)
        if new_head in self.snake[:-1]:
            self.game_over = True
            return
        self.snake.insert(0, new_head)
        ate = self.food and new_head == self.food
        if ate:
            self.score += 1
            xp += 50
            check_level_up()
            self._spawn_food()
        else:
            self.snake.pop()


class ArcadeDodge:
    """Dodge falling blocks; score = hazards cleared without getting hit."""

    def __init__(self):
        self.playing = False
        self.game_over = False
        self.score = 0
        self.player_x = WINDOW_WIDTH // 2
        self.player_w = 56
        self.player_h = 14
        self.player_y = WINDOW_HEIGHT - 36
        self.move_speed = 7
        self.obstacles = []
        self.spawn_timer = 0
        self.fall_speed = 4.2

    def reset(self):
        self.playing = True
        self.game_over = False
        self.score = 0
        self.player_x = WINDOW_WIDTH // 2
        self.obstacles = []
        self.spawn_timer = 0
        self.fall_speed = 4.2

    def draw_exit_button(self):
        exit_rect = pygame.Rect(WINDOW_WIDTH - 100, 20, 80, 30)
        pygame.draw.rect(screen, RED, exit_rect)
        exit_text = pygame.font.SysFont(None, 24).render("Exit", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))
        return exit_rect

    def update(self, keys):
        global xp
        if self.game_over:
            return
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= self.move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += self.move_speed
        self.player_x = max(
            self.player_w // 2 + 10,
            min(WINDOW_WIDTH - self.player_w // 2 - 10, self.player_x),
        )

        self.spawn_timer += 1
        interval = max(22, 52 - min(25, self.score // 2))
        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            w = random.randint(42, 72)
            x = random.randint(24, WINDOW_WIDTH - w - 24)
            self.obstacles.append({"x": float(x), "y": -44.0, "w": w, "h": 34})

        pr = pygame.Rect(
            int(self.player_x - self.player_w // 2),
            self.player_y,
            self.player_w,
            self.player_h,
        )
        for o in self.obstacles[:]:
            o["y"] += self.fall_speed
            orr = pygame.Rect(int(o["x"]), int(o["y"]), o["w"], o["h"])
            if pr.colliderect(orr):
                self.game_over = True
                return
            if o["y"] > WINDOW_HEIGHT:
                self.obstacles.remove(o)
                self.score += 1
                xp += 50
                check_level_up()

class ArcadeBreakout:
    """Breakout-style game; score = bricks broken."""

    def __init__(self):
        self.playing = False
        self.game_over = False
        self.won = False
        self.score = 0
        self.paddle_w = 110
        self.paddle_h = 14
        self.paddle_x = WINDOW_WIDTH // 2 - self.paddle_w // 2
        self.paddle_y = WINDOW_HEIGHT - 45
        self.paddle_speed = 8
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT - 80
        self.ball_r = 8
        self.ball_vx = 4.2
        self.ball_vy = -4.2
        self.bricks = []
        self._make_bricks()

    def _make_bricks(self):
        self.bricks = []
        cols = 10
        rows = 5
        bw, bh = 68, 24
        gap = 8
        total_w = cols * bw + (cols - 1) * gap
        start_x = (WINDOW_WIDTH - total_w) // 2
        start_y = 88
        palette = [(255, 120, 120), (255, 180, 110), (255, 230, 120), (130, 220, 170), (120, 180, 255)]
        for r in range(rows):
            for c in range(cols):
                x = start_x + c * (bw + gap)
                y = start_y + r * (bh + gap)
                self.bricks.append({"rect": pygame.Rect(x, y, bw, bh), "color": palette[r % len(palette)]})

    def reset(self):
        self.playing = True
        self.game_over = False
        self.won = False
        self.score = 0
        self.paddle_x = WINDOW_WIDTH // 2 - self.paddle_w // 2
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT - 80
        self.ball_vx = random.choice([-1, 1]) * 4.2
        self.ball_vy = -4.2
        self._make_bricks()

    def draw_exit_button(self):
        exit_rect = pygame.Rect(WINDOW_WIDTH - 100, 20, 80, 30)
        pygame.draw.rect(screen, RED, exit_rect)
        exit_text = pygame.font.SysFont(None, 24).render("Exit", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))
        return exit_rect

    def update(self, keys):
        global xp
        if self.game_over:
            return
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle_x -= self.paddle_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle_x += self.paddle_speed
        self.paddle_x = max(12, min(WINDOW_WIDTH - self.paddle_w - 12, self.paddle_x))

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # Walls
        if self.ball_x - self.ball_r <= 0 or self.ball_x + self.ball_r >= WINDOW_WIDTH:
            self.ball_vx *= -1
        if self.ball_y - self.ball_r <= 0:
            self.ball_vy *= -1
        if self.ball_y - self.ball_r > WINDOW_HEIGHT:
            self.game_over = True
            self.won = False
            return

        # Paddle
        paddle_rect = pygame.Rect(int(self.paddle_x), self.paddle_y, self.paddle_w, self.paddle_h)
        ball_rect = pygame.Rect(int(self.ball_x - self.ball_r), int(self.ball_y - self.ball_r), self.ball_r * 2, self.ball_r * 2)
        if ball_rect.colliderect(paddle_rect) and self.ball_vy > 0:
            self.ball_vy = -abs(self.ball_vy)
            hit_pos = (self.ball_x - (self.paddle_x + self.paddle_w / 2)) / (self.paddle_w / 2)
            self.ball_vx = max(-6.5, min(6.5, self.ball_vx + hit_pos * 1.6))

        # Bricks
        for b in self.bricks[:]:
            if ball_rect.colliderect(b["rect"]):
                self.bricks.remove(b)
                self.score += 1
                xp += 45
                check_level_up()
                # crude but solid bounce resolution
                overlap_l = ball_rect.right - b["rect"].left
                overlap_r = b["rect"].right - ball_rect.left
                overlap_t = ball_rect.bottom - b["rect"].top
                overlap_b = b["rect"].bottom - ball_rect.top
                min_overlap = min(overlap_l, overlap_r, overlap_t, overlap_b)
                if min_overlap in (overlap_l, overlap_r):
                    self.ball_vx *= -1
                else:
                    self.ball_vy *= -1
                break

        if not self.bricks:
            self.game_over = True
            self.won = True


class ArcadePong:
    """1v1 Pong vs AI; score = goals when the ball passes the AI paddle."""

    def __init__(self):
        self.playing = False
        self.game_over = False
        self.score = 0
        self.paddle_h = 92
        self.paddle_w = 12
        self.left_x = 22
        self.right_x = WINDOW_WIDTH - 34
        self.player_y = WINDOW_HEIGHT // 2 - self.paddle_h // 2
        self.ai_y = self.player_y
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT // 2
        self.ball_r = 9
        self.ball_vx = 5.0
        self.ball_vy = 3.0
        self.paddle_speed = 8.0
        self.ai_speed = 5.6

    def reset(self):
        self.playing = True
        self.game_over = False
        self.score = 0
        self.player_y = WINDOW_HEIGHT // 2 - self.paddle_h // 2
        self.ai_y = self.player_y
        self._serve_ball()

    def _serve_ball(self):
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT // 2
        self.ball_vx = random.choice([-1, 1]) * 5.4
        self.ball_vy = random.uniform(-3.6, 3.6)

    def draw_exit_button(self):
        exit_rect = pygame.Rect(WINDOW_WIDTH - 100, 20, 80, 30)
        pygame.draw.rect(screen, RED, exit_rect)
        exit_text = pygame.font.SysFont(None, 24).render("Exit", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))
        return exit_rect

    def update(self, keys):
        global xp
        if self.game_over:
            return

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_y -= self.paddle_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_y += self.paddle_speed
        self.player_y = max(16, min(WINDOW_HEIGHT - self.paddle_h - 16, self.player_y))

        aim = self.ball_y - self.paddle_h / 2
        if self.ai_y < aim - 5:
            self.ai_y += self.ai_speed
        elif self.ai_y > aim + 5:
            self.ai_y -= self.ai_speed
        self.ai_y = max(16, min(WINDOW_HEIGHT - self.paddle_h - 16, self.ai_y))

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        if self.ball_y - self.ball_r <= 0 or self.ball_y + self.ball_r >= WINDOW_HEIGHT:
            self.ball_vy *= -1
            self.ball_y = max(self.ball_r, min(WINDOW_HEIGHT - self.ball_r, self.ball_y))

        lp = pygame.Rect(self.left_x, int(self.player_y), self.paddle_w, self.paddle_h)
        rp = pygame.Rect(self.right_x, int(self.ai_y), self.paddle_w, self.paddle_h)
        br = pygame.Rect(
            int(self.ball_x - self.ball_r),
            int(self.ball_y - self.ball_r),
            self.ball_r * 2,
            self.ball_r * 2,
        )

        if br.colliderect(lp) and self.ball_vx < 0:
            self.ball_x = lp.right + self.ball_r
            self.ball_vx = abs(self.ball_vx) * 1.02
            rel = (self.ball_y - (self.player_y + self.paddle_h / 2)) / (self.paddle_h / 2)
            self.ball_vy += rel * 3.2
            self.ball_vx = min(10.5, self.ball_vx)
        elif br.colliderect(rp) and self.ball_vx > 0:
            self.ball_x = rp.left - self.ball_r
            self.ball_vx = -abs(self.ball_vx) * 1.02
            rel = (self.ball_y - (self.ai_y + self.paddle_h / 2)) / (self.paddle_h / 2)
            self.ball_vy += rel * 3.2
            self.ball_vx = max(-10.5, self.ball_vx)

        if self.ball_x + self.ball_r < 0:
            self.game_over = True
        elif self.ball_x - self.ball_r > WINDOW_WIDTH:
            self.score += 1
            xp += 42
            check_level_up()
            self._serve_ball()


class ArcadeStack:
    """Stack sliding blocks; score = successful layers placed."""

    def __init__(self):
        self.playing = False
        self.game_over = False
        self.score = 0
        self.base_y = WINDOW_HEIGHT - 48
        self.layer_h = 22
        self.foundation_cx = WINDOW_WIDTH // 2
        self.foundation_w = 220.0
        self.layers = []
        self.slide_cx = float(WINDOW_WIDTH // 2)
        self.slide_dir = 6.2
        self.max_speed = 10.5

    def reset(self):
        self.playing = True
        self.game_over = False
        self.score = 0
        self.layers = []
        self.slide_cx = float(WINDOW_WIDTH // 2)
        self.slide_dir = 6.2

    def draw_exit_button(self):
        exit_rect = pygame.Rect(WINDOW_WIDTH - 100, 20, 80, 30)
        pygame.draw.rect(screen, RED, exit_rect)
        exit_text = pygame.font.SysFont(None, 24).render("Exit", True, WHITE)
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))
        return exit_rect

    def update(self):
        if self.game_over:
            return
        tw = self.foundation_w if not self.layers else float(self.layers[-1][1])
        half = tw / 2
        self.slide_cx += self.slide_dir
        lo = 32 + half
        hi = WINDOW_WIDTH - 32 - half
        if self.slide_cx <= lo:
            self.slide_cx = lo
            self.slide_dir = abs(self.slide_dir)
        elif self.slide_cx >= hi:
            self.slide_cx = hi
            self.slide_dir = -abs(self.slide_dir)

    def try_place(self):
        global xp
        if self.game_over:
            return
        if not self.layers:
            tcx, tw = float(self.foundation_cx), float(self.foundation_w)
        else:
            tcx, tw = float(self.layers[-1][0]), float(self.layers[-1][1])
        hw = tw / 2
        p_left, p_right = tcx - hw, tcx + hw
        s_left = self.slide_cx - hw
        s_right = self.slide_cx + hw
        ol = max(p_left, s_left)
        orr = min(p_right, s_right)
        if orr <= ol:
            self.game_over = True
            return
        new_w = orr - ol
        if new_w < 11:
            self.game_over = True
            return
        new_cx = (ol + orr) / 2.0
        y = self.base_y - self.layer_h * (len(self.layers) + 1)
        self.layers.append((new_cx, new_w, y))
        self.slide_cx = new_cx
        sp = min(self.max_speed, 4.8 + len(self.layers) * 0.32)
        self.slide_dir = (1.0 if self.slide_dir > 0 else -1.0) * sp
        self.score += 1
        xp += 55
        check_level_up()


class ArcadeShop:
    def __init__(self):
        self.original_x = 600  # Position after clothing shop
        self.width = 140
        self.height = 150
        self.y = 350
        self.flappy_bird = FlappyBird()
        self.snake = ArcadeSnake()
        self.dodge = ArcadeDodge()
        self.breakout = ArcadeBreakout()
        self.pong = ArcadePong()
        self.stack = ArcadeStack()
        self.game_price = 15  # Price to play one game

    def any_arcade_playing(self):
        return (
            self.flappy_bird.playing
            or self.snake.playing
            or self.dodge.playing
            or self.breakout.playing
            or self.pong.playing
            or self.stack.playing
        )
        
    def check_collision(self, player_x, player_width):
        return (self.original_x < player_x + player_width and 
                player_x < self.original_x + self.width)
        
    def draw(self, camera):
        shop_x = camera.apply(self.original_x)
        
        if -self.width < shop_x < WINDOW_WIDTH + self.width:
            # Main building
            pygame.draw.rect(screen, PURPLE_DARK, (shop_x, self.y, self.width, self.height))
            
            # Neon outline
            pygame.draw.rect(screen, NEON_BLUE, (shop_x, self.y, self.width, self.height), 3)
            
            # Windows with arcade machines
            for i in range(2):
                window_x = shop_x + 20 + i * 50
                pygame.draw.rect(screen, BLACK, (window_x, self.y + 30, 40, 60))
                # Arcade screen
                pygame.draw.rect(screen, NEON_GREEN, 
                               (window_x + 5, self.y + 35, 30, 20))
                # Arcade controls
                pygame.draw.circle(screen, NEON_PINK, 
                                 (window_x + 15, self.y + 70), 5)
                pygame.draw.rect(screen, NEON_PINK, 
                               (window_x + 25, self.y + 65, 10, 10))
            
            # Door
            pygame.draw.rect(screen, BLACK, (shop_x + 45, self.y + 60, 50, 90))
            pygame.draw.rect(screen, NEON_BLUE, (shop_x + 45, self.y + 60, 50, 90), 2)
            
            # Neon sign
            sign_y = self.y - 40
            sign_width = 120
            sign_height = 35
            sign_x = shop_x + (self.width - sign_width) // 2
            
            pygame.draw.rect(screen, BLACK, (sign_x, sign_y, sign_width, sign_height))
            pygame.draw.rect(screen, NEON_PINK, (sign_x, sign_y, sign_width, sign_height), 3)
            
            # Blinking effect
            if pygame.time.get_ticks() % 2000 < 1000:
                sign_color = NEON_GREEN
            else:
                sign_color = NEON_PINK
            
            sign_font = pygame.font.SysFont(None, 36)
            sign_text = sign_font.render("ARCADE", True, sign_color)
            text_rect = sign_text.get_rect(center=(sign_x + sign_width//2, sign_y + sign_height//2))
            screen.blit(sign_text, text_rect)

class Supermarket:
    def __init__(self):
        # After cafe (745+140=885); keep gap before hotel at 1050
        self.original_x = 890
        self.width = 150
        self.height = 130
        self.y = 370

    def check_collision(self, player_x, player_width):
        return (self.original_x < player_x + player_width and
                player_x < self.original_x + self.width)

    def draw(self, camera):
        sx = camera.apply(self.original_x)
        if -self.width < sx < WINDOW_WIDTH + self.width:
            pygame.draw.rect(screen, (50, 120, 50), (sx, self.y, self.width, self.height))
            pygame.draw.rect(screen, (20, 60, 20), (sx, self.y, self.width, self.height), 3)
            # door
            pygame.draw.rect(screen, LIGHT_BROWN, (sx + 60, self.y + 60, 30, 70))
            # sign
            sign_font = pygame.font.SysFont(None, 26)
            sign = sign_font.render("MARKET", True, WHITE)
            screen.blit(sign, sign.get_rect(center=(sx + self.width//2, self.y + 20)))
            # crates
            pygame.draw.rect(screen, (120, 80, 40), (sx + 15, self.y + 75, 30, 25))
            pygame.draw.rect(screen, (120, 80, 40), (sx + 105, self.y + 75, 30, 25))


class SeafoodMarket:
    """Sell caught fish (Sun Reef) for cash."""

    def __init__(self):
        # To the right of the ferry dock
        self.original_x = 1640
        self.width = 160
        self.height = 132
        self.y = 368

    def check_collision(self, player_x, player_width):
        return self.original_x < player_x + player_width and player_x < self.original_x + self.width

    def draw(self, camera):
        mx = int(round(camera.apply(self.original_x)))
        if -self.width >= mx or mx >= WINDOW_WIDTH + self.width:
            return
        pygame.draw.rect(screen, (48, 98, 118), (mx, self.y, self.width, self.height), border_radius=6)
        pygame.draw.rect(screen, (20, 55, 70), (mx, self.y, self.width, self.height), 3, border_radius=6)
        # awning
        for i in range(8):
            c = (240, 248, 252) if i % 2 else (225, 92, 78)
            pygame.draw.rect(screen, c, (mx + 6 + i * 19, self.y + 18, 18, 18), border_radius=2)
        pygame.draw.rect(screen, (20, 55, 70), (mx, self.y + 34, self.width, 5))
        # fish sign
        pygame.draw.ellipse(screen, (210, 240, 255), (mx + 18, self.y + 54, 46, 28))
        pygame.draw.polygon(screen, (210, 240, 255), [(mx + 54, self.y + 68), (mx + 72, self.y + 60), (mx + 70, self.y + 76)])
        pygame.draw.circle(screen, (40, 45, 55), (mx + 38, self.y + 64), 2)
        # counter
        pygame.draw.rect(screen, (110, 78, 55), (mx + 10, self.y + 92, self.width - 20, 22), border_radius=6)
        pygame.draw.rect(screen, (75, 52, 38), (mx + 10, self.y + 92, self.width - 20, 22), 2, border_radius=6)
        sf = pygame.font.SysFont(None, 26)
        sign = sf.render("SEAFOOD", True, (245, 252, 255))
        screen.blit(sign, sign.get_rect(center=(mx + self.width // 2, self.y + 12)))


class UtilityCart:
    """Permanent vendor cart unlocked on Day 10."""

    def __init__(self):
        self.original_x = 1860
        self.width = 170
        self.height = 120
        self.y = 380

    def unlocked(self) -> bool:
        return int(day_index) >= 9  # Day 10 (1-indexed)

    def check_collision(self, player_x, player_width):
        if not self.unlocked():
            return False
        return self.original_x < player_x + player_width and player_x < self.original_x + self.width

    def draw(self, camera):
        if not self.unlocked():
            return
        cx = int(round(camera.apply(self.original_x)))
        if -self.width >= cx or cx >= WINDOW_WIDTH + self.width:
            return
        # cart body
        pygame.draw.rect(screen, (160, 120, 70), (cx, self.y + 34, self.width, 74), border_radius=10)
        pygame.draw.rect(screen, (85, 60, 35), (cx, self.y + 34, self.width, 74), 3, border_radius=10)
        # wheels
        pygame.draw.circle(screen, (45, 45, 50), (cx + 28, self.y + 112), 12)
        pygame.draw.circle(screen, (45, 45, 50), (cx + self.width - 28, self.y + 112), 12)
        pygame.draw.circle(screen, (120, 120, 130), (cx + 28, self.y + 112), 6)
        pygame.draw.circle(screen, (120, 120, 130), (cx + self.width - 28, self.y + 112), 6)
        # canopy
        pygame.draw.rect(screen, (60, 150, 120), (cx - 6, self.y + 10, self.width + 12, 26), border_radius=6)
        pygame.draw.rect(screen, (25, 90, 75), (cx - 6, self.y + 10, self.width + 12, 26), 2, border_radius=6)
        for i in range(7):
            pygame.draw.rect(screen, (240, 250, 252) if i % 2 else (90, 200, 160), (cx - 4 + i * 26, self.y + 12, 24, 22), border_radius=4)
        # sign + seller
        sf = pygame.font.SysFont(None, 24)
        screen.blit(sf.render("UTILITIES", True, (245, 252, 255)), (cx + 34, self.y - 4))
        # seller
        pygame.draw.circle(screen, (240, 210, 180), (cx + 26, self.y + 58), 12)
        pygame.draw.rect(screen, (110, 70, 180), (cx + 14, self.y + 70, 24, 34), border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), (cx + 10, self.y + 52, 32, 10), border_radius=5)


class BlackMarket:
    """Shop that opens every 3 days. Sells 50%-off rotating stock."""

    def __init__(self):
        self.original_x = 2060
        self.width = 190
        self.height = 120
        self.y = 380

    def check_collision(self, player_x, player_width):
        return self.original_x < player_x + player_width and player_x < self.original_x + self.width

    def draw(self, camera):
        cx = int(round(camera.apply(self.original_x)))
        if -self.width >= cx or cx >= WINDOW_WIDTH + self.width:
            return
        open_now = black_market_open_today()

        body = (35, 35, 45) if open_now else (55, 55, 65)
        border = (180, 60, 120) if open_now else (110, 110, 120)
        pygame.draw.rect(screen, body, (cx, self.y + 30, self.width, 84), border_radius=10)
        pygame.draw.rect(screen, border, (cx, self.y + 30, self.width, 84), 3, border_radius=10)

        # neon sign
        sf = pygame.font.SysFont(None, 24)
        sign = sf.render("BLACK MARKET", True, (255, 90, 170) if open_now else (160, 160, 170))
        screen.blit(sign, sign.get_rect(center=(cx + self.width // 2, self.y + 18)))

        # door + shutter
        pygame.draw.rect(screen, (20, 20, 25), (cx + 78, self.y + 62, 40, 52), border_radius=6)
        for i in range(5):
            pygame.draw.line(screen, (90, 90, 100), (cx + 18, self.y + 58 + i * 8), (cx + self.width - 18, self.y + 58 + i * 8), 2)

        # open/closed tag
        tag = "OPEN" if open_now else "CLOSED"
        tag_s = pygame.font.SysFont(None, 22).render(tag, True, (245, 245, 250))
        tr = tag_s.get_rect(center=(cx + self.width // 2, self.y + 106))
        pygame.draw.rect(screen, (180, 60, 120) if open_now else (90, 90, 100), tr.inflate(18, 8), border_radius=8)
        screen.blit(tag_s, tag_s.get_rect(center=tr.center))

class Hotel:
    def __init__(self):
        self.original_x = 1050
        self.width = 170
        self.height = 170
        self.y = 330

    def check_collision(self, player_x, player_width):
        return (self.original_x < player_x + player_width and
                player_x < self.original_x + self.width)

    def draw(self, camera):
        hx = camera.apply(self.original_x)
        if -self.width < hx < WINDOW_WIDTH + self.width:
            pygame.draw.rect(screen, (120, 120, 160), (hx, self.y, self.width, self.height))
            pygame.draw.rect(screen, (70, 70, 100), (hx, self.y, self.width, self.height), 3)
            # windows
            for r in range(2):
                for c in range(3):
                    pygame.draw.rect(screen, (180, 220, 255),
                                     (hx + 20 + c*45, self.y + 35 + r*45, 25, 25))
            # door
            pygame.draw.rect(screen, (90, 60, 40), (hx + 70, self.y + 110, 30, 60))
            # sign
            sign_font = pygame.font.SysFont(None, 30)
            sign = sign_font.render("HOTEL", True, WHITE)
            screen.blit(sign, sign.get_rect(center=(hx + self.width//2, self.y + 18)))


# --- Player house (world building + interior build mode) ---
HOUSE_PURCHASE_COST = 500
HOUSE_EXPAND_L1_COST = 440
HOUSE_EXPAND_L2_COST = 760
HOUSE_INTERIOR_W1 = 1700
HOUSE_GRID = 26
HOUSE_LADDER_CX = 118
HOUSE_FURNITURE = {
    "bed": {"w": 200, "h": 88, "price": 92, "chef": False, "coffee": False},
    "microwave": {"w": 118, "h": 52, "price": 118, "chef": False, "coffee": False},
    "stove": {"w": 46, "h": 52, "price": 168, "chef": True, "coffee": False},
    "sink": {"w": 78, "h": 46, "price": 138, "chef": False, "coffee": True},
    "grill": {"w": 86, "h": 54, "price": 220, "chef": False, "coffee": False},
    "seasoner": {"w": 64, "h": 44, "price": 160, "chef": False, "coffee": False},
}


def make_glass_of_water_item() -> ShopItem:
    it = ShopItem("Glass of Water", 0, 2, item_type="drink")
    it.max_carry_one = True
    it.quick_drink = True
    it.stamina_restore_drink = 60
    return it


def house_floor_feet_y(floor: int) -> int:
    return 410 if int(floor) == 0 else 236


def house_interior_width() -> int:
    return HOUSE_INTERIOR_W1 if house_expansion_level >= 1 else WINDOW_WIDTH


def house_ladder_block_world(fl: int) -> pygame.Rect:
    fy = house_floor_feet_y(fl)
    return pygame.Rect(HOUSE_LADDER_CX - 48, fy - 148, 96, 138)


def house_furniture_world_rect(kind: str, cx: float, floor: int) -> pygame.Rect:
    sp = HOUSE_FURNITURE[kind]
    w, h = sp["w"], sp["h"]
    top = house_floor_feet_y(floor) - h
    return pygame.Rect(int(float(cx) - w // 2), int(top), w, h)


def house_building_rect(b: dict) -> pygame.Rect:
    return house_furniture_world_rect(b["kind"], float(b["cx"]), int(b["floor"]))


def house_new_furniture_collides(kind: str, cx: float, floor: int, ignore_idx: int = -1) -> bool:
    r = house_furniture_world_rect(kind, cx, floor)
    if house_expansion_level >= 2 and r.colliderect(house_ladder_block_world(floor)):
        return True
    pad = 8
    r2 = r.inflate(pad, pad)
    for i, o in enumerate(house_buildings):
        if i == ignore_idx or int(o["floor"]) != int(floor):
            continue
        if r2.colliderect(house_building_rect(o)):
            return True
    return False


def house_snap_cx(wx: float) -> float:
    g = float(HOUSE_GRID)
    return round(wx / g) * g


def house_clamp_player():
    global house_player_x
    w = house_interior_width()
    margin = 36.0
    house_player_x = float(max(margin, min(w - margin, house_player_x)))


def house_update_camera():
    global house_cam_offset
    if house_expansion_level < 1:
        house_cam_offset = 0.0
        return
    iw = float(house_interior_width())
    half = WINDOW_WIDTH // 2
    house_cam_offset = float(max(0.0, min(iw - WINDOW_WIDTH, house_player_x - half)))


class House:
    """Buy once ($500); interior builder + expansions."""

    def __init__(self):
        self.original_x = 1235
        self.width = 148
        self.height = 158
        # Align to sidewalk baseline (platform top at y=500)
        self.y = 500 - self.height

    def check_collision(self, player_x, player_width):
        return self.original_x < player_x + player_width and player_x < self.original_x + self.width

    def draw(self, camera):
        hx_f = camera.apply(self.original_x)
        hx = int(round(hx_f))  # pixel-perfect alignment (roof/body/windows)
        if -self.width >= hx or hx >= WINDOW_WIDTH + self.width:
            return
        pygame.draw.rect(screen, (96, 118, 92), (hx, self.y, self.width, self.height))
        pygame.draw.rect(screen, (52, 72, 48), (hx, self.y, self.width, self.height), 3)
        # Symmetric roof so the peak is perfectly centered.
        roof_overhang = 8
        roof_base_y = self.y + 30
        roof_peak_y = self.y - 24
        peak_x = hx + self.width // 2
        left_x = hx - roof_overhang
        right_x = hx + self.width + roof_overhang
        pygame.draw.polygon(
            screen,
            (140, 86, 70),
            [(left_x, int(roof_base_y)), (peak_x, int(roof_peak_y)), (right_x, int(roof_base_y))],
        )
        pygame.draw.rect(screen, (210, 230, 255), (hx + 24, self.y + 52, 36, 32), border_radius=4)
        pygame.draw.rect(screen, (210, 230, 255), (hx + 88, self.y + 52, 36, 32), border_radius=4)
        pygame.draw.rect(screen, (78, 52, 40), (hx + 54, self.y + 98, 40, 60), border_radius=4)
        sf = pygame.font.SysFont(None, 26)
        home_lbl = sf.render("HOME", True, (245, 252, 235))
        screen.blit(home_lbl, home_lbl.get_rect(center=(hx + self.width // 2, self.y + 18)))


class FerryDock:
    """Pier past the suburbs — ride to Sun Reef island."""

    def __init__(self):
        self.original_x = 1420
        self.width = 115
        self.height = 95
        self.y = 405

    def check_collision(self, player_x, player_width):
        return self.original_x < player_x + player_width and player_x < self.original_x + self.width

    def draw(self, camera):
        dx = int(round(camera.apply(self.original_x)))
        if -self.width >= dx or dx >= WINDOW_WIDTH + self.width:
            return
        pygame.draw.rect(screen, (55, 105, 145), (dx - 30, 502, self.width + 90, 98))
        for wx in range(-20, self.width + 40, 7):
            pygame.draw.line(screen, (80, 140, 175), (dx + wx, 505), (dx + wx + 4, 598), 1)
        pygame.draw.rect(screen, (100, 135, 95), (dx - 10, 498, self.width + 28, 8), border_radius=3)
        for i in range(8):
            pygame.draw.rect(screen, (130, 88, 58), (dx - 6 + i * 15, 468, 12, 34), border_radius=2)
            pygame.draw.line(screen, (80, 55, 38), (dx - 6 + i * 15, 468), (dx - 6 + i * 15, 502), 2)
        pygame.draw.rect(screen, (85, 58, 40), (dx - 12, 460, self.width + 28, 12), border_radius=4)
        pygame.draw.rect(screen, (175, 128, 92), (dx + 8, 388, 56, 82), border_radius=5)
        pygame.draw.rect(screen, (55, 40, 30), (dx + 8, 388, 56, 82), 2, border_radius=5)
        pygame.draw.rect(screen, (220, 235, 255), (dx + 20, 402, 22, 18), border_radius=3)
        lf = pygame.font.SysFont(None, 22)
        screen.blit(lf.render("FERRY", True, (255, 248, 235)), (dx + 18, 362))
        tf = pygame.font.SysFont(None, 16)
        screen.blit(tf.render(f"Sun Reef  ·  ${FERRY_FARE}", True, (230, 245, 255)), (dx + 4, 344))


FISH_CATCH_TABLE = (
    ("Sand Minnow", 6, 16, 0.15),
    ("Silver Sprat", 12, 22, 0.12),
    ("Reef Sardine", 18, 26, 0.10),
    ("Coral Bass", 26, 32, 0.09),
    ("Lagoon Perch", 34, 36, 0.08),
    ("Azure Tang", 44, 40, 0.07),
    ("Tide Snapper", 56, 44, 0.06),
    ("Sunscale Mackerel", 70, 48, 0.05),
    ("Bluefin Needlefish", 86, 52, 0.042),
    ("Golden Koi", 105, 56, 0.034),
    ("Pearl Pike", 128, 60, 0.028),
    ("Glitter Grouper", 152, 64, 0.022),
    ("Crown Carp", 178, 68, 0.018),
    ("Storm Barracuda", 210, 72, 0.014),
    ("Opal Eel", 248, 76, 0.011),
    ("Lionheart Tuna", 295, 80, 0.0085),
    ("Aurora Sturgeon", 360, 84, 0.0065),
    ("Deepglass Swordfish", 440, 88, 0.0048),
    ("Starfall Ray", 540, 92, 0.0034),
    ("Moonfin Marlin", 700, 96, 0.0022),
    # --- 100 new fish (stronger, rarer, more valuable) ---
    ("Seabreeze Smelt", 10, 18, 0.11),
    ("Pebble Guppy", 11, 19, 0.105),
    ("Dawn Shiner", 12, 20, 0.10),
    ("Glass Anchovy", 13, 20, 0.095),
    ("Harbor Herring", 14, 21, 0.090),
    ("Lemonfin Fry", 15, 22, 0.086),
    ("Kelp Darter", 16, 22, 0.082),
    ("Foamrunner", 17, 23, 0.078),
    ("Shellback Squeaker", 18, 24, 0.074),
    ("Bay Skipper", 19, 24, 0.071),
    ("Coral Cricketfish", 20, 25, 0.068),
    ("Tidepool Tetra", 21, 26, 0.065),
    ("Sunstripe Sprinter", 22, 26, 0.062),
    ("Reef Ribbonfish", 23, 27, 0.060),
    ("Sandbar Sculpin", 24, 28, 0.057),
    ("Pearl Minnow", 25, 28, 0.055),
    ("Cove Char", 26, 29, 0.052),
    ("Blueblink Bream", 27, 30, 0.050),
    ("Shallow Snapper", 28, 30, 0.048),
    ("Drift Carp", 30, 31, 0.046),
    ("Honeyfin Haddock", 32, 32, 0.044),
    ("Kelpkeeper Codlet", 34, 33, 0.042),
    ("Wavecrest Wrasse", 36, 33, 0.040),
    ("Saffron Scad", 38, 34, 0.038),
    ("Seaglass Sardine", 40, 35, 0.036),
    ("Starlit Mullet", 42, 35, 0.034),
    ("Brine Bopper", 45, 36, 0.032),
    ("Ribbonfin Roach", 48, 37, 0.030),
    ("Current Chub", 52, 38, 0.028),
    ("Dune Drum", 56, 39, 0.026),
    ("Reef Roosterfish", 60, 40, 0.024),
    ("Sunreef Salmonlet", 64, 41, 0.022),
    ("Palmshadow Piranha", 68, 42, 0.020),
    ("Coral Crownfish", 72, 43, 0.0185),
    ("Lantern Ling", 76, 44, 0.0170),
    ("Moonwake Mackerel", 80, 45, 0.0158),
    ("Sapphire Sucker", 84, 46, 0.0146),
    ("Crimson Crevalle", 88, 47, 0.0135),
    ("Stormfin Sheepshead", 92, 48, 0.0125),
    ("Bristlejaw Bream", 96, 49, 0.0116),
    ("Tanglejaw Trout", 100, 50, 0.0108),
    ("Whitesand Wahoo", 110, 52, 0.0100),
    ("Seasong Silverside", 120, 54, 0.0093),
    ("Glimmer Gar", 130, 56, 0.0087),
    ("Inkline Grouper", 140, 58, 0.0081),
    ("Coralcoat Catfish", 150, 60, 0.0076),
    ("Citrusfin Cobia", 160, 62, 0.0071),
    ("Reefblade Raptorfish", 170, 64, 0.0067),
    ("Opaline Oceanpike", 180, 66, 0.0063),
    ("Galejaw Garfish", 195, 68, 0.0059),
    ("Tidebreaker Trevally", 210, 70, 0.0056),
    ("Bluefire Bonito", 225, 72, 0.0053),
    ("Sunflare Snapper", 240, 74, 0.0050),
    ("Pearlstorm Pike", 260, 76, 0.0047),
    ("Abyssal Amberjack", 280, 78, 0.0044),
    ("Starpepper Swordlet", 300, 80, 0.0041),
    ("Nightreef Nibbler", 320, 82, 0.0039),
    ("Glimmerjaw Grouper", 340, 84, 0.0037),
    ("Aurora Angelfish", 360, 86, 0.0035),
    ("Crownscale Carp", 385, 88, 0.0033),
    ("Thundercove Tuna", 410, 90, 0.0031),
    ("Moonlace Moray", 440, 92, 0.0029),
    ("Deepcurrent Dolphinfish", 470, 94, 0.0027),
    ("Sunken Sablefish", 500, 96, 0.0025),
    ("Opalfin Oarfish", 540, 98, 0.0023),
    ("Starfall Surgeonfish", 580, 100, 0.0021),
    ("Crystalcrest Coelacanth", 640, 104, 0.0019),
    ("Reefshadow Ripper", 700, 108, 0.0017),
    ("Abyssglass Arowana", 780, 112, 0.0015),
    ("Lighthouse Leviathanlet", 860, 116, 0.00135),
    ("Mirage Marlinlet", 940, 120, 0.00122),
    ("Nebula Needlefish", 1020, 124, 0.00110),
    ("Starlight Sturgeon", 1100, 128, 0.00100),
    ("Comet Crestfish", 1200, 132, 0.00090),
    ("Mythscale Manta", 1320, 136, 0.00082),
    ("Crown of Coral Koi", 1450, 140, 0.00074),
    ("Skytear Swordfish", 1600, 144, 0.00067),
    ("Moonmint Marlin", 1750, 148, 0.00060),
    ("Aurora Emperor Tuna", 1900, 152, 0.00054),
    ("Starforge Sturgeon", 2100, 156, 0.00049),
    ("Deepglass Dragonfish", 2350, 160, 0.00044),
    ("Celestial Sailfish", 2600, 164, 0.00040),
    ("Eclipse Eel", 2900, 168, 0.00036),
    ("Cosmic Crownray", 3200, 172, 0.00033),
    ("Mythic Moonfin Prime", 3600, 178, 0.00030),
    ("Sun Reef Sovereign", 4200, 184, 0.00027),
    ("Stardrop Seraphfish", 5000, 192, 0.00024),
    ("Ocean Oracle", 6200, 200, 0.00021),
    ("Astral Ancestorfish", 8000, 220, 0.00018),
    ("Voidwake Marlin", 11000, 250, 0.00015),
    ("Heavenreef Herald", 16000, 300, 0.00012),
    ("Sun Reef Mythos", 25000, 380, 0.00009),
    ("One-in-a-Million", 99999, 600, 0.00003),
)


def _fish_reset_minigame():
    global fish_phase, fish_cast_power, fish_wait_until_tick, fish_hook_deadline_tick
    global fish_reel_progress, fish_pos, fish_vel, fish_player_center, fish_struggle_phase, fish_pending_roll
    fish_phase = "idle"
    fish_cast_power = 0.0
    fish_wait_until_tick = 0
    fish_hook_deadline_tick = 0
    fish_reel_progress = 0.0
    fish_pos = 0.5
    fish_vel = 0.0
    fish_player_center = 0.5
    fish_struggle_phase = 0.0
    fish_pending_roll = None


def _fish_make_item(name: str, price: int, hunger: int) -> ShopItem:
    it = ShopItem(name, price, hunger, item_type="food")
    it.caught_fish = True
    return it


def fish_rarity_label(name: str) -> tuple[str, tuple]:
    """Return (label, color) for a fish name based on its rarity tier."""
    names = [row[0] for row in FISH_CATCH_TABLE]
    if name not in names:
        return "Unknown", (140, 150, 160)
    idx = names.index(name)
    n = max(1, len(names))
    p = idx / float(max(1, n - 1))  # 0..1
    # Percentile tiers so this works for any catalog size.
    if p <= 0.35:
        return "Common", (120, 140, 150)
    if p <= 0.60:
        return "Uncommon", (80, 190, 120)
    if p <= 0.78:
        return "Rare", (80, 160, 255)
    if p <= 0.90:
        return "Epic", (190, 110, 255)
    if p <= 0.97:
        return "Legendary", (255, 190, 80)
    return "Mythic", (255, 105, 180)


def refresh_seafood_daily_offer(force: bool = False):
    """Pick a new daily offer fish once per in-game day."""
    global seafood_daily_offer_fish, seafood_daily_offer_day
    if (not force) and seafood_daily_offer_day == day_index and seafood_daily_offer_fish:
        return
    seafood_daily_offer_day = int(day_index)
    names = [row[0] for row in FISH_CATCH_TABLE]
    if not names:
        seafood_daily_offer_fish = None
        return
    # Avoid the absolute last entry so it doesn't dominate the offer UI.
    pick_from = names[:-1] if len(names) > 2 else names
    seafood_daily_offer_fish = random.choice(pick_from)


def skip_days(n: int):
    """Cheat utility: advance in-game days, refresh day-based rolls."""
    global day_index, current_time
    n = int(max(0, n))
    if n <= 0:
        return
    day_index += n
    current_time = 0
    refresh_seafood_daily_offer(force=True)
    refresh_black_market_offers(force=True)
    show_success_toast(f"Skipped {n} day(s).")


def black_market_open_today() -> bool:
    """Open on every 3rd day: Day 3, 6, 9, 12... (1-indexed)."""
    return ((int(day_index) + 1) % 3) == 0


def refresh_black_market_offers(force: bool = False):
    """Roll Black Market stock when an open day starts."""
    global black_market_day, black_market_offers
    if not black_market_open_today():
        return
    if (not force) and int(black_market_day) == int(day_index) and black_market_offers:
        return
    black_market_day = int(day_index)

    pool = []
    # Bakery items
    for nm, it in shop_items.items():
        pool.append({"kind": "item", "source": "Bakery", "name": nm, "base_price": int(it.price), "item": it})
    # Supermarket items
    for nm, it in SUPERMARKET_ITEMS.items():
        pool.append({"kind": "item", "source": "Supermarket", "name": nm, "base_price": int(it.price), "item": it})
    # Cafe drinks
    for d in CAFE_DRINKS:
        pool.append({"kind": "cafe", "source": "Cafe", "name": d["name"], "base_price": int(d["price"]), "drink": d})
    # Clothing shop entries
    for nm, d in clothing_items.items():
        pool.append({"kind": "clothing", "source": "Clothing", "name": nm, "base_price": int(d.get("price", 0) or 0)})

    # Choose 3 distinct random entries
    picks = random.sample(pool, k=min(3, len(pool))) if pool else []
    offers = [{"kind": "coupon", "source": "Black Market", "name": "Clothing Coupon", "base_price": 20}]
    for p in picks:
        offers.append(p)

    # Compute discounted prices (50% off), using effective price first.
    for o in offers:
        base = int(o.get("base_price", 0) or 0)
        eff = get_effective_price(base)
        o["price"] = max(0, int(math.ceil(eff * 0.5)))
        if o["kind"] == "coupon":
            o["price"] = 20

    black_market_offers = offers


def _cart_catalog():
    """Returns list of cart offerings (id, name, desc, cost)."""
    offers = []
    offers.append(("reel_zone", "Wider Reel Zone", "Makes the blue reel zone wider (easier to keep fish inside).", 120 + fish_upgrade_reel_zone * 120))
    offers.append(("hook_window", "Hook Master", "Gives you more time to hookset after a bite.", 140 + fish_upgrade_hook_window * 140))
    offers.append(("reel_power", "Fast Reel", "Reels fish in faster when you stay in the zone.", 160 + fish_upgrade_reel_power * 160))
    offers.append(("luck", "Lucky Lure", "Increases odds of rarer fish.", 220 + fish_upgrade_luck * 220))
    return offers


def draw_utility_cart_menu():
    """Utility cart upgrades (unlocked on Day 10)."""
    menu_rect = pygame.Rect(WINDOW_WIDTH // 7, WINDOW_HEIGHT // 7, int(WINDOW_WIDTH * 0.72), int(WINDOW_HEIGHT * 0.72))
    pygame.draw.rect(screen, (250, 252, 248), menu_rect, border_radius=12)
    pygame.draw.rect(screen, (35, 60, 50), menu_rect, 4, border_radius=12)

    pad = 18
    title = pygame.font.SysFont(None, 48).render("Utility Cart", True, (35, 60, 50))
    screen.blit(title, (menu_rect.x + pad, menu_rect.y + pad - 4))
    sub = pygame.font.SysFont(None, 22).render("Upgrades are permanent. Day 10+ only.", True, (80, 90, 95))
    screen.blit(sub, (menu_rect.x + pad, menu_rect.y + pad + 44))

    y = menu_rect.y + pad + 86
    x = menu_rect.x + pad
    w = menu_rect.width - pad * 2
    btn_h = 62
    gap = 10
    mouse = pygame.mouse.get_pos()

    buttons = []  # (rect, offer_id, can_buy)
    name_font = pygame.font.SysFont(None, 28)
    desc_font = pygame.font.SysFont(None, 20)
    cost_font = pygame.font.SysFont(None, 24)
    for oid, name, desc, cost in _cart_catalog():
        rect = pygame.Rect(x, y, w, btn_h)
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (255, 255, 255) if hover else (246, 250, 246), rect, border_radius=10)
        pygame.draw.rect(screen, (35, 60, 50), rect, 2, border_radius=10)

        can = money >= cost
        screen.blit(name_font.render(name, True, (20, 30, 25)), (rect.x + 12, rect.y + 8))
        screen.blit(desc_font.render(desc, True, (70, 80, 85)), (rect.x + 12, rect.y + 34))

        cost_s = cost_font.render(f"${cost}", True, (30, 110, 80) if can else (140, 90, 90))
        screen.blit(cost_s, cost_s.get_rect(midright=(rect.right - 14, rect.centery)))

        buttons.append((rect, oid, can))
        y += btn_h + gap

    close_rect = pygame.Rect(menu_rect.right - 46, menu_rect.top + 14, 32, 32)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    return buttons, close_rect


def handle_utility_cart_click(pos):
    global utility_cart_open, money
    global fish_upgrade_reel_zone, fish_upgrade_hook_window, fish_upgrade_reel_power, fish_upgrade_luck
    buttons, close_rect = draw_utility_cart_menu()
    if close_rect.collidepoint(pos):
        utility_cart_open = False
        return
    offers = {o[0]: o for o in _cart_catalog()}
    for rect, oid, can in buttons:
        if (not rect.collidepoint(pos)) or (not can):
            continue
        offer = offers.get(oid)
        if not offer:
            return
        cost = int(offer[3])
        if money < cost:
            show_failure_toast("Not enough money.")
            return
        money -= cost
        if oid == "reel_zone":
            fish_upgrade_reel_zone += 1
        elif oid == "hook_window":
            fish_upgrade_hook_window += 1
        elif oid == "reel_power":
            fish_upgrade_reel_power += 1
        elif oid == "luck":
            fish_upgrade_luck += 1
        show_success_toast("Upgrade purchased.")
        return


def draw_black_market_menu():
    """Black Market: coupon + 3 random 50%-off picks (every 3 days)."""
    refresh_black_market_offers()
    menu_rect = pygame.Rect(WINDOW_WIDTH // 7, WINDOW_HEIGHT // 7, int(WINDOW_WIDTH * 0.72), int(WINDOW_HEIGHT * 0.72))
    pygame.draw.rect(screen, (248, 246, 252), menu_rect, border_radius=12)
    pygame.draw.rect(screen, (40, 20, 55), menu_rect, 4, border_radius=12)

    pad = 18
    title = pygame.font.SysFont(None, 48).render("Black Market", True, (40, 20, 55))
    screen.blit(title, (menu_rect.x + pad, menu_rect.y + pad - 4))
    sub = pygame.font.SysFont(None, 22).render("Open every 3 days · 50% off rotating stock", True, (90, 85, 100))
    screen.blit(sub, (menu_rect.x + pad, menu_rect.y + pad + 44))

    if not black_market_open_today():
        msg = pygame.font.SysFont(None, 30).render("Closed today.", True, (140, 90, 110))
        screen.blit(msg, msg.get_rect(center=(menu_rect.centerx, menu_rect.centery)))
        close_rect = pygame.Rect(menu_rect.right - 46, menu_rect.top + 14, 32, 32)
        pygame.draw.rect(screen, RED, close_rect, border_radius=6)
        close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
        screen.blit(close_text, close_text.get_rect(center=close_rect.center))
        return [], close_rect

    y = menu_rect.y + pad + 90
    x = menu_rect.x + pad
    w = menu_rect.width - pad * 2
    row_h = 62
    gap = 10
    mouse = pygame.mouse.get_pos()
    name_font = pygame.font.SysFont(None, 28)
    desc_font = pygame.font.SysFont(None, 20)
    cost_font = pygame.font.SysFont(None, 24)

    buttons = []  # (rect, idx, can)
    for idx, o in enumerate(black_market_offers[:4]):
        rect = pygame.Rect(x, y, w, row_h)
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (255, 255, 255) if hover else (250, 248, 255), rect, border_radius=10)
        pygame.draw.rect(screen, (40, 20, 55), rect, 2, border_radius=10)

        price = int(o.get("price", 0) or 0)
        can = money >= price

        if o["kind"] == "coupon":
            nm = "Clothing Coupon"
            desc = "Next 3 clothing purchases are 50% off."
        else:
            nm = o["name"]
            desc = f"{o.get('source','Shop')} pick — 50% off"

        screen.blit(name_font.render(nm, True, (25, 20, 35)), (rect.x + 12, rect.y + 8))
        screen.blit(desc_font.render(desc, True, (85, 80, 95)), (rect.x + 12, rect.y + 34))

        cost_s = cost_font.render(f"${price}", True, (180, 60, 120) if can else (140, 90, 90))
        screen.blit(cost_s, cost_s.get_rect(midright=(rect.right - 14, rect.centery)))

        buttons.append((rect, idx, can))
        y += row_h + gap

    close_rect = pygame.Rect(menu_rect.right - 46, menu_rect.top + 14, 32, 32)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    return buttons, close_rect


def handle_black_market_click(pos):
    global black_market_open, money, clothing_coupon_uses
    if not black_market_open_today():
        black_market_open = False
        return
    buttons, close_rect = draw_black_market_menu()
    if close_rect.collidepoint(pos):
        black_market_open = False
        return
    for rect, idx, can in buttons:
        if (not can) or (not rect.collidepoint(pos)):
            continue
        if idx >= len(black_market_offers):
            return
        o = black_market_offers[idx]
        price = int(o.get("price", 0) or 0)
        if money < price:
            show_failure_toast("Not enough money.")
            return
        # Coupon
        if o["kind"] == "coupon":
            money -= price
            clothing_coupon_uses += 3
            show_success_toast("Clothing Coupon activated (3 uses).")
            return
        # Clothing
        if o["kind"] == "clothing":
            nm = o["name"]
            if nm not in clothing_items:
                return
            it = clothing_items[nm]
            if it.get("owned", False):
                for name in clothing_items:
                    clothing_items[name]["equipped"] = False
                it["equipped"] = True
                show_success_toast(f"Equipped {nm}.")
                return
            money -= price
            it["owned"] = True
            for name in clothing_items:
                clothing_items[name]["equipped"] = False
            it["equipped"] = True
            show_success_toast(f"Bought {nm}.")
            return
        # Cafe drink
        if o["kind"] == "cafe":
            d = o.get("drink")
            if not d:
                return
            coffee = ShopItem(d["name"], price, int(d.get("hunger_restore", 2)), "drink")
            coffee.coffee_mult = float(d["mult"])
            coffee.coffee_duration_ms = int(d["duration_ms"])
            coffee.coffee_source = True
            if not inventory_can_accept(coffee):
                show_failure_toast("Inventory full.")
                return
            money -= price
            try_add_inventory(coffee)
            show_success_toast(f"Bought {d['name']}.")
            return
        # Regular item
        src_item = o.get("item")
        if not src_item:
            return
        it = clone_item(src_item)
        it.price = price
        if not inventory_can_accept(it):
            show_failure_toast("Inventory full.")
            return
        money -= price
        try_add_inventory(it)
        show_success_toast(f"Bought {it.name}.")
        return


def draw_cheat_panel():
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(170)
    screen.blit(overlay, (0, 0))

    w = max(520, int(WINDOW_WIDTH * 0.46))
    h = max(420, int(WINDOW_HEIGHT * 0.46))
    menu = pygame.Rect((WINDOW_WIDTH - w) // 2, (WINDOW_HEIGHT - h) // 2, w, h)
    pygame.draw.rect(screen, (245, 245, 252), menu, border_radius=12)
    pygame.draw.rect(screen, (40, 40, 65), menu, 4, border_radius=12)

    pad = 18
    title = pygame.font.SysFont(None, 52).render("Cheat Panel", True, (40, 40, 65))
    screen.blit(title, (menu.x + pad, menu.y + pad - 6))
    hint = pygame.font.SysFont(None, 22).render("ADHDSWOP opens this panel. ESC closes.", True, (85, 85, 100))
    screen.blit(hint, (menu.x + pad, menu.y + pad + 44))

    btn_font = pygame.font.SysFont(None, 28)
    buttons = []
    bw = menu.width - pad * 2
    bh = 44
    gap = 12
    y = menu.y + pad + 96
    entries = [
        ("money", "+$10,000", (110, 220, 170)),
        ("xp", "+10,000 XP", (110, 190, 255)),
        ("day1", "Skip +1 day", (250, 210, 120)),
        ("day5", "Skip +5 days", (250, 180, 120)),
        ("close", "Close", (240, 120, 120)),
    ]
    mouse = pygame.mouse.get_pos()
    for key, label, col in entries:
        r = pygame.Rect(menu.x + pad, y, bw, bh)
        hov = r.collidepoint(mouse)
        draw_button(r, col, (25, 25, 40), hover=hov, radius=10)
        txt = btn_font.render(label, True, (20, 20, 30))
        screen.blit(txt, txt.get_rect(center=r.center))
        buttons.append((r, key))
        y += bh + gap

    return buttons


def handle_cheat_panel_click(pos):
    global cheat_panel_open, money, xp
    buttons = draw_cheat_panel()
    for r, key in buttons:
        if not r.collidepoint(pos):
            continue
        if key == "money":
            money += 10000
            show_success_toast("+$10,000.")
        elif key == "xp":
            xp += 10000
            check_level_up()
            show_success_toast("+10,000 XP.")
        elif key == "day1":
            skip_days(1)
        elif key == "day5":
            skip_days(5)
        elif key == "close":
            cheat_panel_open = False
        return


def _fish_weighted_roll(cast_q: float, reel_remain: float) -> tuple:
    """cast_q,reel_remain in ~0..1 improve rare odds slightly."""
    luck_boost = max(0.0, min(0.20, 0.05 * float(fish_upgrade_luck)))
    bonus_cap = 0.12 + luck_boost
    bonus = max(0.0, min(bonus_cap, (cast_q - 0.35) * 0.15 + (reel_remain - 0.5) * 0.08 + luck_boost * 0.5))
    weights = [max(0.02, w + bonus * (0.15 + i * 0.04)) for i, (*_, w) in enumerate(FISH_CATCH_TABLE)]
    s = sum(weights)
    r = random.random() * s
    acc = 0.0
    for i, row in enumerate(FISH_CATCH_TABLE):
        acc += weights[i]
        if r <= acc:
            return row[0], row[1], row[2]
    t = FISH_CATCH_TABLE[-1]
    return t[0], t[1], t[2]


def try_board_ferry_to_island():
    global money, ferry_anim_timer, ferry_anim_to_island
    if ferry_anim_timer > 0:
        return
    if money < FERRY_FARE:
        show_failure_toast(f"Need ${FERRY_FARE} for the ferry.")
        return
    money -= FERRY_FARE
    ferry_anim_to_island = True
    ferry_anim_timer = FERRY_CROSSING_FRAMES
    _fish_reset_minigame()
    show_success_toast("Casting off for Sun Reef…")


def try_board_ferry_to_city():
    global ferry_anim_timer, ferry_anim_to_island
    if ferry_anim_timer > 0:
        return
    ferry_anim_to_island = False
    ferry_anim_timer = FERRY_CROSSING_FRAMES
    _fish_reset_minigame()
    show_success_toast("Returning to the mainland…")


def island_near_ferry() -> bool:
    return island_player_x >= 20.0 and island_player_x <= 155.0


def island_in_fishing_zone() -> bool:
    return island_player_x >= 430.0


def update_ferry_animation_tick():
    global ferry_anim_timer, on_fishing_island, island_player_x, player_x
    if ferry_anim_timer <= 0:
        return
    ferry_anim_timer -= 1
    if ferry_anim_timer == 0:
        on_fishing_island = ferry_anim_to_island
        if on_fishing_island:
            island_player_x = 120.0
            show_success_toast("Welcome to Sun Reef — crystal water, slow time.")
        else:
            player_x = ferry_dock.original_x + 28


def draw_ferry_crossing_cinematic():
    t = 1.0 - (ferry_anim_timer / float(max(1, FERRY_CROSSING_FRAMES)))
    # Sky
    for y in range(WINDOW_HEIGHT):
        u = y / float(WINDOW_HEIGHT)
        c = (
            int(40 + u * 80),
            int(70 + u * 100),
            int(120 + u * 90),
        )
        pygame.draw.line(screen, c, (0, y), (WINDOW_WIDTH, y))
    # Sun / moon glow
    cx, cy = int(WINDOW_WIDTH * 0.72), int(80 + 40 * math.sin(t * math.pi))
    pygame.draw.circle(screen, (255, 230, 160), (cx, cy), 38)
    pygame.draw.circle(screen, (255, 250, 220), (cx, cy), 22)
    # Ocean layers
    base_y = 280
    for layer in range(5):
        oy = base_y + layer * 28
        col = (35 + layer * 12, 95 + layer * 15, 140 + layer * 10)
        pts = []
        for x in range(0, WINDOW_WIDTH + 16, 8):
            wave = 10 * math.sin(x * 0.02 + t * 14 + layer * 0.7) + 6 * math.sin(x * 0.05 - t * 9)
            pts.append((x, int(oy + wave)))
        pts.append((WINDOW_WIDTH, WINDOW_HEIGHT))
        pts.append((0, WINDOW_HEIGHT))
        if len(pts) > 3:
            pygame.draw.polygon(screen, col, pts)
    # Foam
    for x in range(0, WINDOW_WIDTH, 20):
        fx = int(x + 30 * math.sin(t * 8 + x * 0.1))
        pygame.draw.circle(screen, (220, 240, 252), (fx, base_y + 18), 3)

    # Ferry boat
    bx = int(-120 + t * (WINDOW_WIDTH + 240))
    by = 310
    pygame.draw.ellipse(screen, (55, 52, 58), (bx, by + 40, 160, 36))
    pygame.draw.rect(screen, (88, 82, 90), (bx + 20, by, 120, 48), border_radius=6)
    pygame.draw.rect(screen, (120, 200, 255), (bx + 36, by + 10, 36, 22), border_radius=4)
    pygame.draw.rect(screen, (40, 38, 44), (bx + 86, by + 8, 18, 34), border_radius=3)
    pygame.draw.polygon(screen, (70, 68, 75), [(bx + 140, by + 10), (bx + 168, by + 24), (bx + 140, by + 38)])
    lf = pygame.font.SysFont(None, 34)
    title = lf.render("SUN REEF LINE", True, (245, 250, 255))
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 56)))
    sub = pygame.font.SysFont(None, 22).render("Hold tight — salt wind & gulls ahead", True, (220, 235, 250))
    screen.blit(sub, sub.get_rect(center=(WINDOW_WIDTH // 2, 92)))
    bar_w = 280
    prog = pygame.Rect((WINDOW_WIDTH - bar_w) // 2, WINDOW_HEIGHT - 52, int(bar_w * t), 10)
    pygame.draw.rect(screen, (20, 30, 45), ((WINDOW_WIDTH - bar_w) // 2 - 2, WINDOW_HEIGHT - 54, bar_w + 4, 14), border_radius=6)
    pygame.draw.rect(screen, (100, 200, 255), prog, border_radius=4)


def _island_draw_sky():
    for y in range(WINDOW_HEIGHT):
        u = y / float(WINDOW_HEIGHT)
        r = int(255 - u * 120)
        g = int(190 - u * 70)
        b = int(220 - u * 40)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
    cx, cy = WINDOW_WIDTH - 120, 85
    pygame.draw.circle(screen, (255, 248, 210), (cx, cy), 45)
    pygame.draw.circle(screen, (255, 255, 245), (cx, cy), 28)
    for i in range(3):
        pygame.draw.arc(screen, (255, 250, 230), (cx - 60 + i * 8, cy - 60 + i * 6, 120, 120), 0.8, 2.2, 2)


def _island_draw_ocean(surf_t: float):
    horizon = 240
    pygame.draw.rect(screen, (72, 140, 185), (0, horizon, WINDOW_WIDTH, WINDOW_HEIGHT - horizon))
    for layer in range(6):
        oy = horizon + 8 + layer * 14
        shade = 72 + layer * 8
        col = (shade, 130 + layer * 6, 175 + layer * 5)
        pts = []
        for x in range(-8, WINDOW_WIDTH + 8, 6):
            w = 9 * math.sin(x * 0.018 + surf_t * 0.08 + layer * 0.9)
            w += 5 * math.sin(x * 0.04 - surf_t * 0.05)
            pts.append((x, int(oy + w)))
        pts += [(WINDOW_WIDTH + 8, WINDOW_HEIGHT), (-8, WINDOW_HEIGHT)]
        pygame.draw.polygon(screen, col, pts)
    for x in range(0, WINDOW_WIDTH, 14):
        px = int(x + 20 * math.sin(surf_t * 0.12 + x * 0.05))
        pygame.draw.circle(screen, (230, 248, 255), (px, horizon + 6), 3)


def _island_draw_palm(px, base_y, sway):
    trunk_top = base_y - 90
    pygame.draw.rect(screen, (120, 78, 48), (px - 6, trunk_top, 12, 95), border_radius=4)
    pygame.draw.rect(screen, (90, 58, 38), (px - 6, trunk_top, 12, 95), 2, border_radius=4)
    for i in range(7):
        ang = -1.2 + i * 0.35 + sway * 0.08
        lx = px + int(math.cos(ang) * 72)
        ly = trunk_top + int(math.sin(ang) * 28)
        pygame.draw.line(screen, (40, 120, 72), (px, trunk_top), (lx, ly), 5)
        pygame.draw.line(screen, (70, 160, 95), (px, trunk_top), (lx, ly), 2)


def draw_fishing_island_scene():
    global island_ambient_frame
    island_ambient_frame += 1
    st = island_ambient_frame * 0.02
    _island_draw_sky()
    _island_draw_ocean(st)
    # distant islet
    pygame.draw.circle(screen, (85, 140, 110), (90, 220), 28)
    pygame.draw.circle(screen, (95, 150, 118), (78, 212), 14)
    # Beach / sand
    sand_pts = [(0, ISLAND_FEET_Y + 8), (0, WINDOW_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT), (WINDOW_WIDTH, 360), (620, 320), (480, ISLAND_FEET_Y - 12), (320, ISLAND_FEET_Y + 4), (120, ISLAND_FEET_Y + 20)]
    pygame.draw.polygon(screen, (238, 220, 170), sand_pts)
    pygame.draw.polygon(screen, (210, 188, 140), sand_pts, 3)
    for i in range(25):
        sx = int(40 + (i * 73) % (WINDOW_WIDTH - 80))
        sy = ISLAND_FEET_Y + 12 + (i * 17) % 40
        pygame.draw.ellipse(screen, (228, 208, 175), (sx, sy, 10 + (i % 4), 4))
    # Sparkles
    for i in range(18):
        sx = int(50 + (i * 97 + island_ambient_frame) % (WINDOW_WIDTH - 100))
        sy = ISLAND_FEET_Y - 10 + int(8 * math.sin(st + i))
        al = int(80 + 80 * math.sin(st * 2 + i))
        sp = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(sp, (255, 255, 245, al), (3, 3), 2)
        screen.blit(sp, (sx, sy))
    # Rocks at fishing point
    for rx, ry, rw in ((540, ISLAND_FEET_Y - 35, 38), (600, ISLAND_FEET_Y - 22, 52), (680, ISLAND_FEET_Y - 40, 44)):
        pygame.draw.polygon(screen, (88, 92, 98), [(rx, ry), (rx + rw, ry - 8), (rx + rw - 6, ry + 28), (rx - 10, ry + 22)])
        pygame.draw.polygon(screen, (55, 58, 62), [(rx, ry), (rx + rw, ry - 8), (rx + rw - 6, ry + 28), (rx - 10, ry + 22)], 2)
    # Fishing marker (so it's obvious where to start)
    if fish_phase == "idle":
        fx, fy = 620, int(ISLAND_FEET_Y - 64)
        glow = pygame.Surface((200, 90), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (120, 220, 255, 42), (0, 28, 200, 56))
        pygame.draw.ellipse(glow, (255, 255, 255, 26), (20, 34, 160, 44))
        screen.blit(glow, (fx - 100, fy - 20))
        tipf = pygame.font.SysFont(None, 24)
        tip = tipf.render("F: Fish here", True, (30, 45, 60))
        pygame.draw.rect(screen, (255, 245, 230), tip.get_rect(center=(fx, fy)).inflate(18, 10), border_radius=10)
        pygame.draw.rect(screen, (120, 200, 255), tip.get_rect(center=(fx, fy)).inflate(18, 10), 2, border_radius=10)
        screen.blit(tip, tip.get_rect(center=(fx, fy)))
    # Palms
    _island_draw_palm(160, ISLAND_FEET_Y + 35, math.sin(st))
    _island_draw_palm(280, ISLAND_FEET_Y + 40, math.sin(st + 1))
    _island_draw_palm(WINDOW_WIDTH - 100, ISLAND_FEET_Y + 32, math.sin(st + 2))
    # Docked ferry
    pygame.draw.ellipse(screen, (60, 58, 64), (8, ISLAND_FEET_Y - 28, 130, 34))
    pygame.draw.rect(screen, (92, 88, 95), (28, ISLAND_FEET_Y - 78, 96, 52), border_radius=5)
    pygame.draw.rect(screen, (130, 210, 255), (44, ISLAND_FEET_Y - 64, 32, 22), border_radius=3)
    pygame.draw.rect(screen, (45, 120, 160), (0, ISLAND_FEET_Y - 6, 200, 120))
    pygame.draw.rect(screen, (55, 130, 175), (0, ISLAND_FEET_Y - 6, 200, 14), border_radius=4)
    # Gulls
    for g in range(4):
        gx = int(200 + g * 160 + 40 * math.sin(st * 1.2 + g))
        gy = int(60 + g * 25 + 10 * math.sin(st * 0.8 + g))
        pygame.draw.arc(screen, (245, 248, 255), (gx, gy, 22, 14), 0.2, 2.8, 2)
    # Driftwood + shell
    pygame.draw.ellipse(screen, (150, 118, 88), (340, ISLAND_FEET_Y + 8, 62, 14))
    pygame.draw.circle(screen, (255, 228, 220), (410, ISLAND_FEET_Y + 22), 8)
    pygame.draw.circle(screen, (200, 160, 150), (410, ISLAND_FEET_Y + 22), 8, 2)
    # Sign
    sf = pygame.font.SysFont(None, 26)
    screen.blit(sf.render("SUN REEF · fishing cove", True, (60, 45, 35)), (420, ISLAND_FEET_Y - 118))
    draw_player(int(island_player_x), ISLAND_FEET_Y - player_height)
    # Bobber / minigame layers
    if fish_phase in ("wait", "hookset", "reel"):
        bx = min(WINDOW_WIDTH - 40, max(460, 520 + int(30 * math.sin(st * 3))))
        by = 248 + int(6 * math.sin(st * 4))
        if fish_phase == "wait":
            pygame.draw.circle(screen, (240, 90, 70), (bx, int(by)), 5)
            pygame.draw.line(screen, (60, 50, 40), (bx, int(by)), (bx, int(by) - 40), 2)
            for ri in range(3):
                pygame.draw.circle(screen, (255, 255, 255, 60), (bx, int(by)), 16 + ri * 10, 1)
        elif fish_phase == "hookset":
            pygame.draw.circle(screen, (255, 220, 60), (bx, int(by)), 8)
        elif fish_phase == "reel":
            pygame.draw.circle(screen, (255, 100, 80), (bx, int(by)), 6)
            pygame.draw.line(screen, (50, 40, 35), (bx, int(by)), (int(island_player_x) + 20, ISLAND_FEET_Y - 40), 2)
    for sx, sy, vy, life in fish_splash[:]:
        pygame.draw.circle(screen, (220, 240, 255), (int(sx), int(sy)), 3)
    _draw_fishing_minigame_overlay()


def _draw_fishing_minigame_overlay():
    if fish_phase == "idle":
        return
    panel = pygame.Surface((WINDOW_WIDTH, 120), pygame.SRCALPHA)
    panel.fill((12, 18, 28, 210))
    screen.blit(panel, (0, WINDOW_HEIGHT - 120))
    font = pygame.font.SysFont(None, 26)
    small = pygame.font.SysFont(None, 22)
    y0 = WINDOW_HEIGHT - 112
    if fish_phase == "cast":
        screen.blit(font.render("Hold SPACE — build cast power, release to throw", True, WHITE), (20, y0))
        pw = int(min(1.0, fish_cast_power) * 360)
        pygame.draw.rect(screen, (40, 50, 60), (20, y0 + 36, 360, 16), border_radius=6)
        pygame.draw.rect(screen, (100, 200, 255), (20, y0 + 36, pw, 16), border_radius=6)
        screen.blit(small.render("Better casts nudge rare fish odds", True, (200, 210, 220)), (20, y0 + 58))
    elif fish_phase == "wait":
        screen.blit(font.render("Watching the bobber… stay ready", True, (200, 235, 255)), (20, y0))
    elif fish_phase == "hookset":
        rem = max(0, fish_hook_deadline_tick - pygame.time.get_ticks())
        screen.blit(font.render("STRIKE! TAP SPACE NOW!", True, (255, 230, 80)), (20, y0))
        screen.blit(small.render(f"{rem // 40 + 1}…", True, WHITE), (20, y0 + 34))
    elif fish_phase == "reel":
        screen.blit(font.render("Reel! Keep the fish inside your blue bar (A / D)", True, WHITE), (20, y0))
        bar_x, bar_y, bar_w, bar_h = 20, y0 + 34, 360, 28
        pygame.draw.rect(screen, (35, 40, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        z_half = 0.14 + min(0.10, 0.03 * float(fish_upgrade_reel_zone))
        pc = bar_x + int(fish_player_center * bar_w)
        zl = int(max(bar_x + 4, pc - z_half * bar_w))
        zr = int(min(bar_x + bar_w - 4, pc + z_half * bar_w))
        zs = pygame.Surface((max(8, zr - zl), bar_h - 6), pygame.SRCALPHA)
        pygame.draw.rect(zs, (70, 140, 220, 140), zs.get_rect(), border_radius=4)
        screen.blit(zs, (zl, bar_y + 3))
        fx = bar_x + int(max(0, min(1, fish_pos)) * bar_w)
        pygame.draw.circle(screen, (255, 180, 100), (fx, bar_y + bar_h // 2), 10)
        pygame.draw.circle(screen, (80, 60, 40), (fx, bar_y + bar_h // 2), 10, 2)
        pr = int(max(0, min(100, fish_reel_progress)))
        pygame.draw.rect(screen, (30, 35, 45), (400, bar_y, 180, bar_h), border_radius=6)
        pygame.draw.rect(screen, (80, 220, 160), (400, bar_y, int(1.8 * pr), bar_h), border_radius=6)
        screen.blit(small.render(f"Tension {pr}%", True, (200, 255, 220)), (400, y0))
    elif fish_phase == "win":
        nm = fish_pending_roll[0] if fish_pending_roll else "Fish"
        screen.blit(font.render(f"Caught: {nm}!", True, (120, 255, 190)), (20, y0))
        screen.blit(small.render("SPACE to continue", True, (220, 225, 230)), (20, y0 + 36))
    elif fish_phase == "lose":
        screen.blit(font.render("It got away…", True, (255, 200, 200)), (20, y0))
        screen.blit(small.render("SPACE to try again", True, (220, 220, 230)), (20, y0 + 36))


def update_fishing_minigame(keys):
    global fish_phase, fish_cast_power, fish_wait_until_tick, fish_hook_deadline_tick
    global fish_reel_progress, fish_pos, fish_vel, fish_player_center, fish_struggle_phase, fish_pending_roll, fish_splash
    now = pygame.time.get_ticks()
    if fish_phase == "cast":
        if keys[pygame.K_SPACE]:
            fish_cast_power = min(1.0, fish_cast_power + 0.022)
        else:
            if fish_cast_power >= 0.12:
                fish_phase = "wait"
                fish_wait_until_tick = now + random.randint(900, 2800)
                fish_splash = []
            else:
                fish_cast_power = max(0.0, fish_cast_power - 0.04)
    elif fish_phase == "wait":
        if now >= fish_wait_until_tick:
            fish_phase = "hookset"
            fish_hook_deadline_tick = now + 420 + int(120 * float(fish_upgrade_hook_window))
    elif fish_phase == "hookset":
        if now > fish_hook_deadline_tick:
            fish_phase = "lose"
    elif fish_phase == "reel":
        fish_struggle_phase += 0.09
        # 4× slower fish movement (player feedback): reduce all impulses.
        fish_vel += (random.random() - 0.5) * 0.01
        fish_vel += 0.0045 * math.sin(fish_struggle_phase * 1.7)
        fish_vel += 0.0030 * math.sin(fish_struggle_phase * 0.5 + fish_pos * 6)
        fish_vel *= 0.92
        fish_pos += fish_vel
        if fish_pos < 0.08 or fish_pos > 0.92:
            fish_vel *= -0.55
            fish_pos = max(0.08, min(0.92, fish_pos))
        acc = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            acc -= 0.006
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            acc += 0.006
        fish_player_center = max(0.14, min(0.86, fish_player_center + acc))
        z_half = 0.14 + min(0.10, 0.03 * float(fish_upgrade_reel_zone))
        if abs(fish_pos - fish_player_center) < z_half:
            reel_gain = 1.35 * (1.0 + 0.15 * float(fish_upgrade_reel_power))
            fish_reel_progress = min(100.0, fish_reel_progress + reel_gain)
        else:
            fish_reel_progress = max(0.0, fish_reel_progress - 0.35)
        if fish_reel_progress >= 100.0:
            cq = min(1.0, fish_cast_power + 0.1)
            rm = fish_reel_progress / 100.0
            nm, pr, hu = _fish_weighted_roll(cq, rm)
            fish_pending_roll = (nm, pr, hu)
            fish_phase = "win"
        elif fish_reel_progress <= 0.0:
            fish_phase = "lose"
    # splash particles decay
    new_sp = []
    for sx, sy, vy, life in fish_splash:
        life -= 1
        if life > 0:
            new_sp.append((sx, sy + vy, vy + 0.2, life))
    fish_splash = new_sp


def fishing_try_hookset():
    global fish_phase, fish_hook_deadline_tick, fish_reel_progress, fish_pos, fish_vel, fish_struggle_phase
    now = pygame.time.get_ticks()
    if fish_phase == "hookset" and now <= fish_hook_deadline_tick:
        fish_phase = "reel"
        fish_reel_progress = 22.0
        fish_pos = 0.5
        fish_vel = random.choice([-0.04, 0.04])
        fish_struggle_phase = random.random() * 6.28
        fish_hook_deadline_tick = 0
        fish_splash.clear()
        for _ in range(12):
            fish_splash.append((520 + random.uniform(-20, 20), 255, random.uniform(-2, -0.5), 25))


def fishing_try_begin_cast():
    global fish_phase, fish_cast_power
    if fish_phase != "idle":
        return
    fish_phase = "cast"
    fish_cast_power = 0.0


def fishing_resolve_end():
    global fish_phase, fish_pending_roll, xp
    if fish_phase == "win" and fish_pending_roll:
        nm, pr, hu = fish_pending_roll
        it = _fish_make_item(nm, pr, hu)
        if inventory_can_accept(it):
            try_add_inventory(it)
            xp_gain = 35 + pr // 4
            xp += xp_gain
            check_level_up()
            show_success_toast(f"You caught a {nm}! (+{xp_gain} XP)")
        else:
            show_failure_toast("Inventory full — fish slipped back into the surf.")
        fish_pending_roll = None
    _fish_reset_minigame()


def fishing_on_space_key():
    if fish_phase == "hookset":
        fishing_try_hookset()
    elif fish_phase == "win":
        fishing_resolve_end()
    elif fish_phase == "lose":
        _fish_reset_minigame()


def draw_house_lobby_menu():
    border = (52, 92, 58)
    title = "Your House"
    info_font = get_font(26)
    btn_font = get_font(30, bold=True)

    # Dynamic sizing + wrapping so long strings never overflow.
    max_w = min(int(WINDOW_WIDTH * 0.76), 640)
    inner_pad = 22
    content_w = max_w - inner_pad * 2
    exp = house_expansion_level
    lines = []
    lines += wrap_text_lines(info_font, f"Deed: ${HOUSE_PURCHASE_COST} one-time · unlimited visits", content_w)
    lines += wrap_text_lines(info_font, f"Expansion: L{exp}/2 (L1 wider + camera · L2 loft + ladder)", content_w)
    content_h = sum(info_font.get_height() + 4 for _ in lines)
    menu_h = 170 + content_h  # title band + wrapped text + button + breathing room
    menu_h = max(260, min(int(WINDOW_HEIGHT * 0.62), menu_h))
    menu_w = max_w
    menu_x = (WINDOW_WIDTH - menu_w) // 2
    menu_y = (WINDOW_HEIGHT - menu_h) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
    # Use a neutral title color for readability.
    draw_panel(menu_rect, border, title=title, title_color=(25, 35, 30))

    y = menu_rect.y + 72
    x = menu_rect.x + inner_pad
    for ln in lines[:]:
        surf = info_font.render(ln, True, (35, 35, 35))
        screen.blit(surf, (x, y))
        y += surf.get_height() + 4

    enter_rect = pygame.Rect(menu_rect.x + inner_pad, y + 14, menu_rect.width - inner_pad * 2, 50)
    hover = enter_rect.collidepoint(pygame.mouse.get_pos())
    draw_button(enter_rect, BUTTON_HOVER if hover else BUTTON_COLOR, border, hover=hover, radius=10)
    lab = "Enter home" if house_owned else f"Buy deed (${HOUSE_PURCHASE_COST})"
    et = btn_font.render(lab, True, BLACK)
    screen.blit(et, et.get_rect(center=enter_rect.center))

    # Slightly larger hitbox so it's easy to click.
    close_rect = pygame.Rect(menu_rect.right - 52, menu_rect.top + 12, 38, 34)
    pygame.draw.rect(screen, RED, close_rect, border_radius=7)
    xt = get_font(30, bold=True).render("X", True, WHITE)
    screen.blit(xt, xt.get_rect(center=close_rect.center))
    return enter_rect, close_rect


def draw_house_furniture_sprite(kind: str, sx: float, top_y: float):
    if kind == "bed":
        r = pygame.Rect(int(sx), int(top_y), HOUSE_FURNITURE["bed"]["w"], HOUSE_FURNITURE["bed"]["h"])
        pygame.draw.rect(screen, (210, 208, 220), r, border_radius=12)
        pygame.draw.rect(screen, (150, 148, 165), r, 3, border_radius=12)
        pygame.draw.rect(screen, (240, 240, 250), (r.x + 18, r.y + 14, 70, 26), border_radius=6)
    elif kind == "microwave":
        r = pygame.Rect(int(sx), int(top_y), HOUSE_FURNITURE["microwave"]["w"], HOUSE_FURNITURE["microwave"]["h"])
        pygame.draw.rect(screen, (130, 130, 132), r, border_radius=8)
        pygame.draw.rect(screen, (45, 45, 48), r, 2, border_radius=8)
        pygame.draw.rect(screen, (28, 28, 30), (r.x + 12, r.y + 10, 78, 32), border_radius=4)
        pygame.draw.circle(screen, (220, 70, 70), (r.right - 18, r.centery), 6)
    elif kind == "stove":
        r = pygame.Rect(int(sx), int(top_y), HOUSE_FURNITURE["stove"]["w"], HOUSE_FURNITURE["stove"]["h"])
        pygame.draw.rect(screen, (62, 34, 22), r, border_radius=7)
        pygame.draw.rect(screen, (28, 14, 10), r, 2, border_radius=7)
        pygame.draw.circle(screen, ORANGE, (r.centerx, r.y + 16), 4)
        pygame.draw.circle(screen, ORANGE, (r.centerx, r.y + 34), 4)
    elif kind == "sink":
        r = pygame.Rect(int(sx), int(top_y), HOUSE_FURNITURE["sink"]["w"], HOUSE_FURNITURE["sink"]["h"])
        pygame.draw.rect(screen, (200, 210, 220), r, border_radius=8)
        pygame.draw.rect(screen, (120, 140, 155), r, 2, border_radius=8)
        pygame.draw.ellipse(screen, (170, 190, 205), (r.x + 14, r.y + 10, r.w - 28, r.h - 22))
    elif kind == "grill":
        r = pygame.Rect(int(sx), int(top_y), HOUSE_FURNITURE["grill"]["w"], HOUSE_FURNITURE["grill"]["h"])
        pygame.draw.rect(screen, (55, 55, 62), r, border_radius=10)
        pygame.draw.rect(screen, (20, 20, 24), r, 2, border_radius=10)
        pygame.draw.rect(screen, (90, 90, 98), (r.x + 10, r.y + 10, r.w - 20, 10), border_radius=5)
        for i in range(5):
            pygame.draw.line(screen, (140, 140, 150), (r.x + 14 + i * 12, r.y + 22), (r.x + 14 + i * 12, r.y + r.h - 10), 2)
        pygame.draw.circle(screen, (255, 120, 20), (r.right - 16, r.y + 16), 5)
    elif kind == "seasoner":
        r = pygame.Rect(int(sx), int(top_y), HOUSE_FURNITURE["seasoner"]["w"], HOUSE_FURNITURE["seasoner"]["h"])
        pygame.draw.rect(screen, (190, 185, 175), r, border_radius=10)
        pygame.draw.rect(screen, (95, 85, 75), r, 2, border_radius=10)
        pygame.draw.rect(screen, (160, 150, 140), (r.x + 14, r.y + 10, r.w - 28, r.h - 20), border_radius=6)
        for i in range(3):
            pygame.draw.circle(screen, (240, 235, 225), (r.x + 20 + i * 10, r.y + 16), 2)


def draw_house_room():
    global house_notice_timer
    iw = house_interior_width()
    off = int(house_cam_offset)
    screen.fill((24, 22, 32))
    pygame.draw.rect(screen, (38, 34, 48), (0, 0, WINDOW_WIDTH, 108))
    pygame.draw.rect(screen, (30, 28, 40), (0, 108, WINDOW_WIDTH, WINDOW_HEIGHT))
    floor0 = house_floor_feet_y(0)
    pygame.draw.rect(screen, (86, 72, 58), (-off, floor0 - 6, max(iw, WINDOW_WIDTH) + off + 80, WINDOW_HEIGHT))
    pygame.draw.rect(screen, (62, 52, 44), (-off, floor0 - 2, max(iw, WINDOW_WIDTH) + off + 80, 14), border_radius=4)

    if house_expansion_level >= 2:
        f1 = house_floor_feet_y(1)
        pygame.draw.rect(screen, (74, 70, 88), (-off, f1 - 150, iw + 80, 22), border_radius=8)
        pygame.draw.rect(screen, (78, 74, 92), (-off, f1 - 6, iw + 80, 12), border_radius=4)
        lx = HOUSE_LADDER_CX - off
        for fl in (0, 1):
            fy = house_floor_feet_y(fl)
            pygame.draw.rect(screen, (96, 64, 40), (lx - 24, fy - 146, 48, 142), border_radius=8)
            pygame.draw.line(screen, (62, 42, 26), (lx, fy - 138), (lx, fy - 8), 4)
        pygame.draw.rect(screen, (245, 220, 150), (lx - 30, floor0 - 128, 60, 16), border_radius=5)

    for b in house_buildings:
        br = house_building_rect(b)
        sx = float(br.x - off)
        if sx + br.w < 0 or sx > WINDOW_WIDTH:
            continue
        draw_house_furniture_sprite(b["kind"], sx, float(br.y))

    if house_place_pick:
        mx, my = pygame.mouse.get_pos()
        wx = float(mx + off)
        cxg = house_snap_cx(wx)
        flg = house_player_floor
        gr = house_furniture_world_rect(house_place_pick, cxg, flg)
        gsx = float(gr.x - off)
        ok = not house_new_furniture_collides(house_place_pick, cxg, flg)
        col = (80, 220, 160, 110) if ok else (240, 90, 90, 110)
        gh = pygame.Surface((gr.w, gr.h), pygame.SRCALPHA)
        gh.fill(col)
        screen.blit(gh, (int(gsx), int(gr.y)))

    # Mini-map (house only): shows horizontal position + floor
    map_w, map_h = 150, 86
    map_x = WINDOW_WIDTH - map_w - 18
    map_y = 132
    mm = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
    pygame.draw.rect(mm, (10, 12, 18, 210), (0, 0, map_w, map_h), border_radius=10)
    pygame.draw.rect(mm, (140, 200, 255, 230), (0, 0, map_w, map_h), 2, border_radius=10)
    iwf = float(max(1, house_interior_width()))
    # floors
    y0 = int(map_h * 0.70)
    y1 = int(map_h * 0.30)
    pygame.draw.line(mm, (110, 120, 140, 220), (10, y0), (map_w - 10, y0), 2)
    if house_expansion_level >= 2:
        pygame.draw.line(mm, (110, 120, 140, 220), (10, y1), (map_w - 10, y1), 2)
    # ladder marker
    lx = int(10 + (HOUSE_LADDER_CX / iwf) * (map_w - 20))
    pygame.draw.line(mm, (245, 220, 150, 230), (lx, 10), (lx, map_h - 10), 2)
    # player dot
    pxn = float(house_player_x) / iwf
    pxm = int(10 + pxn * (map_w - 20))
    pym = y0 if int(house_player_floor) == 0 else y1
    pygame.draw.circle(mm, (80, 220, 160, 240), (pxm, pym), 5)
    pygame.draw.circle(mm, (0, 0, 0, 200), (pxm, pym), 5, 2)
    # tiny title
    mm.blit(pygame.font.SysFont(None, 18).render("HOME", True, (210, 230, 255)), (10, 8))
    screen.blit(mm, (map_x, map_y))

    px_screen = int(house_player_x - off)
    feet_y = house_floor_feet_y(house_player_floor)
    # draw_player expects top-left y (like the world simulation)
    draw_player(px_screen, feet_y - player_height)

    small = pygame.font.SysFont(None, 22)
    screen.blit(
        small.render(
            "ESC leave  ·  B catalog  ·  E / V / Z use  ·  right / middle / Shift+click remove (50% refund)",
            True,
            (235, 232, 250),
        ),
        (14, 12),
    )
    if house_notice_timer > 0:
        msg = pygame.font.SysFont(None, 28).render(house_notice_text, True, WHITE)
        rr = msg.get_rect(center=(WINDOW_WIDTH // 2, 64))
        pygame.draw.rect(screen, (0, 0, 0), rr.inflate(18, 10))
        screen.blit(msg, rr)


def house_player_body_screen_rect() -> pygame.Rect:
    off = int(house_cam_offset)
    px = int(house_player_x - off)
    fy = house_floor_feet_y(house_player_floor)
    top = int(fy - player_height)
    return pygame.Rect(px, top, int(player_width), int(player_height))


def house_near_interaction_kinds() -> list:
    body = house_player_body_screen_rect().inflate(26, 18)
    hits = []
    for b in house_buildings:
        if int(b["floor"]) != int(house_player_floor):
            continue
        br = house_building_rect(b)
        sr = pygame.Rect(br.x - int(house_cam_offset), br.y, br.w, br.h).inflate(16, 12)
        if sr.colliderect(body):
            hits.append((b["kind"], sr.centerx))
    if house_expansion_level >= 2:
        lr = house_ladder_block_world(house_player_floor)
        lr2 = pygame.Rect(lr.x - int(house_cam_offset), lr.y, lr.w, lr.h).inflate(10, 0)
        if lr2.colliderect(body):
            hits.append(("ladder", lr2.centerx))
    hits.sort(key=lambda t: t[1])
    return [h[0] for h in hits]


def draw_house_room_prompts(keys_list: list):
    if not keys_list:
        return
    labels = {
        "bed": "Sleep",
        "microwave": "Microwave",
        "stove": "Stove",
        "sink": "Sink (water)",
        "seasoner": "Season food (+35%)",
        "grill": "Grill",
        "ladder": "Climb loft" if house_player_floor == 0 else "Climb down",
    }
    font = pygame.font.SysFont(None, 24)
    base_y = WINDOW_HEIGHT // 2 + 110
    for i, kind in enumerate(keys_list[:3]):
        kch = ("E", "V", "Z")[i]
        lab = labels.get(kind, kind)
        txt = font.render(f"{kch}: {lab}", True, (248, 246, 255))
        r = txt.get_rect(center=(WINDOW_WIDTH // 2, base_y + i * 28))
        pygame.draw.rect(screen, (12, 12, 22), r.inflate(16, 8), border_radius=8)
        pygame.draw.rect(screen, (140, 200, 255), r.inflate(16, 8), 2, border_radius=8)
        screen.blit(txt, r)


def draw_house_build_menu():
    """Catalog + expansions; click item then click floor to place (ghost)."""
    global house_build_scroll
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(165)
    screen.blit(overlay, (0, 0))
    panel = pygame.Rect(WINDOW_WIDTH // 2 - 320, 60, 640, WINDOW_HEIGHT - 120)
    pygame.draw.rect(screen, (34, 32, 44), panel, border_radius=14)
    pygame.draw.rect(screen, (160, 210, 255), panel, 2, border_radius=14)
    title = pygame.font.SysFont(None, 36).render("Build & expand", True, WHITE)
    screen.blit(title, (panel.x + 22, panel.y + 14))
    body = pygame.font.SysFont(None, 22)
    f_main = pygame.font.SysFont(None, 24)
    f_lock = pygame.font.SysFont(None, 20)
    # Scrollable content region
    content_top = panel.y + 52
    content_bottom = panel.bottom - 18
    viewport_h = content_bottom - content_top
    clip = pygame.Rect(panel.x + 12, content_top, panel.width - 24, viewport_h)

    instr = "Pick furniture, close with B, then click the floor to place (ghost). ESC cancels pick."
    instr_lines = wrap_text_lines(body, instr, panel.width - 44)
    instr_h = sum(body.get_height() + 2 for _ in instr_lines)
    doc_h = instr_h + 10
    for _kind, sp in HOUSE_FURNITURE.items():
        lock = ""
        if sp["chef"] and not has_skill("Master Chef"):
            lock = "x"
        elif sp["coffee"] and not mission_coffee_guy_done:
            lock = "x"
        row_h = 44 if lock else 40
        doc_h += row_h + 6
    doc_h += 10 + 34 + 40 + 8 + 40 + 16
    max_scroll = max(0, int(doc_h - viewport_h))
    house_build_scroll = max(0, min(int(house_build_scroll), max_scroll))

    prev = screen.get_clip()
    screen.set_clip(clip)

    y = content_top - int(house_build_scroll)
    for ln in instr_lines:
        surf = body.render(ln, True, (210, 210, 220))
        screen.blit(surf, (panel.x + 22, y))
        y += surf.get_height() + 2
    y += 10
    mouse = pygame.mouse.get_pos()
    buttons = []
    for kind, sp in HOUSE_FURNITURE.items():
        lock = ""
        if sp["chef"] and not has_skill("Master Chef"):
            lock = " (need Master Chef)"
        elif sp["coffee"] and not mission_coffee_guy_done:
            lock = " (complete Coffee guy)"
        row_h = 44 if lock else 40
        row = pygame.Rect(panel.x + 18, y, panel.width - 36, row_h)
        hover = row.collidepoint(mouse)
        pygame.draw.rect(screen, (58, 56, 72) if hover else (48, 46, 60), row, border_radius=8)
        pygame.draw.rect(screen, (120, 180, 255), row, 2, border_radius=8)
        price = sp["price"]
        lab_main = f"{kind.title()}  ${price}"
        screen.blit(f_main.render(lab_main, True, WHITE), (row.x + 12, row.y + 8))
        if lock:
            screen.blit(f_lock.render(lock.strip(), True, (210, 210, 220)), (row.x + 12, row.y + 26))
        buttons.append((row, kind, lock == ""))
        y += row_h + 6
    y += 10
    screen.blit(pygame.font.SysFont(None, 26).render("Expansions", True, (255, 230, 180)), (panel.x + 18, y))
    y += 34
    r1 = pygame.Rect(panel.x + 18, y, panel.width - 36, 40)
    can1 = house_expansion_level < 1 and money >= HOUSE_EXPAND_L1_COST
    pygame.draw.rect(screen, (70, 120, 70) if can1 else (70, 70, 70), r1, border_radius=8)
    screen.blit(body.render(f"Level 1 — wider room + camera  ${HOUSE_EXPAND_L1_COST}", True, WHITE), (r1.x + 10, r1.y + 10))
    buttons.append((r1, "expand1", can1))
    y += 48
    r2 = pygame.Rect(panel.x + 18, y, panel.width - 36, 40)
    can2 = house_expansion_level == 1 and money >= HOUSE_EXPAND_L2_COST
    pygame.draw.rect(screen, (70, 120, 70) if can2 else (70, 70, 70), r2, border_radius=8)
    screen.blit(body.render(f"Level 2 — loft + ladder  ${HOUSE_EXPAND_L2_COST}", True, WHITE), (r2.x + 10, r2.y + 10))
    buttons.append((r2, "expand2", can2))
    screen.set_clip(prev)

    return buttons


def handle_house_build_click(pos, buttons):
    global money, house_expansion_level, house_place_pick, house_build_menu_open, house_player_x
    for row, key, ok in buttons:
        if not row.collidepoint(pos):
            continue
        if key in ("expand1", "expand2"):
            if not ok:
                show_failure_toast("Can't buy that expansion yet.")
                return
            if key == "expand1" and house_expansion_level < 1:
                money -= HOUSE_EXPAND_L1_COST
                house_expansion_level = 1
                house_clamp_player()
                house_update_camera()
                show_success_toast("Expansion 1 — room widened, camera follows you.")
            elif key == "expand2" and house_expansion_level < 2:
                if house_expansion_level < 1:
                    show_failure_toast("Buy expansion level 1 before adding the loft.")
                    return
                money -= HOUSE_EXPAND_L2_COST
                house_expansion_level = 2
                show_success_toast("Expansion 2 — loft and ladder added.")
            return
        if not ok:
            show_failure_toast("Locked — read the requirement on this row.")
            return
        if money < HOUSE_FURNITURE[key]["price"]:
            show_failure_toast("Not enough money for this piece.")
            return
        house_place_pick = key
        house_build_menu_open = False
        return


def house_try_sink_use():
    global house_sink_ready_ms
    now = pygame.time.get_ticks()
    if now < house_sink_ready_ms:
        show_failure_toast(f"Sink recharges in {max(1, (house_sink_ready_ms - now) // 1000)}s.")
        return
    g = make_glass_of_water_item()
    if not inventory_can_accept(g):
        show_failure_toast("You can only carry one glass of water at a time.")
        return
    if try_add_inventory(g):
        house_sink_ready_ms = now + 50_000
        show_success_toast("Filled a glass of water from the tap.")


def house_run_interaction(kind: str):
    global microwave_open, stove_open, grill_open, sleep_cutscene_timer, hotel_notice_timer, hotel_notice_text, house_player_floor
    if kind == "ladder":
        house_player_floor = 1 - int(house_player_floor)
        return
    if kind == "bed":
        if can_sleep_now():
            sleep_cutscene_timer = 120
            hotel_notice_timer = 0
        else:
            hotel_notice_text = "Too early to sleep."
            hotel_notice_timer = 120
            show_failure_toast("Too early to sleep — wait for sunset or night.")
        return
    if kind == "microwave":
        microwave_open = True
        stove_open = False
        grill_open = False
    elif kind == "stove":
        stove_open = True
        microwave_open = False
        grill_open = False
    elif kind == "grill":
        grill_open = True
        microwave_open = False
        stove_open = False
    elif kind == "sink":
        house_try_sink_use()
    elif kind == "seasoner":
        if inventory[selected_slot] is None:
            show_failure_toast("Select a cooked meal to season first.")
            return
        it = inventory[selected_slot]["item"]
        if getattr(it, "item_type", "") != "food" or not getattr(it, "cooked_by_player", False):
            show_failure_toast("Only cooked meals can be seasoned.")
            return
        if getattr(it, "seasoned", False):
            show_failure_toast("That meal is already seasoned.")
            return
        # require seasoning item in inventory (house tool uses one packet)
        found = None
        for i in range(MAX_INVENTORY):
            s = inventory[i]
            if s and s["item"].name == "Seasoning":
                found = i
                break
        if found is None:
            show_failure_toast("You need Seasoning from the supermarket.")
            return
        remove_one_from_slot(found)
        it.hunger_restore = int(math.ceil(float(it.hunger_restore) * 1.35))
        it.seasoned = True
        it.seasonable = True
        show_success_toast("Seasoned meal (+35% hunger).")


def house_try_place_at_screen_mx(mx_screen: int):
    global money, house_place_pick, house_buildings
    if not house_place_pick:
        return
    off = int(house_cam_offset)
    wx = float(mx_screen + off)
    cx = house_snap_cx(wx)
    fl = int(house_player_floor)
    price = HOUSE_FURNITURE[house_place_pick]["price"]
    if money < price:
        show_failure_toast("Not enough money to place this piece.")
        return
    if house_new_furniture_collides(house_place_pick, cx, fl):
        show_failure_toast("Can't place here — overlaps furniture or the ladder.")
        return
    money -= price
    house_buildings.append({"kind": house_place_pick, "cx": cx, "floor": fl})
    house_place_pick = None
    show_success_toast("Placed.")

def house_try_delete_at_screen_pos(pos) -> bool:
    """Delete furniture on current floor (right-click) with 50% refund."""
    global money, house_buildings
    sx, sy = int(pos[0]), int(pos[1])
    off = int(house_cam_offset)
    fl = int(house_player_floor)
    for i in range(len(house_buildings) - 1, -1, -1):
        b = house_buildings[i]
        if int(b.get("floor", 0)) != fl:
            continue
        r = house_building_rect(b)
        sr = pygame.Rect(r.x - off, r.y, r.w, r.h)
        if sr.collidepoint(sx, sy):
            kind = b["kind"]
            price = int(HOUSE_FURNITURE.get(kind, {}).get("price", 0) or 0)
            refund = int(round(price * 0.5))
            house_buildings.pop(i)
            if refund > 0:
                money += refund
            show_success_toast(f"Removed {kind} (+${refund}).")
            return True
    return False


def draw_restaurant_facade(rx, y, w, h, tier, business_closed):
    """Tiered Riverside Bistro look: warm stucco, striped awning, expands with tier."""
    body_top = y + 28
    body_h = h - 28
    wall = (
        min(215, 172 + tier * 12),
        min(150, 108 + tier * 10),
        min(118, 86 + tier * 8),
    )
    trim = (118 - tier * 3, 74 - tier * 2, 58 - tier * 2)
    pygame.draw.rect(screen, wall, (rx, body_top, w, body_h))
    pygame.draw.rect(screen, trim, (rx, body_top, w, body_h), 3)
    if tier >= 2:
        pygame.draw.rect(screen, (95, 88, 82), (rx + 4, body_top + body_h - 14, w - 8, 10), border_radius=2)
    if tier >= 3:
        ax = rx + w - 54
        pygame.draw.rect(screen, (192, 130, 102), (ax, body_top + 10, 50, body_h - 24), border_radius=5)
        pygame.draw.rect(screen, trim, (ax, body_top + 10, 50, body_h - 24), 2, border_radius=5)
        pygame.draw.rect(screen, (255, 248, 220), (ax + 8, body_top + 22, 16, 22), border_radius=3)
        pygame.draw.rect(screen, (88, 52, 42), (ax + 28, body_top + 32, 14, 36), border_radius=3)
        pygame.draw.circle(screen, (255, 230, 160), (ax + 35, body_top + 26), 4)

    n_stripes = max(7, w // 15)
    seg = w / n_stripes
    for i in range(n_stripes):
        c = (225, 88, 72) if i % 2 == 0 else (248, 248, 248)
        if tier >= 2:
            c = (218, 75, 65) if i % 2 == 0 else (250, 248, 245)
        x0 = rx + int(i * seg)
        sw = int((i + 1) * seg) - int(i * seg) + 1
        pygame.draw.rect(screen, c, (x0, y + 18, sw, 18), border_radius=2)
    pygame.draw.rect(screen, (88, 42, 38), (rx, y + 34, w, 5))
    if tier >= 2:
        for li in range(7):
            lx = rx + 16 + li * ((w - 32) // 6)
            pygame.draw.circle(screen, (255, 235, 170), (lx, y + 12), 3)
            pygame.draw.circle(screen, (255, 250, 200), (lx, y + 12), 2)
    if tier >= 1:
        pygame.draw.line(screen, (184, 145, 75), (rx + 6, y + 35), (rx + w - 6, y + 35), 2)

    n_win = 3 if tier >= 2 else 2
    win_h = 38 if tier >= 1 else 36
    win_w = min(46, int((w - 40) / max(2, n_win)) - 6)
    for wi in range(n_win):
        cx = rx + int(16 + wi * (w - 32 - win_w) / max(1, n_win - 1))
        pygame.draw.rect(screen, (255, 228, 165), (cx, body_top + 18, win_w, win_h), border_radius=4)
        pygame.draw.rect(screen, (255, 246, 210), (cx + 7, body_top + 24, win_w - 14, win_h - 16), border_radius=3)
        if tier >= 1:
            pygame.draw.rect(screen, (68, 112, 64), (cx, body_top + 18 + win_h, win_w, 9), border_radius=2)
            pygame.draw.rect(screen, (120, 78, 55), (cx + 3, body_top + 15 + win_h, win_w - 6, 5), border_radius=1)

    door_w = 34 if tier < 3 else 36
    pygame.draw.rect(screen, (82, 52, 40), (rx + w // 2 - door_w // 2, body_top + body_h - 50, door_w, 46), border_radius=3)
    pygame.draw.circle(screen, (220, 180, 120), (rx + w // 2 + door_w // 2 - 10, body_top + body_h - 28), 3)

    gf = pygame.font.SysFont(None, 26 if tier < 2 else 28)
    gg = gf.render("BISTRO", True, (255, 248, 235))
    screen.blit(gg, gg.get_rect(center=(rx + w // 2, y + 12)))
    sf = pygame.font.SysFont(None, 17)
    sub = sf.render("Homemade" if tier < 2 else "Homemade · Riverside", True, (55, 38, 32))
    screen.blit(sub, (rx + w - sub.get_width() - 8, y + h - 22))
    if tier >= 1:
        tier_badge = pygame.font.SysFont(None, 15).render(f"★ Tier {tier}", True, (255, 220, 140))
        screen.blit(tier_badge, (rx + 8, y + h - 24))

    if business_closed:
        dim = pygame.Surface((w, body_h), pygame.SRCALPHA)
        dim.fill((15, 12, 18, 115))
        screen.blit(dim, (rx, body_top))
        cf = pygame.font.SysFont(None, 22)
        cl = cf.render("CLOSED", True, (255, 235, 210))
        screen.blit(cl, cl.get_rect(center=(rx + w // 2, body_top + body_h // 2)))


class Restaurant:
    """Abandoned building until repaired; acts as repeat-visit NPC shop with player stock."""

    def __init__(self):
        # Far enough left that tier-3 width (~245) clears mission center at x=-200 (width 120)
        self.original_x = -460
        self.width = RESTAURANT_GEOM_BASE_W
        self.height = RESTAURANT_GEOM_BASE_H
        self.y = RESTAURANT_GEOM_TOP_Y

    def check_collision(self, player_x, player_width):
        return self.original_x < player_x + player_width and player_x < self.original_x + self.width

    def draw(self, camera):
        rx = camera.apply(self.original_x)
        if -self.width >= rx or rx >= WINDOW_WIDTH + self.width:
            return
        if not restaurant_repaired:
            # Dilapidated shell
            pygame.draw.rect(screen, (52, 54, 62), (rx, self.y, self.width, self.height))
            pygame.draw.rect(screen, (28, 28, 34), (rx, self.y, self.width, self.height), 3)
            for wx in (18, 58, 98):
                pygame.draw.rect(screen, (35, 38, 44), (rx + wx, self.y + 38, 28, 36))
                pygame.draw.line(screen, (25, 25, 30), (rx + wx, self.y + 38), (rx + wx + 28, self.y + 74), 2)
                pygame.draw.line(screen, (25, 25, 30), (rx + wx + 28, self.y + 38), (rx + wx, self.y + 74), 2)
            pygame.draw.rect(screen, (45, 42, 38), (rx + 58, self.y + 88, 38, 44))
            pygame.draw.rect(screen, (70, 55, 45), (rx + 15, self.y + 118, 22, 14))
            pygame.draw.rect(screen, (70, 55, 45), (rx + 118, self.y + 118, 22, 14))
            bf = pygame.font.SysFont(None, 22)
            bad = bf.render("OUT OF ORDER", True, (160, 150, 140))
            screen.blit(bad, bad.get_rect(center=(rx + self.width // 2, self.y + 22)))
        else:
            draw_restaurant_facade(rx, self.y, self.width, self.height, restaurant_tier, not restaurant_business_open)


class Cafe:
    def __init__(self):
        # Arcade ends 740 (600+140); supermarket starts 890 — no overlap
        self.original_x = 745
        self.width = 140
        self.height = 140
        self.y = 360

    def check_collision(self, player_x, player_width):
        return (self.original_x < player_x + player_width and
                player_x < self.original_x + self.width)

    def draw(self, camera):
        cx = camera.apply(self.original_x)
        if -self.width < cx < WINDOW_WIDTH + self.width:
            # building
            pygame.draw.rect(screen, (160, 120, 90), (cx, self.y, self.width, self.height))
            pygame.draw.rect(screen, (90, 60, 40), (cx, self.y, self.width, self.height), 3)
            # window + counter
            pygame.draw.rect(screen, (230, 240, 255), (cx + 18, self.y + 34, 48, 40))
            pygame.draw.rect(screen, (110, 75, 50), (cx + 18, self.y + 78, 100, 16), border_radius=4)
            # door
            pygame.draw.rect(screen, (60, 40, 30), (cx + 88, self.y + 62, 34, 78))
            # sign
            sign_font = pygame.font.SysFont(None, 28)
            sign = sign_font.render("CAFE", True, WHITE)
            screen.blit(sign, sign.get_rect(center=(cx + self.width//2, self.y + 18)))
            # cup icon
            pygame.draw.rect(screen, WHITE, (cx + 30, self.y + 44, 18, 18), border_radius=3)
            pygame.draw.rect(screen, WHITE, (cx + 48, self.y + 48, 8, 10), 2, border_radius=5)
            pygame.draw.line(screen, (220, 220, 220), (cx + 32, self.y + 42), (cx + 44, self.y + 42), 2)

# Add these drawing functions
def draw_shop_menu():
    # Draw shop background with title
    menu_rect = pygame.Rect(WINDOW_WIDTH//4, WINDOW_HEIGHT//4, 
                          WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
    draw_panel(menu_rect, BROWN, title="Bakery Shop", title_color=BROWN)
    
    # Draw items as buttons
    buttons = []
    y_offset = menu_rect.y + 70
    item_font = get_font(28)
    
    for item_name, item in shop_items.items():
        # Create button rectangle
        button_rect = pygame.Rect(menu_rect.x + 20, y_offset, 
                                menu_rect.width - 40, 40)
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos)
        button_color = BUTTON_HOVER if hover else BUTTON_COLOR
        draw_button(button_rect, button_color, BROWN, hover=hover, radius=10)
        
        # Draw item text
        price = get_effective_price(item.price)
        text = f"{item_name}: ${price} (+{item.hunger_restore} hunger)"
        item_text = item_font.render(text, True, BLACK)
        text_rect = item_text.get_rect(center=button_rect.center)
        screen.blit(item_text, text_rect)
        
        # Store button data
        buttons.append((button_rect, item_name))
        y_offset += 50
    
    # Draw close button
    close_rect = pygame.Rect(menu_rect.right - 40, menu_rect.top + 10, 30, 30)
    pygame.draw.rect(screen, RED, close_rect)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    close_rect_center = close_text.get_rect(center=close_rect.center)
    screen.blit(close_text, close_rect_center)
    
    # Return clickable areas
    return buttons, close_rect

def draw_clothing_shop_menu():
    # Make the menu even taller to fit all buttons comfortably
    menu_rect = pygame.Rect(WINDOW_WIDTH//4, WINDOW_HEIGHT//6,  # Same horizontal position
                          WINDOW_WIDTH//2, WINDOW_HEIGHT*0.8)    # Increased height from 0.7 to 0.8
    draw_panel(menu_rect, BLUE, title="Clothing Shop", title_color=BLUE)
    
    # Adjust spacing between buttons to be more compact
    button_height = 40  # Slightly decreased from 45
    padding = 8        # Slightly decreased from 10
    
    # Rest of the function remains the same...
    
    # Draw title
    # Draw items as buttons
    buttons = []
    y_offset = menu_rect.y + 70
    item_font = get_font(28)
    
    for item_name, item_data in clothing_items.items():
        button_rect = pygame.Rect(menu_rect.x + 20, y_offset, 
                                menu_rect.width - 40, 40)
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos)
        button_color = BUTTON_HOVER if hover else BUTTON_COLOR
        draw_button(button_rect, button_color, BLUE, hover=hover, radius=10)
        
        # Draw color sample
        pygame.draw.rect(screen, item_data['color'], 
                        (button_rect.x + 5, button_rect.y + 5, 30, 30))
        
        # Draw text and status
        status = (
            "EQUIPPED"
            if item_data['equipped']
            else "OWNED"
            if item_data['owned']
            else f"${get_effective_price(item_data['price'])}"
        )
        text = f"{item_name} - {status}"
        item_text = item_font.render(text, True, BLACK)
        text_rect = item_text.get_rect(midleft=(button_rect.x + 45, button_rect.centery))
        screen.blit(item_text, text_rect)
        
        buttons.append((button_rect, item_name))
        y_offset += 50
    
    # Draw close button
    close_rect = pygame.Rect(menu_rect.right - 40, menu_rect.top + 10, 30, 30)
    pygame.draw.rect(screen, RED, close_rect)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    close_rect_center = close_text.get_rect(center=close_rect.center)
    screen.blit(close_text, close_rect_center)
    
    return buttons, close_rect

def draw_arcade_menu():
    menu_rect = pygame.Rect(
        WINDOW_WIDTH // 4,
        WINDOW_HEIGHT // 8,
        WINDOW_WIDTH // 2,
        int(WINDOW_HEIGHT * 0.78),
    )
    draw_panel(menu_rect, NEON_BLUE, title="ARCADE", title_color=NEON_PINK)

    sub = get_font(22).render(
        f"Each play: ${get_effective_price(arcade_shop.game_price)}",
        True,
        GRAY,
    )
    screen.blit(sub, (menu_rect.centerx - sub.get_width() // 2, menu_rect.top + 52))

    esc_hint = get_font(22).render("ESC: Close", True, GRAY)
    screen.blit(esc_hint, (menu_rect.x + 18, menu_rect.bottom - 30))

    buttons = []
    y_offset = menu_rect.y + 88
    game_font = get_font(28)
    price = get_effective_price(arcade_shop.game_price)

    for label, key in (
        ("Flappy Bird", "FlappyBird"),
        ("Snake", "Snake"),
        ("Dodge (Neon Rain)", "Dodge"),
        ("Breakout", "Breakout"),
        ("Pong (vs AI)", "Pong"),
        ("Stack Tower", "Stack"),
    ):
        button_rect = pygame.Rect(menu_rect.x + 20, y_offset, menu_rect.width - 40, 46)
        hover = button_rect.collidepoint(pygame.mouse.get_pos())
        button_color = BUTTON_HOVER if hover else BUTTON_COLOR
        draw_button(button_rect, button_color, NEON_GREEN, hover=hover, radius=10)
        game_text = game_font.render(f"{label} — ${price}", True, BLACK)
        screen.blit(game_text, game_text.get_rect(center=button_rect.center))
        buttons.append((button_rect, key))
        y_offset += 54

    # Draw close button
    close_rect = pygame.Rect(menu_rect.right - 40, menu_rect.top + 10, 30, 30)
    pygame.draw.rect(screen, RED, close_rect)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    close_rect_center = close_text.get_rect(center=close_rect.center)
    screen.blit(close_text, close_rect_center)
    
    return buttons, close_rect


def draw_cafe_menu():
    menu_rect = pygame.Rect(WINDOW_WIDTH//4, WINDOW_HEIGHT//5,
                            WINDOW_WIDTH//2, int(WINDOW_HEIGHT * 0.62))
    draw_panel(menu_rect, (90, 60, 40), title="CAFE", title_color=(90, 60, 40))

    hint_font = get_font(22)
    hint = hint_font.render("Coffee boosts stamina regen for 1:00–3:00", True, GRAY)
    screen.blit(hint, hint.get_rect(centerx=menu_rect.centerx, top=menu_rect.top + 58))

    esc_hint = hint_font.render("ESC: Close", True, GRAY)
    screen.blit(esc_hint, (menu_rect.x + 18, menu_rect.bottom - 30))

    buttons = []
    y_offset = menu_rect.y + 96
    font_title = get_font(24, bold=True)
    font_detail = get_font(20)
    mouse = pygame.mouse.get_pos()

    for d in CAFE_DRINKS:
        r = pygame.Rect(menu_rect.x + 20, y_offset, menu_rect.width - 40, 56)
        hover = r.collidepoint(mouse)
        draw_button(r, BUTTON_HOVER if hover else BUTTON_COLOR, (90, 60, 40), hover=hover, radius=10)

        price = get_effective_price(int(d["price"]))
        dur_s = int(d["duration_ms"] // 1000)
        dur_text = f"{dur_s//60}:{dur_s%60:02d}"
        line1 = font_title.render(f"{d['name']}  —  ${price}", True, BLACK)
        line2 = font_detail.render(f"Regen x{d['mult']:.0f}  ·  {dur_text}", True, (55, 55, 55))
        gap = 4
        total_h = line1.get_height() + gap + line2.get_height()
        ty = r.centery - total_h // 2
        screen.blit(line1, (r.centerx - line1.get_width() // 2, ty))
        screen.blit(line2, (r.centerx - line2.get_width() // 2, ty + line1.get_height() + gap))

        buttons.append((r, d))
        y_offset += 64

    close_rect = pygame.Rect(menu_rect.right - 40, menu_rect.top + 10, 30, 30)
    pygame.draw.rect(screen, RED, close_rect)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    return buttons, close_rect


def handle_cafe_click(pos, buttons, close_rect):
    global money, cafe_open, cafe_buys
    if close_rect.collidepoint(pos):
        cafe_open = False
        return

    for rect, drink in buttons:
        if rect.collidepoint(pos):
            price = get_effective_price(int(drink["price"]))
            if money < price:
                show_failure_toast("Not enough money.")
                return
            coffee = ShopItem(drink["name"], price, int(drink.get("hunger_restore", 2)), "drink")
            coffee.coffee_mult = float(drink["mult"])
            coffee.coffee_duration_ms = int(drink["duration_ms"])
            coffee.coffee_source = True
            if not inventory_can_accept(coffee):
                show_failure_toast("Inventory full.")
                return
            money -= price
            try_add_inventory(coffee)
            cafe_buys += 1
            if cafe_buys >= achievements["Espresso Yourself"]["requirement"]:
                unlock_achievement("Espresso Yourself")
            cafe_open = False
            return

def draw_supermarket_menu():
    # Taller menu so item list fits better (and allows future expansion)
    menu_rect = pygame.Rect(WINDOW_WIDTH//4, WINDOW_HEIGHT//6,
                            WINDOW_WIDTH//2, int(WINDOW_HEIGHT * 0.72))
    draw_panel(menu_rect, (20, 60, 20), title="Supermarket", title_color=(20, 60, 20))

    buttons = []
    y_offset = menu_rect.y + 80
    item_font = get_font(28)

    for item_name, item in SUPERMARKET_ITEMS.items():
        button_rect = pygame.Rect(menu_rect.x + 20, y_offset,
                                  menu_rect.width - 40, 40)
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos)
        button_color = BUTTON_HOVER if hover else BUTTON_COLOR
        draw_button(button_rect, button_color, (20, 60, 20), hover=hover, radius=10)

        price = get_effective_price(item.price)
        text = f"{item_name}: ${price}"
        item_text = item_font.render(text, True, BLACK)
        screen.blit(item_text, item_text.get_rect(center=button_rect.center))

        buttons.append((button_rect, item_name))
        y_offset += 50

    close_rect = pygame.Rect(menu_rect.right - 40, menu_rect.top + 10, 30, 30)
    pygame.draw.rect(screen, RED, close_rect)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    return buttons, close_rect


def draw_seafood_market_menu():
    """Sell fish from your inventory (1 per click)."""
    refresh_seafood_daily_offer()
    menu_rect = pygame.Rect(WINDOW_WIDTH // 6, WINDOW_HEIGHT // 6, int(WINDOW_WIDTH * 0.66), int(WINDOW_HEIGHT * 0.66))
    pygame.draw.rect(screen, (235, 248, 252), menu_rect, border_radius=10)
    pygame.draw.rect(screen, (20, 55, 70), menu_rect, 4, border_radius=10)

    pad = 18
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Seafood Market", True, (20, 55, 70))
    screen.blit(title, (menu_rect.x + pad, menu_rect.y + pad - 4))

    info_font = pygame.font.SysFont(None, 24)
    info = info_font.render("Click a fish to sell one. Rarer fish are worth more.", True, (70, 80, 85))
    screen.blit(info, (menu_rect.x + pad, menu_rect.y + pad + 44))

    list_x = menu_rect.x + pad
    list_y = menu_rect.y + pad + 84
    list_w = menu_rect.width - pad * 2
    btn_h = 46
    btn_gap = 10
    mouse = pygame.mouse.get_pos()
    font = pygame.font.SysFont(None, 26)

    buttons = []  # (rect, action, slot_idx_or_none, can)
    y = list_y

    # --- Daily offer card ---
    offer_name = seafood_daily_offer_fish
    offer_card = pygame.Rect(list_x, y, list_w, 76)
    pygame.draw.rect(screen, (245, 252, 255), offer_card, border_radius=12)
    pygame.draw.rect(screen, (120, 200, 255), offer_card, 2, border_radius=12)
    of_title = pygame.font.SysFont(None, 28).render("Daily Offer", True, (20, 55, 70))
    screen.blit(of_title, (offer_card.x + 12, offer_card.y + 8))
    if offer_name:
        rlab, rcol = fish_rarity_label(offer_name)
        sub = pygame.font.SysFont(None, 22).render(f"{offer_name}  ({rlab})  sells for +50% today", True, (55, 70, 80))
        screen.blit(sub, (offer_card.x + 12, offer_card.y + 40))
        # Offer sell button
        btn = pygame.Rect(offer_card.right - 156, offer_card.y + 20, 140, 36)
        # enabled only if player has this fish
        has_offer = False
        for si in range(MAX_INVENTORY):
            s = inventory[si]
            if s and getattr(s["item"], "caught_fish", False) and s["item"].name == offer_name:
                has_offer = True
                break
        hov = btn.collidepoint(mouse)
        fill = (110, 220, 170) if has_offer else (150, 160, 165)
        draw_button(btn, fill, (20, 85, 70), hover=hov and has_offer, radius=10)
        lab = "Sell offer" if has_offer else "Need fish"
        bt = pygame.font.SysFont(None, 24).render(lab, True, (15, 35, 30))
        screen.blit(bt, bt.get_rect(center=btn.center))
        buttons.append((btn, "offer", None, has_offer))
    else:
        sub = pygame.font.SysFont(None, 22).render("No offer today.", True, (55, 70, 80))
        screen.blit(sub, (offer_card.x + 12, offer_card.y + 40))
    y += offer_card.height + 12

    any_fish = False
    for i in range(MAX_INVENTORY):
        slot = inventory[i]
        if not slot:
            continue
        it = slot["item"]
        if not getattr(it, "caught_fish", False):
            continue
        any_fish = True
        price = int(getattr(it, "price", 0) or 0)
        name = it.name
        count = int(slot.get("count", 1) or 1)
        rlab, rcol = fish_rarity_label(name)

        rect = pygame.Rect(list_x, y, list_w, btn_h)
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (255, 255, 255) if hover else (248, 252, 255), rect, border_radius=8)
        pygame.draw.rect(screen, (20, 55, 70), rect, 2, border_radius=8)
        # rarity badge (right), price (just left of it), then truncated name on the left
        badge = pygame.Rect(rect.right - 96, rect.y + 8, 84, rect.h - 16)
        pygame.draw.rect(screen, (245, 250, 255), badge, border_radius=12)
        pygame.draw.rect(screen, rcol, badge, 2, border_radius=12)
        rt = pygame.font.SysFont(None, 20).render(rlab, True, rcol)
        screen.blit(rt, rt.get_rect(center=badge.center))
        right = font.render(f"+${price}", True, (70, 90, 100))
        price_x = badge.x - 10 - right.get_width()
        screen.blit(right, (price_x, rect.y + 12))
        max_left_w = max(40, price_x - (rect.x + 12) - 10)
        left_txt = truncate_text(font, f"{name}  x{count}", max_left_w)
        left = font.render(left_txt, True, (20, 35, 45))
        screen.blit(left, (rect.x + 12, rect.y + 12))
        buttons.append((rect, "sell", i, True))
        y += btn_h + btn_gap

    if not any_fish:
        msg = pygame.font.SysFont(None, 28).render("No fish to sell. Take the ferry to Sun Reef and catch some.", True, (60, 70, 80))
        screen.blit(msg, msg.get_rect(center=(menu_rect.centerx, menu_rect.centery + 20)))

    close_rect = pygame.Rect(menu_rect.right - 46, menu_rect.top + 14, 32, 32)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    return buttons, close_rect


def handle_seafood_market_click(pos, buttons, close_rect):
    global money, seafood_market_open
    if close_rect.collidepoint(pos):
        seafood_market_open = False
        return
    for rect, action, slot_idx, can in buttons:
        if (not can) or (not rect.collidepoint(pos)):
            continue
        if action == "offer":
            nm = seafood_daily_offer_fish
            if not nm:
                return
            # find a slot with this fish
            found = None
            for i in range(MAX_INVENTORY):
                s = inventory[i]
                if s and getattr(s["item"], "caught_fish", False) and s["item"].name == nm:
                    found = i
                    break
            if found is None:
                show_failure_toast("You don't have today's offer fish.")
                return
            it = inventory[found]["item"]
            base = int(getattr(it, "price", 0) or 0)
            bonus = int(math.ceil(base * 1.5))
            remove_one_from_slot(found)
            money += max(0, bonus)
            show_success_toast(f"Daily offer: sold {it.name} (+${bonus}).")
            return
        # normal sell
        if slot_idx is None:
            return
        slot = inventory[int(slot_idx)]
        if not slot:
            return
        it = slot["item"]
        if not getattr(it, "caught_fish", False):
            return
        price = int(getattr(it, "price", 0) or 0)
        remove_one_from_slot(int(slot_idx))
        money += max(0, price)
        show_success_toast(f"Sold {it.name} (+${price}).")
        return

def handle_supermarket_click(pos, buttons, close_rect):
    global money, inventory, xp, money_spent, supermarket_open
    if close_rect.collidepoint(pos):
        supermarket_open = False
        return
    for button, item_name in buttons:
        if button.collidepoint(pos):
            item = SUPERMARKET_ITEMS[item_name]
            price = get_effective_price(item.price)
            if money >= price and inventory_can_accept(item):
                money -= price
                try_add_inventory(item)
                notify_chain_buy(item_name)
                xp += int(price * XP_MULTIPLIER)
                check_level_up()
                money_spent += price
                if money_spent >= achievements["First Purchase"]["requirement"]:
                    unlock_achievement("First Purchase")
                if money_spent >= achievements["Shopaholic"]["requirement"]:
                    unlock_achievement("Shopaholic")
            elif money < price:
                show_failure_toast("Not enough money.")
            else:
                show_failure_toast("Inventory full.")

def count_ingredients():
    counts = {}
    for i in range(MAX_INVENTORY):
        slot = inventory[i]
        if slot is None:
            continue
        it = slot["item"]
        if getattr(it, "item_type", "") == "ingredient":
            counts[it.name] = counts.get(it.name, 0) + slot["count"]
    return counts


def consume_ingredients(req):
    """Remove required ingredients from inventory (assumes available)."""
    for name, qty in req.items():
        remaining = qty
        while remaining > 0:
            taken = False
            for idx in range(MAX_INVENTORY):
                slot = inventory[idx]
                if slot is None:
                    continue
                it = slot["item"]
                if getattr(it, "item_type", "") != "ingredient" or it.name != name:
                    continue
                use = min(remaining, slot["count"])
                slot["count"] -= use
                remaining -= use
                if slot["count"] <= 0:
                    inventory[idx] = None
                taken = True
                if remaining <= 0:
                    break
            if not taken:
                break

def get_microwave_recipes():
    return MICROWAVE_RECIPES_BASE + (MICROWAVE_RECIPES_CHEF if has_skill("Master Chef") else [])

def draw_stove_menu():
    menu_rect = pygame.Rect(WINDOW_WIDTH//6, WINDOW_HEIGHT//6,
                            int(WINDOW_WIDTH*0.66), int(WINDOW_HEIGHT*0.66))

    pygame.draw.rect(screen, (235, 235, 235), menu_rect, border_radius=10)
    pygame.draw.rect(screen, (90, 50, 40), menu_rect, 4, border_radius=10)

    pad = 18
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Stove", True, (60, 30, 20))
    screen.blit(title, (menu_rect.x + pad, menu_rect.y + pad - 4))

    info_font = pygame.font.SysFont(None, 26)
    info = info_font.render(f"Fee: ${STOVE_FEE} + ingredients", True, (60, 60, 60))
    screen.blit(info, (menu_rect.x + pad, menu_rect.y + pad + 44))

    list_x = menu_rect.x + pad
    list_y = menu_rect.y + pad + 86
    list_w = menu_rect.width - pad*2
    btn_h = 48
    btn_gap = 10

    counts = count_ingredients()
    buttons = []
    mouse = pygame.mouse.get_pos()
    hovered_recipe = None
    font = pygame.font.SysFont(None, 26)

    y = list_y
    for recipe in STOVE_RECIPES:
        req = recipe["ingredients"]
        ok = all(counts.get(k, 0) >= v for k, v in req.items())
        price_ok = money >= STOVE_FEE
        preview = build_cooked_result(recipe, "stove")
        can = ok and price_ok and inventory_can_accept(preview)

        rect = pygame.Rect(list_x, y, list_w, btn_h)
        is_hover = rect.collidepoint(mouse)
        base = (255, 255, 255) if can else (225, 225, 225)
        if is_hover:
            base = (245, 245, 245) if can else (215, 215, 215)
            hovered_recipe = recipe
        pygame.draw.rect(screen, base, rect, border_radius=8)
        pygame.draw.rect(screen, (90, 50, 40), rect, 2, border_radius=8)

        name = recipe["name"]
        req_text = ", ".join([f"{k}x{v}" for k, v in req.items()])
        left = font.render(name, True, (30, 30, 30))
        right = font.render(req_text, True, (90, 90, 90))
        screen.blit(left, (rect.x + 12, rect.y + 12))
        screen.blit(right, (rect.right - right.get_width() - 12, rect.y + 12))

        buttons.append((rect, recipe, can))
        y += btn_h + btn_gap

    if hovered_recipe:
        r = hovered_recipe
        panel = pygame.Rect(menu_rect.x + pad, menu_rect.bottom - 92, list_w, 72)
        pygame.draw.rect(screen, (250, 250, 250), panel, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 120), panel, 2, border_radius=8)
        small = pygame.font.SysFont(None, 22)
        result = r["result"]
        line1 = small.render(f"Result: {result.name}  (+{result.hunger_restore} hunger)", True, (40, 40, 40))
        line2 = small.render(f"Click to cook (uses ingredients + ${STOVE_FEE})", True, (70, 70, 70))
        screen.blit(line1, (panel.x + 12, panel.y + 10))
        screen.blit(line2, (panel.x + 12, panel.y + 38))

    close_rect = pygame.Rect(menu_rect.right - 46, menu_rect.top + 14, 32, 32)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    return buttons, close_rect


def draw_grill_menu():
    menu_rect = pygame.Rect(
        WINDOW_WIDTH // 6,
        WINDOW_HEIGHT // 6,
        int(WINDOW_WIDTH * 0.66),
        int(WINDOW_HEIGHT * 0.66),
    )

    pygame.draw.rect(screen, (245, 232, 210), menu_rect, border_radius=10)
    pygame.draw.rect(screen, (120, 62, 28), menu_rect, 4, border_radius=10)

    pad = 18
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Grill", True, (90, 42, 18))
    screen.blit(title, (menu_rect.x + pad, menu_rect.y + pad - 4))

    info_font = pygame.font.SysFont(None, 26)
    info = info_font.render(
        f"Fee: ${GRILL_FEE} + ingredients · slower than stove ({GRILL_COOK_FRAMES // 60}s vs {STOVE_COOK_FRAMES // 60}s)",
        True,
        (70, 55, 45),
    )
    screen.blit(info, (menu_rect.x + pad, menu_rect.y + pad + 44))
    sub = info_font.render("Cheap bites and premium cuts — all on one menu.", True, (95, 80, 68))
    screen.blit(sub, (menu_rect.x + pad, menu_rect.y + pad + 72))

    list_x = menu_rect.x + pad
    list_y = menu_rect.y + pad + 108
    list_w = menu_rect.width - pad * 2
    btn_h = 48
    btn_gap = 10

    counts = count_ingredients()
    buttons = []
    mouse = pygame.mouse.get_pos()
    hovered_recipe = None
    font = pygame.font.SysFont(None, 26)

    y = list_y
    for recipe in GRILL_RECIPES:
        req = recipe["ingredients"]
        ok = all(counts.get(k, 0) >= v for k, v in req.items())
        price_ok = money >= GRILL_FEE
        preview = build_cooked_result(recipe, "grill")
        can = ok and price_ok and inventory_can_accept(preview)

        rect = pygame.Rect(list_x, y, list_w, btn_h)
        is_hover = rect.collidepoint(mouse)
        base = (255, 252, 245) if can else (235, 228, 218)
        if is_hover:
            base = (255, 248, 235) if can else (225, 218, 208)
            hovered_recipe = recipe
        pygame.draw.rect(screen, base, rect, border_radius=8)
        pygame.draw.rect(screen, (120, 62, 28), rect, 2, border_radius=8)

        name = recipe["name"]
        req_text = ", ".join([f"{k}x{v}" for k, v in req.items()])
        left = font.render(name, True, (35, 28, 22))
        right = font.render(req_text, True, (95, 85, 75))
        screen.blit(left, (rect.x + 12, rect.y + 12))
        screen.blit(right, (rect.right - right.get_width() - 12, rect.y + 12))

        buttons.append((rect, recipe, can))
        y += btn_h + btn_gap

    if hovered_recipe:
        r = hovered_recipe
        panel = pygame.Rect(menu_rect.x + pad, menu_rect.bottom - 92, list_w, 72)
        pygame.draw.rect(screen, (255, 250, 240), panel, border_radius=8)
        pygame.draw.rect(screen, (140, 110, 90), panel, 2, border_radius=8)
        small = pygame.font.SysFont(None, 22)
        result = r["result"]
        line1 = small.render(f"Result: {result.name}  (+{result.hunger_restore} hunger)", True, (40, 40, 40))
        line2 = small.render(f"Click to grill (uses ingredients + ${GRILL_FEE})", True, (70, 70, 70))
        screen.blit(line1, (panel.x + 12, panel.y + 10))
        screen.blit(line2, (panel.x + 12, panel.y + 38))

    close_rect = pygame.Rect(menu_rect.right - 46, menu_rect.top + 14, 32, 32)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    return buttons, close_rect


def draw_microwave_menu():
    menu_rect = pygame.Rect(WINDOW_WIDTH//6, WINDOW_HEIGHT//6,
                            int(WINDOW_WIDTH*0.66), int(WINDOW_HEIGHT*0.66))

    # panel
    pygame.draw.rect(screen, (235, 235, 235), menu_rect, border_radius=10)
    pygame.draw.rect(screen, (60, 60, 60), menu_rect, 4, border_radius=10)

    pad = 18
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Microwave", True, (40, 40, 40))
    screen.blit(title, (menu_rect.x + pad, menu_rect.y + pad - 4))

    info_font = pygame.font.SysFont(None, 26)
    info = info_font.render(f"Fee: ${MICROWAVE_FEE} + ingredients", True, (60, 60, 60))
    screen.blit(info, (menu_rect.x + pad, menu_rect.y + pad + 44))

    # list area
    list_x = menu_rect.x + pad
    list_y = menu_rect.y + pad + 86
    list_w = menu_rect.width - pad*2
    btn_h = 48
    btn_gap = 10

    counts = count_ingredients()
    buttons = []
    mouse = pygame.mouse.get_pos()
    hovered_recipe = None

    font = pygame.font.SysFont(None, 26)
    y = list_y
    for recipe in get_microwave_recipes():
        req = recipe["ingredients"]
        ok = all(counts.get(k, 0) >= v for k, v in req.items())
        price_ok = money >= MICROWAVE_FEE
        preview = build_cooked_result(recipe, "microwave")
        can = ok and price_ok and inventory_can_accept(preview)

        rect = pygame.Rect(list_x, y, list_w, btn_h)
        is_hover = rect.collidepoint(mouse)
        base = (255, 255, 255) if can else (225, 225, 225)
        if is_hover:
            base = (245, 245, 245) if can else (215, 215, 215)
            hovered_recipe = recipe
        pygame.draw.rect(screen, base, rect, border_radius=8)
        pygame.draw.rect(screen, (80, 80, 80), rect, 2, border_radius=8)

        name = recipe["name"]
        req_text = ", ".join([f"{k}x{v}" for k, v in req.items()])
        left = font.render(name, True, (30, 30, 30))
        right = font.render(req_text, True, (90, 90, 90))
        screen.blit(left, (rect.x + 12, rect.y + 12))
        screen.blit(right, (rect.right - right.get_width() - 12, rect.y + 12))

        if not price_ok:
            warn = pygame.font.SysFont(None, 22).render("Need $5 fee", True, (140, 60, 60))
            screen.blit(warn, (rect.x + 12, rect.y + 30))

        buttons.append((rect, recipe, can))
        y += btn_h + btn_gap

    # hover details panel
    if hovered_recipe:
        r = hovered_recipe
        panel = pygame.Rect(menu_rect.x + pad, menu_rect.bottom - 92, list_w, 72)
        pygame.draw.rect(screen, (250, 250, 250), panel, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 120), panel, 2, border_radius=8)
        small = pygame.font.SysFont(None, 22)
        result = r["result"]
        line1 = small.render(f"Result: {result.name}  (+{result.hunger_restore} hunger)", True, (40, 40, 40))
        line2 = small.render(f"Click to cook (uses ingredients + ${MICROWAVE_FEE})", True, (70, 70, 70))
        screen.blit(line1, (panel.x + 12, panel.y + 10))
        screen.blit(line2, (panel.x + 12, panel.y + 38))

    close_rect = pygame.Rect(menu_rect.right - 46, menu_rect.top + 14, 32, 32)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    return buttons, close_rect

def draw_hotel_lobby_menu():
    menu_rect = pygame.Rect(WINDOW_WIDTH//4, WINDOW_HEIGHT//4,
                            WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
    pygame.draw.rect(screen, MENU_BG, menu_rect)
    pygame.draw.rect(screen, (70, 70, 100), menu_rect, 4)

    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Hotel", True, (70, 70, 100))
    screen.blit(title, title.get_rect(centerx=menu_rect.centerx, top=menu_rect.top + 10))

    info_font = pygame.font.SysFont(None, 28)
    info = info_font.render("Room: $100 (buy once, keep access)", True, BLACK)
    screen.blit(info, (menu_rect.x + 20, menu_rect.y + 80))

    btn_font = pygame.font.SysFont(None, 32)
    enter_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 130, menu_rect.width - 40, 50)
    pygame.draw.rect(screen, BUTTON_HOVER if enter_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR, enter_rect)
    pygame.draw.rect(screen, (70, 70, 100), enter_rect, 2)
    enter_label = "Enter Room" if hotel_room_owned else "Buy Room ($100)"
    enter_text = btn_font.render(enter_label, True, BLACK)
    screen.blit(enter_text, enter_text.get_rect(center=enter_rect.center))

    close_rect = pygame.Rect(menu_rect.right - 40, menu_rect.top + 10, 30, 30)
    pygame.draw.rect(screen, RED, close_rect)
    close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    return enter_rect, close_rect


def hotel_room_geo():
    px = max(20, min(WINDOW_WIDTH - 40, int(room_player_x)))
    bed_rect = pygame.Rect(80, WINDOW_HEIGHT // 2 + 40, 220, 90)
    counter = pygame.Rect(WINDOW_WIDTH - 280, WINDOW_HEIGHT // 2 + 65, 220, 70)
    micro_rect = pygame.Rect(counter.x + 30, counter.y + 10, 120, 50)
    stove_rect = None
    if has_skill("Master Chef"):
        stove_rect = pygame.Rect(counter.x + 165, counter.y + 10, 40, 50)
    return px, bed_rect, counter, micro_rect, stove_rect


def hotel_room_interaction_stack():
    px, bed_rect, counter, micro_rect, stove_rect = hotel_room_geo()
    hits = []
    if abs(px - bed_rect.centerx) < 110:
        hits.append(("bed", bed_rect.centerx))
    if abs(px - micro_rect.centerx) < 110:
        hits.append(("micro", micro_rect.centerx))
    if stove_rect is not None and abs(px - stove_rect.centerx) < 110:
        hits.append(("stove", stove_rect.centerx))
    hits.sort(key=lambda t: t[1])
    return [h[0] for h in hits], stove_rect, bed_rect, micro_rect, counter


def draw_hotel_room():
    # Cleaner room scene
    screen.fill((24, 24, 32))
    # wall gradient-ish bands
    pygame.draw.rect(screen, (28, 28, 40), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT//2))
    pygame.draw.rect(screen, (32, 30, 44), (0, WINDOW_HEIGHT//2, WINDOW_WIDTH, WINDOW_HEIGHT//2))
    # floor
    pygame.draw.rect(screen, (70, 58, 45), (0, WINDOW_HEIGHT//2 + 20, WINDOW_WIDTH, WINDOW_HEIGHT//2))
    px, bed_rect, counter, micro_rect, stove_rect = hotel_room_geo()
    # bed
    pygame.draw.rect(screen, (200, 200, 210), bed_rect, border_radius=10)
    pygame.draw.rect(screen, (160, 160, 170), bed_rect, 3, border_radius=10)
    pygame.draw.rect(screen, (230, 230, 240), (bed_rect.x + 20, bed_rect.y + 15, 70, 25), border_radius=6)
    # microwave counter
    counter = pygame.Rect(WINDOW_WIDTH - 280, WINDOW_HEIGHT//2 + 65, 220, 70)
    pygame.draw.rect(screen, (80, 70, 60), counter, border_radius=10)
    pygame.draw.rect(screen, (50, 40, 30), counter, 3, border_radius=10)
    pygame.draw.rect(screen, (120, 120, 120), micro_rect, border_radius=6)
    pygame.draw.rect(screen, (40, 40, 40), micro_rect, 2, border_radius=6)
    pygame.draw.rect(screen, (30, 30, 30), (micro_rect.x + 10, micro_rect.y + 10, 70, 30), border_radius=4)
    pygame.draw.circle(screen, (200, 80, 80), (micro_rect.right - 20, micro_rect.y + 25), 6)

    if stove_rect is not None:
        pygame.draw.rect(screen, (60, 30, 20), stove_rect, border_radius=6)
        pygame.draw.rect(screen, (20, 10, 10), stove_rect, 2, border_radius=6)
        pygame.draw.circle(screen, ORANGE, (stove_rect.centerx, stove_rect.y + 16), 4)
        pygame.draw.circle(screen, ORANGE, (stove_rect.centerx, stove_rect.y + 32), 4)
        # little flame so it's obvious
        pygame.draw.polygon(screen, (255, 120, 20), [(stove_rect.centerx, stove_rect.bottom - 8),
                                                     (stove_rect.centerx - 6, stove_rect.bottom - 2),
                                                     (stove_rect.centerx + 6, stove_rect.bottom - 2)])

    # player in room
    draw_player(px, ROOM_PLAYER_Y - 20)

    # prompts — E / V / Z when multiple fixtures in range
    font = pygame.font.SysFont(None, 28)
    p3 = font.render("ESC: Leave room", True, WHITE)
    screen.blit(p3, (20, 20))

    stack, _, _, _, _ = hotel_room_interaction_stack()
    small = pygame.font.SysFont(None, 24)
    keys = ("E", "V", "Z")
    lab_map = {
        "bed": "Sleep (skip night)" if can_sleep_now() else "Sleep (locked until sunset/night)",
        "micro": "Microwave",
        "stove": "Stove",
    }
    base_y = WINDOW_HEIGHT // 2 + 108
    for i, hid in enumerate(stack[:3]):
        p1 = small.render(f"{keys[i]}: {lab_map[hid]}", True, (235, 235, 245))
        rr = p1.get_rect(center=(WINDOW_WIDTH // 2, base_y + i * 26))
        pygame.draw.rect(screen, (10, 10, 18), rr.inflate(14, 6), border_radius=8)
        pygame.draw.rect(screen, (140, 190, 255), rr.inflate(14, 6), 2, border_radius=8)
        screen.blit(p1, rr)

    if hotel_notice_timer > 0:
        msg = pygame.font.SysFont(None, 30).render(hotel_notice_text, True, WHITE)
        r = msg.get_rect(center=(WINDOW_WIDTH//2, 70))
        pygame.draw.rect(screen, (0, 0, 0), r.inflate(20, 14))
        screen.blit(msg, r)

    st, stove_r, bed_r, micro_r, _ = hotel_room_interaction_stack()
    near_bed = "bed" in st
    near_micro = "micro" in st
    near_stove = "stove" in st
    return bed_r, micro_r, stove_r, near_bed, near_micro, near_stove

def draw_sleep_cutscene():
    # Fade to black
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((0, 0, 0))
    alpha = 255 - int((sleep_cutscene_timer / 120) * 255)
    overlay.set_alpha(max(0, min(255, alpha)))
    screen.blit(overlay, (0, 0))
    txt = pygame.font.SysFont(None, 48).render("Sleeping...", True, WHITE)
    screen.blit(txt, txt.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))

def draw_flappy_bird_game():
    # Draw background
    screen.fill(SKY_BLUE)
    
    # Draw bird
    pygame.draw.rect(screen, YELLOW, (100, arcade_shop.flappy_bird.bird_y, 30, 30))
    
    # Draw pipes
    for pipe in arcade_shop.flappy_bird.pipes:
        pygame.draw.rect(screen, GREEN, (pipe['x'], 0, 50, pipe['y']))
        pygame.draw.rect(screen, GREEN, 
                        (pipe['x'], pipe['y'] + arcade_shop.flappy_bird.pipe_gap,
                         50, WINDOW_HEIGHT))
    
    # Draw score
    score_font = pygame.font.SysFont(None, 48)
    score_text = score_font.render(str(arcade_shop.flappy_bird.score), True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH//2, 50))
    
    # Draw exit button always visible
    exit_rect = arcade_shop.flappy_bird.draw_exit_button()
    
    if arcade_shop.flappy_bird.game_over:
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("Game Over!", True, RED)
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        screen.blit(game_over_text, text_rect)
        
        # Change restart text to show correct price
        restart_font = pygame.font.SysFont(None, 36)
        restart_text = restart_font.render(
            f"Press SPACE/UP or click to play again (${get_effective_price(arcade_shop.game_price)})",
            True,
            WHITE
        )
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        screen.blit(restart_text, restart_rect)
    
    return exit_rect  # Return exit button rectangle for click detection


def draw_snake_game():
    screen.fill((18, 28, 18))
    s = arcade_shop.snake
    title = pygame.font.SysFont(None, 28).render("SNAKE — Arrows / WASD", True, (180, 220, 180))
    screen.blit(title, (16, 18))
    # Grid border
    gw = s.grid_w * s.cell
    gh = s.grid_h * s.cell
    pygame.draw.rect(
        screen,
        (40, 55, 40),
        (s.offset_x - 4, s.offset_y - 4, gw + 8, gh + 8),
        border_radius=6,
    )
    for gx in range(s.grid_w):
        for gy in range(s.grid_h):
            cx = s.offset_x + gx * s.cell
            cy = s.offset_y + gy * s.cell
            pygame.draw.rect(screen, (30, 42, 30), (cx + 1, cy + 1, s.cell - 2, s.cell - 2), border_radius=2)
    if s.food:
        fx, fy = s.food
        cx = s.offset_x + fx * s.cell + s.cell // 2
        cy = s.offset_y + fy * s.cell + s.cell // 2
        pygame.draw.circle(screen, RED, (cx, cy), s.cell // 2 - 3)
    for i, seg in enumerate(s.snake):
        gx, gy = seg
        cx = s.offset_x + gx * s.cell + 2
        cy = s.offset_y + gy * s.cell + 2
        col = (80, 200, 120) if i == 0 else (50, 160, 90)
        pygame.draw.rect(screen, col, (cx, cy, s.cell - 4, s.cell - 4), border_radius=4)
    score_font = pygame.font.SysFont(None, 48)
    score_text = score_font.render(str(s.score), True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 48))
    exit_rect = s.draw_exit_button()
    if s.game_over:
        go = pygame.font.SysFont(None, 72).render("Game Over!", True, RED)
        screen.blit(go, go.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
        restart_font = pygame.font.SysFont(None, 36)
        restart_text = restart_font.render(
            f"SPACE / click to retry (${get_effective_price(arcade_shop.game_price)})",
            True,
            WHITE,
        )
        screen.blit(
            restart_text,
            restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)),
        )
    return exit_rect


def draw_dodge_game():
    screen.fill((22, 12, 38))
    title = pygame.font.SysFont(None, 28).render("DODGE — A/D or arrows", True, (200, 180, 255))
    screen.blit(title, (16, 18))
    d = arcade_shop.dodge
    for o in d.obstacles:
        pygame.draw.rect(
            screen,
            NEON_PINK,
            (int(o["x"]), int(o["y"]), o["w"], o["h"]),
            border_radius=4,
        )
    pygame.draw.rect(
        screen,
        NEON_BLUE,
        (
            int(d.player_x - d.player_w // 2),
            d.player_y,
            d.player_w,
            d.player_h,
        ),
        border_radius=5,
    )
    score_font = pygame.font.SysFont(None, 48)
    score_text = score_font.render(str(d.score), True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 48))
    exit_rect = d.draw_exit_button()
    if d.game_over:
        go = pygame.font.SysFont(None, 72).render("Hit!", True, RED)
        screen.blit(go, go.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
        restart_font = pygame.font.SysFont(None, 36)
        restart_text = restart_font.render(
            f"SPACE / click to retry (${get_effective_price(arcade_shop.game_price)})",
            True,
            WHITE,
        )
        screen.blit(
            restart_text,
            restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)),
        )
    return exit_rect

def draw_breakout_game():
    screen.fill((18, 18, 28))
    title = pygame.font.SysFont(None, 28).render("BREAKOUT — A/D or arrows", True, (220, 220, 255))
    screen.blit(title, (16, 18))
    g = arcade_shop.breakout

    # Bricks
    for b in g.bricks:
        pygame.draw.rect(screen, b["color"], b["rect"], border_radius=5)
        pygame.draw.rect(screen, (20, 20, 24), b["rect"], 1, border_radius=5)

    # Paddle + ball
    pygame.draw.rect(screen, (170, 230, 255), (int(g.paddle_x), g.paddle_y, g.paddle_w, g.paddle_h), border_radius=6)
    pygame.draw.circle(screen, (255, 255, 255), (int(g.ball_x), int(g.ball_y)), g.ball_r)

    score_font = pygame.font.SysFont(None, 46)
    score_text = score_font.render(str(g.score), True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 50))

    exit_rect = g.draw_exit_button()
    if g.game_over:
        txt = "You Win!" if g.won else "Game Over!"
        c = (120, 255, 170) if g.won else RED
        go = pygame.font.SysFont(None, 72).render(txt, True, c)
        screen.blit(go, go.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
        restart_font = pygame.font.SysFont(None, 34)
        restart = restart_font.render(
            f"SPACE / click to retry (${get_effective_price(arcade_shop.game_price)})",
            True,
            WHITE,
        )
        screen.blit(restart, restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))
    return exit_rect


def draw_pong_game():
    screen.fill((12, 18, 28))
    title = pygame.font.SysFont(None, 28).render("PONG — W/S or arrows", True, (180, 210, 255))
    screen.blit(title, (16, 18))
    g = arcade_shop.pong
    pygame.draw.rect(screen, (60, 200, 120), (g.left_x, int(g.player_y), g.paddle_w, g.paddle_h), border_radius=4)
    pygame.draw.rect(screen, (255, 120, 160), (g.right_x, int(g.ai_y), g.paddle_w, g.paddle_h), border_radius=4)
    pygame.draw.circle(screen, WHITE, (int(g.ball_x), int(g.ball_y)), g.ball_r)
    pygame.draw.aaline(screen, (50, 60, 80), (WINDOW_WIDTH // 2, 60), (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
    score_font = pygame.font.SysFont(None, 46)
    score_text = score_font.render(str(g.score), True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 50))
    exit_rect = g.draw_exit_button()
    if g.game_over:
        go = pygame.font.SysFont(None, 72).render("Missed!", True, RED)
        screen.blit(go, go.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
        restart_font = pygame.font.SysFont(None, 34)
        restart = restart_font.render(
            f"SPACE / click to retry (${get_effective_price(arcade_shop.game_price)})",
            True,
            WHITE,
        )
        screen.blit(restart, restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))
    return exit_rect


def draw_stack_game():
    screen.fill((28, 32, 42))
    title = pygame.font.SysFont(None, 28).render("STACK — SPACE to place", True, (200, 220, 255))
    screen.blit(title, (16, 18))
    g = arcade_shop.stack
    fw = g.foundation_w
    fl = int(g.foundation_cx - fw / 2)
    pygame.draw.rect(screen, (80, 90, 110), (fl, g.base_y, int(fw), 14), border_radius=4)
    for cx, w, y in g.layers:
        half = w / 2
        pygame.draw.rect(
            screen,
            (120, 200, 255),
            (int(cx - half), int(y), int(w), g.layer_h - 2),
            border_radius=4,
        )
    tw = g.foundation_w if not g.layers else g.layers[-1][1]
    half = tw / 2
    slide_y = g.base_y - g.layer_h * (len(g.layers) + 1)
    pygame.draw.rect(
        screen,
        (255, 210, 120),
        (int(g.slide_cx - half), int(slide_y), int(tw), g.layer_h - 2),
        border_radius=4,
    )
    score_font = pygame.font.SysFont(None, 46)
    score_text = score_font.render(str(g.score), True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 50))
    exit_rect = g.draw_exit_button()
    if g.game_over:
        go = pygame.font.SysFont(None, 72).render("Toppled!", True, RED)
        screen.blit(go, go.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
        restart_font = pygame.font.SysFont(None, 34)
        restart = restart_font.render(
            f"SPACE / click to retry (${get_effective_price(arcade_shop.game_price)})",
            True,
            WHITE,
        )
        screen.blit(restart, restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))
    return exit_rect


# First, let's add some item icons using simple shapes
def draw_item_icon(screen, x, y, item_name):
    if item_name == 'Bread':
        # Draw a simple bread loaf
        pygame.draw.ellipse(screen, LIGHT_BROWN, (x + 5, y + 10, 30, 20))
        pygame.draw.ellipse(screen, BROWN, (x + 5, y + 10, 30, 20), 2)
    elif item_name == 'Croissant':
        # Draw a curved croissant
        pygame.draw.arc(screen, LIGHT_BROWN, (x + 5, y + 5, 30, 30), 0.5, 4, 5)
        pygame.draw.arc(screen, BROWN, (x + 5, y + 5, 30, 30), 0.5, 4, 2)
    elif item_name == 'Cake':
        # Draw a simple cake
        pygame.draw.rect(screen, (255, 192, 203), (x + 5, y + 15, 30, 20))  # Pink cake
        pygame.draw.rect(screen, WHITE, (x + 5, y + 10, 30, 5))  # Frosting
        pygame.draw.circle(screen, RED, (x + 20, y + 10), 3)  # Cherry
    elif item_name == 'Apple':
        pygame.draw.circle(screen, RED, (x + 20, y + 20), 15)
        pygame.draw.rect(screen, BROWN, (x + 18, y + 5, 4, 10))
    elif item_name == 'Banana':
        pygame.draw.polygon(screen, YELLOW, [(x + 10, y + 30), (x + 30, y + 30), (x + 20, y + 10)])
    elif item_name == 'Orange':
        pygame.draw.circle(screen, ORANGE, (x + 20, y + 20), 15)
    elif item_name == 'Salad':
        pygame.draw.ellipse(screen, GREEN, (x + 5, y + 10, 30, 20))
        pygame.draw.ellipse(screen, DARK_GREEN, (x + 10, y + 15, 20, 10))
    elif item_name == 'Sandwich':
        pygame.draw.rect(screen, LIGHT_BROWN, (x + 5, y + 15, 30, 20))
        pygame.draw.rect(screen, WHITE, (x + 5, y + 10, 30, 5))
    elif item_name == 'Cheese':
        pygame.draw.rect(screen, YELLOW, (x + 6, y + 10, 28, 22), border_radius=4)
        pygame.draw.circle(screen, (230, 200, 0), (x + 14, y + 18), 2)
        pygame.draw.circle(screen, (230, 200, 0), (x + 24, y + 24), 2)
        pygame.draw.circle(screen, (230, 200, 0), (x + 20, y + 16), 2)
    elif item_name == 'Egg':
        pygame.draw.ellipse(screen, WHITE, (x + 10, y + 8, 20, 28))
        pygame.draw.ellipse(screen, (255, 200, 0), (x + 16, y + 18, 8, 10))
    elif item_name == 'Rice':
        pygame.draw.ellipse(screen, WHITE, (x + 6, y + 16, 28, 14))
        for i in range(5):
            pygame.draw.circle(screen, (220, 220, 220), (x + 10 + i*5, y + 22), 1)
    elif item_name == 'Noodles':
        pygame.draw.rect(screen, (200, 120, 60), (x + 8, y + 14, 24, 18), border_radius=4)
        for i in range(3):
            pygame.draw.arc(screen, (240, 220, 160), (x + 10, y + 16 + i*4, 20, 10), 0, 3.14, 2)
    elif item_name == 'Veggies':
        pygame.draw.circle(screen, GREEN, (x + 16, y + 20), 8)
        pygame.draw.circle(screen, (0, 180, 0), (x + 24, y + 24), 7)
        pygame.draw.circle(screen, (0, 140, 0), (x + 20, y + 28), 6)
    elif item_name == 'Cheesy Rice':
        pygame.draw.ellipse(screen, WHITE, (x + 6, y + 18, 28, 14))
        pygame.draw.rect(screen, YELLOW, (x + 10, y + 14, 20, 6), border_radius=3)
    elif item_name == 'Veggie Noodles':
        pygame.draw.rect(screen, (200, 120, 60), (x + 8, y + 14, 24, 18), border_radius=4)
        pygame.draw.circle(screen, GREEN, (x + 14, y + 18), 3)
        pygame.draw.circle(screen, GREEN, (x + 24, y + 24), 3)
    elif item_name == 'Egg Bowl':
        pygame.draw.ellipse(screen, WHITE, (x + 6, y + 18, 28, 14))
        pygame.draw.ellipse(screen, (255, 200, 0), (x + 16, y + 14, 8, 8))
    elif item_name == 'Espresso':
        pygame.draw.rect(screen, (80, 50, 30), (x + 10, y + 13, 20, 16), border_radius=4)
        pygame.draw.rect(screen, WHITE, (x + 10, y + 13, 20, 4), border_radius=3)
        pygame.draw.rect(screen, WHITE, (x + 29, y + 16, 5, 8), 2, border_radius=3)
    elif item_name == 'Latte':
        pygame.draw.rect(screen, (180, 140, 90), (x + 8, y + 10, 24, 20), border_radius=5)
        pygame.draw.rect(screen, WHITE, (x + 8, y + 10, 24, 6), border_radius=4)
        pygame.draw.rect(screen, WHITE, (x + 31, y + 14, 5, 10), 2, border_radius=3)
    elif item_name == 'Mega Mocha':
        pygame.draw.rect(screen, (120, 80, 50), (x + 6, y + 8, 28, 24), border_radius=5)
        pygame.draw.rect(screen, (240, 220, 200), (x + 6, y + 8, 28, 7), border_radius=4)
        pygame.draw.rect(screen, WHITE, (x + 33, y + 13, 5, 12), 2, border_radius=3)
    elif item_name == "Glass of Water":
        pygame.draw.rect(screen, (200, 230, 255), (x + 10, y + 10, 20, 26), border_radius=4)
        pygame.draw.rect(screen, (120, 170, 220), (x + 10, y + 10, 20, 26), 2, border_radius=4)
        pygame.draw.line(screen, (230, 250, 255), (x + 12, y + 22), (x + 28, y + 18), 2)
    elif item_name == "Bottle of Water":
        pygame.draw.rect(screen, (90, 140, 220), (x + 14, y + 8, 12, 28), border_radius=5)
        pygame.draw.rect(screen, (40, 90, 180), (x + 14, y + 8, 12, 28), 2, border_radius=5)
        pygame.draw.rect(screen, (220, 240, 255), (x + 16, y + 10, 8, 6), border_radius=2)
    elif item_name == "Cash":
        pygame.draw.rect(screen, (70, 190, 120), (x + 7, y + 14, 26, 18), border_radius=4)
        pygame.draw.rect(screen, (20, 90, 50), (x + 7, y + 14, 26, 18), 2, border_radius=4)
        pygame.draw.circle(screen, (220, 255, 230), (x + 20, y + 23), 5)
    elif item_name in {row[0] for row in FISH_CATCH_TABLE}:
        pygame.draw.polygon(screen, (120, 170, 220), [(x + 8, y + 28), (x + 32, y + 18), (x + 28, y + 12)])
        pygame.draw.polygon(screen, (80, 130, 190), [(x + 8, y + 28), (x + 32, y + 18), (x + 28, y + 12)], 2)
        pygame.draw.circle(screen, (40, 40, 50), (x + 22, y + 18), 2)
    else:
        # Generic plate (unlisted cooked meals)
        pygame.draw.ellipse(screen, (250, 245, 235), (x + 4, y + 12, 32, 22))
        pygame.draw.ellipse(screen, (200, 80, 60), (x + 4, y + 12, 32, 22), 2)
        pygame.draw.circle(screen, (60, 160, 80), (x + 20, y + 22), 3)

# Modify the draw_inventory function
def draw_inventory():
    # Draw inventory slots
    for i in range(MAX_INVENTORY):
        slot_x = 20 + i * 50
        slot_y = WINDOW_HEIGHT - 60
        
        # Draw slot background
        pygame.draw.rect(screen, WHITE, (slot_x, slot_y, 40, 40))
        pygame.draw.rect(screen, BLACK, (slot_x, slot_y, 40, 40), 2)
        
        slot = inventory[i]

        # Draw selected slot indicator
        if i == selected_slot:
            pygame.draw.rect(screen, (255, 255, 0), (slot_x, slot_y, 40, 40), 3)
            
            if slot is not None:
                it_sel = slot["item"]
                if getattr(it_sel, "quick_drink", False):
                    instruction_text = pygame.font.SysFont(None, 20).render("Hold F — quick drink", True, WHITE)
                else:
                    action_text = "drink" if it_sel.item_type == "drink" else "eat"
                    instruction_text = pygame.font.SysFont(None, 20).render(f"Hold F to {action_text}", True, WHITE)
                instruction_rect = instruction_text.get_rect(centerx=WINDOW_WIDTH//2, bottom=WINDOW_HEIGHT - 70)
                pygame.draw.rect(screen, BLACK, instruction_rect.inflate(20, 10))
                screen.blit(instruction_text, instruction_rect)
        
        if slot is not None:
            it = slot["item"]
            draw_item_icon(screen, slot_x, slot_y, it.name)
            hunger_text = f"+{it.hunger_restore}"
            small_font = pygame.font.SysFont(None, 16)
            hunger_surf = small_font.render(hunger_text, True, GREEN)
            screen.blit(hunger_surf, (slot_x + 2, slot_y + 30))
            if slot["count"] > 1:
                cnt_font = pygame.font.SysFont(None, 17)
                label = str(slot["count"])
                cx = slot_x + 40 - cnt_font.size(label)[0] - 1
                cy = slot_y + 40 - cnt_font.get_height() - 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    screen.blit(cnt_font.render(label, True, (0, 0, 0)), (cx + dx, cy + dy))
                screen.blit(cnt_font.render(label, True, WHITE), (cx, cy))

def draw_interaction_prompt(label="interact"):
    # Context-aware prompt centered on screen
    font = pygame.font.SysFont(None, 26)
    text = f"E: {label}"
    prompt_text = font.render(text, True, WHITE)
    rect = prompt_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    pygame.draw.rect(screen, (0, 0, 0), rect.inflate(18, 10))
    screen.blit(prompt_text, rect)


def get_interaction_label():
    # Priority order if somehow overlapping
    if mission_center.check_collision(player_x, player_width):
        return "Missions"
    if restaurant.check_collision(player_x, player_width):
        if not restaurant_repaired:
            return "Ruined Bistro"
        return "Bistro" if restaurant_business_open else "Bistro (closed)"
    if hotel.check_collision(player_x, player_width):
        return "Hotel"
    if supermarket.check_collision(player_x, player_width):
        return "Supermarket"
    if cafe.check_collision(player_x, player_width):
        return "Cafe"
    if arcade_shop.check_collision(player_x, player_width):
        return "Arcade"
    if clothing_shop.check_collision(player_x, player_width):
        return "Clothing"
    if shop.check_collision(player_x, player_width):
        return "Bakery"
    if house.check_collision(player_x, player_width):
        return "Your House"
    if utility_cart.check_collision(player_x, player_width):
        return "Utility Cart"
    if black_market.check_collision(player_x, player_width):
        return "Black Market" if black_market_open_today() else "Black Market (closed)"
    if (
        seafood_market.check_collision(player_x, player_width)
        and (not on_fishing_island)
        and ferry_anim_timer <= 0
    ):
        return "Seafood Market"
    if (
        ferry_dock.check_collision(player_x, player_width)
        and (not on_fishing_island)
        and ferry_anim_timer <= 0
    ):
        return "Ferry — Sun Reef"
    return "interact"


WORLD_INTERACTION_LABELS = {
    "missions": "Missions",
    "restaurant": "Bistro",
    "house": "Your House",
    "hotel": "Hotel",
    "supermarket": "Supermarket",
    "cafe": "Cafe",
    "arcade": "Arcade",
    "clothing": "Clothing",
    "bakery": "Bakery",
    "ferry": "Ferry — Sun Reef",
    "seafood": "Seafood Market",
    "cart": "Utility Cart",
    "black": "Black Market",
}


def get_world_interaction_stack():
    """Overlapping shop entrances sorted by distance to player center (closest first)."""
    opts = []
    px = player_x + player_width // 2

    def add(obj, code):
        if obj.check_collision(player_x, player_width):
            cx = obj.original_x + obj.width * 0.5
            opts.append((abs(px - cx), code))

    add(mission_center, "missions")
    add(restaurant, "restaurant")
    add(house, "house")
    add(hotel, "hotel")
    add(supermarket, "supermarket")
    add(cafe, "cafe")
    add(arcade_shop, "arcade")
    add(clothing_shop, "clothing")
    add(shop, "bakery")
    add(utility_cart, "cart")
    add(black_market, "black")
    if ferry_anim_timer <= 0 and (not on_fishing_island):
        add(ferry_dock, "ferry")
        add(seafood_market, "seafood")
    opts.sort(key=lambda t: t[0])
    return [c for _, c in opts]


def apply_world_interaction_code(code: str):
    global mission_center_open, restaurant_open, bistro_chef_dropdown_chef_idx, restaurant_menu_scroll, restaurant_upgrades_scroll, restaurant_menu_tab
    global hotel_lobby_open, house_lobby_open, supermarket_open, shop_open, clothing_shop_open, arcade_shop_open, cafe_open, seafood_market_open
    global utility_cart_open, black_market_open
    if code == "missions":
        mission_center_open = not mission_center_open
        if mission_center_open:
            house_lobby_open = False
    elif code == "restaurant":
        restaurant_open = not restaurant_open
        bistro_chef_dropdown_chef_idx = None
        if restaurant_open:
            restaurant_menu_scroll = 0
            restaurant_upgrades_scroll = 0
            restaurant_menu_tab = "main"
        supermarket_open = False
        shop_open = False
        clothing_shop_open = False
        arcade_shop_open = False
        cafe_open = False
        hotel_lobby_open = False
        house_lobby_open = False
        mission_center_open = False
    elif code == "house":
        house_lobby_open = not house_lobby_open
        supermarket_open = False
        shop_open = False
        clothing_shop_open = False
        arcade_shop_open = False
        cafe_open = False
        hotel_lobby_open = False
        mission_center_open = False
    elif code == "hotel":
        hotel_lobby_open = not hotel_lobby_open
        supermarket_open = False
        shop_open = False
        clothing_shop_open = False
        arcade_shop_open = False
        cafe_open = False
        house_lobby_open = False
        mission_center_open = False
    elif code == "arcade":
        arcade_shop_open = not arcade_shop_open
    elif code == "clothing":
        clothing_shop_open = not clothing_shop_open
    elif code == "bakery":
        shop_open = not shop_open
    elif code == "cafe":
        cafe_open = not cafe_open
        supermarket_open = False
        shop_open = False
        clothing_shop_open = False
        arcade_shop_open = False
        hotel_lobby_open = False
        house_lobby_open = False
        mission_center_open = False
    elif code == "supermarket":
        supermarket_open = not supermarket_open
    elif code == "ferry":
        try_board_ferry_to_island()
    elif code == "seafood":
        seafood_market_open = not seafood_market_open
    elif code == "cart":
        utility_cart_open = not utility_cart_open
        black_market_open = False
    elif code == "black":
        if not black_market_open_today():
            show_failure_toast("Black Market opens every 3 days.")
            return
        refresh_black_market_offers()
        black_market_open = not black_market_open
        utility_cart_open = False


def draw_world_interaction_prompts(codes: list):
    if not codes:
        return
    font = pygame.font.SysFont(None, 26)
    keys = ("E", "V", "Z")
    base_y = WINDOW_HEIGHT // 2 - 22
    for i, c in enumerate(codes[:3]):
        lab = WORLD_INTERACTION_LABELS.get(c, c)
        if c == "restaurant":
            if not restaurant_repaired:
                lab = "Ruined Bistro"
            else:
                lab = "Bistro" if restaurant_business_open else "Bistro (closed)"
        txt = font.render(f"{keys[i]}: {lab}", True, WHITE)
        rr = txt.get_rect(center=(WINDOW_WIDTH // 2, base_y + i * 32))
        pygame.draw.rect(screen, (0, 0, 0), rr.inflate(18, 10), border_radius=8)
        pygame.draw.rect(screen, (120, 200, 255), rr.inflate(18, 10), 2, border_radius=8)
        screen.blit(txt, rr)


def draw_sell_food_prompt():
    prompt_text = pygame.font.SysFont(None, 24).render("Press R to Sell Food", True, WHITE)
    rect = prompt_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
    pygame.draw.rect(screen, BLACK, rect.inflate(20, 10))
    screen.blit(prompt_text, rect)


def shop_entrance_cx(shop):
    return shop.original_x + shop.width * 0.5


def cooked_food_counts_available():
    """Map dish name -> count in inventory (player-cooked meals only)."""
    counts = {}
    for i in range(MAX_INVENTORY):
        slot = inventory[i]
        if slot is None:
            continue
        it = slot["item"]
        if getattr(it, "item_type", "") != "food":
            continue
        if not getattr(it, "cooked_by_player", False):
            continue
        counts[it.name] = counts.get(it.name, 0) + slot["count"]
    return counts


def try_stock_restaurant_dish(name: str) -> bool:
    """Move one cooked plate from inventory into the bistro stock."""
    global inventory, restaurant_stock_units
    for i in range(MAX_INVENTORY):
        slot = inventory[i]
        if slot is None:
            continue
        it = slot["item"]
        if it.name != name:
            continue
        if getattr(it, "item_type", "") != "food":
            continue
        if not getattr(it, "cooked_by_player", False):
            continue
        cost = int(getattr(it, "cooked_cost_basis", 0) or 0)
        if cost <= 0:
            cost = MICROWAVE_FEE
        slot["count"] -= 1
        if slot["count"] <= 0:
            inventory[i] = None
        restaurant_stock_units.append({"name": name, "cost": cost})
        return True
    return False


def process_restaurant_exit(npc, _rest):
    """After dining in-house: buy 1–3 plates; you earn 2× cost × tier price bonus per plate."""
    global restaurant_stock_units, restaurant_plates_sold, bistro_stats_earned
    if not restaurant_stock_units:
        npc.start_custom_dialog(
            random.choice(
                [
                    "Cute place, but nothing on the menu today…",
                    "I heard this spot reopened—empty shelves though.",
                ]
            )
        )
        return
    n = restaurant_order_plate_count(len(restaurant_stock_units))
    total = 0
    last_name = None
    for _ in range(n):
        idx = random.randrange(len(restaurant_stock_units))
        u = restaurant_stock_units.pop(idx)
        c = max(1, int(u.get("cost", 1)))
        total += int(2 * c * restaurant_sale_price_multiplier())
        last_name = u.get("name")
    add_money(total)
    bistro_stats_earned += total
    restaurant_plates_sold += n
    if restaurant_plates_sold >= achievements["Restaurateur"]["requirement"]:
        unlock_achievement("Restaurateur")
    show_success_toast(
        f"Bistro sale: +${total} ({n} serving{'s' if n != 1 else ''})."
    )
    npc.start_custom_dialog(
        random.choice(
            [
                "Ate in-house—that cozy dining room is perfect.",
                "Sat down inside and enjoyed every bite!",
                "That little restaurant is actually fire.",
                "Homemade plates here? I'll be back.",
            ]
        )
    )
    npc.state = "wander"
    npc.food_item = None
    npc.target_bench = None


def wrap_text_lines(font, text: str, max_width: int):
    """Word-wrap to fit max_width (pixels)."""
    words = text.split()
    if not words:
        return []
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = f"{cur} {w}"
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_restaurant_upgrades_panel(menu_rect, tab_bottom_y, inner_w, title_font, body_font, small):
    """Employees + Coming Soon — clipped scroll region; returns extra button tuples."""
    global restaurant_upgrades_scroll, bistro_chef_dropdown_chef_idx
    buttons = []
    mpos = pygame.mouse.get_pos()
    mx = menu_rect.x + 20
    my = tab_bottom_y + 8 - restaurant_upgrades_scroll
    mw = menu_rect.width - 40
    content_bottom = menu_rect.bottom - 42
    clip_r = pygame.Rect(menu_rect.x + 12, tab_bottom_y + 4, menu_rect.width - 24, max(0, content_bottom - tab_bottom_y - 8))
    prev = screen.get_clip()
    screen.set_clip(clip_r)

    # --- Pantry ribbon ---
    pantry_bg = pygame.Rect(mx, my, mw, 56)
    pygame.draw.rect(screen, (48, 36, 52), pantry_bg, border_radius=12)
    pygame.draw.rect(screen, (255, 210, 140), pantry_bg, 2, border_radius=12)
    screen.blit(title_font.render(f"Kitchen pantry  {pantry_total()}/{BISTRO_PANTRY_MAX}", True, (255, 245, 220)), (mx + 14, my + 10))
    chips = " · ".join(f"{k}×{v}" for k, v in sorted(bistro_pantry.items())) if bistro_pantry else "(empty — runners deliver from the market when pantry dips below 5 per ingredient)"
    for li, line in enumerate(wrap_text_lines(small, chips, mw - 28)):
        screen.blit(small.render(line, True, (220, 210, 225)), (mx + 14, my + 38 + li * (small.get_height() + 2)))
    my += 66

    # --- Building & seating (tiered expansions) ---
    sec_b = pygame.Rect(mx, my, mw, 128)
    pygame.draw.rect(screen, (38, 58, 72), sec_b, border_radius=12)
    pygame.draw.rect(screen, (175, 215, 240), sec_b, 2, border_radius=12)
    screen.blit(title_font.render("Building & seating", True, (235, 248, 255)), (mx + 12, my + 8))
    tier_names = ("Starter nook", "Garden room", "Chef's table wing", "Landmark hall")
    cap = restaurant_max_capacity()
    pct = int(RESTAURANT_PRICE_BONUS_PER_TIER * restaurant_tier * 100)
    bl1 = f"{tier_names[restaurant_tier]} — room for {cap} guests dining inside (no outside seating)."
    bl2 = f"Higher tiers grow the facade and add seats. Customer payouts +{pct}% from tier bonus."
    dy = my + 38
    for ln in wrap_text_lines(small, bl1, mw - 148):
        screen.blit(small.render(ln, True, (210, 228, 238)), (mx + 12, dy))
        dy += small.get_height() + 2
    for ln in wrap_text_lines(small, bl2, mw - 148):
        screen.blit(small.render(ln, True, (185, 205, 220)), (mx + 12, dy))
        dy += small.get_height() + 2
    up_r = pygame.Rect(sec_b.right - 138, sec_b.bottom - 42, 126, 34)
    if restaurant_tier >= 3:
        draw_button(up_r, (120, 160, 120), (45, 85, 50), hover=False, radius=8)
        mxw = small.render("Max tier", True, (22, 55, 24))
        screen.blit(mxw, mxw.get_rect(center=up_r.center))
    else:
        cost = RESTAURANT_TIER_COSTS[restaurant_tier]
        hv = up_r.collidepoint(mpos)
        draw_button(up_r, (110, 195, 245) if hv else (85, 165, 215), (40, 70, 95), hover=hv, radius=8)
        ut = small.render(f"Expand (${cost})", True, BLACK)
        screen.blit(ut, ut.get_rect(center=up_r.center))
        buttons.append(("restaurant_tier_up", up_r))
    my += sec_b.height + 10

    # --- Employees header row ---
    sec = pygame.Rect(mx, my, mw, 40)
    pygame.draw.rect(screen, (180, 95, 70), sec, border_radius=10)
    pygame.draw.rect(screen, (255, 220, 160), sec, 2, border_radius=10)
    screen.blit(title_font.render("Employees", True, (40, 20, 18)), (mx + 12, my + 7))
    hire_c = pygame.Rect(sec.right - 178, my + 4, 166, 32)
    hc = hire_c.collidepoint(pygame.mouse.get_pos())
    can_hire_c = len(bistro_chefs) < CHEF_MAX
    draw_button(
        hire_c,
        (160, 215, 160) if can_hire_c and hc else (110, 150, 110),
        (30, 70, 40),
        hover=hc,
        radius=8,
    )
    ht = small.render(f"Hire chef (${CHEF_HIRE_COST})", True, BLACK)
    screen.blit(ht, ht.get_rect(center=hire_c.center))
    buttons.append(("hire_chef", hire_c))
    my += 48

    screen.blit(body_font.render(f"Chefs  {len(bistro_chefs)}/{CHEF_MAX}", True, (55, 40, 38)), (mx, my))
    my += 26

    total_dishes = len(ALL_BISTRO_RECIPES)
    DD_H = 32
    ROW_H = 28
    for ci, chef in enumerate(bistro_chefs):
        lv = chef.get("level", 1)
        xp = chef.get("xp", 0)
        timer = chef.get("timer", 0)
        unlocked_ids = chef_unlocked_recipe_indices(lv)
        nu = len(unlocked_ids)
        is_open = bistro_chef_dropdown_chef_idx == ci
        list_extra = (6 + len(unlocked_ids) * ROW_H) if is_open else 0
        card_h = 68 + DD_H + list_extra + 12
        card = pygame.Rect(mx, my, mw, card_h)
        pygame.draw.rect(screen, (252, 248, 242), card, border_radius=12)
        pygame.draw.rect(screen, (190, 160, 140), card, 2, border_radius=12)
        rec, src = ALL_BISTRO_RECIPES[chef["recipe_idx"]]
        sec_left = max(0, int(math.ceil(timer / 60))) if timer > 0 else 0
        status = f"Plating… ~{sec_left}s" if timer > 0 else "Waiting for pantry ingredients"
        line1 = body_font.render(f"Chef {ci + 1}  ·  Lv {lv}  ·  {nu}/{total_dishes} dishes unlocked", True, (35, 30, 28))
        line2 = small.render(f"XP {xp}  ·  {status}  ·  ~10% faster per level", True, (95, 85, 80))
        line3 = small.render("Level up to add recipes to this chef's menu.", True, (120, 110, 105))
        screen.blit(line1, (mx + 10, my + 6))
        screen.blit(line2, (mx + 10, my + 28))
        screen.blit(line3, (mx + 10, my + 46))
        dd_rect = pygame.Rect(mx + 10, my + 70, mw - 20, DD_H)
        # Dropdown closed bar — warm gradient + gold rim
        grad = pygame.Surface((dd_rect.width, DD_H), pygame.SRCALPHA)
        for gy in range(DD_H):
            t = gy / max(1, DD_H - 1)
            r = int(52 + 28 * t)
            g = int(36 + 22 * t)
            b = int(48 + 20 * t)
            pygame.draw.line(grad, (r, g, b, 255), (0, gy), (dd_rect.width, gy))
        screen.blit(grad, dd_rect.topleft)
        gloss = pygame.Surface((dd_rect.width - 6, 10), pygame.SRCALPHA)
        gloss.fill((255, 255, 255, 38))
        screen.blit(gloss, (dd_rect.left + 3, dd_rect.top + 3))
        pygame.draw.rect(screen, (255, 210, 145), dd_rect, 2, border_radius=9)
        pygame.draw.rect(screen, (120, 75, 55), dd_rect, 1, border_radius=9)
        dish_lbl = f"{rec['name']}  ·  {src}"
        crop_w = dd_rect.width - 52
        if small.size(dish_lbl)[0] > crop_w:
            while dish_lbl and small.size(dish_lbl + "…")[0] > crop_w:
                dish_lbl = dish_lbl[:-1]
            dish_lbl = dish_lbl.rstrip() + "…"
        lbl_s = small.render(dish_lbl, True, (255, 248, 238))
        screen.blit(lbl_s, (dd_rect.x + 12, dd_rect.centery - lbl_s.get_height() // 2))
        chev = small.render("▼" if not is_open else "▲", True, (255, 215, 160))
        screen.blit(chev, (dd_rect.right - 28, dd_rect.centery - chev.get_height() // 2))
        buttons.append(("chef_dd_toggle", ci, dd_rect))
        if is_open:
            list_top = dd_rect.bottom + 5
            list_h = len(unlocked_ids) * ROW_H + 6
            panel = pygame.Rect(dd_rect.left, list_top, dd_rect.width, list_h)
            drop_shadow = pygame.Surface((panel.width + 4, panel.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(drop_shadow, (20, 12, 18, 90), (2, 4, panel.width, panel.height), border_radius=12)
            screen.blit(drop_shadow, (panel.left - 2, panel.top - 1))
            pygame.draw.rect(screen, (44, 30, 38), panel, border_radius=12)
            pygame.draw.rect(screen, (230, 185, 120), panel, 2, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255, 25), (panel.left + 3, panel.top + 3, panel.width - 6, 6), border_radius=6)
            for ji, ridx in enumerate(unlocked_ids):
                row = pygame.Rect(panel.left + 5, panel.top + 4 + ji * ROW_H, panel.width - 10, ROW_H - 3)
                rcp, rsrc = ALL_BISTRO_RECIPES[ridx]
                hov = row.collidepoint(mpos)
                sel = ridx == chef["recipe_idx"]
                if sel:
                    row_bg = (118, 72, 88)
                elif hov:
                    bg = (92, 62, 76)
                    row_bg = bg
                else:
                    row_bg = (68, 48, 58)
                pygame.draw.rect(screen, row_bg, row, border_radius=7)
                if sel:
                    pygame.draw.rect(screen, (255, 200, 115), row, 2, border_radius=7)
                elif hov:
                    pygame.draw.rect(screen, (255, 230, 200), row, 1, border_radius=7)
                tcol = (255, 252, 248) if (sel or hov) else (235, 225, 218)
                row_txt = f"{rcp['name']}  ·  {rsrc}"
                if small.size(row_txt)[0] > row.width - 56:
                    while row_txt and small.size(row_txt + "…")[0] > row.width - 56:
                        row_txt = row_txt[:-1]
                    row_txt = row_txt.rstrip() + "…"
                tx = small.render(row_txt, True, tcol)
                screen.blit(tx, (row.x + 10, row.centery - tx.get_height() // 2))
                ml = BISTRO_RECIPE_MIN_LEVEL[ridx]
                if ml > 1:
                    tag = small.render(f"Lv {ml}+", True, (210, 185, 160))
                    screen.blit(tag, (row.right - tag.get_width() - 10, row.centery - tag.get_height() // 2))
                buttons.append(("chef_dd_pick", ci, ridx, row))
        my += card_h + 8

    my += 6
    hire_r = pygame.Rect(mx + mw - 190, my, 182, 34)
    hr = hire_r.collidepoint(pygame.mouse.get_pos())
    can_r = len(bistro_restockers) < RESTOCKER_MAX and len(bistro_chefs) >= 1
    draw_button(
        hire_r,
        (150, 190, 235) if can_r and hr else (100, 130, 160),
        (40, 60, 90),
        hover=hr,
        radius=8,
    )
    hrt = small.render(f"Hire runner (${RESTOCKER_HIRE_COST})", True, BLACK)
    screen.blit(hrt, hrt.get_rect(center=hire_r.center))
    buttons.append(("hire_runner", hire_r))
    screen.blit(body_font.render(f"Supply runners  {len(bistro_restockers)}/{RESTOCKER_MAX}", True, (55, 40, 38)), (mx, my + 8))
    my += 42

    for ri in range(len(bistro_restockers)):
        rs = bistro_restockers[ri]
        card = pygame.Rect(mx, my, mw, 54)
        pygame.draw.rect(screen, (240, 248, 255), card, border_radius=10)
        pygame.draw.rect(screen, (120, 150, 190), card, 2, border_radius=10)
        st = restocker_workers[ri].state if ri < len(restocker_workers) else "idle"
        screen.blit(
            body_font.render(
                f"Runner {ri + 1}  ·  Lv {rs.get('level', 1)}  ·  XP {rs.get('xp', 0)}  ·  {st}",
                True,
                (35, 45, 60),
            ),
            (mx + 10, my + 15),
        )
        my += 60

    my += 12
    sec_boost = pygame.Rect(mx, my, mw, 38)
    pygame.draw.rect(screen, (88, 52, 72), sec_boost, border_radius=10)
    pygame.draw.rect(screen, (255, 210, 150), sec_boost, 2, border_radius=10)
    screen.blit(title_font.render("Marketing & atmosphere", True, (255, 248, 235)), (mx + 12, my + 5))
    my += 46

    boost_rows = [
        (
            "adv_ad",
            "Advanced Advertising",
            "More townsfolk stop in when they pass your bistro (tier 0 only; tiers 1–3 use fixed higher rates).",
            BISTRO_UPGRADE_COST_ADV_AD,
            bistro_upgrade_advanced_advertising,
        ),
        (
            "better_quality",
            "Better Quality",
            "Patrons spawn faster (about 23 per 2 minutes instead of 20 per 2.5 minutes).",
            BISTRO_UPGRADE_COST_BETTER_QUALITY,
            bistro_upgrade_better_quality,
        ),
        (
            "delicious_smell",
            "Delicious Smell",
            "Customers are more likely to order extra plates in one visit.",
            BISTRO_UPGRADE_COST_DELICIOUS_SMELL,
            bistro_upgrade_delicious_smell,
        ),
        (
            "auto_season",
            "Seasoning Station",
            "Runners keep seasoning stocked and chefs auto-season dishes to boost their sale value by +50%.",
            BISTRO_UPGRADE_COST_AUTO_SEASON,
            bistro_upgrade_auto_seasoning,
        ),
    ]
    for key, bt, desc, price, owned in boost_rows:
        card_h = 102
        card = pygame.Rect(mx, my, mw, card_h)
        bg = (248, 242, 252) if owned else (252, 248, 245)
        pygame.draw.rect(screen, bg, card, border_radius=12)
        pygame.draw.rect(screen, (165, 120, 95) if owned else (190, 155, 130), card, 2, border_radius=12)
        screen.blit(body_font.render(bt, True, (38, 28, 24)), (mx + 12, my + 8))
        dy = my + 36
        for ln in wrap_text_lines(small, desc, mw - 160):
            screen.blit(small.render(ln, True, (88, 78, 72)), (mx + 12, dy))
            dy += small.get_height() + 2
        buy_r = pygame.Rect(card.right - 136, my + card_h - 40, 124, 32)
        if owned:
            draw_button(buy_r, (140, 175, 140), (45, 85, 50), hover=False, radius=8)
            ot = small.render("Owned", True, (20, 50, 22))
            screen.blit(ot, ot.get_rect(center=buy_r.center))
        else:
            hv = buy_r.collidepoint(mpos)
            draw_button(
                buy_r,
                (235, 195, 120) if hv else (210, 165, 95),
                (95, 65, 35),
                hover=hv,
                radius=8,
            )
            bt_txt = small.render(f"Buy ${price}", True, BLACK)
            screen.blit(bt_txt, bt_txt.get_rect(center=buy_r.center))
            buttons.append(("bistro_upgrade", key, buy_r))
        my += card_h + 10

    soon = pygame.Rect(mx, my, mw, 72)
    g = pygame.Surface((mw, 72), pygame.SRCALPHA)
    for yy in range(72):
        a = 35 + int(55 * (yy / 72))
        pygame.draw.line(g, (55, 35, 75, a), (0, yy), (mw, yy))
    screen.blit(g, (mx, my))
    pygame.draw.rect(screen, (255, 215, 140), soon, 3, border_radius=14)
    screen.blit(title_font.render("Coming later", True, (255, 240, 200)), (mx + 16, my + 10))
    screen.blit(
        small.render("Dining room expansions · Catering · Wine pairings · VIP seating.", True, (230, 220, 245)),
        (mx + 16, my + 42),
    )

    screen.set_clip(prev)
    return buttons


def draw_bistro_stats_bar(menu_rect, top_y, inner_w, title_font, body_font, small):
    """Draw earned/spent/net summary; returns total vertical space used."""
    mx = menu_rect.x + 24
    mw = inner_w
    h = 118
    r = pygame.Rect(mx, top_y, mw, h - 10)
    pygame.draw.rect(screen, (52, 38, 46), r, border_radius=11)
    pygame.draw.rect(screen, (235, 195, 130), r, 2, border_radius=11)
    band = pygame.Surface((mw - 6, 22), pygame.SRCALPHA)
    band.fill((255, 255, 255, 22))
    screen.blit(band, (mx + 3, top_y + 3))
    screen.blit(body_font.render("Bistro stats", True, (255, 248, 235)), (mx + 12, top_y + 5))
    net = bistro_stats_earned - bistro_stats_spent
    net_col = (175, 235, 185) if net >= 0 else (255, 175, 160)
    y1 = top_y + 36
    screen.blit(
        small.render(f"Earned (sales + passive while guests inside): ${bistro_stats_earned}", True, (210, 235, 210)),
        (mx + 12, y1),
    )
    y2 = y1 + small.get_height() + 3
    screen.blit(
        small.render(
            f"Spent (repair, staff, upgrades, supply runs): ${bistro_stats_spent}",
            True,
            (235, 215, 195),
        ),
        (mx + 12, y2),
    )
    y3 = y2 + small.get_height() + 4
    screen.blit(small.render(f"Net: ${net}", True, net_col), (mx + 12, y3))
    y4 = y3 + small.get_height() + 3
    pb = int(RESTAURANT_PRICE_BONUS_PER_TIER * restaurant_tier * 100)
    pct = int(RESTAURANT_PASSIVE_BONUS_PER_PATRON * 100)
    screen.blit(
        small.render(
            f"Guests: {restaurant_patrons_inside}/{restaurant_max_capacity()}  ·  passive +{pct}%/guest  ·  Tier {restaurant_tier}/3  ·  +{pb}% sale bonus",
            True,
            (215, 205, 225),
        ),
        (mx + 12, y4),
    )
    return h


def draw_restaurant_menu():
    global restaurant_menu_scroll, restaurant_upgrades_scroll, restaurant_menu_tab
    menu_rect = pygame.Rect(
        WINDOW_WIDTH // 10,
        WINDOW_HEIGHT // 12,
        int(WINDOW_WIDTH * 0.8),
        int(WINDOW_HEIGHT * 0.82),
    )
    draw_panel(menu_rect, (120, 70, 55), title="Riverside Bistro", title_color=(90, 45, 38))

    title_font = get_font(26, bold=True)
    body_font = get_font(21)
    small = get_font(18)
    inner_w = menu_rect.width - 48
    hint_lines = wrap_text_lines(
        small,
        "Diners eat inside (capacity on your stats bar). You earn 2× prep cost plus a % bonus per building tier.",
        inner_w,
    )
    hy = menu_rect.y + 54
    for hl in hint_lines:
        screen.blit(small.render(hl, True, (70, 70, 75)), (menu_rect.x + 24, hy))
        hy += small.get_height() + 4

    buttons = []
    close_rect = pygame.Rect(menu_rect.right - 44, menu_rect.top + 14, 32, 32)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    cx = pygame.font.SysFont(None, 28).render("X", True, WHITE)
    screen.blit(cx, cx.get_rect(center=close_rect.center))

    y0 = hy + 12
    repair_rect = None

    if not restaurant_repaired:
        msg = f"This place is a wreck. Invest ${RESTAURANT_REPAIR_COST} to reopen as your bistro."
        wrapped_msg = wrap_text_lines(body_font, msg, inner_w)
        lh = body_font.get_height() + 6
        for li, line in enumerate(wrapped_msg):
            screen.blit(body_font.render(line, True, BLACK), (menu_rect.x + 28, y0 + li * lh))
        repair_y = y0 + len(wrapped_msg) * lh + 10
        repair_rect = pygame.Rect(menu_rect.centerx - 160, repair_y, 320, 52)
        hover = repair_rect.collidepoint(pygame.mouse.get_pos())
        draw_button(repair_rect, BUTTON_HOVER if hover else BUTTON_COLOR, (120, 70, 55), hover=hover, radius=12)
        lbl = title_font.render(f"Repair & reopen (${RESTAURANT_REPAIR_COST})", True, BLACK)
        screen.blit(lbl, lbl.get_rect(center=repair_rect.center))
        esc = small.render("ESC: Close", True, GRAY)
        screen.blit(esc, (menu_rect.x + 20, menu_rect.bottom - 28))
        return buttons, repair_rect, close_rect

    # --- Tabs (repaired only) ---
    tab_y = y0
    tw = (menu_rect.width - 52) // 2
    tab_main_r = pygame.Rect(menu_rect.x + 24, tab_y, tw - 8, 40)
    tab_up_r = pygame.Rect(tab_main_r.right + 16, tab_y, tw - 8, 40)
    mpos = pygame.mouse.get_pos()
    for rect, tag, label in ((tab_main_r, "main", "Menu & stock"), (tab_up_r, "upgrades", "Upgrades & crew")):
        on = restaurant_menu_tab == tag
        col = (245, 200, 150) if on else (150, 100, 80)
        brd = (90, 50, 40) if on else (70, 45, 38)
        draw_button(rect, BUTTON_HOVER if rect.collidepoint(mpos) else col, brd, hover=rect.collidepoint(mpos), radius=10)
        lt = title_font.render(label, True, (25, 18, 16))
        screen.blit(lt, lt.get_rect(center=rect.center))
    buttons.append(("tab", "main", tab_main_r))
    buttons.append(("tab", "upgrades", tab_up_r))

    stats_y = tab_y + 44
    stats_h = draw_bistro_stats_bar(menu_rect, stats_y, inner_w, title_font, body_font, small)
    hours_y = stats_y + stats_h + 6
    biz_bar = pygame.Rect(menu_rect.x + 24, hours_y, inner_w, 46)
    pygame.draw.rect(screen, (245, 240, 235), biz_bar, border_radius=10)
    pygame.draw.rect(screen, (140, 100, 80), biz_bar, 2, border_radius=10)
    st_col = (45, 95, 55) if restaurant_business_open else (120, 75, 55)
    status_lbl = "Open — customers, kitchen & runners active" if restaurant_business_open else "Closed — no sales, cooking, or supply runs"
    screen.blit(body_font.render("Hours", True, (45, 32, 28)), (biz_bar.x + 12, biz_bar.y + 4))
    screen.blit(small.render(status_lbl, True, st_col), (biz_bar.x + 12, biz_bar.y + 26))
    toggle_biz = pygame.Rect(biz_bar.right - 198, biz_bar.y + 8, 186, 30)
    tb_hover = toggle_biz.collidepoint(mpos)
    if restaurant_business_open:
        draw_button(toggle_biz, (210, 120, 115) if tb_hover else (190, 100, 95), (95, 45, 40), hover=tb_hover, radius=8)
        ttxt = small.render("Close restaurant", True, BLACK)
    else:
        draw_button(toggle_biz, (130, 195, 130) if tb_hover else (105, 170, 105), (35, 75, 40), hover=tb_hover, radius=8)
        ttxt = small.render("Open restaurant", True, BLACK)
    screen.blit(ttxt, ttxt.get_rect(center=toggle_biz.center))
    buttons.append(("restaurant_toggle_business", toggle_biz))
    content_y = hours_y + 54

    if restaurant_menu_tab == "upgrades":
        up_btns = draw_restaurant_upgrades_panel(menu_rect, content_y, inner_w, title_font, body_font, small)
        buttons.extend(up_btns)
        esc = small.render("ESC: Close  ·  Wheel: scroll this panel", True, GRAY)
        screen.blit(esc, (menu_rect.x + 20, menu_rect.bottom - 28))
        return buttons, repair_rect, close_rect

    # Main tab: stock summary
    hy_stock = content_y + 4
    stock_total = len(restaurant_stock_units)
    by_name = {}
    for u in restaurant_stock_units:
        by_name[u["name"]] = by_name.get(u["name"], 0) + 1
    sum_line = body_font.render(f"Plates in service: {stock_total}", True, (40, 40, 45))
    screen.blit(sum_line, (menu_rect.x + 28, hy_stock))
    hy2 = hy_stock + body_font.get_height() + 6
    if by_name:
        detail_text = "  ·  ".join(f"{k} ×{v}" for k, v in sorted(by_name.items()))
        for dl in wrap_text_lines(small, detail_text, inner_w - 8):
            screen.blit(small.render(dl, True, (75, 75, 80)), (menu_rect.x + 28, hy2))
            hy2 += small.get_height() + 3

    col_top = hy2 + 14
    col_h = max(120, menu_rect.bottom - col_top - 36)
    col_w = (menu_rect.width - 56) // 2
    left_r = pygame.Rect(menu_rect.x + 24, col_top, col_w, col_h)
    right_r = pygame.Rect(menu_rect.x + 32 + col_w, col_top, col_w, col_h)

    pygame.draw.rect(screen, (250, 248, 245), left_r, border_radius=10)
    pygame.draw.rect(screen, (230, 228, 224), left_r, 2, border_radius=10)
    lt = title_font.render("Add stock (your cooking)", True, (60, 55, 50))
    screen.blit(lt, (left_r.x + 12, left_r.y + 10))

    counts = cooked_food_counts_available()
    clip_prev = screen.get_clip()
    screen.set_clip(left_r.inflate(-8, -48))
    iy = left_r.y + 46 - restaurant_menu_scroll
    for dish_name in sorted(counts.keys()):
        row = pygame.Rect(left_r.x + 10, iy, left_r.width - 20, 44)
        if row.bottom >= left_r.y and row.top <= left_r.bottom:
            hr = body_font.render(f"{dish_name}  (carry: {counts[dish_name]})", True, BLACK)
            screen.blit(hr, (row.x + 8, row.y + 6))
            add_r = pygame.Rect(row.right - 118, row.y + 6, 108, 32)
            mh = add_r.collidepoint(pygame.mouse.get_pos())
            draw_button(add_r, BUTTON_HOVER if mh else BUTTON_COLOR, (120, 70, 55), hover=mh, radius=8)
            at = small.render("+1 plate", True, BLACK)
            screen.blit(at, at.get_rect(center=add_r.center))
            buttons.append(("add", dish_name, add_r))
        iy += 50
    screen.set_clip(clip_prev)

    pygame.draw.rect(screen, (250, 248, 245), right_r, border_radius=10)
    pygame.draw.rect(screen, (230, 228, 224), right_r, 2, border_radius=10)
    rt = title_font.render("Pricing preview", True, (60, 55, 50))
    screen.blit(rt, (right_r.x + 12, right_r.y + 10))
    expl = [
        "Each sale pays double your prep cost, times the tier bonus (see stats bar).",
        "Prep cost = ingredients you paid at the market",
        "plus the microwave/stove fee you paid to cook.",
        "",
        "Tip: higher-tier recipes cost more to make,",
        "so they earn more when a customer orders them.",
    ]
    ey = right_r.y + 46
    rw = right_r.width - 28
    for line in expl:
        if not line.strip():
            ey += 10
            continue
        for wl in wrap_text_lines(small, line, rw):
            screen.blit(small.render(wl, True, (85, 85, 90)), (right_r.x + 14, ey))
            ey += small.get_height() + 3

    esc = small.render("ESC: Close  ·  Wheel: scroll stock list", True, GRAY)
    screen.blit(esc, (menu_rect.x + 20, menu_rect.bottom - 28))
    return buttons, repair_rect, close_rect


def handle_restaurant_click(pos, buttons, repair_rect, close_rect):
    global money, money_spent, restaurant_repaired, restaurant_business_open, restaurant_menu_scroll
    global restaurant_menu_tab, bistro_chefs, bistro_restockers, bistro_chef_dropdown_chef_idx
    global bistro_upgrade_advanced_advertising, bistro_upgrade_better_quality, bistro_upgrade_delicious_smell, bistro_upgrade_auto_seasoning
    global bistro_seeker_spawn_timer
    global bistro_stats_spent
    global restaurant_tier
    if close_rect.collidepoint(pos):
        bistro_chef_dropdown_chef_idx = None
        return "close"
    if repair_rect is not None and repair_rect.collidepoint(pos):
        if money >= RESTAURANT_REPAIR_COST:
            money -= RESTAURANT_REPAIR_COST
            money_spent += RESTAURANT_REPAIR_COST
            bistro_stats_spent += RESTAURANT_REPAIR_COST
            if money_spent >= achievements["First Purchase"]["requirement"]:
                unlock_achievement("First Purchase")
            if money_spent >= achievements["Shopaholic"]["requirement"]:
                unlock_achievement("Shopaholic")
            restaurant_repaired = True
            restaurant_business_open = True
            sync_restaurant_building_geometry()
            unlock_achievement("Grand Opening")
        else:
            show_failure_toast(f"You need ${RESTAURANT_REPAIR_COST} to repair the bistro.")
        return
    for tup in buttons:
        if not tup:
            continue
        if tup[0] == "tab" and len(tup) >= 3 and tup[2].collidepoint(pos):
            restaurant_menu_tab = tup[1]
            bistro_chef_dropdown_chef_idx = None
            return
        if tup[0] == "restaurant_tier_up" and len(tup) >= 2 and tup[1].collidepoint(pos):
            if restaurant_tier >= 3:
                show_failure_toast("Your bistro is already fully expanded.")
                return
            cost = RESTAURANT_TIER_COSTS[restaurant_tier]
            if money < cost:
                show_failure_toast(f"You need ${cost} to expand.")
                return
            money -= cost
            money_spent += cost
            bistro_stats_spent += cost
            if money_spent >= achievements["First Purchase"]["requirement"]:
                unlock_achievement("First Purchase")
            if money_spent >= achievements["Shopaholic"]["requirement"]:
                unlock_achievement("Shopaholic")
            restaurant_tier += 1
            sync_restaurant_building_geometry()
            show_success_toast(
                f"Expansion complete — tier {restaurant_tier}! More seats, nicer facade, +{int(RESTAURANT_PRICE_BONUS_PER_TIER * restaurant_tier * 100)}% customer payouts."
            )
            bistro_chef_dropdown_chef_idx = None
            return
        if tup[0] == "restaurant_toggle_business" and len(tup) >= 2 and tup[1].collidepoint(pos):
            restaurant_business_open = not restaurant_business_open
            if restaurant_business_open:
                show_success_toast("Bistro is open — customers, kitchen, and runners are active.")
            else:
                show_success_toast("Bistro closed — no walk-ins, cooking, or supply runs until you reopen.")
            bistro_chef_dropdown_chef_idx = None
            return
        if tup[0] == "hire_chef" and len(tup) >= 2 and tup[1].collidepoint(pos):
            if len(bistro_chefs) >= CHEF_MAX:
                show_failure_toast("Maximum 3 chefs.")
                return
            if money < CHEF_HIRE_COST:
                show_failure_toast(f"You need ${CHEF_HIRE_COST} to hire a chef.")
                return
            money -= CHEF_HIRE_COST
            money_spent += CHEF_HIRE_COST
            bistro_stats_spent += CHEF_HIRE_COST
            bistro_chefs.append({"recipe_idx": 0, "xp": 0, "level": 1, "timer": 0})
            bistro_chef_dropdown_chef_idx = None
            show_success_toast("Chef hired — choose their signature dish from the menu.")
            return
        if tup[0] == "hire_runner" and len(tup) >= 2 and tup[1].collidepoint(pos):
            if len(bistro_chefs) < 1:
                show_failure_toast("Hire at least one chef before a runner.")
                return
            if len(bistro_restockers) >= RESTOCKER_MAX:
                show_failure_toast("Maximum 2 runners.")
                return
            if money < RESTOCKER_HIRE_COST:
                show_failure_toast(f"You need ${RESTOCKER_HIRE_COST}.")
                return
            money -= RESTOCKER_HIRE_COST
            money_spent += RESTOCKER_HIRE_COST
            bistro_stats_spent += RESTOCKER_HIRE_COST
            bistro_restockers.append({"xp": 0, "level": 1})
            sync_restocker_workers()
            bistro_chef_dropdown_chef_idx = None
            show_success_toast("Runner hired — they'll restock when pantry runs low.")
            return
        if tup[0] == "bistro_upgrade" and len(tup) >= 3 and tup[2].collidepoint(pos):
            key = tup[1]
            if key == "adv_ad":
                if bistro_upgrade_advanced_advertising:
                    show_failure_toast("You already have Advanced Advertising.")
                    return
                cost = BISTRO_UPGRADE_COST_ADV_AD
                if money < cost:
                    show_failure_toast(f"You need ${cost}.")
                    return
                money -= cost
                money_spent += cost
                bistro_stats_spent += cost
                bistro_upgrade_advanced_advertising = True
                show_success_toast("Advanced Advertising — more customers stop by the bistro.")
            elif key == "better_quality":
                if bistro_upgrade_better_quality:
                    show_failure_toast("You already have Better Quality.")
                    return
                cost = BISTRO_UPGRADE_COST_BETTER_QUALITY
                if money < cost:
                    show_failure_toast(f"You need ${cost}.")
                    return
                money -= cost
                money_spent += cost
                bistro_stats_spent += cost
                bistro_upgrade_better_quality = True
                bistro_seeker_spawn_timer = min(bistro_seeker_spawn_timer, 90)
                show_success_toast("Better Quality — dedicated patrons will visit throughout the day.")
            elif key == "delicious_smell":
                if bistro_upgrade_delicious_smell:
                    show_failure_toast("You already have Delicious Smell.")
                    return
                cost = BISTRO_UPGRADE_COST_DELICIOUS_SMELL
                if money < cost:
                    show_failure_toast(f"You need ${cost}.")
                    return
                money -= cost
                money_spent += cost
                bistro_stats_spent += cost
                bistro_upgrade_delicious_smell = True
                show_success_toast("Delicious Smell — guests order extra plates more often.")
            elif key == "auto_season":
                if bistro_upgrade_auto_seasoning:
                    show_failure_toast("You already have Seasoning Station.")
                    return
                cost = BISTRO_UPGRADE_COST_AUTO_SEASON
                if money < cost:
                    show_failure_toast(f"You need ${cost}.")
                    return
                money -= cost
                money_spent += cost
                bistro_stats_spent += cost
                bistro_upgrade_auto_seasoning = True
                show_success_toast("Seasoning Station — chefs season dishes for +50% value.")
            bistro_chef_dropdown_chef_idx = None
            return
        if tup[0] == "chef_dd_pick" and len(tup) >= 4 and tup[3].collidepoint(pos):
            ci, ridx = tup[1], tup[2]
            if 0 <= ci < len(bistro_chefs):
                ch = bistro_chefs[ci]
                if ridx in chef_unlocked_recipe_indices(ch.get("level", 1)):
                    ch["recipe_idx"] = ridx
            bistro_chef_dropdown_chef_idx = None
            return
        if tup[0] == "chef_dd_toggle" and len(tup) >= 3 and tup[2].collidepoint(pos):
            ci = tup[1]
            if 0 <= ci < len(bistro_chefs):
                if bistro_chef_dropdown_chef_idx == ci:
                    bistro_chef_dropdown_chef_idx = None
                else:
                    bistro_chef_dropdown_chef_idx = ci
            return
        if len(tup) >= 3 and tup[0] == "add" and tup[2].collidepoint(pos):
            if try_stock_restaurant_dish(tup[1]):
                show_success_toast(f"Stocked bistro with {tup[1]}.")
            else:
                show_failure_toast("No matching cooked dish in inventory.")
            return
    if restaurant_menu_tab == "upgrades" and bistro_chef_dropdown_chef_idx is not None:
        bistro_chef_dropdown_chef_idx = None
    return None


def draw_controls_overlay():
    lines = [
        "Controls",
        "Move: Arrow keys / WASD",
        "Jump: SPACE",
        "Sprint: LSHIFT",
        "Interact: E",
        "Talk: T",
        "Use food: Hold F",
        "Drop/Pick: Q / P",
        "Sell cooked food: R",
        "Stacks: up to 10 per slot (5 slots). Slot: 1-5 / wheel",
        "Menus: ESC",
    ]
    w, h = 340, 252
    x, y = WINDOW_WIDTH - w - 18, WINDOW_HEIGHT - h - 18
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (12, 12, 16, 215), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(surf, (255, 255, 255, 40), (0, 0, w, h), 1, border_radius=10)
    title_font = get_font(24, bold=True)
    body_font = get_font(19)
    yy = 12
    for i, line in enumerate(lines):
        txt = title_font.render(line, True, WHITE if i == 0 else (230, 230, 230))
        surf.blit(txt, (12, yy))
        yy += txt.get_height() + (8 if i == 0 else 4)
    screen.blit(surf, (x, y))

def draw_eating_progress():
    if is_eating and inventory[selected_slot] is not None:
        it = inventory[selected_slot]["item"]
        need = 30 if getattr(it, "quick_drink", False) else 180
        progress = eating_timer / float(need)
        width = 100 * progress
        pygame.draw.rect(screen, WHITE, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT - 80, 100, 10), 2)
        pygame.draw.rect(screen, GREEN, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT - 80, width, 10))

# World bench NPCs can sit on
class Bench:
    def __init__(self, x, y=465):
        self.original_x = x
        self.y = y
        self.width = 70
        self.height = 20

    def draw(self, camera):
        bx = camera.apply(self.original_x)
        if -self.width < bx < WINDOW_WIDTH + self.width:
            # legs
            pygame.draw.rect(screen, (90, 60, 40), (bx + 8, self.y + 10, 8, 22))
            pygame.draw.rect(screen, (90, 60, 40), (bx + self.width - 16, self.y + 10, 8, 22))
            # seat
            pygame.draw.rect(screen, (120, 80, 55), (bx, self.y, self.width, 12), border_radius=4)
            # back
            pygame.draw.rect(screen, (110, 75, 50), (bx, self.y - 18, self.width, 10), border_radius=4)

# Initialize game objects
camera = Camera()
platform = Platform()
clouds = [Cloud() for _ in range(30)]  # Increased to 30 for better coverage
shop = Shop()  # Initialize shop
clothing_shop = ClothingShop()  # Initialize clothing shop
arcade_shop = ArcadeShop()  # Initialize arcade shop
cafe = Cafe()  # Initialize cafe
supermarket = Supermarket()  # Initialize supermarket
hotel = Hotel()  # Initialize hotel
house = House()
ferry_dock = FerryDock()
seafood_market = SeafoodMarket()
utility_cart = UtilityCart()
black_market = BlackMarket()
restaurant = Restaurant()
sync_restaurant_building_geometry()
benches = [
    Bench(-120),  # beside mission center (-200)
    Bench(260),   # near bakery
    Bench(720),   # near arcade (moved to avoid store overlap)
]

# Modified draw_background function
def draw_background(camera):
    screen.fill(sky_color)
    time_of_day = current_time / DAY_LENGTH
    
    # Only draw sun during day (6:00 - 18:00)
    if 0.25 <= time_of_day < 0.75:
        draw_sun()
    else:  # Draw moon during night (18:00 - 6:00)
        draw_moon()
        # stars (simple twinkles)
        random.seed(1337)  # deterministic per run
        star_alpha = 160 if time_of_day > 0.80 or time_of_day < 0.15 else 90
        for _ in range(70):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, 170)
            r = 1 if random.random() < 0.85 else 2
            c = (255, 255, 255, star_alpha)
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, c, (3, 3), r)
            screen.blit(s, (x, y))
    
    # Update and draw clouds
    for cloud in clouds:
        cloud.draw(camera)

# Add this function before the game loop
def handle_shop_click(pos, buttons, close_rect):
    global money, inventory, shop_open, xp, money_spent
    
    if close_rect.collidepoint(pos):
        shop_open = False
        return
    
    for button, item_name in buttons:
        if button.collidepoint(pos):
            item = shop_items[item_name]
            price = get_effective_price(item.price)
            if money >= price and inventory_can_accept(item):
                money -= price
                try_add_inventory(item)
                # Add XP based on purchase price
                xp += int(price * XP_MULTIPLIER)
                check_level_up()
                # Track money spent for achievement
                money_spent += price
                if money_spent >= achievements["First Purchase"]["requirement"]:
                    unlock_achievement("First Purchase")
                if money_spent >= achievements["Shopaholic"]["requirement"]:
                    unlock_achievement("Shopaholic")
            elif money < price:
                show_failure_toast("Not enough money.")
            else:
                show_failure_toast("Inventory full.")

# Add this function to handle clothing shop clicks
def handle_clothing_shop_click(pos, buttons, close_rect):
    global money, clothing_items, xp, money_spent, clothing_coupon_uses
    
    if close_rect.collidepoint(pos):
        return False
        
    for button, item_name in buttons:
        if button.collidepoint(pos):
            item = clothing_items[item_name]
            if item['owned']:
                # Unequip all items and equip selected one
                for name in clothing_items:
                    clothing_items[name]['equipped'] = False
                item['equipped'] = True
            else:
                price = get_effective_price(item['price'])
                if clothing_coupon_uses > 0:
                    price = int(math.ceil(price * 0.5))
                if money < price:
                    show_failure_toast("Not enough money.")
                    continue
                money -= price
                item['owned'] = True
                if clothing_coupon_uses > 0:
                    clothing_coupon_uses -= 1
                # Add XP based on purchase price
                xp += int(price * XP_MULTIPLIER)
                check_level_up()
                # Unequip all items and equip new one
                for name in clothing_items:
                    clothing_items[name]['equipped'] = False
                item['equipped'] = True
                # Track money spent for achievement
                money_spent += price
                if money_spent >= achievements["First Purchase"]["requirement"]:
                    unlock_achievement("First Purchase")
                if money_spent >= achievements["Shopaholic"]["requirement"]:
                    unlock_achievement("Shopaholic")
    return True

def _start_paid_arcade(game_name):
    """Pay once, stop other cabinet games, start the selected mini-game."""
    global money, arcade_shop_open, arcade_money_spent
    price = get_effective_price(arcade_shop.game_price)
    if money < price:
        show_failure_toast("Not enough money for the arcade.")
        return
    money -= price
    arcade_money_spent += price
    if arcade_money_spent >= achievements["Quarter Pusher"]["requirement"]:
        unlock_achievement("Quarter Pusher")
    if arcade_money_spent >= achievements["Token Fiend"]["requirement"]:
        unlock_achievement("Token Fiend")
    arcade_shop.flappy_bird.playing = False
    arcade_shop.snake.playing = False
    arcade_shop.dodge.playing = False
    arcade_shop.breakout.playing = False
    arcade_shop.pong.playing = False
    arcade_shop.stack.playing = False
    if game_name == "FlappyBird":
        arcade_shop.flappy_bird.reset()
    elif game_name == "Snake":
        arcade_shop.snake.reset()
    elif game_name == "Dodge":
        arcade_shop.dodge.reset()
    elif game_name == "Breakout":
        arcade_shop.breakout.reset()
    elif game_name == "Pong":
        arcade_shop.pong.reset()
    elif game_name == "Stack":
        arcade_shop.stack.reset()
    arcade_shop_open = False


def _arcade_paid_retry(game_name):
    """Pay for another run of the same arcade game (already in cabinet)."""
    global money, arcade_money_spent
    price = get_effective_price(arcade_shop.game_price)
    if money < price:
        show_failure_toast("Not enough money for another try.")
        return False
    money -= price
    arcade_money_spent += price
    if arcade_money_spent >= achievements["Quarter Pusher"]["requirement"]:
        unlock_achievement("Quarter Pusher")
    if arcade_money_spent >= achievements["Token Fiend"]["requirement"]:
        unlock_achievement("Token Fiend")
    if game_name == "FlappyBird":
        arcade_shop.flappy_bird.reset()
    elif game_name == "Snake":
        arcade_shop.snake.reset()
    elif game_name == "Dodge":
        arcade_shop.dodge.reset()
    elif game_name == "Breakout":
        arcade_shop.breakout.reset()
    elif game_name == "Pong":
        arcade_shop.pong.reset()
    elif game_name == "Stack":
        arcade_shop.stack.reset()
    return True


# Add this function to handle arcade shop clicks
def handle_arcade_shop_click(pos, buttons, close_rect):
    global arcade_shop_open

    if close_rect.collidepoint(pos):
        arcade_shop_open = False
        return

    for button, game_name in buttons:
        if button.collidepoint(pos):
            if game_name in ("FlappyBird", "Snake", "Dodge", "Breakout", "Pong", "Stack"):
                _start_paid_arcade(game_name)

# Add these variables after the stats section
HUNGER_DECREASE_INTERVAL = 180  # 3 seconds at 60 FPS
HUNGER_DECREASE_AMOUNT = 1  # 1% decrease
HEALTH_DECREASE_AMOUNT = 20  # 20 health points every 3 seconds when hunger is 0
hunger_timer = 0

# Add this function to handle leveling up
def check_level_up():
    global xp, level, max_xp, skill_points, money
    leveled = False
    while xp >= max_xp:
        xp = xp - max_xp  # Carry over excess XP
        level += 1
        skill_points += 1
        money += 100
        max_xp = int(math.ceil(XP_PER_LEVEL * (1.5 ** (level - 1))))  # +50% XP required per level, rounded up
        leveled = True
    if leveled and "Level 5" in achievements and level >= achievements["Level 5"]["requirement"]:
        unlock_achievement("Level 5")

# Add after other class definitions
class DroppedItem:
    def __init__(self, item, x, y):
        self.item = item
        self.x = x
        self.y = y
        self.velocity = -10  # Initial upward velocity
        self.ground_y = 480  # Ground level
        self.falling = True
        
    def update(self):
        if self.falling:
            self.velocity += gravity
            self.y += self.velocity
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.falling = False
                
    def draw(self, camera):
        screen_x = camera.apply(self.x)
        if -40 < screen_x < WINDOW_WIDTH + 40:  # Only draw if visible
            draw_item_icon(screen, screen_x, self.y, self.item.name)
            
    def check_collision(self, player_x, player_y, player_width, player_height):
        return (abs(self.x - player_x) < player_width + 20 and 
                abs(self.y - player_y) < player_height + 20)

# Add to global variables section
dropped_items = []  # List to store dropped items
show_pickup_prompt = False
current_droppable = None

# Death penalty (drops): lose a portion of money and spill inventory
DEATH_MONEY_LOSS_FRACTION = 0.25  # lose 25% of cash on death


def make_cash_drop(amount: int) -> ShopItem:
    it = ShopItem("Cash", 0, 0, item_type="money")
    it.cash_value = int(max(1, amount))
    return it


def handle_player_death():
    """Drop all inventory + some cash, then respawn."""
    global health, hunger, stamina, money, player_x, player_y, player_velocity, player_vx
    global inventory, selected_slot, in_hotel_room, in_house_room, microwave_open, stove_open, grill_open, house_build_menu_open, house_place_pick
    global show_pickup_prompt, current_droppable, on_fishing_island, ferry_anim_timer

    # Drop inventory stacks as individual items (cloned by try_add on pickup)
    for slot in inventory:
        if not slot:
            continue
        it = slot["item"]
        for _ in range(int(slot.get("count", 1) or 1)):
            dropped_items.append(DroppedItem(clone_item(it), player_x + random.uniform(-14, 14), player_y))

    inventory = [None] * MAX_INVENTORY
    selected_slot = 0

    # Cash loss (and drop the lost amount as pickup)
    lost = int(max(0, int(money) * float(DEATH_MONEY_LOSS_FRACTION)))
    if lost > 0:
        money -= lost
        dropped_items.append(DroppedItem(make_cash_drop(lost), player_x, player_y))

    # Close interiors/menus and respawn
    in_hotel_room = False
    in_house_room = False
    microwave_open = False
    stove_open = False
    grill_open = False
    house_build_menu_open = False
    house_place_pick = None
    on_fishing_island = False
    ferry_anim_timer = 0
    _fish_reset_minigame()
    current_droppable = None
    show_pickup_prompt = False

    player_x = 100
    player_y = 400
    player_velocity = 0
    player_vx = 0.0

    health = MAX_HEALTH
    hunger = MAX_HUNGER
    stamina = MAX_STAMINA
    show_failure_toast("You passed out — items dropped. (You can pick them back up.)")

# Simple VFX particles (polish)
vfx_particles = []
ENABLE_PARTICLES = True
FULLSCREEN_ENABLED = False
BASE_WINDOW_WIDTH = WINDOW_WIDTH
BASE_WINDOW_HEIGHT = WINDOW_HEIGHT

def set_fullscreen(enabled: bool):
    global screen, FULLSCREEN_ENABLED, WINDOW_WIDTH, WINDOW_HEIGHT
    FULLSCREEN_ENABLED = bool(enabled)
    if FULLSCREEN_ENABLED:
        info = pygame.display.Info()
        WINDOW_WIDTH = int(getattr(info, "current_w", BASE_WINDOW_WIDTH) or BASE_WINDOW_WIDTH)
        WINDOW_HEIGHT = int(getattr(info, "current_h", BASE_WINDOW_HEIGHT) or BASE_WINDOW_HEIGHT)
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    else:
        WINDOW_WIDTH = int(BASE_WINDOW_WIDTH)
        WINDOW_HEIGHT = int(BASE_WINDOW_HEIGHT)
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # Re-sync systems that depend on WINDOW_WIDTH/HEIGHT.
    try:
        platform.reset_for_window(player_x)
    except Exception:
        pass
    try:
        camera.update(player_x)
    except Exception:
        pass

class VFXParticle:
    def __init__(self, x, y, vx, vy, radius, color, life):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = float(radius)
        self.color = color  # (r,g,b)
        self.life = int(life)
        self.max_life = int(life)

    def update(self):
        self.life -= 1
        self.vy += 0.12
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.vy *= 0.98

    def draw(self, camera):
        if self.life <= 0:
            return
        a = max(0, min(180, int(180 * (self.life / max(1, self.max_life)))))
        r = max(1, int(self.radius * (0.6 + 0.4 * (self.life / max(1, self.max_life)))))
        surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, a), (r + 1, r + 1), r)
        screen.blit(surf, (camera.apply(self.x) - (r + 1), self.y - (r + 1)))

# Add NPC class
class NPC:
    def __init__(self, x):
        # Basic attributes
        self.original_x = x
        self.y = 440
        self.width = 30
        self.height = 50
        self.speed = random.uniform(1, 3)
        self.direction = 1 if random.random() > 0.5 else -1
        
        # Appearance attributes (saved for shop exit)
        self.skin_color = random.choice(SKIN_COLORS)
        self.hair_color = random.choice(HAIR_COLORS)
        self.clothes_color = random.choice(CLOTHES_COLORS)
        
        # Shop interaction attributes
        self.in_shop = False
        self.active_shop = None  # which building we're inside (for exit behavior)
        self.shop_timer = 0
        self.shop_duration = random.randint(120, 240)  # 2-4 seconds
        self.time_since_last_shop = 0
        self.force_shop_timer = 1800  # 30 seconds at 60 FPS
        self.visited_shops = set()
        self.bistro_seeker = False  # Better Quality: walks straight to player bistro

        # Needs / food behavior
        self.food_item = None  # ShopItem when bought from bakery
        self.state = "wander"  # wander | go_bench | sit_eat
        self.target_bench = None
        self.sit_timer = 0
        self.sit_duration = random.randint(240, 420)  # 4-7 seconds
        
        # Add direction change timer
        self.direction_timer = 0
        self.direction_interval = 120  # 2 seconds at 60 FPS
        
        self.dialogs = [
            # Weather related
            "Nice weather today!",
            "The weather changes so quickly here!",
            "I love when it rains, everything feels so fresh.",
            "This sunshine is perfect for a walk.",
            "The stars are so bright tonight!",
            "Looks like it might rain soon.",
            "What a beautiful sunset!",
            "The morning air is so crisp today.",
            
            # Shop related
            "Have you tried the bakery? Their croissants are amazing!",
            "The clothing shop has the best fashion in town.",
            "I love shopping here! The clothing shop has great deals.",
            "The arcade is fun! I got a high score in Flappy Bird!",
            "Need to save up for that new blue shirt.",
            "The bakery's bread is always fresh and warm.",
            "I heard the clothing shop is getting new items soon!",
            "The arcade's high scores are impossible to beat!",
            "The bakery's chocolate cake is to die for!",
            "I spend way too much money at these shops...",
            
            # City/Environment
            "This city is amazing! So much to explore.",
            "I heard they're adding new shops soon.",
            "The sunset here is beautiful.",
            "Have you seen the night sky? It's gorgeous!",
            "The city looks so different at night.",
            "I love how peaceful the mornings are here.",
            "The architecture in this city is stunning.",
            "There's always something new to discover here.",
            "This place keeps growing every day!",
            
            # Personal thoughts
            "My legs are tired from all this walking.",
            "Really enjoying the fresh air today.",
            "Running low on energy, might grab some cake.",
            "Wonder if anyone else is getting hungry?",
            "I should probably visit the bakery soon.",
            "Need to manage my money better...",
            "I'm hoping to buy a house here someday.",
            "Met some interesting people today!",
            "Can't wait for the weekend!",
            
            # Time of day
            "The morning market is the best time to shop.",
            "Perfect weather for an afternoon stroll.",
            "The city looks magical at sunset.",
            "Night time here is so peaceful.",
            "Early bird gets the fresh bread!",
            "Love how the shops light up at night.",
            "The morning rush is always exciting.",
            
            # Seasonal
            "Perfect spring weather today!",
            "Summer nights are the best here.",
            "The fall colors are beautiful.",
            "Can't wait for winter to come.",
            "Spring flowers are blooming everywhere!",
            "Summer sales are the best time to shop.",
            "Fall fashion is my favorite.",
            
            # Social
            "Met some great people at the arcade today.",
            "The shopkeepers are so friendly here.",
            "Everyone seems happy today!",
            "This community is so welcoming.",
            "Love chatting with the locals.",
            "Made a new friend at the bakery!",
            "The city feels alive today.",
            
            # Goals/Dreams
            "Saving up for something special!",
            "One day I'll own a shop here.",
            "Working on beating my arcade scores.",
            "Need to try everything at the bakery!",
            "Want to explore every corner of this city.",
            "Hope to make more friends here.",
            
            # Observations
            "The clouds look amazing today.",
            "So many new faces in town!",
            "The streets are busy today.",
            "Everyone seems to be shopping today.",
            "Love seeing kids play in the arcade.",
            "The bakery smells wonderful!",
            
            # Activities
            "Just finished a shopping spree!",
            "Had the best gaming session ever.",
            "Time for my daily walk.",
            "Looking for new outfits today.",
            "Planning to try a new cake flavor.",
            "Need to practice my gaming skills.",
            
            # Future plans
            "Planning a big shopping day tomorrow.",
            "Can't wait for the new arcade games!",
            "Hoping for good weather tomorrow.",
            "Should visit all the shops today.",
            "Going to try that new pastry soon.",
            
            # Health/Wellness
            "Walking is great exercise!",
            "Need to balance treats with exercise.",
            "Feeling energetic today!",
            "A bit tired from shopping.",
            "Sugar rush from the bakery!",
            "hello guyz",
            
            # Money
            "Prices here are so reasonable.",
            "Need to budget better...",
            "Saving up for something nice.",
            "Shopping spree was worth it!",
            "Great deals everywhere today.",
            
            # Life philosophy
            "Life is good in this city!",
            "Every day brings something new.",
            "Living my best life here.",
            "Grateful for this community.",
            "Making memories every day.",
            
            # Compliments
            "This city has the best shops!",
            "Everyone is so nice here!",
            "Love the positive vibes.",
            "Such a beautiful place.",
            "Best community ever!",
            
            # Random thoughts
            "Wonder what's new today?",
            "So much to do, so little time!",
            "Never a dull moment here.",
            "Each day is an adventure.",
            "Can't imagine living anywhere else!"
        ]
        self.current_dialog = ""
        self.dialog_timer = 0
        self.show_dialog = False
        self.can_talk = False  # Add this to track if player is close enough to talk
        
    def start_dialog(self):
        self.current_dialog = random.choice(self.dialogs)
        self.show_dialog = True
        self.dialog_timer = 180  # Show for 3 seconds

    def start_custom_dialog(self, text):
        self.current_dialog = text
        self.show_dialog = True
        self.dialog_timer = 180
        
    def update_dialog(self):
        if self.show_dialog:
            self.dialog_timer -= 1
            if self.dialog_timer <= 0:
                self.show_dialog = False
    
    def draw_dialog(self, screen, camera):
        if self.show_dialog:
            screen_x = camera.apply(self.original_x)
            
            # Create a temporary surface to measure text size
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.current_dialog, True, WHITE)
            text_rect = text.get_rect()
            
            # Calculate bubble size based on text size
            padding = 20
            bubble_width = text_rect.width + padding
            bubble_height = text_rect.height + padding
            
            # Create dialog surface with calculated size
            dialog_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
            pygame.draw.rect(dialog_surface, (0, 0, 0, 128), 
                            (0, 0, bubble_width, bubble_height), border_radius=10)
            
            # Center text in bubble
            text_rect.center = (bubble_width // 2, bubble_height // 2)
            dialog_surface.blit(text, text_rect)
            
            # Draw the dialog bubble with a small arrow pointing to NPC
            screen.blit(dialog_surface, 
                       (screen_x + self.width//2 - bubble_width//2, self.y - bubble_height - 20))
            
            # Draw triangle pointer
            pointer_points = [
                (screen_x + self.width//2 - 10, self.y - 20),
                (screen_x + self.width//2 + 10, self.y - 20),
                (screen_x + self.width//2, self.y - 10)
            ]
            pygame.draw.polygon(screen, (0, 0, 0, 128), pointer_points)
        
    def update(self, shops):
        # If sitting/eating, just run that behavior
        if self.state == "sit_eat":
            self.sit_timer += 1
            if self.sit_timer >= self.sit_duration:
                self.state = "wander"
                self.sit_timer = 0
                self.target_bench = None
                self.food_item = None
                # 30% chance to leave a happy message after eating
                if random.random() < 0.30:
                    self.current_dialog = random.choice([
                        "That was fun!",
                        "Best snack break ever.",
                        "10/10 bench experience.",
                        "Good vibes, good food.",
                        "I needed that.",
                    ])
                    self.show_dialog = True
                    self.dialog_timer = 180
            return

        # Walk towards bench if needed
        if self.state == "go_bench" and self.target_bench is not None:
            target_x = self.target_bench.original_x + self.target_bench.width / 2
            if abs(self.original_x - target_x) <= 2:
                self.state = "sit_eat"
                self.sit_timer = 0
                self.direction = 1
            else:
                self.direction = 1 if target_x > self.original_x else -1
                self.original_x += self.speed * self.direction
            return

        if self.in_shop:
            self.shop_timer += 1
            if self.shop_timer >= self.shop_duration:
                was_restaurant = self.active_shop is not None and isinstance(self.active_shop, Restaurant)
                if self.active_shop is not None:
                    if isinstance(self.active_shop, Restaurant):
                        process_restaurant_exit(self, self.active_shop)
                    elif isinstance(self.active_shop, ClothingShop):
                        available_colors = [c for c in CLOTHES_COLORS if c != self.clothes_color]
                        self.clothes_color = random.choice(available_colors)
                    elif isinstance(self.active_shop, Shop):
                        self.food_item = random.choice(list(shop_items.values()))
                        if benches:
                            self.target_bench = min(benches, key=lambda b: abs(b.original_x - self.original_x))
                            self.state = "go_bench"
                if was_restaurant:
                    restaurant_register_patron_departure()
                    self.visited_shops.add(restaurant)
                self.in_shop = False
                self.shop_timer = 0
                self.active_shop = None
                self.time_since_last_shop = 0
        else:
            self.time_since_last_shop += 1

            if self.bistro_seeker:
                if not restaurant_repaired or not restaurant_business_open:
                    self.bistro_seeker = False
                else:
                    sx = shop_entrance_cx(restaurant)
                    margin = restaurant.width * 0.5 + 22
                    if abs(self.original_x - sx) < margin:
                        if restaurant not in self.visited_shops and restaurant_has_seating_available():
                            self.in_shop = True
                            self.active_shop = restaurant
                            self.shop_timer = 0
                            self.shop_duration = random.randint(280, 440)
                            self.time_since_last_shop = 0
                            restaurant_register_patron_arrival()
                        self.bistro_seeker = False
                    else:
                        self.direction = 1 if sx > self.original_x else -1
                        self.original_x += self.speed * self.direction
                    return
            
            # Direction change every 2 seconds with 20% chance
            self.direction_timer += 1
            if self.direction_timer >= self.direction_interval:
                self.direction_timer = 0
                if random.random() < 0.20:  # 20% chance
                    self.direction *= -1
            
            # Move NPC
            self.original_x += self.speed * self.direction
            
            # Check for shop interaction when near entrance
            for shop in shops:
                sx = shop_entrance_cx(shop)
                margin = shop.width * 0.5 + 22
                near = abs(self.original_x - sx) < margin
                if isinstance(shop, Restaurant):
                    p_in = restaurant_entry_probability()
                    if not restaurant_repaired or not restaurant_business_open or not near or random.random() >= p_in:
                        continue
                    if shop in self.visited_shops or not restaurant_has_seating_available():
                        continue
                    self.in_shop = True
                    self.active_shop = shop
                    self.shop_timer = 0
                    self.shop_duration = random.randint(280, 440)
                    self.time_since_last_shop = 0
                    restaurant_register_patron_arrival()
                    break
                if (
                    shop not in self.visited_shops
                    and near
                    and random.random() < 0.20
                ):
                    self.in_shop = True
                    self.active_shop = shop
                    self.visited_shops.add(shop)
                    self.shop_timer = 0
                    self.time_since_last_shop = 0
                    break

            # Force shop visit after 30 seconds
            if self.time_since_last_shop >= self.force_shop_timer:
                nearest_shop = self.find_nearest_shop(shops)
                if nearest_shop:
                    sx = shop_entrance_cx(nearest_shop)
                    margin = nearest_shop.width * 0.5 + 24
                    self.direction = 1 if sx > self.original_x else -1
                    if abs(self.original_x - sx) < margin:
                        if isinstance(nearest_shop, Restaurant) and (
                            not restaurant_has_seating_available() or restaurant in self.visited_shops
                        ):
                            pass
                        else:
                            self.in_shop = True
                            self.active_shop = nearest_shop
                            if not isinstance(nearest_shop, Restaurant):
                                self.visited_shops.add(nearest_shop)
                            else:
                                self.shop_duration = random.randint(280, 440)
                                restaurant_register_patron_arrival()
                            self.shop_timer = 0
                            self.time_since_last_shop = 0

    def draw(self, camera):
        if not self.in_shop:  # Only draw if not in shop
            screen_x = camera.apply(self.original_x)
            if -self.width < screen_x < WINDOW_WIDTH + self.width:
                # If sitting, lower body a bit to look seated
                y_offset = 10 if self.state == "sit_eat" else 0
                # Body with clothes
                pygame.draw.rect(screen, self.clothes_color, 
                               (screen_x, self.y + 20 + y_offset, self.width, self.height - 20))
                # Head
                pygame.draw.circle(screen, self.skin_color, 
                                 (screen_x + self.width // 2, self.y + 15 + y_offset), 12)
                # Hair
                pygame.draw.arc(screen, self.hair_color,
                              (screen_x + self.width//2 - 12, self.y + y_offset, 24, 24),
                              0, 3.14, 3)
                # Face direction (eyes)
                eye_offset = 3 if self.direction > 0 else -3
                pygame.draw.circle(screen, BLACK, 
                                 (screen_x + self.width//2 + eye_offset, self.y + 13 + y_offset), 2)

                # Eating animation: show food near mouth
                if self.state == "sit_eat" and self.food_item is not None:
                    bob = int(math.sin(pygame.time.get_ticks() / 120) * 2)
                    draw_item_icon(screen, int(screen_x + self.width + 4), int(self.y + 12 + y_offset + bob), self.food_item.name)
                
                # Draw talk prompt if player is close
                if self.can_talk:
                    prompt_font = pygame.font.SysFont(None, 20)
                    prompt_text = prompt_font.render("Press T to talk", True, WHITE)
                    prompt_rect = prompt_text.get_rect(center=(screen_x + self.width//2, self.y - 30))
                    # Draw prompt background
                    pygame.draw.rect(screen, BLACK, prompt_rect.inflate(20, 10))
                    screen.blit(prompt_text, prompt_rect)
        
        # Still draw dialog if showing
        self.draw_dialog(screen, camera)

    def find_nearest_shop(self, shops):
        nearest_shop = None
        min_distance = float("inf")

        for shop in shops:
            if isinstance(shop, Restaurant):
                if not restaurant_repaired or not restaurant_business_open:
                    continue
                if not restaurant_has_seating_available():
                    continue
                if shop in self.visited_shops:
                    continue
            elif shop in self.visited_shops:
                continue
            sx = shop_entrance_cx(shop)
            distance = abs(self.original_x - sx)
            if distance < min_distance:
                min_distance = distance
                nearest_shop = shop

        return nearest_shop

    def check_player_collision(self, player_x, player_width):
        # Check if player is close enough to talk
        return abs(self.original_x - player_x) < (player_width + self.width)

# Add after other global variables
MAX_NPCS = 15  # Maximum number of NPCs in the world
MAX_NPCS_NIGHT = 6  # Fewer NPCs at night
SPAWN_RANGE = 800  # Distance from player to spawn new NPCs
npcs = []  # Start with empty NPC list

def _bistro_seeker_count():
    return sum(1 for n in npcs if getattr(n, "bistro_seeker", False))


def _bistro_seeker_spawn_interval():
    # Requested spawn pacing:
    # - Base: ~20 patrons / 150s => 7.5s avg
    # - Better Quality: ~23 patrons / 120s => 5.22s avg
    if bistro_upgrade_better_quality:
        lo = int(60 * 4.6)
        hi = int(60 * 6.2)
    else:
        lo = int(60 * 6.6)
        hi = int(60 * 8.8)
    return random.randint(lo, hi)


# Add this function to manage NPC spawning
def manage_npcs(player_x):
    global bistro_seeker_spawn_timer
    # Night check based on day/night cycle (matches background sun/moon logic)
    time_of_day = current_time / DAY_LENGTH
    is_night = not (0.25 <= time_of_day < 0.75)
    target_max = MAX_NPCS_NIGHT if is_night else MAX_NPCS
    extra_seeker_slots = (
        BISTRO_SEEKER_MAX_CONCURRENT
        if (
            bistro_upgrade_better_quality
            and restaurant_repaired
            and restaurant_business_open
            and not is_night
        )
        else 0
    )
    hard_cap = target_max + extra_seeker_slots

    # Calculate spawn zones
    left_spawn = player_x - SPAWN_RANGE
    right_spawn = player_x + SPAWN_RANGE
    
    # If night reduces the cap, despawn farthest NPCs first
    if len(npcs) > hard_cap:
        npcs.sort(key=lambda n: abs(n.original_x - player_x), reverse=True)
        del npcs[hard_cap:]

    # Spawn new NPCs if we're below maximum
    while len(npcs) < target_max:
        # 50% chance to spawn on left or right side
        spawn_x = left_spawn if random.random() < 0.5 else right_spawn
        npcs.append(NPC(spawn_x))

    # Bistro patrons: always spawn while repaired+open during daytime.
    if restaurant_repaired and restaurant_business_open and not is_night:
        bistro_seeker_spawn_timer -= 1
        if bistro_seeker_spawn_timer <= 0:
            bistro_seeker_spawn_timer = _bistro_seeker_spawn_interval()
            if _bistro_seeker_count() < BISTRO_SEEKER_MAX_CONCURRENT and len(npcs) < hard_cap:
                rx = shop_entrance_cx(restaurant)
                spawn_x = rx + random.choice([-1, 1]) * random.randint(180, 420)
                seeker = NPC(spawn_x)
                seeker.bistro_seeker = True
                seeker.speed = max(seeker.speed, 1.85)
                npcs.append(seeker)
    
    # Update existing NPCs
    shops = [shop, clothing_shop, arcade_shop, restaurant]  # NPC targets (+ player bistro)
    for npc in npcs:
        npc.update(shops)

# Add these constants after other global variables
BASE_MAX_STAMINA = 100
MAX_STAMINA = BASE_MAX_STAMINA  # can increase via skills
STAMINA_REGEN_RATE = 0.2  # Slower regeneration
STAMINA_DRAIN_RATE = 2 / 14    # 14x slower drain than before
SPRINT_SPEED = 8
STAMINA_REGEN_DELAY = 60  # 1 second delay before stamina starts regenerating
MINIMUM_STAMINA_TO_SPRINT = 0  # Minimum stamina required to sprint (allow draining to 0)

# Add to global variables section
stamina = MAX_STAMINA
is_sprinting = False
stamina_regen_timer = 0

# Timed stamina regen boost (coffee)
stamina_regen_boost_until_ms = 0
stamina_regen_multiplier = 1.0

CAFE_DRINKS = [
    {"name": "Espresso", "price": 8, "duration_ms": 60_000, "mult": 2.0, "hunger_restore": 2},
    {"name": "Latte", "price": 12, "duration_ms": 120_000, "mult": 3.0, "hunger_restore": 3},
    {"name": "Mega Mocha", "price": 18, "duration_ms": 180_000, "mult": 4.0, "hunger_restore": 4},
]

# Skill tree
skill_points = 0
skill_tree_open = False
skills = {
    "Parkour Master": {
        "desc": "+10 Max Stamina.",
        "icon": "parkour",
        "prereq": [],
        "unlocked": False,
    },
    "Shopper": {
        "desc": "10% discount on all prices.",
        "icon": "shopper",
        "prereq": ["Parkour Master"],
        "unlocked": False,
    },
    "Sociality": {
        "desc": "Unlocks selling your own cooked food to NPCs (60% accept).",
        "icon": "social",
        "prereq": ["Parkour Master"],
        "unlocked": False,
    },
    "Vitality": {
        "desc": "+20 Max Health.",
        "icon": "heart",
        "prereq": ["Parkour Master"],
        "unlocked": False,
    },
    "Foodie": {
        "desc": "+15 Max Hunger.",
        "icon": "fork",
        "prereq": ["Shopper"],
        "unlocked": False,
    },
    "Master Chef": {
        "desc": "Unlock more recipes + add a stove (bigger meals).",
        "icon": "chef",
        "prereq": ["Shopper"],
        "unlocked": False,
    },
}

def has_skill(name: str) -> bool:
    return bool(skills.get(name, {}).get("unlocked"))

def get_skill_cost(name: str) -> int:
    """
    Skill cost is based on unlock depth/stage:
    - root (no prereqs): 1
    - children: 2
    - grandchildren: 3
    and so on.
    """
    memo = {}

    def depth(n: str, visiting: set) -> int:
        if n in memo:
            return memo[n]
        if n in visiting:
            # Cycle guard; treat as expensive rather than crashing
            memo[n] = 999
            return 999
        visiting.add(n)
        node = skills.get(n, {})
        prereq = node.get("prereq", []) or []
        if not prereq:
            d = 1
        else:
            d = 1 + max(depth(p, visiting) for p in prereq)
        visiting.remove(n)
        memo[n] = d
        return d

    return int(depth(name, set()))

def apply_skill_effects():
    """Recompute derived stats from skills."""
    global MAX_STAMINA, stamina, MAX_HEALTH, health, MAX_HUNGER, hunger
    old_max_stamina = MAX_STAMINA
    old_max_health = MAX_HEALTH
    old_max_hunger = MAX_HUNGER
    MAX_STAMINA = BASE_MAX_STAMINA + (10 if has_skill("Parkour Master") else 0)
    MAX_HEALTH = BASE_MAX_HEALTH + (20 if has_skill("Vitality") else 0)
    MAX_HUNGER = BASE_MAX_HUNGER + (15 if has_skill("Foodie") else 0)
    # Keep the same fill ratio when max changes so values don't look "reset"
    if old_max_stamina > 0:
        stamina = min(MAX_STAMINA, max(0.0, stamina * (MAX_STAMINA / old_max_stamina)))
    else:
        stamina = min(stamina, MAX_STAMINA)
    if old_max_health > 0:
        health = min(MAX_HEALTH, max(0, int(round(health * (MAX_HEALTH / old_max_health)))))
    else:
        health = min(health, MAX_HEALTH)
    if old_max_hunger > 0:
        hunger = min(MAX_HUNGER, max(0, int(round(hunger * (MAX_HUNGER / old_max_hunger)))))
    else:
        hunger = min(hunger, MAX_HUNGER)

def get_effective_price(price: int) -> int:
    """Apply discounts from skills."""
    if has_skill("Shopper"):
        return int(math.ceil(price * 0.90))
    return int(price)

def can_unlock_skill(name: str) -> bool:
    node = skills.get(name)
    if not node or node["unlocked"]:
        return False
    for req in node.get("prereq", []):
        if not has_skill(req):
            return False
    return skill_points >= get_skill_cost(name)

def unlock_skill(name: str) -> bool:
    global skill_points
    if not can_unlock_skill(name):
        return False
    node = skills[name]
    node["unlocked"] = True
    skill_points -= get_skill_cost(name)
    apply_skill_effects()
    return True

# Apply skill-derived stats at startup
apply_skill_effects()

# Add this function with other drawing functions
def draw_stamina_bar():
    global STAMINA_BAR_ALPHA
    
    # Fade out when in shop/game
    # Keep stamina visible in cafe (you're buying a stamina buff)
    hide_now = (
        shop_open
        or clothing_shop_open
        or arcade_shop_open
        or supermarket_open
        or seafood_market_open
        or utility_cart_open
        or black_market_open
        or hotel_lobby_open
        or house_lobby_open
        or mission_center_open
        or restaurant_open
        or SETTINGS_OPEN
        or achievements_open
        or skill_tree_open
        or arcade_shop.any_arcade_playing()
        or in_hotel_room
        or microwave_open
        or stove_open
        or grill_open
        or sleep_cutscene_timer > 0
        or house_build_menu_open
        or on_fishing_island
        or ferry_anim_timer > 0
        or cheat_panel_open
    )
    if hide_now:
        # These UIs feel cleaner with stamina fully hidden (no half-fade linger).
        STAMINA_BAR_ALPHA = 0
    else:
        STAMINA_BAR_ALPHA = min(255, STAMINA_BAR_ALPHA + FADE_SPEED)
    
    if STAMINA_BAR_ALPHA > 0:
        now = pygame.time.get_ticks()
        show_boost = stamina_regen_boost_until_ms > now
        bar_h = 24
        text_h = 26 if show_boost else 0
        surf_h = bar_h + text_h
        # Create a surface for the stamina bar with alpha channel (taller if coffee buff line shown)
        bar_surface = pygame.Surface((204 + 150, max(24, surf_h)), pygame.SRCALPHA)

        # Draw bar background with alpha
        pygame.draw.rect(bar_surface, (*BLACK, STAMINA_BAR_ALPHA), (0, 0, 204, bar_h))
        # Draw stamina level with alpha
        pygame.draw.rect(bar_surface, (0, 191, 255, STAMINA_BAR_ALPHA),
                        (2, 2, (stamina / MAX_STAMINA) * 200, 20))

        # Draw text with alpha
        stamina_font = pygame.font.SysFont(None, 24)
        stamina_text = stamina_font.render(f"Stamina: {int(stamina)}", True,
                                         (255, 255, 255, STAMINA_BAR_ALPHA))
        bar_surface.blit(stamina_text, (204 + 10, 2))

        # Boost timer (if active) — second line below label so it isn't clipped
        if show_boost:
            remaining = int((stamina_regen_boost_until_ms - now) // 1000)
            mm = remaining // 60
            ss = remaining % 60
            boost_text = stamina_font.render(
                f"Regen x{stamina_regen_multiplier:.0f}  {mm}:{ss:02d}", True,
                (255, 255, 255, STAMINA_BAR_ALPHA))
            bar_surface.blit(boost_text, (204 + 10, 26))

        # Blit the entire surface to the screen
        # Sit below XP label + time/weather block (see draw_status_bars)
        screen.blit(bar_surface, (20, 144))

# Add this constant with other stamina constants
JUMP_STAMINA_COST = 19

# Add this to your global variables
STAMINA_BAR_ALPHA = 255  # Full opacity
FADE_SPEED = 15  # Speed of fade effect

# Add to global variables
DAY_LENGTH = 3600  # 1 minute = 3600 frames at 60 FPS
current_time = 0
sky_color = SKY_BLUE
day_index = 0  # increments each time current_time wraps

# Shop hours (fraction of the 0..1 day cycle).
# 0.0 is midnight, 0.25 sunrise-ish, 0.5 noon-ish, 0.75 sunset-ish.
# Note: day/night visuals are handled by the sky/sun/moon logic.

# Add this function
def update_day_night_cycle():
    global current_time, sky_color, day_index
    prev = current_time
    current_time = (current_time + 1) % DAY_LENGTH
    if prev > current_time:
        day_index += 1
        refresh_seafood_daily_offer(force=True)
        refresh_black_market_offers(force=True)
    
    # Calculate time of day (0.0 to 1.0)
    time_of_day = current_time / DAY_LENGTH
    
    # Calculate sky color
    if time_of_day < 0.25:  # Sunrise (6:00 - 12:00)
        progress = time_of_day * 4  # 0.0 to 1.0 during sunrise
        sky_color = (
            int(0 + progress * 135),  # From dark to light blue
            int(0 + progress * 206),
            int(40 + progress * 195)
        )
    elif time_of_day < 0.5:  # Day (12:00 - 18:00)
        sky_color = SKY_BLUE
    elif time_of_day < 0.75:  # Sunset (18:00 - 24:00)
        progress = (time_of_day - 0.5) * 4  # 0.0 to 1.0 during sunset
        sky_color = (
            int(135 - progress * 135),  # From light blue to dark
            int(206 - progress * 206),
            int(235 - progress * 195)
        )
    else:  # Night (24:00 - 6:00)
        sky_color = (0, 0, 40)  # Dark blue night sky

# Add to global variables
WEATHER_TYPES = ['clear', 'rain', 'snow']
current_weather = 'clear'
weather_timer = 0

def update_weather():
    """Cycle weather type for UI; no on-screen rain/snow particles."""
    global current_weather, weather_timer

    weather_timer += 1
    if weather_timer > 1800:  # Change weather every 30 seconds
        weather_timer = 0
        current_weather = random.choice(WEATHER_TYPES)


def show_failure_toast(message: str):
    """Brief on-screen hint when an action fails (money, inventory, timing, etc.)."""
    global failure_popup
    failure_popup = {"message": str(message), "timer": FAILURE_POPUP_DURATION}


def show_success_toast(message: str):
    """Brief confirmation (sales, stocking, etc.) — same placement as failure toasts."""
    global success_popup
    success_popup = {"message": str(message), "timer": SUCCESS_POPUP_DURATION}


def step_need(mission, idx):
    s = mission.chain_spec[idx]
    if s[0] == "buy":
        return int(s[2])
    return int(s[1])


def prior_steps_done(mission, idx):
    if idx <= 0:
        return True
    for j in range(idx):
        if mission.chain_progress[j] < step_need(mission, j):
            return False
    return True


def next_chain_work_step(mission):
    sp = getattr(mission, "chain_spec", None)
    if not sp:
        return None
    for idx in range(len(sp)):
        if not prior_steps_done(mission, idx):
            continue
        if mission.chain_progress[idx] < step_need(mission, idx):
            return idx
    return None


def chain_fully_complete(mission):
    sp = getattr(mission, "chain_spec", None)
    if not sp:
        return False
    for idx in range(len(sp)):
        if mission.chain_progress[idx] < step_need(mission, idx):
            return False
    return True


def init_chain_mission(mission):
    if mission.condition_type == "chain" and getattr(mission, "chain_spec", None):
        mission.chain_progress = [0] * len(mission.chain_spec)


def notify_chain_buy(item_name):
    for m in mission_center.active_missions:
        if m.condition_type != "chain" or not getattr(m, "chain_spec", None):
            continue
        idx = next_chain_work_step(m)
        if idx is None:
            continue
        step = m.chain_spec[idx]
        if step[0] == "buy" and step[1] == item_name:
            m.chain_progress[idx] += 1
            break


def notify_chain_cook():
    for m in mission_center.active_missions:
        if m.condition_type != "chain" or not getattr(m, "chain_spec", None):
            continue
        idx = next_chain_work_step(m)
        if idx is None:
            continue
        step = m.chain_spec[idx]
        if step[0] == "cook":
            m.chain_progress[idx] += 1
            break


def notify_chain_npc_interaction():
    for m in mission_center.active_missions:
        if m.condition_type != "chain" or not getattr(m, "chain_spec", None):
            continue
        idx = next_chain_work_step(m)
        if idx is None:
            continue
        step = m.chain_spec[idx]
        if step[0] == "npc":
            m.chain_progress[idx] += 1
            break


def objective_lines_for_mission(mission):
    """Return list of strings for the objective card (progress included)."""
    if mission.condition_type == "chain" and getattr(mission, "chain_spec", None):
        idx = next_chain_work_step(mission)
        if idx is None:
            return ["Chain complete — turn in at Mission Center"]
        step = mission.chain_spec[idx]
        need = step_need(mission, idx)
        kind = step[0]
        cur = min(mission.chain_progress[idx], need)
        if kind == "buy":
            label = f"Buy {step[1]}"
        elif kind == "cook":
            label = "Cook meals"
        else:
            label = "Talk or sell to NPC"
        return [f"{label} {cur}/{need}"]

    ct = mission.condition_type
    val = mission.condition_value
    if ct == "flappy_score":
        cur = min(arcade_shop.flappy_bird.score, val)
        return [f"Flappy score {cur}/{val}"]
    if ct == "snake_score":
        cur = min(arcade_shop.snake.score, val)
        return [f"Snake score {cur}/{val}"]
    if ct == "dodge_score":
        cur = min(arcade_shop.dodge.score, val)
        return [f"Dodge score {cur}/{val}"]
    if ct == "breakout_score":
        cur = min(arcade_shop.breakout.score, val)
        return [f"Breakout bricks {cur}/{val}"]
    if ct == "pong_score":
        cur = min(arcade_shop.pong.score, val)
        return [f"Pong goals {cur}/{val}"]
    if ct == "stack_score":
        cur = min(arcade_shop.stack.score, val)
        return [f"Stack layers {cur}/{val}"]
    if ct == "money_spent":
        cur = min(money_spent, val)
        return [f"Money spent ${cur}/${val}"]
    if ct == "items_eaten":
        cur = min(items_eaten, val)
        return [f"Items eaten {cur}/{val}"]
    if ct == "npcs_talked":
        cur = min(npcs_talked, val)
        return [f"NPC chats {cur}/{val}"]
    if ct == "distance_walked":
        cur = min(int(distance_walked), val)
        return [f"Distance {cur}/{val}px"]
    if ct == "level":
        cur = min(level, val)
        return [f"Reach level {cur}/{val}"]
    if ct == "cooked_meals":
        cur = min(cooked_meals, val)
        return [f"Cooked meals {cur}/{val}"]
    if ct == "microwave_meals":
        cur = min(microwave_meals, val)
        return [f"Microwave meals {cur}/{val}"]
    if ct == "stove_meals":
        cur = min(stove_meals, val)
        return [f"Stove meals {cur}/{val}"]
    if ct == "coffee_guy":
        cur = 1 if mission_coffee_guy_done else 0
        return [f"Drink coffee while a coffee buff is active {cur}/1"]
    return [mission.description]


def should_hide_objective_card():
    """Hide mission objectives while any menu, arcade minigame, or hotel/cooking UI is up."""
    return (
        shop_open
        or clothing_shop_open
        or arcade_shop_open
        or supermarket_open
        or hotel_lobby_open
        or mission_center_open
        or restaurant_open
        or SETTINGS_OPEN
        or achievements_open
        or skill_tree_open
        or cafe_open
        or in_hotel_room
        or in_house_room
        or microwave_open
        or stove_open
        or grill_open
        or sleep_cutscene_timer > 0
        or arcade_shop.any_arcade_playing()
        or house_lobby_open
        or house_build_menu_open
        or on_fishing_island
        or ferry_anim_timer > 0
    )


def draw_objective_card():
    if not mission_center.active_missions or should_hide_objective_card():
        return

    pad = 12
    title_font = get_font(22, bold=True)
    body_font = get_font(18)
    margin_x = 20
    margin_y = 118

    max_w = 320
    blocks = []
    for mission in mission_center.active_missions:
        lines = objective_lines_for_mission(mission)
        blocks.append((mission.title, lines))

    line_h = body_font.get_height() + 4
    header_h = title_font.get_height() + 8
    total_h = header_h
    for title, lines in blocks:
        total_h += title_font.get_height() + 6 + len(lines) * line_h + 10

    box_w = min(max_w, WINDOW_WIDTH - 40)
    box_h = total_h + pad * 2
    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (18, 22, 30, 230), (0, 0, box_w, box_h), border_radius=12)
    pygame.draw.rect(surf, (80, 180, 255, 200), (0, 0, box_w, box_h), 2, border_radius=12)

    y = pad
    surf.blit(get_font(20, bold=True).render("Objectives", True, (160, 200, 255)), (pad, y))
    y += header_h
    for title, lines in blocks:
        surf.blit(title_font.render(title, True, WHITE), (pad, y))
        y += title_font.get_height() + 6
        for ln in lines:
            surf.blit(body_font.render(ln, True, (220, 225, 235)), (pad + 4, y))
            y += line_h
        y += 8

    screen.blit(surf, (margin_x, margin_y))


def draw_failure_popup():
    global failure_popup
    if not failure_popup or failure_popup["timer"] <= 0:
        failure_popup = None
        return

    fade_frames = 45
    t = failure_popup["timer"]
    alpha = 255 if t > fade_frames else max(0, int(255 * (t / fade_frames)))

    box_w = min(520, WINDOW_WIDTH - 40)
    box_h = 52
    x = (WINDOW_WIDTH - box_w) // 2
    y = WINDOW_HEIGHT - box_h - 24

    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_alpha = int(210 * (alpha / 255))
    pygame.draw.rect(surf, (40, 18, 18, bg_alpha), (0, 0, box_w, box_h), border_radius=10)
    pygame.draw.rect(surf, (255, 90, 90, alpha), (0, 0, box_w, box_h), 2, border_radius=10)

    msg = failure_popup["message"]
    font = get_font(20)
    if font.size(msg)[0] > box_w - 24:
        font = get_font(17)
    txt = font.render(msg, True, (255, 230, 230, alpha))
    surf.blit(txt, ((box_w - txt.get_width()) // 2, (box_h - txt.get_height()) // 2))
    screen.blit(surf, (x, y))


def draw_success_popup():
    global success_popup
    if not success_popup or success_popup["timer"] <= 0:
        success_popup = None
        return

    fade_frames = 45
    t = success_popup["timer"]
    alpha = 255 if t > fade_frames else max(0, int(255 * (t / fade_frames)))

    box_w = min(520, WINDOW_WIDTH - 40)
    box_h = 52
    x = (WINDOW_WIDTH - box_w) // 2
    y = WINDOW_HEIGHT - box_h - 24

    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_alpha = int(210 * (alpha / 255))
    pygame.draw.rect(surf, (18, 40, 28, bg_alpha), (0, 0, box_w, box_h), border_radius=10)
    pygame.draw.rect(surf, (90, 200, 120, alpha), (0, 0, box_w, box_h), 2, border_radius=10)

    msg = success_popup["message"]
    font = get_font(20)
    if font.size(msg)[0] > box_w - 24:
        font = get_font(17)
    txt = font.render(msg, True, (220, 255, 230, alpha))
    surf.blit(txt, ((box_w - txt.get_width()) // 2, (box_h - txt.get_height()) // 2))
    screen.blit(surf, (x, y))


def check_mission_completion():
    """Complete active missions and award money + XP."""
    global xp, mission_popup
    for mission in mission_center.active_missions[:]:
        ok = False
        if mission.condition_type == "chain":
            ok = chain_fully_complete(mission)
        elif mission.condition_type == "flappy_score":
            ok = arcade_shop.flappy_bird.score >= mission.condition_value
        elif mission.condition_type == "snake_score":
            ok = arcade_shop.snake.score >= mission.condition_value
        elif mission.condition_type == "dodge_score":
            ok = arcade_shop.dodge.score >= mission.condition_value
        elif mission.condition_type == "breakout_score":
            ok = arcade_shop.breakout.score >= mission.condition_value
        elif mission.condition_type == "pong_score":
            ok = arcade_shop.pong.score >= mission.condition_value
        elif mission.condition_type == "stack_score":
            ok = arcade_shop.stack.score >= mission.condition_value
        elif mission.condition_type == "money_spent":
            ok = money_spent >= mission.condition_value
        elif mission.condition_type == "items_eaten":
            ok = items_eaten >= mission.condition_value
        elif mission.condition_type == "npcs_talked":
            ok = npcs_talked >= mission.condition_value
        elif mission.condition_type == "distance_walked":
            ok = distance_walked >= mission.condition_value
        elif mission.condition_type == "level":
            ok = level >= mission.condition_value
        elif mission.condition_type == "cooked_meals":
            ok = cooked_meals >= mission.condition_value
        elif mission.condition_type == "microwave_meals":
            ok = microwave_meals >= mission.condition_value
        elif mission.condition_type == "stove_meals":
            ok = stove_meals >= mission.condition_value
        elif mission.condition_type == "coffee_guy":
            ok = mission_coffee_guy_done

        if ok:
            mission.completed = True
            add_money(mission.reward)
            xp_gain = int(getattr(mission, "xp_reward", 0))
            xp += xp_gain
            check_level_up()
            mission_center.active_missions.remove(mission)
            mission_popup = {
                "title": mission.title,
                "reward_money": int(mission.reward),
                "reward_xp": int(xp_gain),
                "timer": MISSION_POPUP_DURATION,
            }

# Add moon drawing function after draw_sun():
def draw_moon():
    # Draw main moon circle with glow effect
    glow_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    for radius in range(40, 20, -5):
        alpha = (40 - radius) * 3
        pygame.draw.circle(glow_surface, (255, 255, 255, alpha), (50, 50), radius)
    screen.blit(glow_surface, (650, 50))
    
    # Draw main moon
    pygame.draw.circle(screen, WHITE, (700, 100), 35)
    
    # Draw crater details
    pygame.draw.circle(screen, (200, 200, 200), (685, 90), 8)
    pygame.draw.circle(screen, (200, 200, 200), (715, 95), 10)
    pygame.draw.circle(screen, (200, 200, 200), (700, 110), 7)


def update_and_draw_vfx(camera):
    """Update and draw particles (world-space)."""
    if not ENABLE_PARTICLES:
        vfx_particles.clear()
        return
    for p in vfx_particles[:]:
        p.update()
        if p.life <= 0 or p.y > WINDOW_HEIGHT + 80:
            vfx_particles.remove(p)
        else:
            p.draw(camera)

# Add these constants after other global variables
HUNGER_WELL_FED = 80  # Threshold for being "well fed" (80% or higher)
HEALTH_REGEN_RATE = 0.1  # Health regeneration per frame when well fed
HEALTH_REGEN_INTERVAL = 60  # Regenerate health every second

# Add to global variables
health_regen_timer = 0

# Add after other class definitions
class Mission:
    def __init__(self, title, description, reward, xp_reward, condition_type, condition_value, chain_spec=None):
        self.title = title
        self.description = description
        self.reward = reward
        self.xp_reward = xp_reward
        self.condition_type = condition_type  # e.g., 'flappy_score' or 'chain'
        self.condition_value = condition_value  # e.g., 20 points (unused for chain)
        self.chain_spec = chain_spec  # tuple/list of steps: ("buy", "Rice", 2), ("cook", 2), ("npc", 1)
        self.chain_progress = []  # filled when mission is accepted
        self.active = False
        self.completed = False

class MissionCenter:
    def __init__(self, x):
        self.original_x = x
        self.width = 120
        self.height = 120
        self.y = 380
        self.missions = [
            Mission(
                "Flappy Master",
                "Score 20 points in Flappy Bird",
                459,
                400,
                'flappy_score',
                20
            ),
            Mission(
                "Flappy Warmup",
                "Score 10 points in Flappy Bird",
                180,
                200,
                'flappy_score',
                10
            ),
            Mission(
                "Flappy Legend",
                "Score 35 points in Flappy Bird",
                800,
                650,
                'flappy_score',
                35
            ),
            Mission(
                "Snake Snack",
                "Eat 8 apples in Snake",
                220,
                240,
                "snake_score",
                8,
            ),
            Mission(
                "Serpent Streak",
                "Score 15 in Snake (one run)",
                400,
                420,
                "snake_score",
                15,
            ),
            Mission(
                "Drop Zone",
                "Clear 25 hazards in Dodge",
                240,
                260,
                "dodge_score",
                25,
            ),
            Mission(
                "Neon Rain",
                "Clear 50 hazards in Dodge",
                540,
                520,
                "dodge_score",
                50,
            ),
            Mission(
                "Brick Basics",
                "Break 20 bricks in Breakout",
                260,
                280,
                "breakout_score",
                20,
            ),
            Mission(
                "Wall Wrecker",
                "Break 45 bricks in Breakout",
                600,
                560,
                "breakout_score",
                45,
            ),
            Mission(
                "Net Gain",
                "Score 4 goals in Pong vs AI",
                240,
                260,
                "pong_score",
                4,
            ),
            Mission(
                "Rally Export",
                "Score 9 goals in Pong vs AI",
                520,
                500,
                "pong_score",
                9,
            ),
            Mission(
                "Foundation Course",
                "Stack 6 layers in Stack Tower",
                230,
                250,
                "stack_score",
                6,
            ),
            Mission(
                "Skyline Permit",
                "Stack 12 layers in Stack Tower",
                560,
                540,
                "stack_score",
                12,
            ),
            Mission(
                "Big Spender",
                "Spend $500 total in shops",
                250,
                300,
                'money_spent',
                500
            ),
            Mission(
                "Gourmet Day",
                "Eat 5 items",
                160,
                250,
                'items_eaten',
                5
            ),
            Mission(
                "Social Hour",
                "Talk to NPCs 5 times",
                160,
                250,
                'npcs_talked',
                5
            ),
            Mission(
                "Coffee guy",
                "Drink a cafe coffee while your stamina is still under a previous coffee's regen boost.",
                220,
                280,
                "coffee_guy",
                1,
            ),
            Mission(
                "From Shelf to Citizen",
                "Buy rice, cook two meals in your hotel, then talk to someone or sell them your food.",
                420,
                480,
                "chain",
                0,
                chain_spec=(
                    ("buy", "Rice", 2),
                    ("cook", 2),
                    ("npc", 1),
                ),
            ),
        ]
        self.active_missions = []
    
    def check_collision(self, player_x, player_width):
        return (self.original_x < player_x + player_width and 
                player_x < self.original_x + self.width)
    
    def draw(self, camera):
        shop_x = camera.apply(self.original_x)
        if -self.width < shop_x < WINDOW_WIDTH + self.width:
            # Main building
            pygame.draw.rect(screen, BROWN, (shop_x, self.y, self.width, self.height))
            # Door
            pygame.draw.rect(screen, LIGHT_BROWN, (shop_x + 45, self.y + 60, 30, 60))
            # Sign
            sign_y = self.y - 30
            sign_width = 100
            sign_height = 25
            sign_x = shop_x + (self.width - sign_width) // 2
            pygame.draw.rect(screen, WHITE, (sign_x, sign_y, sign_width, sign_height))
            sign_font = pygame.font.SysFont(None, 30)
            sign_text = sign_font.render("MISSIONS", True, BROWN)
            text_rect = sign_text.get_rect(center=(sign_x + sign_width//2, sign_y + sign_height//2))
            screen.blit(sign_text, text_rect)

    def draw_menu(self):
        # Larger menu + consistent spacing to avoid overlaps
        menu_width = WINDOW_WIDTH // 2
        menu_height = int(WINDOW_HEIGHT * 0.7)
        menu_rect = pygame.Rect((WINDOW_WIDTH - menu_width)//2, (WINDOW_HEIGHT - menu_height)//2,
                                menu_width, menu_height)
        pygame.draw.rect(screen, MENU_BG, menu_rect)
        pygame.draw.rect(screen, BROWN, menu_rect, 4)
        
        header_height = 70
        title_font = pygame.font.SysFont(None, 44)
        title = title_font.render("Mission Center", True, BROWN)
        title_rect = title.get_rect(centerx=menu_rect.centerx, top=menu_rect.top + 18)
        screen.blit(title, title_rect)
        
        buttons = []
        global mission_scroll
        list_top = menu_rect.y + header_height + 10
        list_bottom = menu_rect.bottom - 20
        viewport_h = list_bottom - list_top

        mission_font = pygame.font.SysFont(None, 22)
        line_height = 18
        button_height = 66
        gap = 12

        content_h = len(self.missions) * (button_height + gap) - gap if self.missions else 0
        max_scroll = max(0, content_h - viewport_h)
        mission_scroll = max(0, min(max_scroll, mission_scroll))

        previous_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(menu_rect.x + 20, list_top, menu_rect.width - 40, viewport_h))

        y_offset = list_top - mission_scroll
        
        for mission in self.missions:
            # Stop drawing if we'd overflow the menu area
            button_rect = pygame.Rect(menu_rect.x + 20, y_offset, menu_rect.width - 40, button_height)
            status = "ACTIVE" if mission in self.active_missions else "COMPLETED" if mission.completed else "NEW"
            
            # Draw button
            if button_rect.bottom >= list_top and button_rect.top <= list_bottom:
                button_color = BUTTON_HOVER if button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
                pygame.draw.rect(screen, button_color, button_rect)
                pygame.draw.rect(screen, BROWN, button_rect, 2)
            
                # Draw mission info
                text_lines = [
                    f"{mission.title} - {status}",
                    f"{mission.description}",
                    f"Reward: ${mission.reward}  +{mission.xp_reward} XP"
                ]
                
                for i, line in enumerate(text_lines):
                    text = mission_font.render(line, True, BLACK)
                    screen.blit(text, (button_rect.x + 10, button_rect.y + 10 + i * line_height))
            
            buttons.append((button_rect, mission))
            y_offset += button_height + gap

        screen.set_clip(previous_clip)

        if max_scroll > 0:
            hint = pygame.font.SysFont(None, 22).render("Scroll: mouse wheel", True, GRAY)
            screen.blit(hint, (menu_rect.x + 20, menu_rect.bottom - 18))
        
        # Draw close button
        close_rect = pygame.Rect(menu_rect.right - 44, menu_rect.top + 16, 28, 28)
        pygame.draw.rect(screen, RED, close_rect)
        close_text = pygame.font.SysFont(None, 30).render("X", True, WHITE)
        close_rect_center = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, close_rect_center)
        
        return buttons, close_rect
    
    def draw_active_missions(self):
        if self.active_missions:
            y_offset = 20
            mission_font = pygame.font.SysFont(None, 20)
            title_font = pygame.font.SysFont(None, 24)
            
            # Draw "Active Missions" title
            title = title_font.render("Active Missions:", True, WHITE)
            title_rect = title.get_rect(topright=(WINDOW_WIDTH - 20, y_offset))
            
            # Draw title background
            pygame.draw.rect(screen, BLACK, title_rect.inflate(20, 10))
            screen.blit(title, title_rect)
            
            y_offset += 30
            
            for mission in self.active_missions:
                text = mission_font.render(f"{mission.title}: {mission.description}", True, WHITE)
                text_rect = text.get_rect(topright=(WINDOW_WIDTH - 20, y_offset))
                
                # Draw mission background
                pygame.draw.rect(screen, (*BLACK, 128), text_rect.inflate(20, 10))
                screen.blit(text, text_rect)
                y_offset += 25

# Add to global variables
mission_center = MissionCenter(-200)  # Position it on the left side of spawn (spawn is at x=100)
mission_center_open = False

# Game loop
running = True
clock = pygame.time.Clock()
shop_open = False  # Track if shop menu is open
clothing_shop_open = False  # Track if clothing shop menu is open
arcade_shop_open = False  # Track if arcade shop menu is open

# Add in the game loop, before drawing
# Shop interaction
shop_collision = shop.check_collision(player_x, player_width)
clothing_shop_collision = clothing_shop.check_collision(player_x, player_width)
arcade_shop_collision = arcade_shop.check_collision(player_x, player_width)
show_shop_menu = False
show_clothing_shop_menu = False
show_arcade_shop_menu = False

# Add to global variables
achievements_open = False  # Track if achievements menu is open

# Add to global variables
achievements = {
    "First Purchase": {
        "description": "Buy anything from a shop",
        "flavor_text": "Retail therapy: initiated.",
        "difficulty": "Easy",
        "xp_reward": 225,
        "unlocked": False,
        "condition": "money_spent",
        "requirement": 1
    },
    "Rookie Pilot": {
        "description": "Score 10 points in Flappy Bird at once",
        "flavor_text": "Wings? Borrowed. Confidence? Maxed.",
        "difficulty": "Easy",
        "xp_reward": 270,
        "unlocked": False,
        "condition": "flappy_score",
        "requirement": 10
    },
    "Flappy Bird Champion": {
        "description": "Score 30 points in Flappy Bird at once",
        "flavor_text": "Phew, that was hard, now my eyes hurt!",
        "difficulty": "Hard",
        "xp_reward": 1080,
        "unlocked": False,
        "condition": "flappy_score",
        "requirement": 30
    },
    "Snake Rookie": {
        "description": "Score 8 in Snake in one run",
        "flavor_text": "Pixels consumed. Morals questionable.",
        "difficulty": "Easy",
        "xp_reward": 270,
        "unlocked": False,
        "condition": "snake_score",
        "requirement": 8
    },
    "Snake Legend": {
        "description": "Score 22 in Snake in one run",
        "flavor_text": "You are the long boi now.",
        "difficulty": "Hard",
        "xp_reward": 990,
        "unlocked": False,
        "condition": "snake_score",
        "requirement": 22
    },
    "Dodge Rookie": {
        "description": "Clear 15 hazards in Dodge",
        "flavor_text": "Gravity is rude. You are ruder.",
        "difficulty": "Easy",
        "xp_reward": 270,
        "unlocked": False,
        "condition": "dodge_score",
        "requirement": 15
    },
    "Dodge Legend": {
        "description": "Clear 45 hazards in Dodge",
        "flavor_text": "Neon rain. Zero hits. Maximum focus.",
        "difficulty": "Hard",
        "xp_reward": 990,
        "unlocked": False,
        "condition": "dodge_score",
        "requirement": 45
    },
    "Brick Breaker": {
        "description": "Break 20 bricks in Breakout in one run",
        "flavor_text": "Paddle up. Walls down.",
        "difficulty": "Easy",
        "xp_reward": 315,
        "unlocked": False,
        "condition": "breakout_score",
        "requirement": 20
    },
    "Demolition Expert": {
        "description": "Break 45 bricks in Breakout in one run",
        "flavor_text": "No wall survives this run.",
        "difficulty": "Hard",
        "xp_reward": 1035,
        "unlocked": False,
        "condition": "breakout_score",
        "requirement": 45
    },
    "Speed Demon": {
        "description": "Sprint for 10 seconds without stopping",
        "flavor_text": "I am speed! My legs are burning though...",
        "difficulty": "Medium",
        "xp_reward": 540,
        "unlocked": False,
        "condition": "sprint_time",
        "requirement": 600  # 10 seconds at 60 FPS
    },
    "Foodie": {
        "description": "Eat 10 food items",
        "flavor_text": "If it fits in the inventory, it fits in the stomach.",
        "difficulty": "Easy",
        "xp_reward": 315,
        "unlocked": False,
        "condition": "items_eaten",
        "requirement": 10
    },
    "Social Butterfly": {
        "description": "Talk to NPCs 10 times",
        "flavor_text": "Small talk speedrun any%.",
        "difficulty": "Easy",
        "xp_reward": 315,
        "unlocked": False,
        "condition": "npcs_talked",
        "requirement": 10
    },
    "Marathon": {
        "description": "Walk 50000 pixels total",
        "flavor_text": "My feet left the chat.",
        "difficulty": "Medium",
        "xp_reward": 630,
        "unlocked": False,
        "condition": "distance_walked",
        "requirement": 50000
    },
    "Level 5": {
        "description": "Reach level 5",
        "flavor_text": "I’m basically a professional citizen now.",
        "difficulty": "Medium",
        "xp_reward": 720,
        "unlocked": False,
        "condition": "level",
        "requirement": 5
    },
    "Shopaholic": {
        "description": "Spend over 1000 coins in shops",
        "flavor_text": "My wallet is crying, but my wardrobe is happy!",
        "difficulty": "Medium",
        "xp_reward": 720,
        "unlocked": False,
        "condition": "money_spent",
        "requirement": 1000
    },
    "First Cook": {
        "description": "Cook your first recipe",
        "flavor_text": "Chef arc begins.",
        "difficulty": "Easy",
        "xp_reward": 270,
        "unlocked": False,
        "condition": "cooked_meals",
        "requirement": 1
    },
    "Microwave Wizard": {
        "description": "Cook 10 microwave meals",
        "flavor_text": "Beep... beep... gourmet!",
        "difficulty": "Medium",
        "xp_reward": 540,
        "unlocked": False,
        "condition": "microwave_meals",
        "requirement": 10
    },
    "Stove Supreme": {
        "description": "Cook 5 stove meals",
        "flavor_text": "Now we're talking real heat.",
        "difficulty": "Hard",
        "xp_reward": 810,
        "unlocked": False,
        "condition": "stove_meals",
        "requirement": 5
    },
    "Paddle Up": {
        "description": "Score 4 goals in Pong (one run)",
        "flavor_text": "Left paddle supremacy.",
        "difficulty": "Easy",
        "xp_reward": 288,
        "unlocked": False,
        "condition": "pong_score",
        "requirement": 4
    },
    "Ping Commander": {
        "description": "Score 10 goals in Pong (one run)",
        "flavor_text": "The AI filed a complaint. It was denied.",
        "difficulty": "Hard",
        "xp_reward": 990,
        "unlocked": False,
        "condition": "pong_score",
        "requirement": 10
    },
    "Stack Apprentice": {
        "description": "Stack 7 layers in Stack Tower",
        "flavor_text": "Steady hands. Questionable architecture.",
        "difficulty": "Easy",
        "xp_reward": 306,
        "unlocked": False,
        "condition": "stack_score",
        "requirement": 7
    },
    "Skyline Chef": {
        "description": "Stack 14 layers in Stack Tower",
        "flavor_text": "You built a vertical city out of rectangles.",
        "difficulty": "Hard",
        "xp_reward": 1035,
        "unlocked": False,
        "condition": "stack_score",
        "requirement": 14
    },
    "Quarter Pusher": {
        "description": "Spend $120 at the arcade (lifetime)",
        "flavor_text": "The machine ate your wallet politely.",
        "difficulty": "Medium",
        "xp_reward": 540,
        "unlocked": False,
        "condition": "arcade_spent",
        "requirement": 120
    },
    "Token Fiend": {
        "description": "Spend $400 at the arcade (lifetime)",
        "flavor_text": "You are the reason the high score board exists.",
        "difficulty": "Hard",
        "xp_reward": 900,
        "unlocked": False,
        "condition": "arcade_spent",
        "requirement": 400
    },
    "Glutton for Fun": {
        "description": "Eat 25 food or drink items total",
        "flavor_text": "Calories are just XP in disguise.",
        "difficulty": "Medium",
        "xp_reward": 585,
        "unlocked": False,
        "condition": "items_eaten",
        "requirement": 25
    },
    "Town Gossip": {
        "description": "Talk to NPCs 20 times",
        "flavor_text": "You know everyone's business now.",
        "difficulty": "Medium",
        "xp_reward": 585,
        "unlocked": False,
        "condition": "npcs_talked",
        "requirement": 20
    },
    "Espresso Yourself": {
        "description": "Buy 5 drinks at the cafe",
        "flavor_text": "Your mug runneth over.",
        "difficulty": "Easy",
        "xp_reward": 315,
        "unlocked": False,
        "condition": "cafe_buys",
        "requirement": 5
    },
    "Grand Opening": {
        "description": "Repair the abandoned bistro on the edge of town",
        "flavor_text": "From condemned to five stars (according to you).",
        "difficulty": "Medium",
        "xp_reward": 675,
        "unlocked": False,
        "condition": "restaurant_repaired",
        "requirement": 1
    },
    "Restaurateur": {
        "description": "Sell 40 homemade plates from your bistro",
        "flavor_text": "You're basically running the city's appetite.",
        "difficulty": "Hard",
        "xp_reward": 990,
        "unlocked": False,
        "condition": "restaurant_sales",
        "requirement": 40
    },
}

# Add to global variables
SETTINGS_OPEN = False  # Track if settings menu is open
sprint_timer = 0  # frames of continuous sprinting while moving

# Achievement popup state
achievement_popup = None  # dict: {title, description, flavor_text, timer}
ACHIEVEMENT_POPUP_DURATION = 240  # 4 seconds at 60 FPS
mission_popup = None  # dict: {title, reward_money, reward_xp, timer}
MISSION_POPUP_DURATION = 210  # 3.5 seconds at 60 FPS
failure_popup = None  # dict: {message, timer}
FAILURE_POPUP_DURATION = 165  # ~2.75 s at 60 FPS
success_popup = None  # dict: {message, timer}
SUCCESS_POPUP_DURATION = 165

# Achievement progress trackers
items_eaten = 0
npcs_talked = 0
distance_walked = 0.0
_last_player_x_for_distance = None
cooked_meals = 0
microwave_meals = 0
stove_meals = 0
arcade_money_spent = 0
cafe_buys = 0
restaurant_plates_sold = 0

# Selling cooked food dialogs (30+ each)
SELL_ACCEPT_DIALOGS = [
    "Oh wow, that smells amazing. Deal!",
    "You cooked this? I'll buy it right now.",
    "My stomach just said yes.",
    "That looks restaurant-level. Sold.",
    "Okay, chef. Take my money.",
    "I was literally starving. Perfect timing.",
    "I trust you. It looks safe... mostly.",
    "This is the best offer I've seen all day.",
    "If this slaps, I'm coming back.",
    "I can’t say no to homemade food.",
    "That aroma is doing crimes. I’m in.",
    "You’re basically a food vendor now.",
    "Hand it over. I’m hungry.",
    "This is a win-win. Here you go.",
    "Looks delicious—I'll take it.",
    "I was about to buy snacks, but this is better.",
    "That's some serious cooking energy.",
    "Shut up and take my money.",
    "Homemade? That's premium.",
    "I respect the grind. Sold.",
    "That’s exactly what I wanted.",
    "The color is right. The vibe is right. Sold.",
    "I choose food. Always food.",
    "I’m trusting you with my happiness.",
    "This will fuel my walking arc.",
    "Yes. Immediately yes.",
    "I accept this tasty transaction.",
    "Chef moment. Let's go.",
    "That's a masterpiece in a box.",
    "You got yourself a customer.",
]

SELL_DENY_DIALOGS = [
    "Uh… I just ate. Maybe later.",
    "No thanks, I'm trying to save money.",
    "I don't know... I’m picky.",
    "It looks good, but I'm not hungry right now.",
    "Sorry, I only buy from stores.",
    "My stomach said no. My heart said maybe. Still no.",
    "I’m on a diet... for like, today.",
    "I don’t trust food that doesn’t come with a label.",
    "That might be delicious, but I'm not risking it.",
    "I appreciate it, but I’ll pass.",
    "Maybe if it was a different recipe.",
    "I’m scared of homemade food. Childhood trauma.",
    "Not today, chef.",
    "I can't. I'm broke.",
    "Looks suspiciously tasty. I’m suspicious.",
    "I’m waiting for bakery cake vibes.",
    "My mood says snacks, not meals.",
    "I promised myself I’d cook at home.",
    "I’m allergic to… effort. No thanks.",
    "I’m not buying food from strangers in the street.",
    "I’m good. I’m just walking.",
    "I already have food in my bag.",
    "My friend warned me about street food.",
    "Tempting, but no.",
    "That’s cool, but I’ll pass this time.",
    "I'm not feeling it today.",
    "I’m saving room for something sweet.",
    "I can’t commit to that right now.",
    "Not hungry. Not brave. Not today.",
    "You should open a shop though. Just… not with me.",
]

# Achievements menu scroll
achievements_scroll = 0

# Mission menu scroll
mission_scroll = 0
MAX_ACTIVE_MISSIONS = 3


def unlock_achievement(title):
    """Unlock achievement once, award XP, and trigger popup."""
    global xp, achievement_popup
    data = achievements.get(title)
    if not data or data.get("unlocked"):
        return
    data["unlocked"] = True
    reward = int(data.get("xp_reward", 0))
    if reward > 0:
        xp += reward
        check_level_up()
    achievement_popup = {
        "title": title,
        "description": data.get("description", ""),
        "flavor_text": data.get("flavor_text", ""),
        "timer": ACHIEVEMENT_POPUP_DURATION,
    }

def draw_achievement_popup():
    global achievement_popup
    if not achievement_popup or achievement_popup["timer"] <= 0:
        achievement_popup = None
        return

    # Steam-like toast: compact, bottom-right, dark translucent, small icon
    fade_frames = 60
    t = achievement_popup["timer"]
    alpha = 255 if t > fade_frames else max(0, int(255 * (t / fade_frames)))

    pad = 12
    icon_size = 44
    box_w = 360
    box_h = 72
    x = WINDOW_WIDTH - box_w - 18
    y = WINDOW_HEIGHT - box_h - 18

    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_alpha = int(200 * (alpha / 255))
    pygame.draw.rect(surf, (20, 20, 20, bg_alpha), (0, 0, box_w, box_h), border_radius=8)
    pygame.draw.rect(surf, (0, 0, 0, int(140 * (alpha / 255))), (1, 1, box_w - 2, box_h - 2), 1, border_radius=8)

    # Icon (simple trophy placeholder)
    icon_rect = pygame.Rect(pad, (box_h - icon_size)//2, icon_size, icon_size)
    pygame.draw.rect(surf, (45, 45, 45, alpha), icon_rect, border_radius=6)
    # Trophy glyph
    cup_color = (255, 215, 0, alpha)
    cx = icon_rect.centerx
    cy = icon_rect.centery
    pygame.draw.polygon(surf, cup_color, [(cx - 12, cy - 10), (cx + 12, cy - 10), (cx + 8, cy + 4), (cx - 8, cy + 4)])
    pygame.draw.rect(surf, cup_color, (cx - 4, cy + 4, 8, 8))
    pygame.draw.rect(surf, cup_color, (cx - 10, cy + 12, 20, 4))

    header_font = pygame.font.SysFont(None, 20)
    title_font = pygame.font.SysFont(None, 24)
    body_font = pygame.font.SysFont(None, 18)

    header = header_font.render("Achievement unlocked", True, (200, 200, 200, alpha))
    name = title_font.render(achievement_popup["title"], True, (255, 255, 255, alpha))
    # Prefer description; if too long, flavor still shows in achievements menu anyway
    body_line = achievement_popup["description"] or achievement_popup["flavor_text"]
    body = body_font.render(body_line, True, (170, 170, 170, alpha))

    text_x = icon_rect.right + pad
    surf.blit(header, (text_x, 10))
    surf.blit(name, (text_x, 28))
    surf.blit(body, (text_x, 50))

    screen.blit(surf, (x, y))

def draw_mission_popup():
    global mission_popup
    if not mission_popup or mission_popup["timer"] <= 0:
        mission_popup = None
        return

    fade_frames = 60
    t = mission_popup["timer"]
    alpha = 255 if t > fade_frames else max(0, int(255 * (t / fade_frames)))

    pad = 12
    box_w = 360
    box_h = 64
    # Stack above achievement toast
    x = WINDOW_WIDTH - box_w - 18
    y = WINDOW_HEIGHT - box_h - 18 - 78

    surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg_alpha = int(200 * (alpha / 255))
    pygame.draw.rect(surf, (20, 20, 20, bg_alpha), (0, 0, box_w, box_h), border_radius=8)
    pygame.draw.rect(surf, (80, 180, 255, alpha), (0, 0, box_w, box_h), 2, border_radius=8)

    header_font = pygame.font.SysFont(None, 20)
    title_font = pygame.font.SysFont(None, 24)
    body_font = pygame.font.SysFont(None, 18)

    header = header_font.render("Mission completed", True, (200, 200, 200, alpha))
    name = title_font.render(mission_popup["title"], True, (255, 255, 255, alpha))
    body = body_font.render(
        f"+${mission_popup['reward_money']}   +{mission_popup['reward_xp']} XP",
        True,
        (170, 170, 170, alpha),
    )

    surf.blit(header, (pad, 8))
    surf.blit(name, (pad, 24))
    surf.blit(body, (pad, 44))
    screen.blit(surf, (x, y))

def draw_settings_menu():
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    button_font = get_font(28, bold=True)
    sub_font = get_font(20)
    buttons = []
    button_texts = [
        "Continue",
        f"Fullscreen: {'ON' if FULLSCREEN_ENABLED else 'OFF'}",
        f"Particles: {'ON' if ENABLE_PARTICLES else 'OFF'}",
        "Achievements",
        "Skill Tree",
        "Quit",
    ]
    # Dynamic sizing so box/buttons are never smaller than text content
    max_text_w = max(button_font.size(t)[0] for t in button_texts)
    button_h = 42
    button_gap = 10
    side_pad = 40
    top_pad = 96
    bottom_pad = 44
    button_w = max(320, max_text_w + 56)
    menu_width = max(440, button_w + side_pad * 2)
    content_h = len(button_texts) * button_h + (len(button_texts) - 1) * button_gap
    menu_height = max(420, top_pad + content_h + bottom_pad)

    menu_x = (WINDOW_WIDTH - menu_width) // 2
    menu_y = (WINDOW_HEIGHT - menu_height) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    draw_panel(menu_rect, BROWN, title="Settings", title_color=BROWN)

    button_y = menu_y + top_pad
    
    for text in button_texts:
        button_rect = pygame.Rect(menu_x + (menu_width - button_w) // 2, button_y, button_w, button_h)
        hover = button_rect.collidepoint(pygame.mouse.get_pos())
        button_color = BUTTON_HOVER if hover else BUTTON_COLOR
        draw_button(button_rect, button_color, BROWN, hover=hover, radius=10)
        
        text_surf = button_font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)
        
        buttons.append((button_rect, text))
        button_y += button_h + button_gap

    hint = sub_font.render("ESC: Close", True, GRAY)
    screen.blit(hint, (menu_x + 18, menu_y + menu_height - 30))
    
    return buttons

def draw_achievements_menu():
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    menu_width = 600
    menu_height = 400
    menu_x = (WINDOW_WIDTH - menu_width) // 2
    menu_y = (WINDOW_HEIGHT - menu_height) // 2
    
    # Draw menu background
    pygame.draw.rect(screen, MENU_BG, (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, BROWN, (menu_x, menu_y, menu_width, menu_height), 4)
    
    # Draw title
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Achievements", True, BROWN)
    title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, top=menu_y + 20)
    screen.blit(title, title_rect)
    
    # Scrollable achievements list
    global achievements_scroll
    list_top = menu_y + 80
    list_bottom = menu_y + menu_height - 20
    viewport_h = list_bottom - list_top
    
    item_h = 88
    item_gap = 12
    content_h = len(achievements) * (item_h + item_gap) - item_gap if achievements else 0
    max_scroll = max(0, content_h - viewport_h)
    achievements_scroll = max(0, min(max_scroll, achievements_scroll))
    
    # Clip drawing to viewport
    previous_clip = screen.get_clip()
    screen.set_clip(pygame.Rect(menu_x + 20, list_top, menu_width - 40, viewport_h))
    
    achievement_font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 20)
    y = list_top - achievements_scroll
    
    for title, data in achievements.items():
        box_rect = pygame.Rect(menu_x + 20, y, menu_width - 40, item_h)
        
        # Only draw if visible
        if box_rect.bottom >= list_top and box_rect.top <= list_bottom:
            pygame.draw.rect(screen, WHITE, box_rect)
            pygame.draw.rect(screen, BROWN, box_rect, 2)
            
            status = "UNLOCKED" if data["unlocked"] else "LOCKED"
            status_color = GREEN if data["unlocked"] else RED
            diff = data.get("difficulty", "Easy")
            
            title_text = f"{title} [{diff}] - {status}"
            title_surf = achievement_font.render(title_text, True, status_color)
            screen.blit(title_surf, (box_rect.x + 10, box_rect.y + 10))
            
            desc_surf = small_font.render(data.get("description", ""), True, BLACK)
            screen.blit(desc_surf, (box_rect.x + 10, box_rect.y + 36))
            
            flavor_surf = small_font.render(data.get("flavor_text", ""), True, GRAY)
            screen.blit(flavor_surf, (box_rect.x + 10, box_rect.y + 58))
        
        y += item_h + item_gap
    
    screen.set_clip(previous_clip)
    
    # Scroll hint (only if needed)
    if max_scroll > 0:
        hint = pygame.font.SysFont(None, 22).render("Scroll: mouse wheel", True, GRAY)
        screen.blit(hint, (menu_x + 20, menu_y + menu_height - 18))
    
    # Draw back button
    back_rect = pygame.Rect(menu_x + menu_width - 90, menu_y + 20, 70, 30)
    pygame.draw.rect(screen, RED, back_rect)
    back_text = pygame.font.SysFont(None, 24).render("Back", True, WHITE)
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)
    
    return back_rect

def draw_skill_tree_menu():
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))

    menu_width = 720
    menu_height = 440
    menu_x = (WINDOW_WIDTH - menu_width) // 2
    menu_y = (WINDOW_HEIGHT - menu_height) // 2

    pygame.draw.rect(screen, MENU_BG, (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, BROWN, (menu_x, menu_y, menu_width, menu_height), 4)

    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Skill Tree", True, BROWN)
    screen.blit(title, (menu_x + 20, menu_y + 16))

    info_font = pygame.font.SysFont(None, 26)
    info = info_font.render(f"Skill Points: {skill_points}", True, BLACK)
    screen.blit(info, (menu_x + 20, menu_y + 64))

    # Node layout — stagger siblings in the same column so connector mid_x values differ (no overlap)
    nodes_all = {
        "Parkour Master": pygame.Rect(menu_x + 48, menu_y + 180, 80, 80),
        "Shopper": pygame.Rect(menu_x + 248, menu_y + 118, 80, 80),
        "Sociality": pygame.Rect(menu_x + 288, menu_y + 242, 80, 80),
        "Vitality": pygame.Rect(menu_x + 560, menu_y + 180, 80, 80),
        "Foodie": pygame.Rect(menu_x + 520, menu_y + 72, 80, 80),
        "Master Chef": pygame.Rect(menu_x + 560, menu_y + 288, 80, 80),
    }
    nodes = {"Parkour Master": nodes_all["Parkour Master"]}
    if has_skill("Parkour Master"):
        nodes["Shopper"] = nodes_all["Shopper"]
        nodes["Sociality"] = nodes_all["Sociality"]
        nodes["Vitality"] = nodes_all["Vitality"]
        if has_skill("Shopper"):
            nodes["Foodie"] = nodes_all["Foodie"]
            nodes["Master Chef"] = nodes_all["Master Chef"]

    # Draw connections (only for visible nodes) — mid_x from endpoint centers so parallel edges don't share one spine
    def center(r):
        return (r.centerx, r.centery)
    def elbow(a, b, color=GRAY, w=3):
        ax, ay = a
        bx, by = b
        mid_x = (ax + bx) // 2
        pygame.draw.line(screen, color, (ax, ay), (mid_x, ay), w)
        pygame.draw.line(screen, color, (mid_x, ay), (mid_x, by), w)
        pygame.draw.line(screen, color, (mid_x, by), (bx, by), w)
    if "Shopper" in nodes:
        elbow(center(nodes["Parkour Master"]), center(nodes["Shopper"]))
    if "Sociality" in nodes:
        elbow(center(nodes["Parkour Master"]), center(nodes["Sociality"]))
    if "Vitality" in nodes:
        elbow(center(nodes["Parkour Master"]), center(nodes["Vitality"]))
    if "Foodie" in nodes:
        elbow(center(nodes["Shopper"]), center(nodes["Foodie"]))
    if "Master Chef" in nodes:
        elbow(center(nodes["Shopper"]), center(nodes["Master Chef"]))

    # Draw nodes + icons
    mouse = pygame.mouse.get_pos()
    hovered = None
    for name, rect in nodes.items():
        unlocked = has_skill(name)
        available = can_unlock_skill(name)
        fill = (200, 220, 200) if unlocked else (220, 220, 220) if available else (170, 170, 170)
        border = DARK_GREEN if unlocked else BROWN
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 3, border_radius=10)

        # icon
        icon = skills[name]["icon"]
        if icon == "parkour":
            pygame.draw.polygon(screen, BLUE, [(rect.x+18, rect.y+56), (rect.x+40, rect.y+18), (rect.x+62, rect.y+56)])
            pygame.draw.circle(screen, BLACK, (rect.x+40, rect.y+22), 6)
        elif icon == "shopper":
            pygame.draw.rect(screen, ORANGE, (rect.x+22, rect.y+28, 36, 34), border_radius=6)
            pygame.draw.arc(screen, BLACK, (rect.x+20, rect.y+18, 40, 30), 3.5, 5.8, 3)
        elif icon == "heart":
            pygame.draw.circle(screen, RED, (rect.x + 34, rect.y + 38), 12)
            pygame.draw.circle(screen, RED, (rect.x + 52, rect.y + 38), 12)
            pygame.draw.polygon(screen, RED, [(rect.x + 24, rect.y + 42), (rect.x + 62, rect.y + 42), (rect.x + 43, rect.y + 66)])
        elif icon == "fork":
            pygame.draw.rect(screen, (120, 120, 120), (rect.x + 38, rect.y + 18, 6, 44), border_radius=3)
            for i in range(4):
                pygame.draw.rect(screen, (120, 120, 120), (rect.x + 26 + i*6, rect.y + 18, 4, 14), border_radius=2)
        elif icon == "chef":
            pygame.draw.ellipse(screen, WHITE, (rect.x + 18, rect.y + 18, 44, 26))
            pygame.draw.rect(screen, WHITE, (rect.x + 24, rect.y + 30, 32, 20), border_radius=8)
            pygame.draw.rect(screen, BLACK, (rect.x + 24, rect.y + 48, 32, 6))
        else:  # social
            pygame.draw.circle(screen, PURPLE, (rect.x+34, rect.y+38), 12)
            pygame.draw.circle(screen, PURPLE, (rect.x+52, rect.y+46), 10)
            pygame.draw.circle(screen, BLACK, (rect.x+30, rect.y+36), 2)
            pygame.draw.circle(screen, BLACK, (rect.x+50, rect.y+44), 2)

        if rect.collidepoint(mouse):
            hovered = name

    # Tooltip on hover
    if hovered:
        node = skills[hovered]
        tt_title_font = pygame.font.SysFont(None, 28)
        tt_body_font = pygame.font.SysFont(None, 22)
        lines = [
            hovered,
            node["desc"],
            f"Cost: {get_skill_cost(hovered)}  |  Status: {'UNLOCKED' if node['unlocked'] else 'LOCKED'}",
        ]
        prereq = node.get("prereq", [])
        if prereq:
            lines.append("Requires: " + ", ".join(prereq))
        # size tooltip
        rendered = [tt_title_font.render(lines[0], True, WHITE)] + [tt_body_font.render(l, True, WHITE) for l in lines[1:]]
        w = max(s.get_width() for s in rendered) + 20
        h = sum(s.get_height() for s in rendered) + 20
        tx = min(WINDOW_WIDTH - w - 10, mouse[0] + 16)
        ty = min(WINDOW_HEIGHT - h - 10, mouse[1] + 16)
        tip = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(tip, (0, 0, 0, 200), (0, 0, w, h), border_radius=8)
        pygame.draw.rect(tip, (255, 215, 0, 220), (0, 0, w, h), 2, border_radius=8)
        y = 10
        tip.blit(rendered[0], (10, y)); y += rendered[0].get_height() + 6
        for s in rendered[1:]:
            tip.blit(s, (10, y))
            y += s.get_height() + 3
        screen.blit(tip, (tx, ty))

    # Back button
    back_rect = pygame.Rect(menu_x + menu_width - 90, menu_y + 20, 70, 30)
    pygame.draw.rect(screen, RED, back_rect)
    back_text = pygame.font.SysFont(None, 24).render("Back", True, WHITE)
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    # Return node hitboxes for click handling
    return nodes, back_rect

while running:
    keys = pygame.key.get_pressed()  # Get keyboard state once at start of loop
    paused = (shop_open or clothing_shop_open or arcade_shop_open or supermarket_open or seafood_market_open or utility_cart_open or black_market_open or hotel_lobby_open or
              house_lobby_open or mission_center_open or restaurant_open or SETTINGS_OPEN or achievements_open or skill_tree_open or
              arcade_shop.any_arcade_playing() or cafe_open or in_hotel_room or in_house_room or microwave_open or stove_open or grill_open or
              sleep_cutscene_timer > 0 or house_build_menu_open or on_fishing_island or ferry_anim_timer > 0 or cheat_panel_open)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if cheat_panel_open:
                    cheat_panel_open = False
                    continue
            ch = None
            if event.unicode and len(event.unicode) == 1:
                u = event.unicode.upper()
                if "A" <= u <= "Z":
                    ch = u
            if ch is None and pygame.K_a <= event.key <= pygame.K_z:
                ch = chr(ord("A") + (event.key - pygame.K_a))
            if ch:
                cheat_code_buffer = (cheat_code_buffer + ch)[-16:]
                if cheat_code_buffer.endswith("ADHDSWOP"):
                    cheat_panel_open = True
                    utility_cart_open = False
                    cheat_code_buffer = ""
                    show_success_toast("Cheat panel opened.")

        # Modern mouse wheel event (some pygame versions)
        if event.type == pygame.MOUSEWHEEL:
            if achievements_open:
                achievements_scroll = max(0, achievements_scroll - event.y * 12)
            elif mission_center_open:
                mission_scroll = max(0, mission_scroll - event.y * 12)
            elif in_house_room and house_build_menu_open:
                house_build_scroll = max(0, house_build_scroll - event.y * 18)
            elif restaurant_open and restaurant_repaired:
                if restaurant_menu_tab == "upgrades":
                    restaurant_upgrades_scroll = max(0, restaurant_upgrades_scroll - event.y * 14)
                else:
                    restaurant_menu_scroll = max(0, restaurant_menu_scroll - event.y * 14)
            elif not (
                shop_open
                or clothing_shop_open
                or arcade_shop_open
                or cafe_open
                or supermarket_open
                or hotel_lobby_open
                or house_lobby_open
                or mission_center_open
                or restaurant_open
                or SETTINGS_OPEN
                or achievements_open
                or skill_tree_open
                or microwave_open
                or stove_open
                or grill_open
                or on_fishing_island
                or ferry_anim_timer > 0
                or arcade_shop.any_arcade_playing()
            ):
                # Inventory slot cycle (world or hotel room; matches 1–5 keys)
                if event.y > 0:
                    selected_slot = (selected_slot - 1) % MAX_INVENTORY
                elif event.y < 0:
                    selected_slot = (selected_slot + 1) % MAX_INVENTORY
            
        if arcade_shop.any_arcade_playing():
            exit_rect = pygame.Rect(WINDOW_WIDTH - 100, 20, 80, 30)
            if arcade_shop.pong.playing:
                if event.type == pygame.KEYDOWN:
                    if arcade_shop.pong.game_over and event.key in (pygame.K_SPACE, pygame.K_UP):
                        _arcade_paid_retry("Pong")
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_rect.collidepoint(event.pos):
                        arcade_shop.pong.playing = False
                        arcade_shop_open = True
                    elif arcade_shop.pong.game_over:
                        _arcade_paid_retry("Pong")
                continue
            if arcade_shop.stack.playing:
                if event.type == pygame.KEYDOWN:
                    if arcade_shop.stack.game_over:
                        if event.key in (pygame.K_SPACE, pygame.K_UP):
                            _arcade_paid_retry("Stack")
                    elif event.key in (pygame.K_SPACE, pygame.K_UP):
                        arcade_shop.stack.try_place()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_rect.collidepoint(event.pos):
                        arcade_shop.stack.playing = False
                        arcade_shop_open = True
                    elif arcade_shop.stack.game_over:
                        _arcade_paid_retry("Stack")
                    else:
                        arcade_shop.stack.try_place()
                continue
            if arcade_shop.breakout.playing:
                if event.type == pygame.KEYDOWN:
                    if arcade_shop.breakout.game_over and event.key in (pygame.K_SPACE, pygame.K_UP):
                        _arcade_paid_retry("Breakout")
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_rect.collidepoint(event.pos):
                        arcade_shop.breakout.playing = False
                        arcade_shop_open = True
                    elif arcade_shop.breakout.game_over:
                        _arcade_paid_retry("Breakout")
                continue
            if arcade_shop.snake.playing:
                if event.type == pygame.KEYDOWN:
                    if arcade_shop.snake.game_over:
                        if event.key in (pygame.K_SPACE, pygame.K_UP):
                            _arcade_paid_retry("Snake")
                    else:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            arcade_shop.snake.try_set_direction((0, -1))
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            arcade_shop.snake.try_set_direction((0, 1))
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            arcade_shop.snake.try_set_direction((-1, 0))
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            arcade_shop.snake.try_set_direction((1, 0))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_rect.collidepoint(event.pos):
                        arcade_shop.snake.playing = False
                        arcade_shop_open = True
                    elif arcade_shop.snake.game_over:
                        _arcade_paid_retry("Snake")
                continue
            if arcade_shop.dodge.playing:
                if event.type == pygame.KEYDOWN:
                    if arcade_shop.dodge.game_over and event.key in (pygame.K_SPACE, pygame.K_UP):
                        _arcade_paid_retry("Dodge")
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if exit_rect.collidepoint(event.pos):
                        arcade_shop.dodge.playing = False
                        arcade_shop_open = True
                    elif arcade_shop.dodge.game_over:
                        _arcade_paid_retry("Dodge")
                continue
            if arcade_shop.flappy_bird.playing:
                if event.type == pygame.KEYDOWN:
                    if event.key in arcade_shop.flappy_bird.jump_keys:
                        if arcade_shop.flappy_bird.game_over:
                            _arcade_paid_retry("FlappyBird")
                        else:
                            arcade_shop.flappy_bird.bird_velocity = arcade_shop.flappy_bird.jump_strength
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_rect.collidepoint(event.pos):
                        arcade_shop.flappy_bird.playing = False
                        arcade_shop_open = True
                    elif event.button == 1:
                        if arcade_shop.flappy_bird.game_over:
                            _arcade_paid_retry("FlappyBird")
                        else:
                            arcade_shop.flappy_bird.bird_velocity = arcade_shop.flappy_bird.jump_strength
                continue
        else:
            # Regular game controls
            if event.type == pygame.KEYDOWN:
                # Player house interior
                if in_house_room:
                    if event.key == pygame.K_ESCAPE:
                        if house_place_pick:
                            house_place_pick = None
                        elif house_build_menu_open:
                            house_build_menu_open = False
                        elif microwave_open or stove_open or grill_open:
                            microwave_open = False
                            stove_open = False
                            grill_open = False
                        else:
                            in_house_room = False
                            microwave_open = False
                            stove_open = False
                            grill_open = False
                            sleep_cutscene_timer = 0
                            house_build_menu_open = False
                        continue
                    if event.key == pygame.K_b and (not microwave_open) and (not stove_open) and (not grill_open):
                        house_build_menu_open = not house_build_menu_open
                        continue
                    if event.key in (pygame.K_e, pygame.K_v, pygame.K_z) and (not microwave_open) and (not stove_open) and (not grill_open) and (not house_build_menu_open):
                        acts = house_near_interaction_kinds()
                        idx = {pygame.K_e: 0, pygame.K_v: 1, pygame.K_z: 2}[event.key]
                        if idx < len(acts):
                            house_run_interaction(acts[idx])
                        continue
                    if event.key == pygame.K_m:
                        microwave_open = not microwave_open
                        if microwave_open:
                            stove_open = False
                            grill_open = False
                        continue
                elif on_fishing_island and ferry_anim_timer <= 0:
                    if event.key == pygame.K_ESCAPE:
                        if fish_phase != "idle":
                            _fish_reset_minigame()
                        elif island_near_ferry():
                            try_board_ferry_to_city()
                        continue
                    if event.key == pygame.K_e and fish_phase == "idle" and island_near_ferry():
                        try_board_ferry_to_city()
                        continue
                    if (
                        event.key == pygame.K_f
                        and fish_phase == "idle"
                        and island_in_fishing_zone()
                        and (not island_near_ferry())
                    ):
                        fishing_try_begin_cast()
                        continue
                elif in_hotel_room:
                    if event.key == pygame.K_ESCAPE:
                        in_hotel_room = False
                        microwave_open = False
                        stove_open = False
                        # Safety: if you leave mid-cutscene, don't keep the world paused
                        sleep_cutscene_timer = 0
                        continue
                    elif event.key == pygame.K_m:
                        microwave_open = not microwave_open
                        continue
                    elif event.key in (pygame.K_e, pygame.K_v, pygame.K_z):
                        acts, _st, _b, _m, _c = hotel_room_interaction_stack()
                        idx = {pygame.K_e: 0, pygame.K_v: 1, pygame.K_z: 2}[event.key]
                        if idx >= len(acts):
                            continue
                        hid = acts[idx]
                        if hid == "stove":
                            stove_open = True
                            microwave_open = False
                        elif hid == "micro":
                            microwave_open = True
                            stove_open = False
                        elif hid == "bed":
                            if can_sleep_now():
                                sleep_cutscene_timer = 120
                                hotel_notice_timer = 0
                            else:
                                hotel_notice_text = "Too early to sleep."
                                hotel_notice_timer = 120
                                show_failure_toast("Too early to sleep — wait for sunset or night.")
                        continue
                if event.key == pygame.K_SPACE:
                    if on_fishing_island and ferry_anim_timer <= 0:
                        fishing_on_space_key()
                    elif not (
                        shop_open
                        or clothing_shop_open
                        or arcade_shop_open
                        or restaurant_open
                        or house_lobby_open
                    ):
                        # Jump buffer (movement feel): press slightly early and still jump on landing
                        jump_buffer_timer = JUMP_BUFFER_FRAMES
                elif event.key in (pygame.K_e, pygame.K_v, pygame.K_z):
                    if on_fishing_island or ferry_anim_timer > 0:
                        pass
                    else:
                        st = get_world_interaction_stack()
                        idx = {pygame.K_e: 0, pygame.K_v: 1, pygame.K_z: 2}[event.key]
                        if idx < len(st):
                            apply_world_interaction_code(st[idx])
                elif event.key == pygame.K_p:
                    if current_droppable:
                        it = current_droppable.item
                        cash = int(getattr(it, "cash_value", 0) or 0)
                        if cash > 0:
                            money += cash
                            dropped_items.remove(current_droppable)
                            show_pickup_prompt = False
                            show_success_toast(f"+${cash}")
                        elif try_add_inventory(it):
                            dropped_items.remove(current_droppable)
                            show_pickup_prompt = False
                        else:
                            show_failure_toast("Inventory full — drop something first.")
                elif event.key == pygame.K_q:
                    if (not on_fishing_island) and inventory[selected_slot] is not None:
                        it = remove_one_from_slot(selected_slot)
                        dropped_items.append(DroppedItem(it, player_x, player_y))
                elif event.key == pygame.K_1:
                    selected_slot = 0
                elif event.key == pygame.K_2:
                    selected_slot = 1
                elif event.key == pygame.K_3:
                    selected_slot = 2
                elif event.key == pygame.K_4:
                    selected_slot = 3
                elif event.key == pygame.K_5:
                    selected_slot = 4
                elif event.key == pygame.K_t:
                    if not on_fishing_island and ferry_anim_timer <= 0:
                        # Bistro runners (uniform NPCs) — talk first if in range
                        rw_talked = False
                        for w in restocker_workers:
                            if restaurant_repaired and w.check_player_collision(player_x, player_width):
                                w.start_custom_dialog(
                                    random.choice(
                                        [
                                            "'sup boss",
                                            "Market run's looking smooth.",
                                            "I'll keep the pantry fed.",
                                            "Say the word if you need extras.",
                                        ]
                                    )
                                )
                                rw_talked = True
                                break
                        if not rw_talked:
                            for npc in npcs:
                                if npc.can_talk and not npc.in_shop:
                                    npc.start_dialog()
                                    notify_chain_npc_interaction()
                                    npcs_talked += 1
                                    if npcs_talked >= achievements["Social Butterfly"]["requirement"]:
                                        unlock_achievement("Social Butterfly")
                                    if npcs_talked >= achievements["Town Gossip"]["requirement"]:
                                        unlock_achievement("Town Gossip")
                                    break
                elif event.key == pygame.K_r:
                    # Sell cooked food to a nearby NPC if Sociality skill is unlocked
                    if not has_skill("Sociality"):
                        show_failure_toast("Unlock Sociality in the skill tree to sell food to people.")
                    elif inventory[selected_slot] is None:
                        show_failure_toast("Nothing in that inventory slot.")
                    else:
                        item = inventory[selected_slot]["item"]
                        if not getattr(item, "cooked_by_player", False):
                            show_failure_toast("Only meals you cooked can be sold (not raw groceries).")
                        else:
                            sold_to_someone = False
                            for npc in npcs:
                                if npc.can_talk and not npc.in_shop:
                                    notify_chain_npc_interaction()
                                    sold_to_someone = True
                                    if random.random() < 0.60:
                                        payout = int(math.ceil(getattr(item, "cooked_cost_basis", 0) * 1.75))
                                        remove_one_from_slot(selected_slot)
                                        add_money(payout)
                                        npc.start_custom_dialog(random.choice(SELL_ACCEPT_DIALOGS))
                                        show_success_toast(f"Sold {item.name} for ${payout}.")
                                    else:
                                        npc.start_custom_dialog(random.choice(SELL_DENY_DIALOGS))
                                        show_failure_toast("They passed — try another passerby.")
                                    break
                            if not sold_to_someone:
                                show_failure_toast("No one in range — stand next to someone first.")
                elif event.key == pygame.K_ESCAPE:
                    if cheat_panel_open:
                        cheat_panel_open = False
                        continue
                    elif utility_cart_open:
                        utility_cart_open = False
                        continue
                    elif black_market_open:
                        black_market_open = False
                        continue
                    if restaurant_open:
                        restaurant_open = False
                        bistro_chef_dropdown_chef_idx = None
                    elif mission_center_open:
                        mission_center_open = False
                    elif shop_open:
                        shop_open = False
                    elif clothing_shop_open:
                        clothing_shop_open = False
                    elif arcade_shop_open:
                        arcade_shop_open = False
                    elif cafe_open:
                        cafe_open = False
                    elif supermarket_open:
                        supermarket_open = False
                    elif seafood_market_open:
                        seafood_market_open = False
                    elif hotel_lobby_open:
                        hotel_lobby_open = False
                    elif house_lobby_open:
                        house_lobby_open = False
                    elif skill_tree_open:
                        skill_tree_open = False
                        SETTINGS_OPEN = True
                    elif achievements_open:
                        achievements_open = False
                        SETTINGS_OPEN = True
                    else:
                        SETTINGS_OPEN = not SETTINGS_OPEN

            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_house_room and (not on_fishing_island) and (not house_build_menu_open) and (not microwave_open) and (not stove_open) and (not grill_open) and (not house_place_pick):
                    if event.button in (2, 3) or (
                        event.button == 1 and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
                    ):
                        if house_try_delete_at_screen_pos(event.pos):
                            continue

                if event.button == 3:
                    continue

                if event.button != 1:
                    continue

                # Left click
                if cheat_panel_open:
                    handle_cheat_panel_click(event.pos)
                    continue
                if microwave_open:
                    buttons, close_rect = draw_microwave_menu()
                    if close_rect.collidepoint(event.pos):
                        microwave_open = False
                    else:
                        for rect, recipe, can in buttons:
                            if can and rect.collidepoint(event.pos):
                                if cooking_in_progress:
                                    show_failure_toast("Already cooking.")
                                elif not inventory_can_accept(build_cooked_result(recipe, "microwave")):
                                    show_failure_toast("Inventory full.")
                                elif start_cooking(recipe, "microwave"):
                                    microwave_open = False
                elif stove_open:
                    buttons, close_rect = draw_stove_menu()
                    if close_rect.collidepoint(event.pos):
                        stove_open = False
                    else:
                        for rect, recipe, can in buttons:
                            if can and rect.collidepoint(event.pos):
                                if cooking_in_progress:
                                    show_failure_toast("Already cooking.")
                                elif not inventory_can_accept(build_cooked_result(recipe, "stove")):
                                    show_failure_toast("Inventory full.")
                                elif start_cooking(recipe, "stove"):
                                    stove_open = False
                elif grill_open:
                    buttons, close_rect = draw_grill_menu()
                    if close_rect.collidepoint(event.pos):
                        grill_open = False
                    else:
                        for rect, recipe, can in buttons:
                            if can and rect.collidepoint(event.pos):
                                if cooking_in_progress:
                                    show_failure_toast("Already cooking.")
                                elif not inventory_can_accept(build_cooked_result(recipe, "grill")):
                                    show_failure_toast("Inventory full.")
                                elif start_cooking(recipe, "grill"):
                                    grill_open = False
                elif in_house_room:
                    if house_build_menu_open:
                        b2 = draw_house_build_menu()
                        handle_house_build_click(event.pos, b2)
                    elif house_place_pick:
                        house_try_place_at_screen_mx(event.pos[0])
                elif in_hotel_room:
                    # clicks do nothing in room for now
                    pass
                else:
                    if mission_center_open:
                            buttons, close_rect = mission_center.draw_menu()
                            if close_rect.collidepoint(event.pos):
                                mission_center_open = False
                            else:
                                for button, mission in buttons:
                                    if button.collidepoint(event.pos):
                                        if not mission.completed and mission not in mission_center.active_missions:
                                            if len(mission_center.active_missions) >= MAX_ACTIVE_MISSIONS:
                                                show_failure_toast(
                                                    f"Only {MAX_ACTIVE_MISSIONS} active missions at a time. Abandon one in the list or finish one first."
                                                )
                                            else:
                                                mission_center.active_missions.append(mission)
                                                init_chain_mission(mission)
                    elif shop_open:
                        buttons, close_rect = draw_shop_menu()
                        handle_shop_click(event.pos, buttons, close_rect)
                    elif clothing_shop_open:
                        buttons, close_rect = draw_clothing_shop_menu()
                        clothing_shop_open = handle_clothing_shop_click(event.pos, buttons, close_rect)
                    elif arcade_shop_open:
                        buttons, close_rect = draw_arcade_menu()
                        handle_arcade_shop_click(event.pos, buttons, close_rect)
                    elif cafe_open:
                        buttons, close_rect = draw_cafe_menu()
                        handle_cafe_click(event.pos, buttons, close_rect)
                    elif supermarket_open:
                        buttons, close_rect = draw_supermarket_menu()
                        handle_supermarket_click(event.pos, buttons, close_rect)
                    elif seafood_market_open:
                        buttons, close_rect = draw_seafood_market_menu()
                        handle_seafood_market_click(event.pos, buttons, close_rect)
                    elif restaurant_open:
                        buttons, repair_rect, close_rect = draw_restaurant_menu()
                        r = handle_restaurant_click(event.pos, buttons, repair_rect, close_rect)
                        if r == "close":
                            restaurant_open = False
                    elif hotel_lobby_open:
                        enter_rect, close_rect = draw_hotel_lobby_menu()
                        if close_rect.collidepoint(event.pos):
                            hotel_lobby_open = False
                        elif enter_rect.collidepoint(event.pos):
                            if hotel_room_owned:
                                hotel_lobby_open = False
                                in_hotel_room = True
                            else:
                                if money >= 100:
                                    money -= 100
                                    hotel_room_owned = True
                                    hotel_lobby_open = False
                                    in_hotel_room = True
                                else:
                                    show_failure_toast("Not enough money for a room ($100).")
                    elif house_lobby_open:
                        enter_rect, close_rect = draw_house_lobby_menu()
                        if close_rect.collidepoint(event.pos):
                            house_lobby_open = False
                        elif enter_rect.collidepoint(event.pos):
                            if house_owned:
                                house_lobby_open = False
                                in_house_room = True
                                house_clamp_player()
                                house_update_camera()
                            else:
                                if money >= HOUSE_PURCHASE_COST:
                                    money -= HOUSE_PURCHASE_COST
                                    house_owned = True
                                    house_lobby_open = False
                                    in_house_room = True
                                    house_player_x = house_interior_width() * 0.45
                                    house_clamp_player()
                                    house_update_camera()
                                    show_success_toast("You own the house — press B inside to furnish it.")
                                else:
                                    show_failure_toast(f"Need ${HOUSE_PURCHASE_COST} for the deed.")
                    elif utility_cart_open:
                        handle_utility_cart_click(event.pos)
                    elif black_market_open:
                        handle_black_market_click(event.pos)
                    elif SETTINGS_OPEN:
                        buttons = draw_settings_menu()
                        for button, text in buttons:
                            if button.collidepoint(event.pos):
                                if text == "Continue":
                                    SETTINGS_OPEN = False
                                elif text.startswith("Fullscreen:"):
                                    set_fullscreen(not FULLSCREEN_ENABLED)
                                elif text.startswith("Particles:"):
                                    # toggle particle system
                                    globals()["ENABLE_PARTICLES"] = not ENABLE_PARTICLES
                                elif text == "Achievements":
                                    achievements_open = True
                                    SETTINGS_OPEN = False
                                elif text == "Skill Tree":
                                    skill_tree_open = True
                                    SETTINGS_OPEN = False
                                elif text == "Quit":
                                    running = False
                    elif achievements_open:
                        back_rect = draw_achievements_menu()
                        if back_rect.collidepoint(event.pos):
                            achievements_open = False
                            SETTINGS_OPEN = True
                    elif skill_tree_open:
                        nodes, back_rect = draw_skill_tree_menu()
                        if back_rect.collidepoint(event.pos):
                            skill_tree_open = False
                            SETTINGS_OPEN = True
                        else:
                            for name, rect in nodes.items():
                                if rect.collidepoint(event.pos):
                                    if not unlock_skill(name):
                                        show_failure_toast("Can't unlock that skill yet.")
                # Mouse wheel scroll for achievements menu (pygame MOUSEBUTTONDOWN 4/5)
                if achievements_open:
                    if event.button == 4:
                        achievements_scroll = max(0, achievements_scroll - 12)
                    elif event.button == 5:
                        achievements_scroll += 12
                # Mouse wheel scroll for mission menu (pygame MOUSEBUTTONDOWN 4/5)
                if mission_center_open:
                    if event.button == 4:
                        mission_scroll = max(0, mission_scroll - 12)
                    elif event.button == 5:
                        mission_scroll += 12
                    # Add after other mouse handling
                    for npc in npcs:
                        screen_x = camera.apply(npc.original_x)
                        if abs(screen_x - event.pos[0]) < 30 and \
                           abs(npc.y - event.pos[1]) < 50:
                            npc.start_dialog()

    update_ferry_animation_tick()
    if on_fishing_island and ferry_anim_timer <= 0:
        update_fishing_minigame(keys)

    # Room movement (hotel interior)
    if in_hotel_room and sleep_cutscene_timer <= 0 and (not microwave_open) and (not stove_open) and (not grill_open):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            room_player_x -= ROOM_PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            room_player_x += ROOM_PLAYER_SPEED

    # House interior movement + camera
    if in_house_room and sleep_cutscene_timer <= 0 and (not microwave_open) and (not stove_open) and (not grill_open) and (not house_build_menu_open):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            house_player_x -= ROOM_PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            house_player_x += ROOM_PLAYER_SPEED
        house_clamp_player()
        house_update_camera()

    if on_fishing_island and ferry_anim_timer <= 0 and fish_phase == "idle":
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            island_player_x -= ROOM_PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            island_player_x += ROOM_PLAYER_SPEED
        island_player_x = max(44.0, min(float(WINDOW_WIDTH - 84), island_player_x))

    # Player movement (only if not paused)
    if not paused:
        # Track total walking distance for achievements
        if _last_player_x_for_distance is None:
            _last_player_x_for_distance = float(player_x)
        else:
            dx = float(player_x) - float(_last_player_x_for_distance)
            # Only count intentional movement input
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]:
                distance_walked += abs(dx)
                if distance_walked >= achievements["Marathon"]["requirement"]:
                    unlock_achievement("Marathon")
            _last_player_x_for_distance = float(player_x)

        # Can only sprint if stamina is above minimum threshold
        can_sprint = stamina > MINIMUM_STAMINA_TO_SPRINT
        is_sprinting = keys[pygame.K_LSHIFT] and can_sprint
        target_speed = float(SPRINT_SPEED if is_sprinting else player_speed)
        
        # Update stamina
        moving_lr = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]
        if is_sprinting and moving_lr:
            stamina = max(0, stamina - STAMINA_DRAIN_RATE)
            stamina_regen_timer = 0
            sprint_timer += 1
            if sprint_timer >= achievements["Speed Demon"]["requirement"]:
                unlock_achievement("Speed Demon")
        else:
            sprint_timer = 0
            # Only regenerate after delay and when not sprinting
            if stamina < MAX_STAMINA:
                stamina_regen_timer += 1
                if stamina_regen_timer >= STAMINA_REGEN_DELAY:
                    now_ms = pygame.time.get_ticks()
                    if stamina_regen_boost_until_ms <= now_ms:
                        stamina_regen_multiplier = 1.0
                    stamina = min(MAX_STAMINA, stamina + (STAMINA_REGEN_RATE * stamina_regen_multiplier))
        
        # Clamp to valid range (stamina is a float)
        stamina = max(0, min(MAX_STAMINA, stamina))
        
        # Movement feel: acceleration + friction instead of instant velocity
        move_dir = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_dir -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_dir += 1
        if move_dir != 0:
            facing_dir = 1 if move_dir > 0 else -1

        accel = MOVE_ACCEL if on_ground else MOVE_AIR_ACCEL
        fric = MOVE_FRICTION if on_ground else MOVE_AIR_FRICTION
        if move_dir != 0:
            player_vx += move_dir * accel
        else:
            player_vx *= fric

        # clamp
        player_vx = max(-target_speed, min(target_speed, player_vx))
        player_x += player_vx

        # update walk phase for animation
        walk_phase += (abs(player_vx) * 0.08)

    # Apply gravity (only if not paused)
    if not paused:
        player_velocity += gravity
        player_y += player_velocity

    if not paused:
        # Update camera
        camera.update(player_x)

        # Platform collision
        platform.update(camera)
        collision_y = platform.check_collision(player_x, player_y, player_width, player_height)
        if collision_y is not None:
            was_on_ground = on_ground
            on_ground = True
            player_y = collision_y - player_height
            # landing dust
            if ENABLE_PARTICLES and (not was_on_ground) and player_velocity > 6:
                for _ in range(10):
                    vfx_particles.append(
                        VFXParticle(
                            player_x + random.uniform(6, player_width - 6),
                            player_y + player_height - 2,
                            random.uniform(-1.6, 1.6),
                            random.uniform(-2.4, -0.6),
                            random.uniform(2.0, 4.0),
                            (210, 210, 210),
                            random.randint(18, 30),
                        )
                    )
            player_velocity = 0
            coyote_timer = COYOTE_FRAMES
        else:
            was_on_ground = on_ground
            on_ground = False
            if coyote_timer > 0:
                coyote_timer -= 1

        if jump_buffer_timer > 0:
            jump_buffer_timer -= 1

        # Execute buffered jump if possible
        if jump_buffer_timer > 0 and (on_ground or coyote_timer > 0) and stamina >= JUMP_STAMINA_COST:
            player_velocity = player_jump
            stamina = max(0, stamina - JUMP_STAMINA_COST)
            stamina_regen_timer = 0
            jump_buffer_timer = 0
            on_ground = False
            coyote_timer = 0

        # Sprint streak particles
        if ENABLE_PARTICLES and is_sprinting and abs(player_vx) > 0.5 and on_ground and (pygame.time.get_ticks() % 2 == 0):
            vfx_particles.append(
                VFXParticle(
                    player_x + (0 if facing_dir < 0 else player_width),
                    player_y + player_height - 10,
                    random.uniform(-1.2, 1.2) - facing_dir * random.uniform(0.8, 1.6),
                    random.uniform(-0.4, 0.2),
                    random.uniform(2.0, 3.5),
                    (120, 220, 255),
                    random.randint(10, 18),
                )
            )

    # Eating mechanics (world pauses with menus; hotel / home interior still allow eating unless cooking UI is open)
    _eat_room = (
        in_hotel_room
        or in_house_room
        or (on_fishing_island and ferry_anim_timer <= 0)
    ) and (not microwave_open) and (not stove_open) and (not grill_open) and (not house_build_menu_open)
    if (not paused) or _eat_room:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] and inventory[selected_slot] is not None:
            is_eating = True
            eating_timer += 1
            it_slot = inventory[selected_slot]["item"]
            eat_need = 30 if getattr(it_slot, "quick_drink", False) else 180
            if eating_timer >= eat_need:
                item = inventory[selected_slot]["item"]
                hunger = min(MAX_HUNGER, hunger + item.hunger_restore)
                sr = getattr(item, "stamina_restore_drink", None)
                if sr is not None:
                    stamina = min(MAX_STAMINA, stamina + int(sr))
                # Consumable coffee grants timed stamina regen boost when drunk
                if getattr(item, "coffee_source", False):
                    now_ms = pygame.time.get_ticks()
                    if now_ms < stamina_regen_boost_until_ms and stamina_regen_multiplier > 1.0:
                        notify_coffee_guy_mission()
                    stamina_regen_boost_until_ms = now_ms + int(getattr(item, "coffee_duration_ms", 0))
                    stamina_regen_multiplier = float(getattr(item, "coffee_mult", 1.0))
                    stamina_regen_timer = STAMINA_REGEN_DELAY
                remove_one_from_slot(selected_slot)
                items_eaten += 1
                if items_eaten >= achievements["Foodie"]["requirement"]:
                    unlock_achievement("Foodie")
                if items_eaten >= achievements["Glutton for Fun"]["requirement"]:
                    unlock_achievement("Glutton for Fun")
                eating_timer = 0
                is_eating = False
        elif not keys[pygame.K_f]:
            eating_timer = 0
            is_eating = False
    elif not _eat_room:
        eating_timer = 0
        is_eating = False

    # Cooking ticks even when `paused` (hotel room / open GUIs set paused so world sim stops).
    if cooking_in_progress:
        cooking_timer -= 1
        if cooking_timer <= 0:
            cooking_in_progress = False
            cooking_timer = 0
            if cooking_pending_item is not None:
                if try_add_inventory(cooking_pending_item):
                    notify_chain_cook()
                    cooked_meals += 1
                    if cooking_pending_source == "microwave":
                        microwave_meals += 1
                        if microwave_meals >= achievements["Microwave Wizard"]["requirement"]:
                            unlock_achievement("Microwave Wizard")
                    elif cooking_pending_source in ("stove", "grill"):
                        stove_meals += 1
                        if stove_meals >= achievements["Stove Supreme"]["requirement"]:
                            unlock_achievement("Stove Supreme")
                    if cooked_meals >= achievements["First Cook"]["requirement"]:
                        unlock_achievement("First Cook")
                else:
                    show_failure_toast("Inventory full — couldn't store the meal.")
            cooking_pending_item = None
            cooking_pending_source = ""

    # Hunger / health only updates when not paused
    if not paused:
        hunger_timer += 1
        if hunger_timer >= HUNGER_DECREASE_INTERVAL:
            hunger_timer = 0
            hunger = max(0, hunger - HUNGER_DECREASE_AMOUNT)
            if hunger <= 0:
                health = max(0, health - HEALTH_DECREASE_AMOUNT)
        
        # Health regeneration when well fed
        if hunger >= HUNGER_WELL_FED:
            health_regen_timer += 1
            if health_regen_timer >= HEALTH_REGEN_INTERVAL:
                health_regen_timer = 0
                health = min(MAX_HEALTH, health + HEALTH_REGEN_RATE)
    
    # Game over check
    if health <= 0:
        handle_player_death()

    # Update dropped items (only when not paused)
    if not paused:
        current_droppable = None
        for item in dropped_items:
            item.update()
            if item.check_collision(player_x, player_y, player_width, player_height):
                current_droppable = item
                show_pickup_prompt = True
                break
        if not current_droppable:
            show_pickup_prompt = False
    else:
        current_droppable = None
        show_pickup_prompt = False

    # Update NPCs only when not paused
    if not paused:
        manage_npcs(player_x)
        for npc in npcs:
            npc.can_talk = npc.check_player_collision(player_x, player_width)

    # Bistro chefs & supply runners (keep simulating while bistro menu / other GUIs pause the world)
    if restaurant_repaired:
        tick_restaurant_passive_income()
        update_bistro_chefs()
        sync_restocker_workers()
        for w in restocker_workers:
            w.update()
        for w in restocker_workers:
            w.can_talk = w.check_player_collision(player_x, player_width)

    # Update environment cycles only when not paused
    if not paused:
        update_day_night_cycle()
        update_weather()

    # Ferry crossing cinematic
    if ferry_anim_timer > 0:
        draw_ferry_crossing_cinematic()
        draw_status_bars()
    # Sun Reef island (fishing)
    elif on_fishing_island:
        draw_fishing_island_scene()
        draw_status_bars()
        if fish_phase == "idle":
            draw_inventory()
        hf = pygame.font.SysFont(None, 22)
        if fish_phase == "idle":
            hint_y = WINDOW_HEIGHT - 92  # sit above inventory hotbar
            if island_near_ferry():
                t = hf.render("E: Board ferry · return to city (free)", True, (255, 252, 245))
                screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, hint_y)))
            elif island_in_fishing_zone():
                t = hf.render("F: Cast line · ESC cancel · A/D reel when hooked", True, (255, 252, 245))
                screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, hint_y)))
            else:
                t = hf.render("Walk the beach toward the rocks — or E at the ferry", True, (255, 250, 240))
                screen.blit(t, t.get_rect(center=(WINDOW_WIDTH // 2, hint_y)))
        if is_eating:
            draw_eating_progress()
    # House interior (player-owned)
    elif in_house_room:
        draw_house_room()
        if house_build_menu_open:
            draw_house_build_menu()
        draw_status_bars()
        draw_inventory()
        if cooking_in_progress:
            draw_cooking_progress()
        if microwave_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            draw_microwave_menu()
        if stove_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            draw_stove_menu()
        if grill_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            draw_grill_menu()
        if sleep_cutscene_timer > 0:
            sleep_cutscene_timer -= 1
            if sleep_cutscene_timer == 1:
                current_time = int(DAY_LENGTH * 0.30)
                health = min(MAX_HEALTH, health + 20)
                hunger = min(MAX_HUNGER, hunger + 20)
            draw_sleep_cutscene()
        if (not microwave_open) and (not stove_open) and (not grill_open) and (not house_build_menu_open):
            draw_house_room_prompts(house_near_interaction_kinds())
        if is_eating:
            draw_eating_progress()
    # Hotel room scene (separate from world)
    elif in_hotel_room:
        bed_rect, micro_rect, stove_rect, near_bed, near_micro, near_stove = draw_hotel_room()
        # Keep inventory visible in the room
        draw_status_bars()
        draw_inventory()
        if cooking_in_progress:
            draw_cooking_progress()
        if microwave_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            draw_microwave_menu()
        if stove_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            draw_stove_menu()
        if sleep_cutscene_timer > 0:
            sleep_cutscene_timer -= 1
            if sleep_cutscene_timer == 1:
                current_time = int(DAY_LENGTH * 0.30)
                health = min(MAX_HEALTH, health + 20)
                hunger = min(MAX_HUNGER, hunger + 20)
            draw_sleep_cutscene()
        if is_eating:
            draw_eating_progress()
    else:
        # Draw game world
        screen.fill(SKY_BLUE)
        draw_background(camera)
        platform.draw(camera)
        for bench in benches:
            bench.draw(camera)
        shop.draw(camera)
        clothing_shop.draw(camera)
        arcade_shop.draw(camera)
        cafe.draw(camera)
        supermarket.draw(camera)
        hotel.draw(camera)
        house.draw(camera)
        ferry_dock.draw(camera)
        seafood_market.draw(camera)
        utility_cart.draw(camera)
        black_market.draw(camera)
        mission_center.draw(camera)
        restaurant.draw(camera)
        draw_player(camera.apply(player_x), player_y)
        # VFX particles (landing dust, sprint streaks, etc.)
        update_and_draw_vfx(camera)
        # (vignette removed by request)
    
    if (
        not in_hotel_room
        and not in_house_room
        and (not on_fishing_island)
        and ferry_anim_timer <= 0
    ):
        # Draw NPCs
        for npc in npcs:
            npc.draw(camera)
        for w in restocker_workers:
            w.draw(camera)

        # Draw UI elements
        draw_status_bars()
        draw_inventory()
        
        if is_eating:
            draw_eating_progress()
    
    # Draw shop/settings UI last (on top of everything)
    if (not in_hotel_room) and (not in_house_room) and (not on_fishing_island) and ferry_anim_timer <= 0 and (shop_open or clothing_shop_open or arcade_shop_open or cafe_open or supermarket_open or seafood_market_open or utility_cart_open or black_market_open or hotel_lobby_open or house_lobby_open or mission_center_open or restaurant_open or SETTINGS_OPEN or achievements_open or skill_tree_open or cheat_panel_open):
        # Add semi-transparent overlay to dim the background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)  # 50% transparent
        screen.blit(overlay, (0, 0))
        # Draw shop menu
        if cheat_panel_open:
            draw_cheat_panel()
        elif shop_open:
            buttons, close_rect = draw_shop_menu()
        elif clothing_shop_open:
            buttons, close_rect = draw_clothing_shop_menu()
        elif arcade_shop_open:
            buttons, close_rect = draw_arcade_menu()
        elif cafe_open:
            buttons, close_rect = draw_cafe_menu()
        elif supermarket_open:
            buttons, close_rect = draw_supermarket_menu()
        elif seafood_market_open:
            buttons, close_rect = draw_seafood_market_menu()
        elif utility_cart_open:
            buttons, close_rect = draw_utility_cart_menu()
        elif black_market_open:
            buttons, close_rect = draw_black_market_menu()
        elif hotel_lobby_open:
            enter_rect, close_rect = draw_hotel_lobby_menu()
        elif house_lobby_open:
            enter_rect, close_rect = draw_house_lobby_menu()
        elif mission_center_open:
            buttons, close_rect = mission_center.draw_menu()
        elif restaurant_open:
            draw_restaurant_menu()
        elif SETTINGS_OPEN:
            draw_settings_menu()
        elif achievements_open:
            draw_achievements_menu()
        elif skill_tree_open:
            draw_skill_tree_menu()
    elif (not in_hotel_room) and (not in_house_room) and (not on_fishing_island) and ferry_anim_timer <= 0 and (shop.check_collision(player_x, player_width) or \
         clothing_shop.check_collision(player_x, player_width) or \
         arcade_shop.check_collision(player_x, player_width) or \
         cafe.check_collision(player_x, player_width) or \
         supermarket.check_collision(player_x, player_width) or \
         hotel.check_collision(player_x, player_width) or \
         house.check_collision(player_x, player_width) or \
         ferry_dock.check_collision(player_x, player_width) or \
         seafood_market.check_collision(player_x, player_width) or \
         utility_cart.check_collision(player_x, player_width) or \
         black_market.check_collision(player_x, player_width) or \
         restaurant.check_collision(player_x, player_width) or \
         mission_center.check_collision(player_x, player_width)):
        wstack = get_world_interaction_stack()
        if wstack:
            draw_world_interaction_prompts(wstack)
        # Sell prompt: Sociality + holding player-cooked food + near NPC
        if has_skill("Sociality") and inventory[selected_slot] is not None:
            item = inventory[selected_slot]["item"]
            if getattr(item, "cooked_by_player", False):
                for npc in npcs:
                    if npc.can_talk and not npc.in_shop:
                        draw_sell_food_prompt()
                        break

    # Add to drawing section after drawing player
    # Draw dropped items (world only)
    if not in_house_room:
        for item in dropped_items:
            item.draw(camera)

    # Draw pickup prompt if applicable
    if show_pickup_prompt and (not in_house_room) and (not on_fishing_island):
        prompt_text = pygame.font.SysFont(None, 24).render("Press P to pick up", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30))
        screen.blit(prompt_text, prompt_rect)

    # Arcade mini-games (only one active)
    if arcade_shop.flappy_bird.playing:
        arcade_shop.flappy_bird.update()
        draw_flappy_bird_game()
        if arcade_shop.flappy_bird.game_over and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            _arcade_paid_retry("FlappyBird")
        if arcade_shop.flappy_bird.score >= achievements["Rookie Pilot"]["requirement"]:
            unlock_achievement("Rookie Pilot")
        if arcade_shop.flappy_bird.score >= achievements["Flappy Bird Champion"]["requirement"]:
            unlock_achievement("Flappy Bird Champion")
    elif arcade_shop.snake.playing:
        arcade_shop.snake.update()
        draw_snake_game()
        if arcade_shop.snake.game_over and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            _arcade_paid_retry("Snake")
        if arcade_shop.snake.score >= achievements["Snake Rookie"]["requirement"]:
            unlock_achievement("Snake Rookie")
        if arcade_shop.snake.score >= achievements["Snake Legend"]["requirement"]:
            unlock_achievement("Snake Legend")
    elif arcade_shop.dodge.playing:
        arcade_shop.dodge.update(keys)
        draw_dodge_game()
        if arcade_shop.dodge.game_over and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            _arcade_paid_retry("Dodge")
        if arcade_shop.dodge.score >= achievements["Dodge Rookie"]["requirement"]:
            unlock_achievement("Dodge Rookie")
        if arcade_shop.dodge.score >= achievements["Dodge Legend"]["requirement"]:
            unlock_achievement("Dodge Legend")
    elif arcade_shop.breakout.playing:
        arcade_shop.breakout.update(keys)
        draw_breakout_game()
        if arcade_shop.breakout.game_over and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            _arcade_paid_retry("Breakout")
        if arcade_shop.breakout.score >= achievements["Brick Breaker"]["requirement"]:
            unlock_achievement("Brick Breaker")
        if arcade_shop.breakout.score >= achievements["Demolition Expert"]["requirement"]:
            unlock_achievement("Demolition Expert")
    elif arcade_shop.pong.playing:
        arcade_shop.pong.update(keys)
        draw_pong_game()
        if arcade_shop.pong.game_over and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            _arcade_paid_retry("Pong")
        if arcade_shop.pong.score >= achievements["Paddle Up"]["requirement"]:
            unlock_achievement("Paddle Up")
        if arcade_shop.pong.score >= achievements["Ping Commander"]["requirement"]:
            unlock_achievement("Ping Commander")
    elif arcade_shop.stack.playing:
        arcade_shop.stack.update()
        draw_stack_game()
        if arcade_shop.stack.game_over and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
            _arcade_paid_retry("Stack")
        if arcade_shop.stack.score >= achievements["Stack Apprentice"]["requirement"]:
            unlock_achievement("Stack Apprentice")
        if arcade_shop.stack.score >= achievements["Skyline Chef"]["requirement"]:
            unlock_achievement("Skyline Chef")

    # Check all mission types continuously
    check_mission_completion()

    draw_stamina_bar()

    # Add to drawing section
    for npc in npcs:
        npc.update_dialog()
        npc.draw_dialog(screen, camera)

    # Achievement popup (always on top)
    if mission_popup:
        mission_popup["timer"] -= 1
    draw_mission_popup()

    if achievement_popup:
        achievement_popup["timer"] -= 1
    draw_achievement_popup()

    draw_objective_card()

    if success_popup:
        success_popup["timer"] -= 1
    draw_success_popup()

    if failure_popup:
        failure_popup["timer"] -= 1
    draw_failure_popup()

    if hotel_notice_timer > 0:
        hotel_notice_timer -= 1
    if house_notice_timer > 0:
        house_notice_timer -= 1

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

