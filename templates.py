
import datetime as dt
import random

SPLITS = ["Back+Biceps","Chest+Triceps","Legs+Shoulders"]

def pick_variation(day_seed:int, choices):
    random.seed(day_seed)
    c = list(choices)
    random.shuffle(c)
    return c

def generate_routine(split:str, equipment:dict, knee_safe:bool=True, day:dt.date=None):
    day = day or dt.date.today()
    seed = int(day.strftime("%Y%m%d"))
    plan = []  # [(exercise, bodypart)]
    if split=="Back+Biceps":
        back_pool = [
            ("Pull-up","Back"),
            ("Lat Pulldown (wide overhand)","Back"),
            ("Lat Pulldown (medium underhand)","Back"),
            ("Seated Row (wide)","Back"),
            ("Seated Row (neutral close)","Back"),
            ("T-Bar Row","Back"),
            ("Smith Barbell Row","Back"),
            ("Rotary Pulldown","Back"),
            ("Straight-Arm Pulldown (Cable)","Back"),
        ]
        biceps_pool = [
            ("EZ-Bar Curl","Biceps"),
            ("Arm Curl Machine","Biceps"),
            ("Incline DB Curl","Biceps"),
            ("Cable Hammer Curl (rope)","Biceps"),
        ]
        back_sel = pick_variation(seed, back_pool)[:4]
        bi_sel = pick_variation(seed+7, biceps_pool)[:1]
        plan = back_sel + bi_sel

    elif split=="Chest+Triceps":
        chest_pool = [
            ("Smith Incline Bench Press","Chest"),
            ("Incline Bench Press Machine","Chest"),
            ("Chest Press Machine","Chest"),
            ("Pec Deck","Chest"),
            ("Cable Chest Fly (slight down)","Chest"),
            ("Dips","Chest"),
        ]
        tri_pool = [
            ("Lying Triceps Extension (EZ)","Triceps"),
            ("Rope Pushdown","Triceps"),
            ("DB Overhead Extension","Triceps"),
        ]
        chest_sel = pick_variation(seed, chest_pool)[:4]
        tri_sel = pick_variation(seed+13, tri_pool)[:1]
        plan = chest_sel + tri_sel

    else:  # Legs+Shoulders
        legs_pool_safe = [
            ("Inner Thigh (Adductor)","Legs"),
            ("Outer Thigh (Abductor)","Legs"),
            ("Seated Leg Curl","Legs"),
            ("Smith Calf Raise","Legs"),
        ]
        sh_pool = [
            ("Shoulder Press Machine","Shoulders"),
            ("Side Lateral Raise Machine","Shoulders"),
            ("Reverse Pec Deck","Shoulders"),
            ("Smith Overhead Press","Shoulders"),
            ("Cable Lateral Raise (single)","Shoulders"),
        ]
        legs_sel = legs_pool_safe[:4]  # keep safe
        sh_sel = pick_variation(seed, sh_pool)[:3]
        plan = legs_sel + sh_sel

    # Default set/rep suggestions per exercise
    suggestions = {}
    for ex, bp in plan:
        if bp in ("Chest","Back","Legs","Shoulders"):
            suggestions[ex] = {"sets":3, "reps":"8-12", "notes":""}
        else:
            suggestions[ex] = {"sets":3, "reps":"10-15", "notes":""}

    return plan, suggestions
