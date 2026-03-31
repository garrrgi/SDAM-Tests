from psychopy import visual, core, event, gui
import random
import csv

# ---------------- PARTICIPANT INFO ----------------
info = {'Participant ID': ''}
dlg = gui.DlgFromDict(info, title='Experiment Info')
if not dlg.OK:
    core.quit()
participant = info['Participant ID']

# ---------------- WINDOW ----------------
win = visual.Window(size=(800, 600), color='black', units='pix')

# ---------------- STIMULUS FUNCTION ----------------
def make_stim(shape, color, pos):
    if shape == 'circle':
        return visual.Circle(win, radius=20, fillColor=color, lineColor=color, pos=pos)
    else:
        return visual.Rect(win, width=40, height=40, fillColor=color, lineColor=color, pos=pos)

colors = ['red', 'green', 'blue', 'yellow']
shapes = ['circle', 'square']

# ---------------- PARAMETERS ----------------
blocks = 5
trials_per_block = 48   # 5 × 48 = 240

set_sizes = [6, 10, 14]

# ---------------- GRID POSITIONS ----------------
grid_x = [-250, -125, 0, 125, 250]
grid_y = [-150, 0, 150]
grid_positions = [(x, y) for x in grid_x for y in grid_y]

# ---------------- DATA ----------------
data = []

# ---------------- SAFE QUIT FUNCTION ----------------
def quit_experiment():
    filename = f"{participant}_visual_search_partial.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "participant", "trial", "block", "search_type",
            "set_size", "target_shape", "target_color",
            "target_present", "response", "correct", "rt"
        ])
        writer.writerows(data)

    win.close()
    core.quit()

# ---------------- FIXATION ----------------
fixation = visual.TextStim(win, text="+", color='white')

# ---------------- INSTRUCTIONS ----------------
instr = visual.TextStim(
    win,
    text="Block 1 = Serial Search\nBlocks 2–5 = Conjunction Search\n\nPress Y if target present\nPress N if absent\n\nPress any key to start",
    color='white'
)
instr.draw()
win.flip()
event.waitKeys()

trial_index = 0

# ---------------- EXPERIMENT ----------------
for block in range(blocks):

    for t in range(trials_per_block):

        trial_index += 1

        set_size = random.choice(set_sizes)
        target_present = random.choice([True, False])

        # -------- FIXATION --------
        fixation.draw()
        win.flip()
        core.wait(0.8)
        if 'escape' in event.getKeys():
            quit_experiment()

        # ==================================================
        # BLOCK 1 = SERIAL SEARCH
        # ==================================================
        if block == 0:
            search_type = "serial"

            target_shape = "circle"
            target_color = "red"

            label = visual.TextStim(win, text="TARGET", pos=(0, 150), color='white')
            target_stim = make_stim(target_shape, target_color, (0, 0))

            label.draw()
            target_stim.draw()
            win.flip()
            core.wait(1.5)

            if 'escape' in event.getKeys():
                quit_experiment()

            # Delay
            win.flip()
            core.wait(1)

            positions = random.sample(grid_positions, set_size)

            stimuli = []

            if target_present:
                stimuli.append(make_stim(target_shape, target_color, positions[0]))

            for pos in positions[1:]:
                stimuli.append(make_stim("circle", "blue", pos))

        # ==================================================
        # BLOCKS 2-5 = CONJUNCTION SEARCH
        # ==================================================
        else:
            search_type = "conjunction"

            target_shape = random.choice(shapes)
            target_color = random.choice(colors)

            label = visual.TextStim(win, text="TARGET", pos=(0, 150), color='white')
            target_stim = make_stim(target_shape, target_color, (0, 0))

            label.draw()
            target_stim.draw()
            win.flip()
            core.wait(1.5)

            if 'escape' in event.getKeys():
                quit_experiment()

            # Delay
            win.flip()
            core.wait(1)

            positions = random.sample(grid_positions, set_size)

            stimuli = []

            if target_present:
                stimuli.append(make_stim(target_shape, target_color, positions[0]))

            for pos in positions[1:]:
                s = random.choice(shapes)
                c = random.choice(colors)
                stimuli.append(make_stim(s, c, pos))

        # -------- SEARCH DISPLAY --------
        for stim in stimuli:
            stim.draw()

        win.flip()

        if 'escape' in event.getKeys():
            quit_experiment()

        # -------- RESPONSE --------
        clock = core.Clock()
        keys = event.waitKeys(keyList=['y', 'n', 'escape'], timeStamped=clock)

        key, rt = keys[0]

        if key == 'escape':
            quit_experiment()

        correct = 1 if (
            (key == 'y' and target_present) or
            (key == 'n' and not target_present)
        ) else 0

        # -------- SAVE --------
        data.append([
            participant,
            trial_index,
            block + 1,
            search_type,
            set_size,
            target_shape,
            target_color,
            target_present,
            key,
            correct,
            round(rt, 4)
        ])

        core.wait(0.3)

    # -------- BREAK --------
    if block < blocks - 1:
        brk = visual.TextStim(
            win,
            text=f"End of Block {block+1}\n\nPress SPACE to continue",
            color='white'
        )
        brk.draw()
        win.flip()

        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            quit_experiment()

# ---------------- SAVE FINAL DATA ----------------
filename = f"{participant}_visual_search.csv"

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "participant", "trial", "block", "search_type",
        "set_size", "target_shape", "target_color",
        "target_present", "response", "correct", "rt"
    ])
    writer.writerows(data)

# ---------------- END SCREEN ----------------
end = visual.TextStim(win, text="Experiment complete.\nThank you!", color='white')
end.draw()
win.flip()
core.wait(2)

win.close()
core.quit()
