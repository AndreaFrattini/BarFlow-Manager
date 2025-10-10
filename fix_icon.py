#!/usr/bin/env python3
"""
Script per creare un'icona .ico di alta qualità da un file PNG
Genera icone multi-risoluzione con algoritmi di ridimensionamento ottimizzati
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter

def create_high_quality_ico(png_path, ico_path):
    """Crea un file .ico di alta qualità da un PNG con ottimizzazioni avanzate"""
    try:
        print(f"📂 Caricamento immagine sorgente: {png_path}")
        
        # Apri l'immagine PNG
        with Image.open(png_path) as img:
            print(f"   📏 Dimensioni originali: {img.size}")
            print(f"   🎨 Modalità colore: {img.mode}")
            
            # Converti in RGBA se necessario per supportare trasparenza
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
                print("   🔄 Convertito in modalità RGBA")
            
            # Dimensioni standard per icone Windows (ordinate per qualità ottimale)
            # Includiamo anche 96x96 che è usato da Windows per icone di media dimensione
            sizes = [256, 128, 96, 64, 48, 32, 24, 16]
            
            print(f"   🎯 Generazione di {len(sizes)} risoluzioni...")
            
            # Lista per contenere tutte le versioni ridimensionate
            icon_images = []
            
            # Crea versioni ridimensionate per ogni dimensione
            for i, size in enumerate(sizes):
                print(f"   ⚙️  Elaborazione {size}x{size}...", end=" ")
                
                # Ridimensiona con algoritmo LANCZOS (alta qualità)
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                
                # Per dimensioni piccole (<=32px), applica miglioramenti specifici
                if size <= 32:
                    # Leggero sharpen per mantenere dettagli sui piccoli formati
                    resized = resized.filter(ImageFilter.UnsharpMask(
                        radius=0.3,    # Raggio piccolo per evitare artefatti
                        percent=120,   # Incremento moderato
                        threshold=2    # Soglia bassa per preservare gradienti
                    ))
                    print("(con sharpening)")
                elif size <= 64:
                    # Leggero enhancement per dimensioni medie
                    resized = resized.filter(ImageFilter.UnsharpMask(
                        radius=0.5,
                        percent=110,
                        threshold=3
                    ))
                    print("(con enhancement)")
                else:
                    print("(qualità standard)")
                
                icon_images.append(resized)
            
            print(f"   💾 Salvataggio icona .ico...")
            
            # Salva come icona .ico multi-risoluzione
            # La prima immagine è quella principale, le altre vengono aggiunte
            icon_images[0].save(
                ico_path,
                format='ICO',
                sizes=[(size, size) for size in sizes],
                append_images=icon_images[1:]
            )
            
            # Verifica che il file sia stato creato correttamente
            if ico_path.exists():
                file_size = ico_path.stat().st_size
                print(f"✅ Icona .ico creata con successo!")
                print(f"   📁 Percorso: {ico_path}")
                print(f"   📊 Dimensione file: {file_size:,} bytes")
                print(f"   🎯 Risoluzioni incluse: {', '.join(f'{s}x{s}' for s in sizes)}")
                return True
            else:
                print(f"❌ Errore: File .ico non è stato creato")
                return False
                
    except Exception as e:
        print(f"❌ Errore durante la creazione dell'icona: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Funzione principale"""
    print("=" * 70)
    print("  🎨 GENERATORE ICONA ACCOUNTFLOW - QUALITÀ PROFESSIONALE 🎨")
    print("=" * 70)
    
    # Percorsi
    script_dir = Path(__file__).parent
    icons_dir = script_dir / "barflow" / "resources" / "icons"
    png_path = icons_dir / "icon.png"
    ico_path = icons_dir / "icon.ico"
    
    print(f"� Verifica file sorgente...")
    
    if not png_path.exists():
        print(f"❌ File PNG non trovato: {png_path}")
        return False
    
    if not icons_dir.exists():
        print(f"❌ Directory icone non trovata: {icons_dir}")
        return False
    
    print(f"✅ File PNG trovato: {png_path}")
    
    # Backup dell'icona esistente se presente
    if ico_path.exists():
        backup_path = ico_path.with_suffix('.ico.backup')
        # Rimuovi backup esistente se presente
        if backup_path.exists():
            backup_path.unlink()
        ico_path.rename(backup_path)
        print(f"📋 Backup creato: {backup_path}")
    
    success = create_high_quality_ico(png_path, ico_path)
    
    print("=" * 70)
    if success:
        print("🎉 COMPLETATO: Icona di qualità professionale generata con successo!")
        print("   L'icona è ora ottimizzata per tutte le dimensioni Windows standard")
    else:
        print("💥 ERRORE: Impossibile generare l'icona")
        # Ripristina backup se fallisce
        backup_path = ico_path.with_suffix('.ico.backup')
        if backup_path.exists():
            backup_path.rename(ico_path)
            print(f"🔄 Backup ripristinato: {ico_path}")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)