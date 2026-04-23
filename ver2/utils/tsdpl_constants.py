"""
utils/tsdpl_constants.py
TSDPL Kalinganagar – all domain constants, failure codes, machine specs,
shift definitions. Single source of truth imported by all other modules.
"""

# ── Shift Definitions ────────────────────────────────────────────────────────
SHIFTS = {
    "A - Morning":  {"start": "06:00", "end": "14:00", "code": "A"},
    "B - Afternoon":{"start": "14:00", "end": "22:00", "code": "B"},
    "C - Night":    {"start": "22:00", "end": "06:00", "code": "C"},
}

SHIFT_CODES = ["A - Morning", "B - Afternoon", "C - Night"]

def get_shift_from_hour(hour: int) -> str:
    if 6 <= hour < 14:
        return "A - Morning"
    elif 14 <= hour < 22:
        return "B - Afternoon"
    else:
        return "C - Night"


# ── Lines & Zones ─────────────────────────────────────────────────────────────
LINES = ["HR-CTL Line", "HR Slitting Line", "CR Processing Facility"]

LINE_ZONES = {
    "HR-CTL Line": ["Entry (Uncoiler)", "Mid (Cassette Leveller)", "Exit (Flying Shear / Stacker)"],
    "HR Slitting Line": ["Entry (Uncoiler/Bridle)", "Mid (Slitter Head)", "Exit (Recoiler / Scrap Chopper)"],
    "CR Processing Facility": ["Entry (Skin Pass Mill)", "Mid (Inspection)", "Exit (Parting Line)"],
}

# ── Machine Registry ──────────────────────────────────────────────────────────
MACHINES = {
    # HR-CTL Line
    "Uncoiler (HR-CTL)": {
        "line": "HR-CTL Line", "zone": "Entry (Uncoiler)",
        "criticality": "High",
        "params": {
            "Mandrel Torque %": {"unit": "%", "alarm_high": 85, "alarm_low": None, "normal_range": (0, 85)},
            "Mandrel Expansion Pressure (bar)": {"unit": "bar", "alarm_high": 200, "alarm_low": 50, "normal_range": (80, 180)},
            "Coil Weight (ton)": {"unit": "ton", "alarm_high": 30, "alarm_low": None, "normal_range": (5, 30)},
        },
        "pm_tasks": [
            {"task": "Mandrel Jaw Lubrication", "frequency": "Shift", "category": "Mechanical"},
            {"task": "Hydraulic Pressure Check", "frequency": "Weekly", "category": "Hydraulic"},
            {"task": "Mandrel Bearing Temp Check", "frequency": "Daily", "category": "Mechanical"},
        ],
    },
    "Cassette Leveller (HR-CTL)": {
        "line": "HR-CTL Line", "zone": "Mid (Cassette Leveller)",
        "criticality": "Critical",
        "params": {
            "Roller Bearing Temp (°C)": {"unit": "°C", "alarm_high": 75, "alarm_low": None, "normal_range": (20, 65)},
            "Delta T (°C)": {"unit": "°C", "alarm_high": 20, "alarm_low": None, "normal_range": (0, 15)},
            "Leveller Roll Gap (mm)": {"unit": "mm", "alarm_high": None, "alarm_low": None, "normal_range": (0.1, 8.0)},
            "Hydraulic Cassette Pressure (bar)": {"unit": "bar", "alarm_high": 250, "alarm_low": 80, "normal_range": (100, 220)},
        },
        "pm_tasks": [
            {"task": "Leveller Roll Scale/Buildup Inspection", "frequency": "Shift", "category": "Mechanical", "loto": True},
            {"task": "Cassette Alignment (Shim Check)", "frequency": "Weekly", "category": "Mechanical", "loto": True},
            {"task": "Hydraulic Pack Pressure Check", "frequency": "Weekly", "category": "Hydraulic"},
            {"task": "Roll Bearing Grease", "frequency": "Monthly", "category": "Mechanical"},
        ],
    },
    "Flying Shear (HR-CTL)": {
        "line": "HR-CTL Line", "zone": "Exit (Flying Shear / Stacker)",
        "criticality": "High",
        "params": {
            "Blade Gap Deviation (mm)": {"unit": "mm", "alarm_high": 0.5, "alarm_low": None, "normal_range": (0.05, 0.4)},
            "Shear Cycle Count": {"unit": "cycles", "alarm_high": 50000, "alarm_low": None, "normal_range": (0, 45000)},
            "Encoder Position Error (pulses)": {"unit": "pulses", "alarm_high": 10, "alarm_low": None, "normal_range": (0, 5)},
        },
        "pm_tasks": [
            {"task": "Blade Gap Measurement", "frequency": "Daily", "category": "Mechanical"},
            {"task": "Encoder Calibration Check", "frequency": "Monthly", "category": "Electrical"},
            {"task": "Blade Change / Edge Condition Check", "frequency": "Per Coil Batch", "category": "Mechanical", "loto": True},
        ],
    },
    "Air Cushion Stacker (HR-CTL)": {
        "line": "HR-CTL Line", "zone": "Exit (Flying Shear / Stacker)",
        "criticality": "Medium",
        "params": {
            "Air Cushion Pressure (bar)": {"unit": "bar", "alarm_high": 8, "alarm_low": 2, "normal_range": (3, 7)},
            "Stack Height Sensor (mm)": {"unit": "mm", "alarm_high": 1800, "alarm_low": None, "normal_range": (0, 1600)},
        },
        "pm_tasks": [
            {"task": "Air Nozzle Cleaning", "frequency": "Weekly", "category": "Mechanical"},
            {"task": "Cushion Pressure Valve Check", "frequency": "Monthly", "category": "Mechanical"},
        ],
    },
    "Slitter Head (HR Slitting)": {
        "line": "HR Slitting Line", "zone": "Mid (Slitter Head)",
        "criticality": "Critical",
        "params": {
            "Knife Overlap (mm)": {"unit": "mm", "alarm_high": 2.5, "alarm_low": 0.1, "normal_range": (0.3, 2.0)},
            "Arbor Bearing Temp (°C)": {"unit": "°C", "alarm_high": 80, "alarm_low": None, "normal_range": (20, 65)},
            "Strip Tension (kN)": {"unit": "kN", "alarm_high": 120, "alarm_low": 10, "normal_range": (20, 100)},
        },
        "pm_tasks": [
            {"task": "Slitter Knife Nick/Chip Inspection (Per Coil)", "frequency": "Per Coil", "category": "Mechanical", "loto": True},
            {"task": "Knife Arbor Bearing Lubrication", "frequency": "Weekly", "category": "Mechanical"},
            {"task": "Spacer/Ring Inspection for Telescoping", "frequency": "Weekly", "category": "Mechanical"},
        ],
    },
    "Tension Bridle (HR Slitting)": {
        "line": "HR Slitting Line", "zone": "Entry (Uncoiler/Bridle)",
        "criticality": "Medium",
        "params": {
            "Bridle Roll Pressure (bar)": {"unit": "bar", "alarm_high": 150, "alarm_low": 20, "normal_range": (40, 120)},
            "Strip Speed Deviation (%)": {"unit": "%", "alarm_high": 5, "alarm_low": None, "normal_range": (0, 4)},
        },
        "pm_tasks": [
            {"task": "Bridle Roll Nip Pressure Check", "frequency": "Daily", "category": "Mechanical"},
            {"task": "VFD Drive Fan Clean", "frequency": "Monthly", "category": "Electrical"},
        ],
    },
    "Recoiler (HR Slitting)": {
        "line": "HR Slitting Line", "zone": "Exit (Recoiler / Scrap Chopper)",
        "criticality": "High",
        "params": {
            "Mandrel Torque % (Recoiler)": {"unit": "%", "alarm_high": 85, "alarm_low": None, "normal_range": (0, 80)},
            "Telescoping Deviation (mm)": {"unit": "mm", "alarm_high": 5, "alarm_low": None, "normal_range": (0, 3)},
        },
        "pm_tasks": [
            {"task": "Mandrel Expansion Jaw Lubrication", "frequency": "Shift", "category": "Mechanical"},
            {"task": "Coil Telescoping Check Post-Recoil", "frequency": "Per Coil", "category": "Mechanical"},
        ],
    },
    "Scrap Chopper (HR Slitting)": {
        "line": "HR Slitting Line", "zone": "Exit (Recoiler / Scrap Chopper)",
        "criticality": "Medium",
        "params": {
            "Blade Condition Score (1-5)": {"unit": "score", "alarm_high": None, "alarm_low": 2, "normal_range": (3, 5)},
        },
        "pm_tasks": [
            {"task": "Chopper Blade Edge Inspection", "frequency": "Daily", "category": "Mechanical", "loto": True},
            {"task": "Drive Belt Tension Check", "frequency": "Weekly", "category": "Mechanical"},
        ],
    },
    "Skin Pass Mill (CR)": {
        "line": "CR Processing Facility", "zone": "Entry (Skin Pass Mill)",
        "criticality": "Critical",
        "params": {
            "Roll Force (kN)": {"unit": "kN", "alarm_high": 8000, "alarm_low": 500, "normal_range": (1000, 7000)},
            "Elongation % Actual vs Setpoint": {"unit": "%", "alarm_high": 2.0, "alarm_low": None, "normal_range": (0.0, 1.5)},
            "Work Roll Surface Roughness (Ra)": {"unit": "µm Ra", "alarm_high": 2.5, "alarm_low": None, "normal_range": (0.5, 2.0)},
        },
        "pm_tasks": [
            {"task": "Work Roll Surface Inspection (Skin Pass)", "frequency": "Daily", "category": "Mechanical"},
            {"task": "Roll Change Schedule Check", "frequency": "Weekly", "category": "Mechanical"},
            {"task": "Roll Force Calibration", "frequency": "Monthly", "category": "Mechanical"},
        ],
    },
    "Robotic Tool Setup (CR 2024)": {
        "line": "CR Processing Facility", "zone": "Mid (Inspection)",
        "criticality": "High",
        "params": {
            "Servo Position Error (mm)": {"unit": "mm", "alarm_high": 0.3, "alarm_low": None, "normal_range": (0.0, 0.2)},
            "Servo Torque % (All Axes)": {"unit": "%", "alarm_high": 90, "alarm_low": None, "normal_range": (10, 75)},
            "TCP Repeatability (mm)": {"unit": "mm", "alarm_high": 0.15, "alarm_low": None, "normal_range": (0.0, 0.10)},
        },
        "pm_tasks": [
            {"task": "Servo Torque Check (All Axes)", "frequency": "Quarterly", "category": "Electrical"},
            {"task": "PLC Laser Sensor Calibration", "frequency": "Monthly", "category": "Electrical"},
            {"task": "Robot Arm Cable Harness Inspection", "frequency": "Monthly", "category": "Electrical"},
            {"task": "TCP Tool Calibration Verification", "frequency": "Weekly", "category": "Electrical"},
        ],
    },
    "Inspection & Parting Line (CR)": {
        "line": "CR Processing Facility", "zone": "Exit (Parting Line)",
        "criticality": "Medium",
        "params": {
            "Parting Shear Gap (mm)": {"unit": "mm", "alarm_high": 0.6, "alarm_low": None, "normal_range": (0.1, 0.5)},
        },
        "pm_tasks": [
            {"task": "Parting Blade Condition Check", "frequency": "Daily", "category": "Mechanical", "loto": True},
            {"task": "Inspection Camera Lens Clean", "frequency": "Weekly", "category": "Electrical"},
        ],
    },
}

MACHINE_NAMES = list(MACHINES.keys())

# ── Failure Code Registry ─────────────────────────────────────────────────────
FAILURE_CODES = {
    # Mechanical
    "ME-01": {"desc": "Leveller Roll Spalling",         "category": "Mechanical", "machine": "Cassette Leveller (HR-CTL)"},
    "ME-02": {"desc": "Mandrel Jaw Slippage",           "category": "Mechanical", "machine": "Uncoiler (HR-CTL)"},
    "ME-03": {"desc": "Slitter Knife Chip/Nick",        "category": "Mechanical", "machine": "Slitter Head (HR Slitting)"},
    "ME-04": {"desc": "Flying Shear Blade Worn",        "category": "Mechanical", "machine": "Flying Shear (HR-CTL)"},
    "ME-05": {"desc": "Recoiler Telescoping Defect",    "category": "Mechanical", "machine": "Recoiler (HR Slitting)"},
    "ME-06": {"desc": "Skin Pass Work Roll Change",     "category": "Mechanical", "machine": "Skin Pass Mill (CR)"},
    "ME-07": {"desc": "Shim Alignment Deviation",       "category": "Mechanical", "machine": "Cassette Leveller (HR-CTL)"},
    "ME-08": {"desc": "Scrap Chopper Blade Dull",       "category": "Mechanical", "machine": "Scrap Chopper (HR Slitting)"},
    "ME-09": {"desc": "Air Cushion Stacker Nozzle Clog","category": "Mechanical", "machine": "Air Cushion Stacker (HR-CTL)"},
    # Electrical / Automation
    "EE-01": {"desc": "VFD Overcurrent Trip",           "category": "Electrical", "machine": "Tension Bridle (HR Slitting)"},
    "EE-02": {"desc": "PLC Laser Sensor Misread",       "category": "Electrical", "machine": "Robotic Tool Setup (CR 2024)"},
    "EE-03": {"desc": "Servo Position Fault (Robot)",  "category": "Electrical", "machine": "Robotic Tool Setup (CR 2024)"},
    "EE-04": {"desc": "Flying Shear Encoder Fault",     "category": "Electrical", "machine": "Flying Shear (HR-CTL)"},
    "EE-05": {"desc": "Stacker Sensor Misalignment",    "category": "Electrical", "machine": "Air Cushion Stacker (HR-CTL)"},
    # Hydraulic/Pneumatic
    "HY-01": {"desc": "Hydraulic Pack Pressure Drop",  "category": "Hydraulic/Pneumatic",  "machine": "Cassette Leveller (HR-CTL)"},
    "HY-02": {"desc": "Mandrel Expansion Slippage",     "category": "Hydraulic/Pneumatic",  "machine": "Uncoiler (HR-CTL)"},
    "HY-03": {"desc": "Cassette Clamp Cylinder Leak",  "category": "Hydraulic/Pneumatic",  "machine": "Cassette Leveller (HR-CTL)"},
    # Performance Degradation
    "PD-01": {"desc": "Speed Loss Out of Spec",         "category": "Performance Degradation","machine": "Tension Bridle (HR Slitting)"},
    "PD-02": {"desc": "Yield Decline / Quality Drop",   "category": "Performance Degradation","machine": "Flying Shear (HR-CTL)"},
    # Intermittent
    "IN-01": {"desc": "Random Sensor Dropouts",         "category": "Intermittent",           "machine": "Robotic Tool Setup (CR 2024)"},
    "IN-02": {"desc": "Unexplained Controller Reset",   "category": "Intermittent",           "machine": "Cassette Leveller (HR-CTL)"},
    # Surface Degradation
    "SD-01": {"desc": "Work Roll Erosion / Spalling",   "category": "Surface Degradation",    "machine": "Skin Pass Mill (CR)"},
    "SD-02": {"desc": "Conveyor Belt Wear/Corrosion",   "category": "Surface Degradation",    "machine": "Air Cushion Stacker (HR-CTL)"},
    # Process
    "PR-01": {"desc": "Strip Breakage",                 "category": "Process",    "machine": "Slitter Head (HR Slitting)"},
    "PR-02": {"desc": "Coil Telescoping",               "category": "Process",    "machine": "Recoiler (HR Slitting)"},
    "PR-03": {"desc": "Camber / Flatness Deviation",   "category": "Process",    "machine": "Cassette Leveller (HR-CTL)"},
    # Planned
    "PL-01": {"desc": "Planned Knife Change",           "category": "Planned",    "machine": "Slitter Head (HR Slitting)"},
    "PL-02": {"desc": "Scheduled PM",                   "category": "Planned",    "machine": "All"},
}

FAILURE_CODE_LIST = list(FAILURE_CODES.keys())
FAILURE_CATEGORIES = [
    "Mechanical", "Electrical", "Hydraulic/Pneumatic", 
    "Performance Degradation", "Intermittent", "Surface Degradation", 
    "Process", "Planned"
]

# ── Machine Status Options ────────────────────────────────────────────────────
MACHINE_STATUS_OPTIONS = [
    "Running",
    "Planned Stop",
    "Breakdown - Mechanical",
    "Breakdown - Electrical",
    "Breakdown - Hydraulic/Pneumatic",
    "Breakdown - Performance Degradation",
    "Breakdown - Intermittent",
    "Breakdown - Surface Degradation",
    "Breakdown - Process",
    "PM In Progress",
    "Idle / No Production",
]

# ── PM Frequency Map (hours) ──────────────────────────────────────────────────
PM_FREQUENCY_HOURS = {
    "Per Coil":       8,
    "Per Coil Batch": 16,
    "Shift":          8,
    "Daily":          24,
    "Weekly":         168,
    "Monthly":        720,
    "Quarterly":      2160,
}

# ── Master Roster Sample ──────────────────────────────────────────────────────
MASTER_ROSTER = [
    # Shift A - Morning
    {"employee_id": "EMP-101", "name": "Rajesh Kumar",      "role": "Operator",       "shift": "A - Morning", "line": "HR-CTL Line",           "zone": "Entry (Uncoiler)"},
    {"employee_id": "EMP-102", "name": "Suresh Mahanta",    "role": "Operator",       "shift": "A - Morning", "line": "HR-CTL Line",           "zone": "Mid (Cassette Leveller)"},
    {"employee_id": "EMP-103", "name": "Prabhat Nayak",     "role": "Operator",       "shift": "A - Morning", "line": "HR-CTL Line",           "zone": "Exit (Flying Shear / Stacker)"},
    {"employee_id": "EMP-104", "name": "Deepak Sahu",       "role": "Operator",       "shift": "A - Morning", "line": "HR Slitting Line",      "zone": "Mid (Slitter Head)"},
    {"employee_id": "EMP-105", "name": "Manoj Behera",      "role": "Operator",       "shift": "A - Morning", "line": "HR Slitting Line",      "zone": "Exit (Recoiler / Scrap Chopper)"},
    {"employee_id": "EMP-106", "name": "Amit Dash",         "role": "Operator",       "shift": "A - Morning", "line": "CR Processing Facility","zone": "Entry (Skin Pass Mill)"},
    {"employee_id": "EMP-S01", "name": "Sanjay Tripathy",   "role": "Supervisor",     "shift": "A - Morning", "line": "All",                   "zone": "All"},
    {"employee_id": "EMP-M01", "name": "Girish Panda",      "role": "Maint. Tech",    "shift": "A - Morning", "line": "All",                   "zone": "All"},
    # Shift B - Afternoon
    {"employee_id": "EMP-201", "name": "Santosh Jena",      "role": "Operator",       "shift": "B - Afternoon","line": "HR-CTL Line",          "zone": "Entry (Uncoiler)"},
    {"employee_id": "EMP-202", "name": "Ravi Pradhan",      "role": "Operator",       "shift": "B - Afternoon","line": "HR-CTL Line",          "zone": "Mid (Cassette Leveller)"},
    {"employee_id": "EMP-203", "name": "Umesh Biswal",      "role": "Operator",       "shift": "B - Afternoon","line": "HR-CTL Line",          "zone": "Exit (Flying Shear / Stacker)"},
    {"employee_id": "EMP-204", "name": "Tapan Mohanty",     "role": "Operator",       "shift": "B - Afternoon","line": "HR Slitting Line",     "zone": "Mid (Slitter Head)"},
    {"employee_id": "EMP-205", "name": "Nikhil Samal",      "role": "Operator",       "shift": "B - Afternoon","line": "HR Slitting Line",     "zone": "Exit (Recoiler / Scrap Chopper)"},
    {"employee_id": "EMP-206", "name": "Pradeep Kar",       "role": "Operator",       "shift": "B - Afternoon","line": "CR Processing Facility","zone": "Entry (Skin Pass Mill)"},
    {"employee_id": "EMP-S02", "name": "Hemant Mishra",     "role": "Supervisor",     "shift": "B - Afternoon","line": "All",                  "zone": "All"},
    {"employee_id": "EMP-M02", "name": "Bibhu Routray",     "role": "Maint. Tech",    "shift": "B - Afternoon","line": "All",                  "zone": "All"},
    # Shift C - Night
    {"employee_id": "EMP-301", "name": "Akash Sethy",       "role": "Operator",       "shift": "C - Night",   "line": "HR-CTL Line",           "zone": "Entry (Uncoiler)"},
    {"employee_id": "EMP-302", "name": "Subrat Nanda",      "role": "Operator",       "shift": "C - Night",   "line": "HR-CTL Line",           "zone": "Mid (Cassette Leveller)"},
    {"employee_id": "EMP-303", "name": "Lingaraj Das",      "role": "Operator",       "shift": "C - Night",   "line": "HR-CTL Line",           "zone": "Exit (Flying Shear / Stacker)"},
    {"employee_id": "EMP-304", "name": "Surendra Sahoo",    "role": "Operator",       "shift": "C - Night",   "line": "HR Slitting Line",      "zone": "Mid (Slitter Head)"},
    {"employee_id": "EMP-305", "name": "Prasanta Swain",    "role": "Operator",       "shift": "C - Night",   "line": "HR Slitting Line",      "zone": "Exit (Recoiler / Scrap Chopper)"},
    {"employee_id": "EMP-306", "name": "Bikash Pattnaik",   "role": "Operator",       "shift": "C - Night",   "line": "CR Processing Facility","zone": "Entry (Skin Pass Mill)"},
    {"employee_id": "EMP-S03", "name": "Dilip Mahapatra",   "role": "Supervisor",     "shift": "C - Night",   "line": "All",                   "zone": "All"},
    {"employee_id": "EMP-M03", "name": "Ramesh Nayak",      "role": "Maint. Tech",    "shift": "C - Night",   "line": "All",                   "zone": "All"},
]
