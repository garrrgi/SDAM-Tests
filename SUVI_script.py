from psychopy import visual, core, event, gui
from psychopy import visual, core, event, gui
import pandas as pd
import os
from datetime import datetime

# =========================
# PARTICIPANT INFO
# =========================

info = {"Participant ID": ""}
dlg = gui.DlgFromDict(info)
if not dlg.OK:
    core.quit()

participant_id = info["Participant ID"]

# =========================
# FILE SETUP (SAFE)
# =========================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

filename = os.path.join(data_dir, f"{participant_id}_{timestamp}.csv")

columns = ["participant","trial","condition","cue","left_stim","right_stim","response","correct","accuracy","rt"]
pd.DataFrame(columns=columns).to_csv(filename, index=False)

# =========================
# PATH SETUP (IMPORTANT)
# =========================

base_dir = os.getcwd()
image_folder = os.path.join(base_dir, "stimuli")

# =========================
# WINDOW
# =========================

win = visual.Window(size=[1000, 700], color="grey", units="pix")

clock = core.Clock()

# =========================
# LOAD CONDITIONS
# =========================

trials_df = pd.read_csv("suvi_4stim_120_trials.csv")
trials = trials_df.to_dict('records')

# =========================
# STIMULI
# =========================

fixation = visual.TextStim(win, text="+", height=40, color="white")

cue_text = visual.TextStim(win, text="", height=40, color="white")

left_text = visual.TextStim(win, pos=(-200, 0), height=40, color="white")
right_text = visual.TextStim(win, pos=(200, 0), height=40, color="white")

left_image = visual.ImageStim(win, pos=(-200, 0), size=(150,150))
right_image = visual.ImageStim(win, pos=(200, 0), size=(150,150))

instruction = visual.TextStim(
    win,
    text="""Welcome!

You will see a WORD. Visualize it as clearly as possible.

Then choose which item matches it.

Use LEFT and RIGHT arrow keys.

Press SPACE to start.
Press ESC anytime to quit.""",
    height=25,
    wrapWidth=800,
    color="white"
)

end_text = visual.TextStim(win, text="Thank you! Press any key to exit.", height=30)

# =========================
# INSTRUCTIONS
# =========================

instruction.draw()
win.flip()

keys = event.waitKeys(keyList=["space", "escape"])
if "escape" in keys:
    win.close()
    core.quit()

# =========================
# TRIAL LOOP
# =========================

for trial in trials:

    # ESC CHECK (safe exit)
    if "escape" in event.getKeys():
        win.close()
        core.quit()

    # ---------------------
    # FIXATION
    # ---------------------
    fixation.draw()
    win.flip()
    core.wait(0.5)

    # ---------------------
    # CUE
    # ---------------------
    cue_text.text = trial["cue"]
    cue_text.draw()
    win.flip()
    core.wait(1)

    # ---------------------
    # IMAGERY PERIOD
    # ---------------------
    fixation.draw()
    win.flip()
    core.wait(3)

    # ---------------------
    # SEARCH DISPLAY
    # ---------------------
    event.clearEvents()
    clock.reset()

    if trial["condition"] == "word":
        left_text.text = trial["left_stim"]
        right_text.text = trial["right_stim"]
        left_text.draw()
        right_text.draw()

    elif trial["condition"] == "image":
        left_path = os.path.join(image_folder, trial["left_stim"])
        right_path = os.path.join(image_folder, trial["right_stim"])

        left_image.image = left_path
        right_image.image = right_path

        left_image.draw()
        right_image.draw()

    win.flip()

    keys = event.waitKeys(keyList=["left", "right", "escape"], timeStamped=clock)
    key, rt = keys[0]

    if key == "escape":
        win.close()
        core.quit()

    # ---------------------
    # RESPONSE CODING
    # ---------------------
    resp = 0 if key == "left" else 1
    correct = trial["correct_resp"]
    acc = 1 if resp == correct else 0

    # ---------------------
    # SAVE IMMEDIATELY
    # ---------------------
    row = {
        "participant": participant_id,
        "trial": trial["trial"],
        "condition": trial["condition"],
        "cue": trial["cue"],
        "left_stim": trial["left_stim"],
        "right_stim": trial["right_stim"],
        "response": resp,
        "correct": correct,
        "accuracy": acc,
        "rt": rt
    }

    pd.DataFrame([row]).to_csv(filename, mode='a', header=False, index=False)

# =========================
# END SCREEN
# =========================

end_text.draw()
win.flip()
event.waitKeys()

win.close()
core.quit()