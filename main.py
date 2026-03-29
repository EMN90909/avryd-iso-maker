import os
import sys
import webview
import json
from backend.usb_detector import get_usb_drives
from backend.iso_builder import create_grub_iso
from backend.burner import safe_burn_iso

# Global state
current_session = {}

def get_drives():
    """API: Return USB-only drives"""
    return json.dumps(get_usb_drives())

def start_session():
    """API: Initialize new burn session"""
    import uuid, tempfile
    session_id = str(uuid.uuid4())
    temp_dir = os.path.join("temp", session_id)
    os.makedirs(temp_dir, exist_ok=True)
    current_session[session_id] = {"temp_dir": temp_dir}
    return json.dumps({"session_id": session_id, "temp_dir": temp_dir})

def handle_files(session_id, files_info):
    """API: Save uploaded files to session temp dir"""
    if session_id not in current_session:
        return json.dumps({"error": "Invalid session"})
    
    session = current_session[session_id]
    temp_dir = session["temp_dir"]
    
    # files_info = [{"name": "file.txt", "content": "base64..."}, ...]
    for f in files_info:
        file_path = os.path.join(temp_dir, f["name"])
        # Decode base64 if needed, or handle as text
        with open(file_path, "wb") as out:
            import base64
            out.write(base64.b64decode(f["content"]))
    
    return json.dumps({"status": "saved", "count": len(files_info)})

def build_iso(session_id, iso_name, grub_cfg, boot_mode):
    """API: Create GRUB bootable ISO"""
    if session_id not in current_session:
        return json.dumps({"error": "Invalid session"})
    
    session = current_session[session_id]
    source_dir = session["temp_dir"]
    
    try:
        iso_path = create_grub_iso(source_dir, iso_name, grub_cfg, boot_mode)
        session["iso_path"] = iso_path
        return json.dumps({"status": "success", "iso_path": iso_path})
    except Exception as e:
        return json.dumps({"error": str(e)})

def burn_usb(iso_path, usb_device, partition_scheme):
    """API: Burn ISO to USB"""
    success, message = safe_burn_iso(iso_path, usb_device, partition_scheme)
    return json.dumps({"success": success, "message": message})

def select_existing_iso():
    """API: Open file dialog for existing ISO"""
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select ISO file",
        filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
    )
    root.destroy()
    return json.dumps({"iso_path": file_path if file_path else None})

if __name__ == "__main__":
    # Create API endpoints for JS
    api = {
        "get_drives": get_drives,
        "start_session": start_session,
        "handle_files": handle_files,
        "build_iso": build_iso,
        "burn_usb": burn_usb,
        "select_existing_iso": select_existing_iso
    }
    
    # Launch window
    window = webview.create_window(
        "PyRufus GRUB Edition",
        "frontend/index.html",
        js_api=api,
        width=600,
        height=700,
        resizable=True
    )
    
    print("🚀 Avyrd-bunner starting... (USB-only mode, GRUB support)")
    webview.start(private_mode=False)
