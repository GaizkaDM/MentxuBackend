"""
Script para compilar los archivos .po a .mo
Ejecutar: python compile_translations.py
"""
import os
import struct
import array


def compile_po_to_mo(po_path, mo_path):
    """Compila un archivo .po a .mo (formato binario gettext)"""
    
    messages = {}
    
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_msgid = None
    current_msgstr = None
    reading = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('msgid '):
            if current_msgid is not None and current_msgstr is not None:
                if current_msgid:  # Skip empty msgid (header)
                    messages[current_msgid] = current_msgstr
            value = line[6:].strip('"')
            current_msgid = value
            current_msgstr = None
            reading = 'msgid'
        elif line.startswith('msgstr '):
            value = line[7:].strip('"')
            current_msgstr = value
            reading = 'msgstr'
        elif line.startswith('"') and line.endswith('"'):
            value = line.strip('"')
            if reading == 'msgid':
                current_msgid += value
            elif reading == 'msgstr':
                current_msgstr += value
        elif line == '' or line.startswith('#'):
            if current_msgid is not None and current_msgstr is not None:
                if current_msgid:
                    messages[current_msgid] = current_msgstr
            if line == '':
                current_msgid = None
                current_msgstr = None
                reading = None
    
    # Don't forget the last entry
    if current_msgid is not None and current_msgstr is not None:
        if current_msgid:
            messages[current_msgid] = current_msgstr
    
    # Generate .mo file
    # Sort keys
    keys = sorted(messages.keys())
    
    # MO file format
    offsets = []
    ids = b''
    strs = b''
    
    for key in keys:
        key_bytes = key.encode('utf-8')
        value_bytes = messages[key].encode('utf-8')
        
        offsets.append((len(key_bytes), len(ids), len(value_bytes), len(strs)))
        ids += key_bytes + b'\x00'
        strs += value_bytes + b'\x00'
    
    # Header
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    
    # The .mo format
    output = []
    # Magic number
    output.append(struct.pack('I', 0x950412de))
    # Version
    output.append(struct.pack('I', 0))
    # Number of strings
    output.append(struct.pack('I', len(keys)))
    # Offset of table with original strings
    output.append(struct.pack('I', 7 * 4))
    # Offset of table with translation strings
    output.append(struct.pack('I', 7 * 4 + len(keys) * 8))
    # Size of hashing table (0 = no hashing)
    output.append(struct.pack('I', 0))
    # Offset of hashing table
    output.append(struct.pack('I', 0))
    
    # Table of original strings
    for length, offset, _, _ in offsets:
        output.append(struct.pack('II', length, keystart + offset))
    
    # Table of translated strings
    for _, _, length, offset in offsets:
        output.append(struct.pack('II', length, valuestart + offset))
    
    output.append(ids)
    output.append(strs)
    
    with open(mo_path, 'wb') as f:
        for chunk in output:
            f.write(chunk)
    
    print(f"  ✅ Compilado: {mo_path} ({len(messages)} cadenas)")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(base_dir, 'app', 'translations')
    
    for lang in ['es', 'eu', 'en']:
        po_path = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_path = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_path):
            print(f"Compilando {lang}...")
            compile_po_to_mo(po_path, mo_path)
        else:
            print(f"  ⚠️ No encontrado: {po_path}")
    
    print("\n✅ ¡Compilación completada!")


if __name__ == '__main__':
    main()
