import os
import pycdlib
import shutil
import tempfile

def create_grub_iso(source_path, iso_name, grub_cfg_content, boot_mode="both"):
    """
    Create bootable ISO with GRUB for custom OS
    boot_mode: "mbr", "efi", or "both"
    """
    iso_path = os.path.join("output_isos", iso_name)
    os.makedirs("output_isos", exist_ok=True)
    
    iso = pycdlib.PyCdlib()
    
    # ISO9660 + Joliet + Rock Ridge for Unix permissions
    iso.new(
        interchange_level=4,
        joliet=3,
        rock_ridge='1.10',
        vol_ident='CUSTOM_OS',
        publisher='PyRufus',
        application_id='GRUB_BOOT'
    )
    
    # Add GRUB boot files for MBR (BIOS)
    if boot_mode in ["mbr", "both"]:
        # Create boot/grub/i386-pc structure
        grub_dir = "boot/grub/i386-pc"
        iso.add_directory(directory=f'/{grub_dir.upper()};1', rr_name='boot/grub/i386-pc')
        
        # Add core.img (user must provide this in source or we embed a placeholder)
        # For real use, copy from GRUB installation
        core_src = os.path.join(source_path, "boot/grub/i386-pc/core.img")
        if os.path.exists(core_src):
            iso.add_file(core_src, f'/{grub_dir.upper()}/CORE.IMG;1', rr_name='boot/grub/i386-pc/core.img')
    
    # Add GRUB EFI files for UEFI
    if boot_mode in ["efi", "both"]:
        efi_dir = "boot/grub/x86_64-efi"
        iso.add_directory(directory=f'/{efi_dir.upper()};1', rr_name='boot/grub/x86_64-efi')
        
        efi_src = os.path.join(source_path, "boot/grub/x86_64-efi/grubx64.efi")
        if os.path.exists(efi_src):
            iso.add_file(efi_src, f'/{efi_dir.upper()}/GRUBX64.EFI;1', rr_name='boot/grub/x86_64-efi/grubx64.efi')
    
    # Add grub.cfg
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg') as tmp:
        tmp.write(grub_cfg_content)
        tmp_cfg = tmp.name
    
    iso.add_file(tmp_cfg, '/BOOT/GRUB/GRUB.CFG;1', rr_name='boot/grub/grub.cfg')
    os.unlink(tmp_cfg)
    
    # Add user's source files recursively
    if os.path.isdir(source_path):
        for root, dirs, files in os.walk(source_path):
            rel_path = os.path.relpath(root, source_path)
            for file in files:
                # Skip GRUB files we already added
                if 'grub' in file.lower() and 'grub.cfg' not in file:
                    continue
                    
                full_path = os.path.join(root, file)
                if rel_path == '.':
                    iso_path_name = f'/{file.upper()};1'
                    rr_name = file
                else:
                    clean_rel = rel_path.replace(os.sep, '/').upper()
                    iso_path_name = f'/{clean_rel}/{file.upper()};1'
                    rr_name = f"{rel_path}/{file}"
                
                try:
                    iso.add_file(full_path, iso_path_name, rr_name=rr_name)
                except Exception as e:
                    print(f"[ISO] Skipped {file}: {e}")
    
    # El Torito boot setup for MBR
    if boot_mode in ["mbr", "both"] and os.path.exists(core_src):
        boot_catalog = '/BOOT.CAT;1'
        iso.add_boot_catalog(boot_catalog, boot_info_table=True)
        iso.add_el_torito_entry(
            boot_entry=pycdlib.ElToritoEntry(
                boot_catalog_loc=boot_catalog,
                boot_file='/BOOT/GRUB/I386-PC/CORE.IMG;1',
                platform_id=pycdlib.ElToritoPlatform.X86,
                emu_type=pycdlib.ElToritoEmulationType.NO_EMULATION,
                boot_info_table=True,
                load_segment=0,
                initial_entry_count=1
            )
        )
    
    iso.write(iso_path)
    iso.close()
    return iso_path
