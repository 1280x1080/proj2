"""EDL for VIDEO_005 - OPEN 24/7, Part 1 (built from the scene sheet the user supplied).

SCENES -> SEGMENTS / OVERLAYS / CAPTIONS.  Cuts sit on the line starts (the lines are placed at the sheet's
scene times), so the edit follows the sheet: ~1:24, 33 scenes (+ the freeze), ~185 words.
Captions use the sheet's caption text per line (CAPTIONS.line_text), one key word RED/YELLOW.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

# (id, line, shot, caption text or None for the spoken words, {key word: colour}, visual, camera, sfx, clock, customers, note)
SCENES = [
    dict(id="01", line="S01", shot="store_ext", cap=None, keys={"night": RED}, clock="2:58 AM", cust=0,
         visual="Wide: lone store glowing on an empty road in the rain, OPEN 24/7 sign buzzing.", cam="slow push",
         sfx=[("door_chime", -26, 1.2)], note="Title card OPEN 24/7 / PART 1."),
    dict(id="02", line="S02", shot="clerk_cu", cap=None, keys={"triple.": YEL}, clock="2:58 AM", cust=0,
         visual="You behind the register in a store vest, staring at a sticky note 'Night pay x3'. Uneasy.",
         cam="slow push", sfx=[]),
    dict(id="03", line="S03", shot="glass_pov", cap=None, keys={}, clock="2:58 AM", cust=0,
         visual="Through the front glass: empty road, rain streaks, one flickering streetlight.", cam="slow push", sfx=[]),
    dict(id="04", line="S04", shot="chime_cu", cap="THE DOOR CHIME KEEPS RINGING.", keys={"ringing.": RED},
         clock="2:58 AM", cust=0, visual="CU the brass chime swinging by itself. The door is closed.", cam="hold",
         sfx=[("door_chime", -8, -0.35), ("door_chime", -12, 1.6)]),
    dict(id="05", line="S05", shot="counter_wide", cap=None, keys={}, clock="3:00 AM", cust=0,
         visual="You slowly turn toward the door. Nobody.", cam="slow push", sfx=[]),
    dict(id="06", line="S06", shot="phone_counter", cap="", keys={}, clock="3:00 AM", cust=0,
         visual="Phone on the counter: MANAGER: 'Whatever happens, DON'T open the back room.'", cam="slow push",
         sfx=[("phone_vibrate", -10, 0.0), ("text_ping", -12, 0.25)]),
    dict(id="07", line="S07", shot="monitor_cu", cap=None, keys={"cameras.": YEL}, clock="3:00 AM", cust=0,
         visual="Security monitor: 4 grainy feeds (door, aisle 2, aisle 4, back room door).", cam="slow push",
         sfx=[("crt_hum", None, 0)]),
    dict(id="08", line="S08", shot="monitor_cu", cap="SOMEONE'S STANDING THERE.", keys={"someone's": RED}, clock="3:00 AM",
         cust=1, visual="The aisle-4 feed fills the screen: a tall figure facing the shelf, too still.", cam="punch-in",
         sfx=[("glitch", -14, 0.0)]),
    dict(id="09", line="S09", shot="aisle_pov", cap="THE AISLE IS EMPTY.", keys={"empty.": YEL}, clock="3:00 AM", cust=1,
         visual="The real aisle 4: empty. Wet bare footprints on the tiles.", cam="slow push", sfx=[("drip", -14, 1.0)],
         note="CLUE -> option 1: the monitor shows what the room doesn't."),
    dict(id="10", line="S10", shot="backroom_door", cap="THE BACK ROOM DOOR.", keys={"back": RED, "room": RED},
         clock="3:00 AM", cust=1, visual="Behind the counter the back-room door swings open, warm light spilling out.",
         cam="slow push", sfx=[("door_creak_long", -6, 0.3)]),
    dict(id="11", line="S11", shot="janitor_wide", cap="AN OLD JANITOR.", keys={"janitor.": YEL}, clock="3:12 AM", cust=2,
         visual="An old janitor with a mop bucket, tired eyes, name tag scratched off.", cam="slow push",
         sfx=[("footstep_soft", -14, 0.2), ("footstep_soft", -15, 0.8)]),
    dict(id="12", line="S12", shot="janitor_low", cap="\"NEW? THEN LISTEN.\"", keys={"listen.\"": YEL}, clock="3:12 AM",
         cust=2, visual="Low angle close on the janitor.", cam="slow push", sfx=[]),
    dict(id="13", line="S13", shot="card_cu", cap="THREE RULES.", keys={"three": YEL, "rules.": YEL}, clock="3:12 AM",
         cust=2, visual="The laminated card slaps onto the counter; all 3 rules in handwriting.", cam="punch-in",
         sfx=[("card_slap", -2, 0.55)]),
    dict(id="14", line="S14", shot="card_cu", cap="NOBODY BEHIND THE COUNTER.", keys={"counter.": YEL}, clock="3:12 AM",
         cust=2, card=1, visual="His finger taps rule 1.", cam="hold", sfx=[("tick", -16, 0.3), ("tick", -16, 0.6)]),
    dict(id="15", line="S15", shot="janitor_cu", cap="DON'T LOOK AT THE MONITOR.", keys={"monitor.": YEL},
         clock="3:12 AM", cust=2, card=2, visual="The janitor glances at the monitor - then away, fast.", cam="slow push",
         sfx=[]),
    dict(id="16", line="S16", shot="wall_phone", cap="NEVER ANSWER AT 3:33.", keys={"3:33.": YEL}, clock="3:12 AM",
         cust=2, card=3, visual="The old wall phone behind the counter. Slow push in.", cam="slow push", sfx=[]),
    dict(id="17", line=None, shot="doorway_quiet", cap=None, keys={}, clock="3:12 AM", cust=2,
         visual="Quiet beat: the empty doorway, rain outside. No VO. 'YOUR COMMENT COULD DECIDE PART 2'.",
         cam="slow push", sfx=[]),
    dict(id="18", line="S18", shot="woman_door", cap="BAREFOOT.", keys={"barefoot.": RED}, clock="3:20 AM", cust=3,
         visual="A woman in the doorway, dripping, hair over her face, smile slightly too wide.", cam="slow push",
         sfx=[("door_chime", -8, -0.2), ("drip", -10, 1.2), ("drip", -12, 1.9)]),
    dict(id="19", line="S19", shot="woman_counter", cap=None, keys={"anything.": RED}, clock="3:20 AM", cust=3,
         visual="She stands at the counter, hands flat on it, still smiling.", cam="slow push",
         sfx=[("wet_steps", -12, -0.6)]),
    dict(id="20", line="S20", shot="woman_smile", cap="\"CAN I COME BEHIND THE COUNTER?\"", keys={"counter?\"": RED},
         clock="3:20 AM", cust=3, visual="Close on her smile as she starts to lean over the counter.", cam="slow push",
         sfx=[("breath_close", -18, 0.0)]),
    dict(id="21", line="S21a", shot="mop_block", cap="", keys={}, clock="3:20 AM", cust=3,
         visual="The mop handle slams across the counter opening.", cam="shake push", sfx=[("mop_slam", -2, 0.45)],
         note="CLUE -> option 2: he protected you."),
    dict(id="21b", line="S21b", shot="mop_block", cap="\"COUNTER'S CLOSED.\"", keys={"closed.\"": YEL}, cont=True,
         clock="3:20 AM", cust=3, visual="(continues)", cam="", sfx=[]),
    dict(id="22", line="S22", shot="chime_cu", cap="THE CHIME DOESN'T RING.", keys={"doesn't": RED}, clock="3:20 AM",
         cust=2, visual="The door closes behind her. The chime hangs perfectly still.", cam="slow push",
         sfx=[("wet_steps", -14, 0.0)]),
    dict(id="23", line="S23", shot="wall_phone", cap="3:33", keys={"3:33": RED}, clock="3:33 AM", cust=2,
         visual="3:33 - the wall phone shakes with each ring.", cam="shake",
         sfx=[("old_phone_ring", -12, -0.1), ("old_phone_ring", -14, 2.1)]),
    dict(id="24", line="S24", shot="callerid_cu", cap="YOUR SISTER'S VOICE.", keys={"sister's": RED}, clock="3:33 AM",
         cust=2, visual="Caller ID: HOME. A waveform glows.", cam="slow push", sfx=[("old_phone_ring", -22, 0.6)]),
    dict(id="25", line="S25", shot="hand_receiver", cap="\"PLEASE PICK UP.\"", keys={"pick": YEL}, clock="3:33 AM", cust=2,
         visual="Your hand hovering over the receiver, shaking.", cam="slow push", sfx=[("old_phone_ring", -14, 1.2)]),
    dict(id="26", line="S26", shot="hand_receiver", cap="\"DON'T.\"", keys={"don't.\"": RED}, clock="3:33 AM", cust=2,
         visual="The janitor's hand clamps your wrist. The ringing stops.", cam="punch-in", sfx=[("impact_soft", -10, 0.05)]),
    dict(id="27", line="S27", shot="wall_phone", cap="IT RINGS AGAIN.", keys={"again.": RED}, clock="3:34 AM", cust=2,
         visual="3:34. The phone shakes again.", cam="shake", sfx=[("old_phone_ring", -12, 0.0), ("old_phone_ring", -10, 2.0)],
         note="CLUE -> option 4: the rule only says 3:33."),
    dict(id="28", line="S28", shot="black", cap="THE LIGHTS DIE.", keys={"lights": RED, "die.": RED}, clock="3:34 AM", cust=2,
         visual="Hard cut to black.", cam="", sfx=[("power_down", -2, -0.15)]),
    dict(id="29", line="S29", shot="monitor_face", cap="ONLY THE MONITOR GLOWS.", keys={"monitor": YEL}, clock="3:34 AM",
         cust="glitch", visual="Monitor light on your face. We never see the screen.", cam="slow push",
         sfx=[("glitch", -10, 0.4), ("crt_hum", None, 0)]),
    dict(id="30", line="S30a", shot="ear_ecu", cap="", keys={}, clock="3:34 AM", cust=4,
         visual="ECU of your ear, darkness right behind it.", cam="slow push", sfx=[("breath_close", -14, 0.0)]),
    dict(id="30b", line="S30b", shot="ear_ecu", cap="\"DON'T LOOK AT THE MONITOR.\"", keys={"monitor.\"": YEL}, cont=True,
         clock="3:34 AM", cust=4, visual="(continues)", cam="", sfx=[]),
    dict(id="31", line="S31", shot="backroom_door", cap="FROM THE BACK ROOM.", keys={"back": RED, "room.": RED},
         clock="3:34 AM", cust=4, visual="The back-room door, a line of light still glowing under it.", cam="slow push",
         sfx=[], note="CLUE -> option 3: the only light left."),
    dict(id="32", line="S32", shot="shoulder_hand", cap="SOMETHING TOUCHES YOUR SHOULDER.", keys={"touches": RED},
         clock="3:34 AM", cust=4, visual="Wet, pale fingers on your shoulder.", cam="slow push",
         sfx=[("drip", -8, 0.3), ("drip", -10, 1.1)]),
    dict(id="32b", line=None, shot="face_cu", freeze=True, cap=None, keys={}, clock="3:34 AM", cust=4,
         visual="Freeze on your terrified face, red tint.", cam="freeze", sfx=[("impact_cinematic", -8, 0.0)]),
    dict(id="33", line=None, shot="choice_bg", cap=None, keys={}, clock=None, cust=None,
         visual="Dark store; each option pinned to its spot: monitor, the whisper behind you, the light under the back-room "
                "door, the ringing phone.", cam="slow push", sfx=[]),
]

FOCUS = dict(store_ext=(540, 900), clerk_cu=(540, 900), glass_pov=(540, 900), chime_cu=(540, 760),
             counter_wide=(540, 900), phone_counter=(540, 960), monitor_cu=(760, 1180), aisle_pov=(540, 1100),
             backroom_door=(540, 900), janitor_wide=(540, 900), janitor_low=(540, 800), card_cu=(540, 960),
             janitor_cu=(540, 860), wall_phone=(540, 900), doorway_quiet=(540, 960), woman_door=(540, 900),
             woman_counter=(540, 900), woman_smile=(540, 900), mop_block=(540, 1000), callerid_cu=(540, 960),
             hand_receiver=(540, 960), monitor_face=(540, 860), ear_ecu=(560, 900), shoulder_hand=(540, 900),
             face_cu=(540, 860), choice_bg=(540, 960))


def _t0(sc):
    if sc["id"] == "01":
        return 0.0
    if sc["id"] == "17":
        return B["s17"]
    if sc["id"] == "32b":
        return B["freeze"]
    if sc["id"] == "33":
        return B["choice"]
    return start(sc["line"]) - 0.1


def _cam(sc, t0, t1):
    c, f = sc["cam"], FOCUS.get(sc["shot"], (540, 960))
    fx = []
    if "punch" in c:
        fx.append(dict(fx="zoom", keys=[(t0, 1.0, f), (t0 + 0.14, 1.3, f), (t1, 1.36, f)], ease="out"))
    elif "push" in c:
        fx.append(dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.09, f)], ease="linear"))
    elif c == "hold":
        fx.append(dict(fx="zoom", keys=[(t0, 1.02, f), (t1, 1.05, f)], ease="linear"))
    if "shake" in c:
        fx.append(dict(fx="shake", t0=t0, t1=min(t1, t0 + 0.6), amp=12, freq=20))
    return fx


CUTS = [sc for sc in SCENES if not sc.get("cont")]
SEGMENTS = []
for i, sc in enumerate(CUTS):
    t0 = _t0(sc)
    t1 = _t0(CUTS[i + 1]) if i + 1 < len(CUTS) else DURATION
    if sc["id"] == "32":
        t1 = B["freeze"]
    src = sc["shot"]
    seg = dict(t0=t0, t1=t1, src=src, offset=t0, fx=_cam(sc, t0, t1), scene=sc["id"])
    if sc.get("freeze"):
        seg.update(freeze=B["freeze"] - 0.6, offset=B["freeze"] - 0.6)
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, FOCUS["face_cu"]), (t1, 1.12, FOCUS["face_cu"])]),
                     dict(fx="tint", color=RED, amount=0.35, t0=t0, t1=t1), dict(fx="flash", t=t0, dur=0.15)]
    if B["lights_die"] <= t0 and not sc.get("freeze"):
        seg["fx"].append(dict(fx="vignette", strength=0.5, t0=t0, t1=t1))
    SEGMENTS.append(seg)

SOURCES = {name: dict(kind="2d", shot=name) for name in {s["src"] for s in SEGMENTS}}
SOURCES["black"] = dict(kind="color", color="#000000")

# ---- HUD -----------------------------------------------------------------------------------------------------
HUD_END = B["choice"]
clock_keys, cust_keys = [], []
for sc in SCENES:
    if sc.get("clock") and (not clock_keys or clock_keys[-1][1] != sc["clock"]):
        clock_keys.append((_t0(sc), sc["clock"]))
for sc in SCENES:
    v = sc.get("cust")
    if v is None:
        continue
    if v == "glitch":  # 2 -> 4 with a digital stutter
        g = B["glitch"]
        for k, val in enumerate((4, 2, 4, 2, 4, 2, 4)):
            cust_keys.append((g + k * 0.07, val))
        continue
    if not cust_keys or cust_keys[-1][1] != v:
        cust_keys.append((_t0(sc), v))

red_from, red_to = B["ring333"] - 0.1, B["ring334"] - 0.1
OVERLAYS = [
    dict(kind="title", t0=0.05, t1=B["title_out"], text="OPEN 24/7", sub="PART 1", size=130, y=0.2, sub_color=YEL, stroke=14),
    dict(kind="chip", t0=0.0, t1=HUD_END, text="NIGHT 1 · HWY 9 MART", size=24, x=0.17, y=0.03, bg="#15161b", color="#d7d7dc"),
    dict(kind="hud", t0=0.0, t1=red_from, x=0.15, y=0.068, size=40, items=[("", [k for k in clock_keys if k[0] < red_from])],
         flash=YEL),
    dict(kind="text", t0=red_from, t1=red_to, text="3:33 AM", size=40, x=0.15, y=0.068, weight="ExtraBold", color="#ffffff",
         stroke=0, bg=RED, bg_alpha=0.95),
    dict(kind="hud", t0=red_to, t1=HUD_END, x=0.15, y=0.068, size=40, items=[("", [(0.0, "3:34 AM")])], flash=YEL),
    dict(kind="hud", t0=0.0, t1=HUD_END, x=0.82, y=0.05, size=34, items=[("CUSTOMERS", cust_keys)], flash=RED),
    # top-comment reminder (scene 17, no VO)
    dict(kind="text", t0=B["s17"] + 0.1, t1=start("S18") - 0.15, text="YOUR COMMENT COULD DECIDE PART 2", size=62, y=0.62,
         weight="Black", color="#ffffff", stroke=12, stroke_color="#141418"),
]
RULES = {1: "NEVER LET ANYONE BEHIND THE COUNTER", 2: "IF THE LIGHTS GO OUT, DON'T LOOK AT THE MONITOR",
         3: "NEVER ANSWER THE PHONE AT 3:33"}
_card = {sc["card"]: sc for sc in SCENES if sc.get("card")}
for n in (1, 2, 3):
    t0 = _t0(_card[n])
    t1 = _t0(_card[n + 1]) if n < 3 else B["s17"]
    OVERLAYS += [
        dict(kind="stamp", t0=t0, t1=t1, text=f"SURVIVAL RULE #{n}", size=46, y=0.135, rot=-3, color=RED, bg="#f1e9d6"),
        dict(kind="text", t0=t0 + 0.08, t1=t1, text=RULES[n], size=50, y=0.205, weight="ExtraBold", color="#2a2420",
             stroke=0, bg="#f1e9d6", bg_alpha=0.97),
    ]
# choice screen: options pinned to their spots (leader lines + dots are drawn in anim2d.choice_bg)
CHOICE_PILLS = [  # text, x, y (fractions), colour - anchors match anim2d.CHOICE_TARGETS
    ("1  LOOK AT THE MONITOR", 0.66, 0.72, "#e2574c"),
    ("2  TRUST THE JANITOR", 0.40, 0.255, "#3f8fd6"),
    ("3  RUN TO THE BACK ROOM", 0.30, 0.46, "#55a868"),
    ("4  ANSWER THE PHONE", 0.70, 0.34, "#d9a43b"),
]
OVERLAYS += [
    dict(kind="title", t0=B["choice"], t1=DURATION, text="PART 2", sub="WHAT DO YOU DO?", size=120, y=0.1, sub_color=YEL,
         sub_size=56, stroke=12),
] + [dict(kind="text", t0=B["choice"] + 0.3 + 0.15 * k, t1=DURATION, text=txt, size=44, x=x, y=y, weight="ExtraBold",
          color="#ffffff", stroke=0, bg=col, bg_alpha=0.96) for k, (txt, x, y, col) in enumerate(CHOICE_PILLS)] + [
    dict(kind="text", t0=B["choice"] + 0.9, t1=DURATION, text="TOP COMMENT CHOOSES WHAT HAPPENS NEXT", size=46, y=0.80,
         weight="Black", color=YEL, stroke=10, stroke_color="#141418"),
    dict(kind="text", t0=B["choice"] + 1.1, t1=DURATION, text="Comment your number + why", size=40, y=0.85,
         weight="Bold", color="#ffffff", stroke=8, stroke_color="#141418"),
]

# ---- CAPTIONS: the sheet's caption text per line (line_text), ALL CAPS, key words RED / YELLOW ----------------
_line_text = {sc["line"]: sc["cap"] for sc in SCENES if sc.get("line") and sc.get("cap") is not None}
_line_colors = {sc["line"]: sc["keys"] for sc in SCENES if sc.get("line") and sc.get("keys")}
CAPTIONS = dict(
    timing="audio/timing.json", y=0.70, size=84, max_words=5, highlight="#ffffff", speakers=False,
    upper=True, line_text=_line_text, line_colors=_line_colors,
    overrides=[(sg["t0"], sg["t1"], 0.62) for sg in SEGMENTS if sg["src"] == "clerk_cu"]  # above the sticky note
    + [(sg["t0"], sg["t1"], 0.80) for sg in SEGMENTS
               if sg["src"] in ("janitor_low", "janitor_cu", "woman_smile", "monitor_face", "face_cu", "ear_ecu",
                                "card_cu", "phone_counter", "monitor_cu", "callerid_cu")],
)

AUDIO = "audio/mix_master.wav"
