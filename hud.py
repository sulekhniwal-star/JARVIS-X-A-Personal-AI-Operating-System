import customtkinter as ctk  # type: ignore
import threading
import time
from datetime import datetime
import tkinter as tk


class JarvisOverlay:
    def __init__(self, assistant_callback=None):
        self.assistant_callback = assistant_callback
        self.is_enabled = True
        self.is_listening = False
        self.is_sleeping = False

        # Create overlay window
        self.root = tk.Toplevel()
        self.root.title("JARVIS Assistant")
        self.root.geometry("350x500")
        self.root.configure(bg='#0a0a0a')

        # Position at bottom right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 370
        y = screen_height - 550
        self.root.geometry(f"350x500+{x}+{y}")

        # Make window always on top and semi-transparent
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9)

        self._setup_ui()
        self._start_status_animation()

    def _setup_ui(self):
        # Header with status
        header_frame = tk.Frame(self.root, bg='#0a0a0a')
        header_frame.pack(fill='x', padx=10, pady=5)

        self.status_label = tk.Label(
            header_frame,
            text="🤖 JARVIS - Ready",
            font=("Arial", 12, "bold"),
            fg="#00ffff",
            bg="#0a0a0a"
        )
        self.status_label.pack(side='left')

        # Control buttons
        btn_frame = tk.Frame(header_frame, bg='#0a0a0a')
        btn_frame.pack(side='right')

        self.enable_btn = tk.Button(
            btn_frame,
            text="●",
            font=("Arial", 8),
            fg="#00ff00",
            bg="#1a1a1a",
            command=self.toggle_enable,
            width=3
        )
        self.enable_btn.pack(side='left', padx=2)

        self.sleep_btn = tk.Button(
            btn_frame,
            text="💤",
            font=("Arial", 8),
            bg="#1a1a1a",
            command=self.toggle_sleep,
            width=3
        )
        self.sleep_btn.pack(side='left', padx=2)

        # Chat area
        chat_frame = tk.Frame(self.root, bg='#0a0a0a')
        chat_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.chat_display = tk.Text(
            chat_frame,
            font=("Consolas", 9),
            fg="#00ffff",
            bg="#0f0f0f",
            insertbackground="#00ffff",
            wrap='word',
            state='disabled'
        )
        self.chat_display.pack(fill='both', expand=True)

        # Input area
        input_frame = tk.Frame(self.root, bg='#0a0a0a')
        input_frame.pack(fill='x', padx=10, pady=5)

        self.input_entry = tk.Entry(
            input_frame,
            font=("Arial", 10),
            fg="#00ffff",
            bg="#1a1a1a",
            insertbackground="#00ffff"
        )
        self.input_entry.pack(fill='x', pady=2)
        self.input_entry.bind('<Return>', self.send_message)

        # Wake word indicator
        self.wake_indicator = tk.Label(
            self.root,
            text="Say 'Jarvis' to wake up",
            font=("Arial", 8),
            fg="#666666",
            bg="#0a0a0a"
        )
        self.wake_indicator.pack(pady=2)

    def _start_status_animation(self):
        def animate():
            colors = ['#00ffff', '#0088ff', '#0066cc', '#0088ff']
            i = 0
            while True:
                if self.is_listening:
                    color = colors[i % len(colors)]
                    self.root.after(0, lambda c=color: self.status_label.configure(fg=c))
                    i += 1
                time.sleep(0.5)

        threading.Thread(target=animate, daemon=True).start()

    def toggle_enable(self):
        self.is_enabled = not self.is_enabled
        if self.is_enabled:
            self.enable_btn.configure(fg="#00ff00")
            self.status_label.configure(text="🤖 JARVIS - Ready")
            self.add_system_message("JARVIS enabled")
        else:
            self.enable_btn.configure(fg="#ff0000")
            self.status_label.configure(text="🤖 JARVIS - Disabled")
            self.add_system_message("JARVIS disabled")

    def toggle_sleep(self):
        if not self.is_enabled:
            return

        self.is_sleeping = not self.is_sleeping
        if self.is_sleeping:
            self.sleep_btn.configure(fg="#ffaa00")
            self.status_label.configure(text="🤖 JARVIS - Sleeping")
            self.add_system_message("JARVIS is sleeping. Say 'Jarvis' to wake up.")
        else:
            self.sleep_btn.configure(fg="#666666")
            self.status_label.configure(text="🤖 JARVIS - Ready")
            self.add_system_message("JARVIS is awake")

    def send_message(self, event=None):
        if not self.is_enabled or self.is_sleeping:
            return

        message = self.input_entry.get().strip()
        if not message:
            return

        self.input_entry.delete(0, 'end')
        self.add_message("You", message)

        if self.assistant_callback:
            threading.Thread(target=self._process_command, args=(message,), daemon=True).start()

    def _process_command(self, command):
        self.set_listening(True)
        try:
            response = self.assistant_callback(command)
            self.add_message("JARVIS", response)
        except Exception as e:
            self.add_message("JARVIS", f"Error: {str(e)}")
        finally:
            self.set_listening(False)

    def set_listening(self, listening):
        self.is_listening = listening
        if listening:
            self.root.after(0, lambda: self.status_label.configure(text="🤖 JARVIS - Listening..."))
        else:
            self.root.after(0, lambda: self.status_label.configure(text="🤖 JARVIS - Ready"))

    def add_message(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M")
        formatted_msg = f"[{timestamp}] {sender}: {message}\n"

        def update_chat():
            self.chat_display.configure(state='normal')
            self.chat_display.insert('end', formatted_msg)
            self.chat_display.configure(state='disabled')
            self.chat_display.see('end')

        self.root.after(0, update_chat)

    def add_system_message(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        formatted_msg = f"[{timestamp}] System: {message}\n"

        def update_chat():
            self.chat_display.configure(state='normal')
            self.chat_display.insert('end', formatted_msg)
            self.chat_display.configure(state='disabled')
            self.chat_display.see('end')

        self.root.after(0, update_chat)

    def wake_up(self):
        if self.is_sleeping:
            self.is_sleeping = False
            self.sleep_btn.configure(fg="#666666")
            self.status_label.configure(text="🤖 JARVIS - Ready")
            self.add_system_message("JARVIS woke up")
            return True
        return False

    def start(self):
        self.root.mainloop()


class JarvisHUD:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("JARVIS HUD")
        self.root.geometry("800x600")
        self.root.configure(fg_color="#0a0a0a")

        self._setup_ui()
        self._start_animation()

    def _setup_ui(self):
        # Status label
        self.status_label = ctk.CTkLabel(
            self.root,
            text="Initializing...",
            font=("Arial", 24, "bold"),
            text_color="#00ffff"
        )
        self.status_label.pack(pady=20)

        # Animated circle frame
        self.circle_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.circle_frame.pack(pady=10)

        self.circle = ctk.CTkProgressBar(
            self.circle_frame,
            width=100,
            height=100,
            progress_color="#00ffff",
            fg_color="#1a1a1a"
        )
        self.circle.pack()

        # Conversation log
        self.log_frame = ctk.CTkFrame(self.root)
        self.log_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.conversation_log = ctk.CTkTextbox(
            self.log_frame,
            font=("Courier", 12),
            text_color="#00ffff",
            fg_color="#0f0f0f"
        )
        self.conversation_log.pack(fill="both", expand=True, padx=10, pady=10)

    def _start_animation(self):
        """Start the pulsing animation in a separate thread."""
        def animate():
            progress = 0
            direction = 1
            while True:
                progress += direction * 0.02
                if progress >= 1 or progress <= 0:
                    direction *= -1
                self.circle.set(progress)
                time.sleep(0.05)

        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()

    def update_status(self, text: str):
        """Update the status label."""
        self.root.after(0, lambda: self.status_label.configure(text=text))

    def add_message(self, sender: str, message: str):
        """Add a message to the conversation log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {sender}: {message}\n"

        def update_log():
            self.conversation_log.insert("end", formatted_message)
            self.conversation_log.see("end")

        self.root.after(0, update_log)

    def start(self):
        """Start the HUD in a separate thread."""
        def run_gui():
            self.root.mainloop()

        gui_thread = threading.Thread(target=run_gui, daemon=True)
        gui_thread.start()

    def destroy(self):
        """Close the HUD."""
        self.root.after(0, self.root.destroy)
