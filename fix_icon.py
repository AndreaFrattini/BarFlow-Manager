#!/usr/bin/env python3
"""
Script per creare un'icona .ico valida da un file PNG
"""
import sys
from pathlib import Path
from PIL import Image

def create_ico_from_png(png_path, ico_path):
    """Crea un file .ico valido da un PNG"""
    try:
        # Apri l'immagine PNG
        img = Image.open(png_path)
        
        # Converti in RGBA se necessario
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Crea diverse dimensioni per l'icona (standard Windows)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Crea le immagini ridimensionate
        icon_images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Salva come .ico
        icon_images[0].save(ico_path, format='ICO', sizes=[(image.width, image.height) for image in icon_images])
        
        print(f"✅ Icona .ico creata con successo: {ico_path}")
        return True
        
    except Exception as e:
        print(f"❌ Errore nella creazione dell'icona: {e}")
        return False

def main():
    """Funzione principale"""
    # Percorsi
    script_dir = Path(__file__).parent
    icons_dir = script_dir / "barflow" / "resources" / "icons"
    png_path = icons_dir / "icon.png"
    ico_path = icons_dir / "icon.ico"
    
    print("🔧 Creazione icona .ico valida...")
    print(f"   PNG source: {png_path}")
    print(f"   ICO target: {ico_path}")
    
    if not png_path.exists():
        print(f"❌ File PNG non trovato: {png_path}")
        return False
    
    success = create_ico_from_png(png_path, ico_path)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)