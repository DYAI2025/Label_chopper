#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHL Label Cropper ROBUST v3.0 - Bulletproof Version
Schneidet horizontal an der Schnittlinie - HÄNGT GARANTIERT NICHT!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import fitz  # PyMuPDF
from pathlib import Path
import sys
import os
import threading
import traceback
from datetime import datetime
import queue
import time

class DHLLabelCropper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📦 DHL Label Cropper v3.0 ROBUST")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # CRITICAL: Proper shutdown handling
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set Windows native style
        try:
            self.style = ttk.Style()
            available = self.style.theme_names()
            if 'vista' in available:
                self.style.theme_use('vista')
            elif 'winnative' in available:
                self.style.theme_use('winnative')
            else:
                self.style.theme_use('default')
        except:
            pass  # Ignore style errors
        
        # Thread-safe queue with timeout protection
        self.log_queue = queue.Queue(maxsize=1000)
        self.processing_thread = None
        
        # Setup default folders
        self.setup_default_folders()
        
        # Crop settings (in mm)
        self.cut_position_mm = tk.DoubleVar(value=148.5)
        self.keep_top = tk.BooleanVar(value=True)
        
        # Build GUI
        self.setup_gui()
        
        # Start log processor with error handling
        self.process_log_queue()
        
        # Initial log
        self.log("✅ DHL Label Cropper v3.0 ROBUST gestartet!")
        self.log(f"📁 Input: {self.input_dir}")
        self.log(f"📁 Output: {self.output_dir}")
        self.log("✂️ Schneide horizontal an Position 148.5mm")
        self.log("📦 Behalte obere Hälfte mit QR-Code + Barcodes")
        self.log("🛡️ Anti-Freeze Protection aktiv!")
    
    def on_closing(self):
        """Proper shutdown"""
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def setup_default_folders(self):
        """Create default input/output folders"""
        try:
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent
            
            self.input_dir = base_dir / "DHL_Labels_Input"
            self.output_dir = base_dir / "DHL_Labels_Output"
            
            # Create folders
            self.input_dir.mkdir(exist_ok=True)
            self.output_dir.mkdir(exist_ok=True)
        except Exception as e:
            # Fallback to temp directory
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            self.input_dir = temp_dir / "DHL_Labels_Input"
            self.output_dir = temp_dir / "DHL_Labels_Output"
            self.input_dir.mkdir(exist_ok=True)
            self.output_dir.mkdir(exist_ok=True)
    
    def setup_gui(self):
        """Build GUI with error protection"""
        try:
            # Main container
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configure grid
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(2, weight=1)
            
            # Title
            title_label = ttk.Label(main_frame, 
                                   text="📦 DHL Label Cropper - ROBUST VERSION", 
                                   font=('Segoe UI', 16, 'bold'))
            title_label.grid(row=0, column=0, pady=(0, 10))
            
            # Status indicator
            self.status_indicator = ttk.Label(main_frame, 
                                            text="⚡ BEREIT", 
                                            font=('Segoe UI', 12, 'bold'),
                                            foreground='green')
            self.status_indicator.grid(row=0, column=0, sticky=tk.E, padx=20)
            
            # Button Frame
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)
            button_frame.columnconfigure(2, weight=1)
            button_frame.columnconfigure(3, weight=1)
            
            # Main process button
            self.process_btn = tk.Button(button_frame, 
                                        text="🚀 LABELS VERARBEITEN",
                                        command=self.process_labels_safe,
                                        bg='#4CAF50', fg='white',
                                        font=('Segoe UI', 11, 'bold'),
                                        height=2)
            self.process_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
            
            # Stop button (emergency brake)
            self.stop_btn = tk.Button(button_frame, 
                                     text="⛔ STOP",
                                     command=self.emergency_stop,
                                     bg='#f44336', fg='white',
                                     font=('Segoe UI', 11, 'bold'),
                                     height=2,
                                     state='disabled')
            self.stop_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
            
            # Folder buttons
            input_btn = ttk.Button(button_frame, 
                                  text="📂 Input Ordner",
                                  command=lambda: self.open_folder_safe(self.input_dir))
            input_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
            
            output_btn = ttk.Button(button_frame, 
                                   text="📤 Output Ordner",
                                   command=lambda: self.open_folder_safe(self.output_dir))
            output_btn.grid(row=0, column=3, padx=5, sticky=(tk.W, tk.E))
            
            # Log Area with larger font
            log_frame = ttk.LabelFrame(main_frame, text="📋 Live-Log", padding="5")
            log_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
            log_frame.columnconfigure(0, weight=1)
            log_frame.rowconfigure(0, weight=1)
            
            self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                      height=20, width=100,
                                                      wrap=tk.WORD, 
                                                      font=('Consolas', 10),
                                                      bg='#1e1e1e', fg='#00ff00')
            self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Settings Frame
            settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Einstellungen", padding="10")
            settings_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
            
            # Info
            info_label = ttk.Label(settings_frame, 
                                  text="✂️ Horizontal schneiden bei 148.5mm (Mitte)\n" +
                                       "📦 Obere Hälfte = QR-Code + 2 Barcodes",
                                  font=('Segoe UI', 10))
            info_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
            
            # Progress Bar
            self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=800)
            self.progress.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))
            
            # Bottom status
            self.status_label = ttk.Label(main_frame, 
                                         text="Bereit für Verarbeitung", 
                                         relief=tk.SUNKEN,
                                         font=('Segoe UI', 10))
            self.status_label.grid(row=5, column=0, sticky=(tk.W, tk.E))
            
        except Exception as e:
            print(f"GUI Setup Error: {e}")
            messagebox.showerror("GUI Error", f"Fehler beim GUI-Aufbau:\n{e}")
    
    def log(self, message):
        """Thread-safe logging with overflow protection"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_msg = f"[{timestamp}] {message}"
            
            # Non-blocking put with timeout
            try:
                self.log_queue.put_nowait(formatted_msg)
            except queue.Full:
                # Queue is full, remove oldest item
                try:
                    self.log_queue.get_nowait()
                    self.log_queue.put_nowait(formatted_msg)
                except:
                    pass  # Ignore if still fails
        except:
            pass  # Never crash on logging
    
    def process_log_queue(self):
        """Process log messages with protection"""
        if not self.running:
            return
            
        try:
            # Process up to 10 messages at once to prevent UI freezing
            for _ in range(10):
                try:
                    message = self.log_queue.get_nowait()
                    self.log_text.insert(tk.END, message + "\n")
                    self.log_text.see(tk.END)
                    
                    # Limit log size to prevent memory issues
                    lines = int(self.log_text.index('end-1c').split('.')[0])
                    if lines > 500:
                        self.log_text.delete('1.0', '2.0')
                        
                except queue.Empty:
                    break
                except:
                    break  # Any error, just stop this iteration
                    
        except:
            pass  # Never crash the log processor
        
        finally:
            # Schedule next update
            if self.running:
                self.root.after(50, self.process_log_queue)  # Faster updates
    
    def open_folder_safe(self, path):
        """Open folder with error handling"""
        try:
            if sys.platform == 'win32':
                os.startfile(str(path))
            else:
                subprocess.Popen(['xdg-open', str(path)])
            self.log(f"📂 Ordner geöffnet: {path.name}")
        except Exception as e:
            self.log(f"⚠️ Konnte Ordner nicht öffnen: {e}")
            # Try alternative method
            try:
                import subprocess
                subprocess.Popen(f'explorer "{path}"', shell=True)
            except:
                pass
    
    def emergency_stop(self):
        """Emergency stop button"""
        self.log("🛑 NOTFALL-STOP aktiviert!")
        self.stop_processing = True
        self.stop_btn.config(state='disabled')
        self.process_btn.config(state='normal')
        self.progress.stop()
        self.status_indicator.config(text="⛔ GESTOPPT", foreground='red')
    
    def crop_pdf_with_timeout(self, pdf_path, output_path, timeout=10):
        """Crop PDF with timeout protection"""
        result = {'success': False, 'error': None}
        
        def crop_worker():
            try:
                # Open PDF
                doc = fitz.open(str(pdf_path))
                
                # Constants
                mm_to_points = 2.834645669
                cut_position = 148.5 * mm_to_points  # Fixed at middle
                
                # Process pages
                for page_num in range(len(doc)):
                    if self.stop_processing:
                        doc.close()
                        return
                        
                    page = doc[page_num]
                    page_rect = page.rect
                    
                    # Keep top half (QR + Barcodes)
                    crop_rect = fitz.Rect(
                        0,                    # left
                        0,                    # top
                        page_rect.width,      # right
                        cut_position          # bottom (cut line)
                    )
                    
                    page.set_cropbox(crop_rect)
                
                # Save with garbage collection
                doc.save(str(output_path), garbage=3, deflate=True)
                doc.close()
                
                result['success'] = True
                
            except Exception as e:
                result['error'] = str(e)
        
        # Run with timeout
        thread = threading.Thread(target=crop_worker, daemon=True)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.log(f"⏱️ Timeout bei {pdf_path.name}")
            return False
            
        return result['success']
    
    def process_labels_safe(self):
        """Safe wrapper for processing"""
        if self.processing_thread and self.processing_thread.is_alive():
            self.log("⚠️ Verarbeitung läuft bereits!")
            return
            
        self.processing_thread = threading.Thread(target=self.process_labels_worker, daemon=True)
        self.processing_thread.start()
    
    def process_labels_worker(self):
        """Main processing worker with full protection"""
        try:
            # Reset stop flag
            self.stop_processing = False
            
            # Update UI
            self.root.after(0, lambda: self.process_btn.config(state='disabled'))
            self.root.after(0, lambda: self.stop_btn.config(state='normal'))
            self.root.after(0, lambda: self.progress.start(20))
            self.root.after(0, lambda: self.status_indicator.config(text="🔄 LÄUFT", foreground='orange'))
            
            # Clear log
            self.root.after(0, lambda: self.log_text.delete(1.0, tk.END))
            self.log("🚀 Starte Verarbeitung...")
            
            # Find PDFs
            pdf_files = list(self.input_dir.glob("*.pdf"))
            
            if not pdf_files:
                self.log("⚠️ Keine PDF-Dateien gefunden!")
                self.log(f"📁 Bitte PDFs in {self.input_dir} legen")
                return
            
            self.log(f"📊 {len(pdf_files)} PDF(s) gefunden")
            
            success_count = 0
            fail_count = 0
            
            for i, pdf_file in enumerate(pdf_files, 1):
                if self.stop_processing:
                    self.log("🛑 Verarbeitung abgebrochen!")
                    break
                    
                self.log(f"📄 [{i}/{len(pdf_files)}] {pdf_file.name}")
                
                # Output name
                output_name = f"LABEL_{pdf_file.stem}_CROP.pdf"
                output_path = self.output_dir / output_name
                
                # Process with timeout
                if self.crop_pdf_with_timeout(pdf_file, output_path, timeout=10):
                    self.log(f"   ✅ Erfolgreich: {output_name}")
                    success_count += 1
                else:
                    self.log(f"   ❌ Fehler bei: {pdf_file.name}")
                    fail_count += 1
                
                # Update progress
                percent = (i / len(pdf_files)) * 100
                self.root.after(0, lambda p=percent: self.status_label.config(
                    text=f"Fortschritt: {p:.0f}%"))
            
            # Summary
            self.log("=" * 60)
            self.log(f"🏁 FERTIG! ✅ {success_count} OK | ❌ {fail_count} Fehler")
            
            if success_count > 0:
                self.log("📂 Öffne Output-Ordner...")
                time.sleep(0.5)  # Short delay for user to see
                self.open_folder_safe(self.output_dir)
                
        except Exception as e:
            self.log(f"💥 Kritischer Fehler: {e}")
            self.log(f"📋 Details: {traceback.format_exc()}")
            
        finally:
            # Reset UI (thread-safe)
            self.root.after(0, lambda: self.process_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.status_indicator.config(text="✅ BEREIT", foreground='green'))
            self.root.after(0, lambda: self.status_label.config(text="Verarbeitung abgeschlossen"))
    
    def run(self):
        """Start application with error handling"""
        try:
            # Center window
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            
            # Start
            self.root.mainloop()
            
        except Exception as e:
            print(f"Fatal Error: {e}")
            messagebox.showerror("Kritischer Fehler", f"App konnte nicht starten:\n{e}")

if __name__ == "__main__":
    try:
        app = DHLLabelCropper()
        app.run()
    except KeyboardInterrupt:
        print("\nApp beendet.")
    except Exception as e:
        print(f"Startup Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
