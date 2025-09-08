#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import datetime, os, sys, subprocess, termios, tty

LOGFILE = "KEYLOGGER_log.txt"

ASCII_BANNER = r"""
  _  __  ____  _  __    _      _                 
 | |/ / |  _ \| |/ /   | |    | |                
 | ' /  | |_) | ' / ___| | ___| |__   ___  _ __  
 |  <   |  _ <|  < / _ \ |/ __| '_ \ / _ \| '_ \ 
 | . \  | |_) | . \  __/ | (__| | | | (_) | | | |
 |_|\_\ |____/|_|\_\___|_|\___|_| |_|\___/|_| |_|
"""
ASCII_SUBTITLE = "KEYLOGGER - Simple Keylogger Tool"

def masked_input(prompt=""):
    """Reads input from terminal, shows * for each key typed."""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        chars = []
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                sys.stdout.write("\n")
                break
            elif ch == "\x7f":  # Backspace
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
            else:
                chars.append(ch)
                sys.stdout.write("*")
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return "".join(chars)

class KeyLoggerApp:
    def __init__(self, root):
        self.root = root
        self.demo_inputs_done = False
        root.title("KEYLOGGER — Educational Demo (Visible & Consented)")
        self.recording = False

        tk.Label(root, text="KEYLOGGER", font=("Helvetica", 24, "bold"),
                 fg="white", bg="#333", padx=10, pady=8).pack(fill="x")
        tk.Label(root, text="Simple Keylogger Tool",
                 font=("Helvetica", 14), fg="black").pack(pady=(0, 10))

        info = ("This is an educational, consent-driven demo.\n"
                "It records keystrokes ONLY while this window is focused and consent is given.\n"
                "Do NOT use on other people's machines without permission.")
        tk.Label(root, text=info, wraplength=600, justify="left").pack(pady=8)

        self.consent_var = tk.IntVar()
        self.consent_cb = tk.Checkbutton(
            root,
            text="I give explicit written consent to record keystrokes (educational/testing only).",
            variable=self.consent_var,
            command=self.on_consent_change,
            wraplength=600,
            justify="left"
        )
        self.consent_cb.pack(pady=6)

        frame = tk.Frame(root)
        frame.pack(pady=6)
        self.start_btn = tk.Button(frame, text="Start Recording", state="disabled", command=self.start_recording)
        self.start_btn.pack(side="left", padx=6)
        self.stop_btn = tk.Button(frame, text="Stop Recording", state="disabled", command=self.stop_recording)
        self.stop_btn.pack(side="left", padx=6)
        self.clear_btn = tk.Button(frame, text="Clear Log", command=self.clear_log)
        self.clear_btn.pack(side="left", padx=6)
        self.open_btn = tk.Button(root, text="Open Log File", command=self.open_log)
        self.open_btn.pack(pady=6)

        self.status = tk.Label(root, text="Status: Idle", fg="black")
        self.status.pack(pady=6)

        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write("\n" + "="*60 + "\n")
            f.write("KEYLOGGER session created: " + datetime.datetime.now().isoformat() + "\n")
            f.write("="*60 + "\n")

        root.bind("<FocusOut>", self.on_focus_out)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_demo_inputs(self):
        print("\nLOGIN DETAILS >>> ")
        demo_username = input("Username: ")
        demo_secret = masked_input("Password: ")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write("==== DEMO INPUT START ====\n")
            f.write(f"Username: {demo_username}\n")
            f.write(f"Password: {demo_secret}\n")
            f.write("==== DEMO INPUT END ====\n")

    def on_consent_change(self):
        try:
            if self.consent_var.get():
                if not self.demo_inputs_done:
                    self.get_demo_inputs()
                    self.demo_inputs_done = True
                if self.start_btn.winfo_exists():
                    self.start_btn.config(state="normal")
            else:
                if self.recording:
                    self.stop_recording()
                if self.start_btn.winfo_exists():
                    self.start_btn.config(state="disabled")
                if self.stop_btn.winfo_exists():
                    self.stop_btn.config(state="disabled")
        except tk.TclError:
            pass  # GUI already closed

    def start_recording(self):
        if not self.consent_var.get():
            messagebox.showwarning("Consent required", "Please check the consent box before starting.")
            return
        self.recording = True
        self.root.bind("<Key>", self.on_key)
        self.status.config(text="Status: Recording (window must be focused)", fg="red")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write("--- Recording started: " + datetime.datetime.now().isoformat() + " ---\n")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.root.unbind("<Key>")
            self.status.config(text="Status: Idle", fg="black")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            with open(LOGFILE, "a", encoding="utf-8") as f:
                f.write("--- Recording stopped: " + datetime.datetime.now().isoformat() + " ---\n")

    def on_focus_out(self, event):
        if self.recording:
            self.stop_recording()
            messagebox.showinfo("Focus lost", "Window lost focus — recording stopped automatically.")

    def on_key(self, event):
        if not self.recording:
            return
        ts = datetime.datetime.now().isoformat()
        keysym = event.keysym
        char = event.char if event.char and event.char.isprintable() else ""
        line = f"{ts}\tkeysym:{keysym}\tchar:{char}\n"
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(line)

    def clear_log(self):
        if messagebox.askyesno("Clear log", "Erase the log file contents?"):
            open(LOGFILE, "w", encoding="utf-8").close()
            messagebox.showinfo("Cleared", "Log file cleared.")

    def open_log(self):
        path = os.path.abspath(LOGFILE)
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception:
            messagebox.showinfo("Log file", f"Log saved to: {path}")

    def on_close(self):
        try:
            if self.recording:
                if not messagebox.askyesno("Quit", "Recording is active. Stop and quit?"):
                    return
                self.stop_recording()
            self.root.destroy()
        except tk.TclError:
            pass
        finally:
            print("Goodbye")

if __name__ == "__main__":
    print(ASCII_BANNER)
    print(ASCII_SUBTITLE.center(60, " "))
    root = tk.Tk()
    app = KeyLoggerApp(root)
    root.mainloop()
