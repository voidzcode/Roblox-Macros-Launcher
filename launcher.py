import customtkinter as ctk
import os
import subprocess
import json
from tkinter import filedialog

# --- CONFIGURATION LOGIC ---
# Safely get the Windows AppData/Local folder to guarantee write permissions
APPDATA_DIR = os.environ.get('LOCALAPPDATA', os.path.expanduser(r'~\AppData\Local'))
CONFIG_FOLDER = os.path.join(APPDATA_DIR, "RobloxMacrosLauncher")
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "launcher_config.json")

# Ensure the folder exists before trying to save
if not os.path.exists(CONFIG_FOLDER):
    os.makedirs(CONFIG_FOLDER)

# Default empty configuration
config_data = {
    "bloxstrap_path": "",
    "scripts_folder": ""
}

# Load saved paths if the config file exists
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
    except json.JSONDecodeError:
        pass

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)


# --- UI SETUP ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.geometry("400x450")
app.title("Roblox Macros")

# Create two separate "screens" (Frames) so we can switch between them
setup_frame = ctk.CTkFrame(app, fg_color="transparent")
main_frame = ctk.CTkFrame(app, fg_color="transparent")


# --- MAIN SCREEN LOGIC ---
def launch_bloxstrap():
    path = config_data.get("bloxstrap_path", "")
    if os.path.exists(path):
        subprocess.Popen([path])
        status_label.configure(text="Bloxstrap launched!", text_color="green")
    else:
        status_label.configure(text="Bloxstrap not found.", text_color="red")

def launch_script(script_path):
    try:
        os.startfile(script_path)
        script_name = os.path.basename(script_path)
        status_label.configure(text=f"Launched: {script_name}", text_color="green")
    except Exception as e:
        status_label.configure(text="Error launching script.", text_color="red")

def load_scripts():
    # Clear any old buttons before loading
    for widget in scroll_frame.winfo_children():
        widget.destroy()
        
    folder = config_data.get("scripts_folder", "")
    if not os.path.exists(folder):
        status_label.configure(text="Scripts folder not found.", text_color="red")
        return
    
    # Generate a button for every .ahk file
    for file in os.listdir(folder):
        if file.endswith(".ahk"):
            full_path = os.path.join(folder, file)
            btn = ctk.CTkButton(
                scroll_frame, 
                text=file, 
                command=lambda p=full_path: launch_script(p),
                height=35,
                font=("Segoe UI", 12),
                fg_color="#2b7a4b", 
                hover_color="#1e5c37"
            )
            btn.pack(pady=5, padx=10, fill="x")

def show_main_menu():
    setup_frame.pack_forget() # Hides the setup screen
    main_frame.pack(fill="both", expand=True) # Shows the main screen
    load_scripts()


# --- SETUP SCREEN LOGIC ---
def ask_bloxstrap():
    # Opens a Windows file explorer dialog
    path = filedialog.askopenfilename(title="Select Bloxstrap Executable", filetypes=[("Executables", "*.exe")])
    if path:
        config_data["bloxstrap_path"] = path
        # Shorten the display text so it fits on screen
        lbl_blox_path.configure(text="..." + path[-30:] if len(path) > 30 else path)

def ask_scripts():
    # Opens a Windows folder explorer dialog
    path = filedialog.askdirectory(title="Select Scripts Folder")
    if path:
        config_data["scripts_folder"] = path
        lbl_script_path.configure(text="..." + path[-30:] if len(path) > 30 else path)

def finish_setup():
    if not config_data["bloxstrap_path"] or not config_data["scripts_folder"]:
        setup_error_label.configure(text="Please select both paths!")
        return
    save_config()
    show_main_menu()


# --- BUILD SETUP SCREEN ---
lbl_setup_title = ctk.CTkLabel(setup_frame, text="First Time Setup", font=("Segoe UI", 24, "bold"))
lbl_setup_title.pack(pady=(40, 20))

btn_ask_blox = ctk.CTkButton(setup_frame, text="1. Select Bloxstrap (.exe)", command=ask_bloxstrap, height=40)
btn_ask_blox.pack(pady=(10, 0))
lbl_blox_path = ctk.CTkLabel(setup_frame, text="Not selected", text_color="gray")
lbl_blox_path.pack(pady=(0, 20))

btn_ask_script = ctk.CTkButton(setup_frame, text="2. Select Scripts Folder", command=ask_scripts, height=40)
btn_ask_script.pack(pady=(10, 0))
lbl_script_path = ctk.CTkLabel(setup_frame, text="Not selected", text_color="gray")
lbl_script_path.pack(pady=(0, 30))

btn_finish = ctk.CTkButton(setup_frame, text="Save & Continue", command=finish_setup, height=40, fg_color="#2b7a4b", hover_color="#1e5c37")
btn_finish.pack(pady=10)

setup_error_label = ctk.CTkLabel(setup_frame, text="", text_color="red")
setup_error_label.pack()


# --- BUILD MAIN SCREEN ---
title = ctk.CTkLabel(main_frame, text="Roblox Macros", font=("Segoe UI", 24, "bold"))
title.pack(pady=(15, 10))

btn_bloxstrap = ctk.CTkButton(main_frame, text="Launch Bloxstrap", command=launch_bloxstrap, height=40, font=("Segoe UI", 14))
btn_bloxstrap.pack(pady=(0, 15), padx=20, fill="x")

scripts_label = ctk.CTkLabel(main_frame, text="AutoHotkey Scripts", font=("Segoe UI", 14, "bold"))
scripts_label.pack(pady=(5, 5))

scroll_frame = ctk.CTkScrollableFrame(main_frame)
scroll_frame.pack(pady=5, padx=20, fill="both", expand=True)

status_label = ctk.CTkLabel(main_frame, text="", font=("Segoe UI", 12))
status_label.pack(pady=10)


# --- STARTUP CHECK ---
blox_path = config_data.get("bloxstrap_path", "")
script_path = config_data.get("scripts_folder", "")

# If both paths exist in the real world, go straight to main menu
if blox_path and os.path.exists(blox_path) and script_path and os.path.exists(script_path):
    show_main_menu()
else:
    # Otherwise, force the setup screen
    setup_frame.pack(fill="both", expand=True)

app.mainloop()