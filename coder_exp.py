from psychopy import visual, core, event, data, gui
import random
import os

# -----------------------------
# PARTICIPANT INFO
# -----------------------------
exp_info = {'participant': ''}
dlg = gui.DlgFromDict(exp_info, title='Brown-Peterson Task')

if not dlg.OK or exp_info['participant'] == '':
    core.quit()

participant_id = exp_info['participant']

# -----------------------------
# FILE SETUP
# -----------------------------
filename = f"data_{participant_id}.csv"

# -----------------------------
# WINDOW
# -----------------------------
win = visual.Window(size=(800, 600), color='black')

# -----------------------------
# STIMULI
# -----------------------------
fixation = visual.TextStim(win, text='+', height=0.1)
trigram_text = visual.TextStim(win, height=0.15)
distractor_text = visual.TextStim(win, height=0.08)

recall_prompt = visual.TextStim(win, text='Type the 3 letters:', pos=(0, 0.2), height=0.08)
response_text = visual.TextStim(win, text='', pos=(0, -0.1), height=0.1)

instructions = visual.TextStim(
    win,
    text=(
        "You will see three letters.\n\n"
        "Remember them.\n\n"
        "Then count backwards by 3s from a number.\n\n"
        "Finally, type the letters and press ENTER.\n\n"
        "Press SPACE to begin."
    ),
    height=0.06,
    wrapWidth=1.2
)

end_text = visual.TextStim(
    win,
    text="Thank you!\n\nPress any key to exit.",
    height=0.08
)

# -----------------------------
# ESCAPE HANDLER
# -----------------------------
def check_escape(keys):
    if 'escape' in keys:
        win.close()
        core.quit()

# -----------------------------
# INSTRUCTIONS
# -----------------------------
event.clearEvents()

while True:
    instructions.draw()
    win.flip()

    keys = event.getKeys()
    check_escape(keys)

    if 'space' in keys:
        break

event.clearEvents()

# -----------------------------
# LOAD CSV CONDITIONS
# -----------------------------
conditions_file = 'brown_peterson_conditions.csv'

trial_handler = data.TrialHandler(
    trialList=data.importConditions(conditions_file),
    nReps=1,
    method='random'
)

# -----------------------------
# SAVE HEADER MANUALLY
# -----------------------------
with open(filename, 'w') as f:
    f.write('participant,trigram,delay,response,correct,rt\n')

# -----------------------------
# TRIAL LOOP
# -----------------------------
for trial in trial_handler:

    trigram = trial['trigram']
    delay = float(trial['delay'])

    # FIXATION (0.5s)
    timer = core.Clock()
    while timer.getTime() < 0.5:
        fixation.draw()
        win.flip()
        check_escape(event.getKeys())

    # TRIGRAM (2s)
    timer = core.Clock()
    while timer.getTime() < 2:
        trigram_text.text = trigram
        trigram_text.draw()
        win.flip()
        check_escape(event.getKeys())

    # DISTRACTOR
    start_num = random.randint(200, 999)
    distractor_text.text = f"Count backwards from {start_num} by 3s"

    timer = core.Clock()
    while timer.getTime() < delay:
        distractor_text.draw()
        win.flip()
        check_escape(event.getKeys())

    # RECALL
    response = ''
    event.clearEvents()
    recall_clock = core.Clock()

    while True:
        recall_prompt.draw()
        response_text.text = response
        response_text.draw()
        win.flip()

        keys = event.getKeys(timeStamped=recall_clock)
        check_escape([k[0] for k in keys])

        for key, t in keys:
            if key == 'return':
                rt = t
                break
            elif key == 'backspace':
                response = response[:-1]
            elif len(key) == 1:
                response += key.upper()

        if any(k[0] == 'return' for k in keys):
            break

    # SCORING
    correct = int(response == trigram)

    # SAVE ROW (guaranteed, no overwrite issues)
    with open(filename, 'a') as f:
        f.write(f"{participant_id},{trigram},{delay},{response},{correct},{rt}\n")

# -----------------------------
# END SCREEN
# -----------------------------
event.clearEvents()

while True:
    end_text.draw()
    win.flip()

    keys = event.getKeys()
    check_escape(keys)

    if len(keys) > 0:
        break

# -----------------------------
# EXIT
# -----------------------------
win.close()
core.quit()