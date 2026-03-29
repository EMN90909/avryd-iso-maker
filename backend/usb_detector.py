import platform
import subprocess
import psutil

def get_usb_drives():
    """Return ONLY removable USB drives (safe from internal disks)"""
    drives = []
    system = platform.system()
    
    try:
        if system == "Windows":
            # Use wmic to get ONLY Removable Media (USB)
            cmd = 'wmic diskdrive where "MediaType=\'Removable Media\'" get DeviceID,Model,Size,Index /format:csv'
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
            lines = [l for l in output.strip().split('\n') if l and 'PHYSICALDRIVE' in l]
            
            for line in lines:
                parts = [p.strip() for p in line.split(',') if p.strip()]
                if len(parts) >= 5:
                    drives.append({
                        'id': f"\\\\.\\PHYSICALDRIVE{parts[4]}",  # \\.\PHYSICALDRIVE1
                        'model': parts[2] or "USB Drive",
                        'size': f"{int(parts[3])//1000000000}GB" if parts[3].isdigit() else parts[3],
                        'index': parts[4]
                    })
                    
        elif system == "Linux":
            # Check /sys/block/*/removable == 1
            for disk in psutil.disk_partitions():
                device = disk.device
                if device.startswith('/dev/sd') or device.startswith('/dev/mmcblk'):
                    name = device.split('/')[-1].replace('p1','').replace('p2','')
                    try:
                        with open(f'/sys/block/{name}/removable', 'r') as f:
                            if f.read().strip() == '1':
                                # Get size
                                size_cmd = f"blockdev --getsize64 {device}"
                                size = subprocess.check_output(size_cmd, shell=True).decode().strip()
                                size_gb = f"{int(size)//1000000000}GB" if size.isdigit() else "Unknown"
                                drives.append({
                                    'id': device,
                                    'model': name.upper(),
                                    'size': size_gb,
                                    'index': name
                                })
                    except:
                        continue
    except Exception as e:
        print(f"[USB Detect Error] {e}")
        
    return drives
