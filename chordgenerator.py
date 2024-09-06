from europi import *
from europi_script import EuroPiScript
import random
import machine

# Define each mode starting on C
SCALES = {
    "Ionian": [0, 2, 4, 5, 7, 9, 11],    # C Major
    "Dorian": [0, 2, 3, 5, 7, 9, 10],    # C Dorian
    "Phrygian": [0, 1, 3, 5, 7, 8, 10],  # C Phrygian
    "Lydian": [0, 2, 4, 6, 7, 9, 11],    # C Lydian
    "Mixolydian": [0, 2, 4, 5, 7, 9, 10],# C Mixolydian
    "Aeolian": [0, 2, 3, 5, 7, 8, 10],   # C Aeolian (Natural Minor)
    "Locrian": [0, 1, 3, 5, 6, 8, 10],   # C Locrian
}

# CV Output Settings Defaults (weights from 1 to 100)
DEFAULT_CV_WEIGHTS = {
    "cv1": {"root": 100, "2nd": 0, "3rd": 0, "4th": 0, "5th": 0, "6th": 0, "7th": 0, "9th": 0},
    "cv2": {"root": 100, "2nd": 0, "3rd": 0, "4th": 0, "5th": 0, "6th": 0, "7th": 0, "9th": 0},
    "cv3": {"root": 0, "2nd": 0, "3rd": 100, "4th": 0, "5th": 0, "6th": 0, "7th": 0, "9th": 0},
    "cv4": {"root": 0, "2nd": 0, "3rd": 0, "4th": 0, "5th": 100, "6th": 0, "7th": 0, "9th": 0},
    "cv5": {"root": 0, "2nd": 0, "3rd": 100, "4th": 0, "5th": 0, "6th": 0, "7th": 0, "9th": 0},
    "cv6": {"root": 0, "2nd": 0, "3rd": 0, "4th": 0, "5th": 100, "6th": 0, "7th": 0, "9th": 0},
}

class ChordGenerator(EuroPiScript):
    def __init__(self):
        super().__init__()
        self.current_scale = "Ionian"  # Default scale
        self.current_key = "C"  # Default key
        self.cv_weights = DEFAULT_CV_WEIGHTS.copy()  # Initialize CV weights
        self.menu_position = 0  # Main menu position
        self.submenu_position = 0  # Submenu position for CV settings
        self.current_cv = "cv1"  # Track current CV for submenu
        self.editing = False  # Track if a setting is being edited
        self.current_menu = "main"  # Track current menu (main, cv, scale, key, global)
        self.trigger_recvd = False  # Flag for trigger handling
        self.last_k2_position = 50  # Initialize last known position for k2

        # Button handlers
        @din.handler
        def on_din():
            self.trigger_recvd = True

        @b1.handler
        def on_b1_press():
            if self.editing:
                self.editing = False  # Cancel editing
            else:
                self.navigate_back()  # Navigate back

        @b2.handler
        def on_b2_press():
            if self.editing:
                self.editing = False  # Confirm change
            else:
                self.navigate_forward()  # Navigate forward or edit setting

        self.update_display()

    def navigate_back(self):
        if self.current_menu == "main":
            return  # Already at the top level, do nothing
        elif self.current_menu == "cv":
            self.current_menu = "main"  # Go back to main menu
            self.menu_position = 0
        elif self.editing:
            self.editing = False  # Cancel editing
        self.update_display()

    def navigate_forward(self):
        if self.current_menu == "main":
            if self.menu_position < 6:
                self.current_menu = "cv"
                self.current_cv = f"cv{self.menu_position + 1}"
                self.submenu_position = 0
            elif self.menu_position == 6:
                self.current_menu = "scale"
            elif self.menu_position == 7:
                self.current_menu = "key"
            elif self.menu_position == 8:
                self.current_menu = "global"
        elif self.current_menu == "cv":
            if not self.editing:
                self.editing = True  # Start editing the weight
            else:
                self.editing = False  # Confirm editing
        elif self.current_menu in ["scale", "key"]:
            if not self.editing:
                self.editing = True  # Start editing
            else:
                self.editing = False  # Confirm editing
        self.update_display()

    def update_display(self):
        oled.fill(0)  # Clear the display
        if self.current_menu == "main":
            self.display_main_menu()
        elif self.current_menu == "cv":
            self.display_cv_menu()
        elif self.current_menu == "scale":
            self.display_scale_menu()
        elif self.current_menu == "key":
            self.display_key_menu()
        oled.show()

    def display_main_menu(self):
        oled.text(f"{self.current_key} {self.current_scale}", 0, 0)
        menu_items = ["cv1", "cv2", "cv3", "cv4", "cv5", "cv6", "Scale", "Key", "Global"]
        for i, item in enumerate(menu_items):
            if i == self.menu_position:
                self.invert_text(item, 0, 10)  # Highlight selected item on the second line
            elif i == self.menu_position + 1:
                oled.text(item, 0, 20)  # Display the third line

    def display_cv_menu(self):
        oled.text(f"{self.current_key} {self.current_scale}", 0, 0)
        cv = self.current_cv
        note = list(self.cv_weights[cv].keys())[self.submenu_position]
        weight = self.cv_weights[cv][note]
        oled.text(f"{cv}: {note}", 0, 10)
        if self.editing:
            self.invert_text(f"weight: {weight}", 0, 20)
        else:
            oled.text(f"weight: {weight}", 0, 20)

    def display_scale_menu(self):
        oled.text(f"{self.current_key} {self.current_scale}", 0, 0)
        if self.editing:
            self.invert_text(self.current_scale, 0, 10)
        else:
            oled.text(self.current_scale, 0, 10)

    def display_key_menu(self):
        oled.text(f"{self.current_key} {self.current_scale}", 0, 0)
        if self.editing:
            self.invert_text(self.current_key, 0, 10)
        else:
            oled.text(self.current_key, 0, 10)

    def invert_text(self, text, x, y):
        text_width = len(text) * 8  # Approximate width (assuming 8x8 pixel font)
        text_height = 10  # Height of the text line
        oled.fill_rect(x, y, text_width, text_height, 1)
        oled.text(text, x, y, 0)

    def on_knob_turn(self):
        if self.editing:
            self.adjust_setting()
        else:
            self.navigate_menu()

    def adjust_setting(self):
        if self.current_menu == "cv":
            cv = self.current_cv
            note = list(self.cv_weights[cv].keys())[self.submenu_position]

            # Use k2.read_position() to get the current position (0-100)
            current_position = k2.read_position()
            
            # Calculate the change in position
            delta = current_position - self.last_k2_position
            
            # Update the weight based on the change in position
            if abs(delta) > 1:  # Add a small threshold to avoid unintended changes
                new_weight = self.cv_weights[cv][note] + delta
                if current_position == 99:
                    self.cv_weights[cv][note] = 100
                elif current_position == 0:
                    self.cv_weights[cv][note] = 0
                else:
                    self.cv_weights[cv][note] = max(0, min(100, new_weight))
                self.last_k2_position = current_position

        elif self.current_menu == "scale":
            scale_names = list(SCALES.keys())
            self.current_scale = k2.choice(scale_names)
        elif self.current_menu == "key":
            # For now, just C, so no adjustment needed
            pass
        self.update_display()

    def navigate_menu(self):
        if self.current_menu == "main":
            self.menu_position = k1.range(9)  # Choose from 9 menu items
        elif self.current_menu == "cv":
            cv_notes = list(self.cv_weights[self.current_cv].keys())
            self.submenu_position = k1.range(len(cv_notes))
        self.update_display()

    def generate_chord(self):
        scale_name = self.current_scale
        scale = SCALES[scale_name]

        # Select a random root note from the scale
        root_note = random.choice(scale)

        # Generate notes for each CV output based on their respective weights
        for i in range(1, 7):
            cv_name = f"cv{i}"
            note = self.select_note_from_weights(scale, self.cv_weights[cv_name], root_note)
            voltage = self.note_to_voltage(note)
            globals()[cv_name].voltage(voltage)

    def select_note_from_weights(self, scale, weights, root_note):
        notes = list(weights.keys())
        weight_values = list(weights.values())
        total_weight = sum(weight_values)

        if total_weight == 0:
            return root_note  # Default to root note if all weights are zero

        random_value = random.uniform(0, total_weight)
        cumulative_weight = 0
        for note, weight in zip(notes, weight_values):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return self.get_note_from_interval(scale, root_note, note)
        return root_note  # Fallback to root note

    def get_note_from_interval(self, scale, root_note, interval_name):
        interval_map = {
            "root": 0,
            "2nd": 1,  # 1 step in scale
            "3rd": 2,  # 2 steps in scale
            "4th": 3,  # 3 steps in scale
            "5th": 4,  # 4 steps in scale
            "6th": 5,  # 5 steps in scale
            "7th": 6,  # 6 steps in scale
            "9th": 8,  # 2nd note in the next octave, so it's the same as 2nd but with an octave jump
        }

        # Calculate the actual interval index in the scale
        interval_index = interval_map[interval_name]
        
        # Find the root note index in the scale
        root_index = scale.index(root_note)

        # Calculate the target note index by moving within the scale
        note_index = (root_index + interval_index) % len(scale)
        
        note = scale[note_index]

        # Adjust for octave if it's a 9th or if we've wrapped around the scale
        if interval_name == "9th" or note < root_note:
            note += 12

        return scale[note_index]


    def note_to_voltage(self, note):
        return (note % 12) / 12 # use 1v/oct but allow for more than 1 octave

    def main(self):
        while True:
            if self.trigger_recvd:
                self.trigger_recvd = False
                self.generate_chord()

            # Handle knob input
            self.on_knob_turn()
            
            # Use machine.idle() to save power and allow for interrupts
            machine.idle()

if __name__ == "__main__":
    ChordGenerator().main()
