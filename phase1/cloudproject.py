import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

# Default Ubuntu ISO path (Windows)
DEFAULT_ISO_PATH = r"C:\\Users\\mahmo\\Desktop\\Cloud_project\\ubuntu-24.04.2-desktop-amd64.iso"

def validate_size(size_str):
    if not any(size_str.endswith(unit) for unit in ['G', 'M', 'K']) or not size_str[:-1].isdigit():
        raise ValueError("Invalid size format. Use numbers followed by 'G', 'M', or 'K' (e.g., 10G, 500M).")
    return size_str

def validate_int_input(value_str, field_name):
    if not value_str.isdigit():
        raise ValueError(f"Invalid {field_name}. Please enter a whole number.")
    return value_str

def create_virtual_disk(path, size_str, fmt, log_widget):
    try:
        validated_size = validate_size(size_str)
        subprocess.run(["qemu-img", "create", "-f", fmt, path, validated_size], check=True, capture_output=True, text=True)
        message = f"Created virtual disk: {path}"
        gui_log(log_widget, message)
        return True
    except ValueError as ve:
        gui_log(log_widget, f"Error in virtual disk size: {ve}")
        return False
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'qemu-img' command not found. Ensure QEMU is installed and in your system's PATH.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error creating virtual disk: {e.stderr}")
        return False
    except Exception as e:
        gui_log(log_widget, f"An unexpected error occurred during virtual disk creation: {e}")
        return False

def build_vm(disk_path, iso_path, ram_str, cpus_str, boot_iso, fmt, log_widget):
    try:
        validated_ram = validate_int_input(ram_str, "RAM")
        validated_cpus = validate_int_input(cpus_str, "CPU count")
        cmd = ["qemu-system-x86_64", "-drive", f"file={disk_path},format={fmt}",
               "-m", validated_ram, "-smp", validated_cpus, "-cpu", "qemu64"]
        if boot_iso:
            cmd += ["-cdrom", iso_path, "-boot", "d"]
        subprocess.Popen(cmd)
        message = "VM launched."
        gui_log(log_widget, message)
        return True
    except ValueError as ve:
        gui_log(log_widget, f"Error in VM configuration: {ve}")
        return False
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'qemu-system-x86_64' command not found. Ensure QEMU is installed and in your system's PATH.")
        return False
    except Exception as e:
        gui_log(log_widget, f"An unexpected error occurred while launching the VM: {e}")
        return False

def search_and_launch_vm(iso_path, ram, cpus, boot_iso, fmt, log_widget):
    disk_path = filedialog.askopenfilename(title="Select Existing Virtual Disk", filetypes=[("All Files", "*.*")])
    if disk_path:
        if build_vm(disk_path, iso_path, ram, cpus, boot_iso, fmt, log_widget):
            pass # build_vm handles the logging
    else:
        gui_log(log_widget, "No virtual disk selected.")

def gui_log(log_widget, message):
    log_widget.insert(tk.END, message + "\n")
    log_widget.see(tk.END)

def main_gui():
    root = tk.Tk()
    root.title("Cloud Management System")
    tab_control = ttk.Notebook(root)

    # ------------------- VM TAB -------------------
    vm_tab = ttk.Frame(tab_control)
    tab_control.add(vm_tab, text='Virtual Machines')

    disk_path_var = tk.StringVar()
    iso_path_var = tk.StringVar(value=DEFAULT_ISO_PATH)
    size_var = tk.StringVar(value="10G")
    format_var = tk.StringVar(value="qcow2")
    ram_var = tk.StringVar(value="1024")
    cpu_var = tk.StringVar(value="2")

    ttk.Label(vm_tab, text="Virtual Disk:").grid(row=0, column=0, sticky="w")
    tk.Entry(vm_tab, textvariable=disk_path_var, width=40).grid(row=0, column=1)
    tk.Button(vm_tab, text="Browse", command=lambda: disk_path_var.set(filedialog.asksaveasfilename(defaultextension=".qcow2"))).grid(row=0, column=2)

    ttk.Label(vm_tab, text="Size:").grid(row=1, column=0, sticky="w")
    tk.Entry(vm_tab, textvariable=size_var).grid(row=1, column=1, sticky="w")

    ttk.Label(vm_tab, text="Format:").grid(row=2, column=0, sticky="w")
    tk.Entry(vm_tab, textvariable=format_var).grid(row=2, column=1, sticky="w")

    ttk.Button(vm_tab, text="Create Virtual Disk", command=lambda: create_virtual_disk(disk_path_var.get(), size_var.get(), format_var.get(), output_box)).grid(row=3, column=1)

    ttk.Separator(vm_tab).grid(row=4, columnspan=3, pady=10, sticky="ew")

    ttk.Label(vm_tab, text="ISO File:").grid(row=5, column=0, sticky="w")
    tk.Entry(vm_tab, textvariable=iso_path_var, width=40).grid(row=5, column=1)
    tk.Button(vm_tab, text="Browse", command=lambda: iso_path_var.set(filedialog.askopenfilename())).grid(row=5, column=2)

    ttk.Label(vm_tab, text="RAM (MB):").grid(row=6, column=0, sticky="w")
    tk.Entry(vm_tab, textvariable=ram_var).grid(row=6, column=1, sticky="w")

    ttk.Label(vm_tab, text="CPUs:").grid(row=7, column=0, sticky="w")
    tk.Entry(vm_tab, textvariable=cpu_var).grid(row=7, column=1, sticky="w")

    boot_iso_var = tk.BooleanVar(value=True)
    tk.Checkbutton(vm_tab, text="Boot from ISO", variable=boot_iso_var).grid(row=8, column=1, sticky="w")

    ttk.Button(vm_tab, text="Launch VM", command=lambda: build_vm(
        disk_path_var.get(), iso_path_var.get(), ram_var.get(), cpu_var.get(), boot_iso_var.get(), format_var.get(), output_box)).grid(row=9, column=1, pady=10)

    ttk.Button(vm_tab, text="Use Existing Disk", command=lambda: search_and_launch_vm(
        iso_path_var.get(), ram_var.get(), cpu_var.get(), boot_iso_var.get(), format_var.get(), output_box)).grid(row=9, column=2, pady=10)

    # ------------------- Output Box -------------------
    output_box = scrolledtext.ScrolledText(root, height=15, width=100)
    output_box.pack(fill="both", expand=True)

    tab_control.pack(expand=1, fill="both")
    root.mainloop()

def simple_input_popup(prompt):
    win = tk.Toplevel()
    win.title(prompt)
    tk.Label(win, text=prompt).pack()
    entry = tk.Entry(win)
    entry.pack()
    result = []
    def on_ok():
        result.append(entry.get())
        win.destroy()
    tk.Button(win, text="OK", command=on_ok).pack()
    win.wait_window()
    return result[0] if result else ""

if __name__ == '__main__':
    main_gui()