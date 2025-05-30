import os
import time
import paramiko
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

COMMANDS = [
    "terminal length 0",
    "show running-config",
    "show ip interface brief",
    "show interface status",
    "show cdp neighbors",
    "show cdp neighbors detail"
]

def backup_device(ip, username, password, output_folder, log_widget):
    log_widget.insert(tk.END, f"\nConnecting to {ip}...\n")
    log_widget.see(tk.END)
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password, timeout=5)

        shell = client.invoke_shell()
        output = ""
        for cmd in COMMANDS:
            shell.send(cmd + '\n')
            time.sleep(1)
            while shell.recv_ready():
                output += shell.recv(65535).decode(errors='ignore')

        filename = os.path.join(output_folder, f"{ip}_backup.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(output)

        client.close()
        log_widget.insert(tk.END, f"[SUCCESS] Backup done for {ip}\n")
    except Exception as e:
        log_widget.insert(tk.END, f"[ERROR] Failed to connect to {ip}: {e}\n")
    log_widget.see(tk.END)

def start_backup():
    username = entry_user.get().strip()
    password = entry_pass.get().strip()
    output_folder = entry_path.get().strip()
    ips = text_ips.get("1.0", tk.END).strip().splitlines()

    if not username or not password or not output_folder or not ips:
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return

    for ip in ips:
        backup_device(ip.strip(), username, password, output_folder, log_output)

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder)

# === UI SETUP ===
window = tk.Tk()
window.title("Cisco Switch Backup Tool")
window.geometry("600x500")
window.resizable(False, False)

tk.Label(window, text="Username:").pack()
entry_user = tk.Entry(window, width=50)
entry_user.pack()

tk.Label(window, text="Password:").pack()
entry_pass = tk.Entry(window, show="*", width=50)
entry_pass.pack()

tk.Label(window, text="Device IPs (one per line):").pack()
text_ips = scrolledtext.ScrolledText(window, width=60, height=8)
text_ips.pack()

tk.Label(window, text="Output Folder:").pack()
frame_path = tk.Frame(window)
frame_path.pack()
entry_path = tk.Entry(frame_path, width=40)
entry_path.pack(side=tk.LEFT)
btn_browse = tk.Button(frame_path, text="Browse", command=select_folder)
btn_browse.pack(side=tk.LEFT, padx=5)

tk.Button(window, text="Start Backup", command=start_backup, bg="green", fg="white").pack(pady=10)

log_output = scrolledtext.ScrolledText(window, width=70, height=10, bg="black", fg="lime")
log_output.pack(pady=5)

window.mainloop()
