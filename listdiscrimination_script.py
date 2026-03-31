from psychopy import visual, core, event, gui
import pandas as pd
import os

# =========================
# PARTICIPANT INFO
# =========================
exp_info = {'participant_id': ''}
dlg = gui.DlgFromDict(dictionary=exp_info, title='List Discrimination Task')
if not dlg.OK:
    core.quit()

participant_id = exp_info['participant_id']

# =========================
# FILE PATHS
# =========================
study_file = 'studylist.csv'
test_file = 'testlist.csv'

# =========================
# LOAD DATA
# =========================
study_df = pd.read_csv(study_file)
test_df = pd.read_csv(test_file)

required_study_cols = {'image', 'list_id'}
required_test_cols = {'image', 'correct_list'}

if not required_study_cols.issubset(study_df.columns):
    raise ValueError("Study CSV must contain: image, list_id")
if not required_test_cols.issubset(test_df.columns):
    raise ValueError("Test CSV must contain: image, correct_list")

# Randomize within each list block
study_blocks = {
    list_num: group.sample(frac=1).reset_index(drop=True)
    for list_num, group in study_df.groupby('list_id')
}

# Randomize full test phase
test_df = test_df.sample(frac=1).reset_index(drop=True)

# =========================
# OUTPUT
# =========================
os.makedirs('data', exist_ok=True)
outfile = os.path.join('data', f'{participant_id}_list_discrimination.csv')
results = []

# =========================
# WINDOW + STIMULI
# =========================
win = visual.Window(fullscr=False, color='black', units='height')
img_stim = visual.ImageStim(win, size=(0.6, 0.6))
fixation = visual.TextStim(win, text='+', color='white', height=0.08)


def text_screen(message, height=0.045):
    stim = visual.TextStim(
        win,
        text=message,
        color='white',
        height=height,
        wrapWidth=1.4
    )
    stim.draw()
    win.flip()


def save_and_exit():
    pd.DataFrame(results).to_csv(outfile, index=False)
    win.close()
    core.quit()


def wait_for_space_or_escape():
    keys = event.waitKeys(keyList=['space', 'escape'])
    if 'escape' in keys:
        save_and_exit()


def check_escape():
    if 'escape' in event.getKeys():
        save_and_exit()

# =========================
# INSTRUCTIONS
# =========================
text_screen(
    "Welcome to the List Discrimination Task\n\n"
    "You will first study 3 separate lists of images.\n"
    "Please remember which LIST each image belongs to.\n\n"
    "During the test:\n"
    "1 = List 1\n"
    "2 = List 2\n"
    "3 = List 3\n"
    "4 = New\n\n"
    "Press SPACE to begin.\n"
    "Press ESC anytime to quit."
)
wait_for_space_or_escape()

# =========================
# STUDY PHASE
# =========================
max_list = max(study_blocks.keys())

for list_num in sorted(study_blocks.keys()):
    text_screen(
        f"Beginning LIST {list_num}\n\n"
        f"All upcoming images belong to List {list_num}.\n\n"
        "Press SPACE to continue."
    )
    wait_for_space_or_escape()

    for _, row in study_blocks[list_num].iterrows():
        check_escape()

        fixation.draw()
        win.flip()
        core.wait(0.5)

        img_stim.image = row['image']
        img_stim.draw()
        win.flip()
        core.wait(2.0)

    if list_num < max_list:
        text_screen(
            f"End of LIST {list_num}\n\n"
            "Take a short break.\n\n"
            f"Press SPACE to begin LIST {list_num + 1}."
        )
        wait_for_space_or_escape()

# =========================
# TEST INSTRUCTIONS
# =========================
text_screen(
    "Study phase complete.\n\n"
    "Now indicate which list each image belonged to.\n\n"
    "1 = List 1\n"
    "2 = List 2\n"
    "3 = List 3\n"
    "4 = New\n\n"
    "Press SPACE to begin the test."
)
wait_for_space_or_escape()

question = visual.TextStim(
    win,
    text="Which list was this image in?\n\n1 = List 1   2 = List 2   3 = List 3   4 = New",
    color='white',
    height=0.04,
    pos=(0, -0.4),
    wrapWidth=1.4
)

# =========================
# TEST PHASE
# =========================
for trial_index, row in test_df.iterrows():
    check_escape()

    fixation.draw()
    win.flip()
    core.wait(0.5)

    img_stim.image = row['image']
    img_stim.draw()
    question.draw()
    win.flip()

    rt_clock = core.Clock()
    key, rt = event.waitKeys(
        keyList=['1', '2', '3', '4', 'escape'],
        timeStamped=rt_clock
    )[0]

    if key == 'escape':
        save_and_exit()

    correct_answer = str(row['correct_list'])
    accuracy = 1 if key == correct_answer else 0

    results.append({
        'participant_id': participant_id,
        'trial_num': trial_index + 1,
        'image': row['image'],
        'correct_list': correct_answer,
        'response': key,
        'accuracy': accuracy,
        'rt': rt
    })

# =========================
# SAVE DATA + END
# =========================
pd.DataFrame(results).to_csv(outfile, index=False)

text_screen("Task complete.\n\nThank you for participating!")
core.wait(3)

win.close()
core.quit()