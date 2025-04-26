from dataclasses import dataclass
from typing import Optional, Dict, List
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
import time
import threading


@dataclass
class ToastNotification:
    id: int
    title: str
    message: str
    created_at: float
    widget: Optional[ttk.Frame] = None


class ToastContainer(ttk.Frame):
    """Widget for displaying toast notifications."""
    
    DISPLAY_TIME = 3.0  # seconds
    FADE_TIME = 0.5  # seconds
    MAX_TOASTS = 3
    TOAST_HEIGHT = 60
    TOAST_WIDTH = 300
    TOAST_MARGIN = 10
    
    def __init__(self, parent: tk.Widget):
        """Initialize the toast container.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._next_id = 1
        self._active_toasts: Dict[int, ToastNotification] = {}
        self._toast_queue: List[ToastNotification] = []
        
        # Configure the container
        self.pack(side=tk.TOP, anchor=tk.NE, padx=20, pady=20)
        
        # Start the cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self._cleanup_thread.start()
    
    def show_toast(self, title: str, message: str) -> None:
        """Show a new toast notification.
        
        Args:
            title: Toast title
            message: Toast message
        """
        toast = ToastNotification(
            id=self._next_id,
            title=title,
            message=message,
            created_at=time.time()
        )
        self._next_id += 1
        
        if len(self._active_toasts) < self.MAX_TOASTS:
            self._show_toast_widget(toast)
        else:
            self._toast_queue.append(toast)
    
    def _show_toast_widget(self, toast: ToastNotification) -> None:
        """Create and show the toast widget.
        
        Args:
            toast: Toast notification to display
        """
        # Create toast frame
        toast_frame = ttk.Frame(
            self,
            style="primary.TFrame",
            padding=10
        )
        
        # Title
        title_label = ttk.Label(
            toast_frame,
            text=toast.title,
            style="primary.Inverse.TLabel",
            font=("TkDefaultFont", 10, "bold")
        )
        title_label.pack(anchor=tk.W)
        
        # Message
        message_label = ttk.Label(
            toast_frame,
            text=toast.message,
            style="primary.Inverse.TLabel",
            wraplength=self.TOAST_WIDTH - 40
        )
        message_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Close button
        close_btn = ttk.Button(
            toast_frame,
            text="×",
            style="primary.Inverse.TButton",
            width=2,
            command=lambda: self._remove_toast(toast.id)
        )
        close_btn.place(relx=1.0, rely=0.0, anchor=tk.NE)
        
        # Position the toast
        y_position = len(self._active_toasts) * (self.TOAST_HEIGHT + self.TOAST_MARGIN)
        toast_frame.place(
            x=0,
            y=y_position,
            width=self.TOAST_WIDTH,
            height=self.TOAST_HEIGHT
        )
        
        # Store the widget reference
        toast.widget = toast_frame
        self._active_toasts[toast.id] = toast
    
    def _remove_toast(self, toast_id: int) -> None:
        """Remove a toast notification.
        
        Args:
            toast_id: ID of the toast to remove
        """
        if toast_id not in self._active_toasts:
            return
            
        toast = self._active_toasts.pop(toast_id)
        if toast.widget:
            toast.widget.destroy()
        
        # Reposition remaining toasts
        self._reposition_toasts()
        
        # Show next toast from queue if any
        if self._toast_queue:
            next_toast = self._toast_queue.pop(0)
            self._show_toast_widget(next_toast)
    
    def _reposition_toasts(self) -> None:
        """Reposition all active toasts after one is removed."""
        active_toasts = sorted(
            self._active_toasts.values(),
            key=lambda t: t.created_at
        )
        
        for i, toast in enumerate(active_toasts):
            if toast.widget:
                y_position = i * (self.TOAST_HEIGHT + self.TOAST_MARGIN)
                toast.widget.place(
                    x=0,
                    y=y_position,
                    width=self.TOAST_WIDTH,
                    height=self.TOAST_HEIGHT
                )
    
    def _cleanup_loop(self) -> None:
        """Background thread for removing expired toasts."""
        while True:
            current_time = time.time()
            expired_toasts = [
                toast_id
                for toast_id, toast in self._active_toasts.items()
                if current_time - toast.created_at >= self.DISPLAY_TIME
            ]
            
            for toast_id in expired_toasts:
                # Schedule removal on the main thread
                self.after(0, self._remove_toast, toast_id)
            
            time.sleep(0.1)  # Sleep to prevent high CPU usage
