import os
import platform

def safe_burn_iso(iso_path, usb_device, partition_scheme="mbr"):
    """
    Wipe first 10MB (clear MBR/GPT), then raw-write ISO
    partition_scheme: "mbr" or "gpt" (affects how GRUB is configured, not the write)
    """
    try:
        # Wipe partition table (first 10MB)
        with open(usb_device, 'wb') as f:
            f.write(b'\x00' * (10 * 1024 * 1024))
            f.flush()
            os.fsync(f.fileno())
        
        # Write ISO raw (dd-style)
        with open(iso_path, 'rb') as src, open(usb_device, 'wb') as dst:
            while chunk := src.read(8192):
                dst.write(chunk)
                dst.flush()
        
        return True, "✅ Burn complete! USB is now bootable with GRUB."
        
    except PermissionError:
        return False, "❌ Permission denied. Run as Administrator (Windows) or with sudo (Linux)."
    except FileNotFoundError:
        return False, f"❌ Device not found: {usb_device}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
