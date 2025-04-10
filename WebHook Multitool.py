import tkinter as tk
from tkinter import messagebox
import requests, threading, time, base64
from io import BytesIO
from PIL import Image

class WebhookTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Webhook Multi-Tool")
        self.root.geometry("600x700")
        self.root.configure(bg="#2c2f33")
        self.root.resizable(False, False)

        self.make_label("Webhook URL:")
        self.url_entry = self.make_entry()

        self.make_label("Message:")
        self.message_entry = self.make_entry()

        self.make_button("Send Message", self.send_message, "#7289da")
        self.make_label("Spam Options:")
        self.spam_count = self.make_entry("Number of messages (e.g., 5)")
        self.spam_delay = self.make_entry("Delay between messages in seconds (e.g., 1)")
        self.make_button("Spam Webhook", self.spam_webhook, "#5865f2")

        self.make_label("Edit Webhook:")
        self.name_entry = self.make_entry("New Webhook Name (optional)")
        self.avatar_entry = self.make_entry("New Avatar URL (optional)")
        self.make_button("Edit Webhook", self.edit_webhook, "#57f287")

        self.make_button("Get Webhook Info", self.get_info, "#faa61a", fg="#000")
        self.make_button("Delete Webhook", self.delete_webhook, "#ed4245")

    def make_label(self, text):
        tk.Label(self.root, text=text, bg="#2c2f33", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=(15, 5))

    def make_entry(self, placeholder=None):
        entry = tk.Entry(self.root, width=50, font=("Segoe UI", 10))
        entry.pack(pady=4)
        if placeholder:
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e, ent=entry, ph=placeholder: self.clear_placeholder(ent, ph))
        return entry

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def make_button(self, text, command, bg, fg="white"):
        tk.Button(self.root, text=text, command=command, bg=bg, fg=fg, font=("Segoe UI", 10, "bold"),
                  width=30, height=2, bd=0, relief="ridge", activebackground=bg).pack(pady=8)

    def send_message(self):
        url = self.url_entry.get().strip()
        msg = self.message_entry.get().strip()
        if not url or not msg:
            messagebox.showwarning("Missing Info", "Enter both a webhook URL and message.")
            return
        r = requests.post(url, json={"content": msg})
        if r.status_code in [200, 204]:
            messagebox.showinfo("Success", "Message sent.")
        else:
            messagebox.showerror("Error", f"Failed to send message. Status code: {r.status_code}")

    def spam_webhook(self):
        def spam_thread():
            url = self.url_entry.get().strip()
            msg = self.message_entry.get().strip()
            try:
                count = int(self.spam_count.get())
                delay = float(self.spam_delay.get())
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers for count and delay.")
                return
            if not url or not msg or count <= 0:
                messagebox.showerror("Error", "Missing or invalid input.")
                return
            for i in range(count):
                r = requests.post(url, json={"content": msg})
                status = "✅" if r.status_code in [200, 204] else f"❌ ({r.status_code})"
                print(f"[{i+1}/{count}] Sent message {status}")
                time.sleep(delay)
            messagebox.showinfo("Done", f"Finished sending {count} messages.")

        threading.Thread(target=spam_thread).start()

    def edit_webhook(self):
        url = self.url_entry.get().strip()
        name = self.name_entry.get().strip()
        avatar_url = self.avatar_entry.get().strip()
        data = {}

        if name and "Name" not in name:
            data["name"] = name

        if avatar_url and "URL" not in avatar_url:
            try:
                img_response = requests.get(avatar_url)
                img_response.raise_for_status()
                img = Image.open(BytesIO(img_response.content)).convert("RGBA")
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                data["avatar"] = f"data:image/png;base64,{img_b64}"
            except Exception as e:
                messagebox.showerror("Avatar Error", f"Failed to load avatar image:\n{str(e)}")
                return

        if not data:
            messagebox.showwarning("No Changes", "Enter a new name or avatar URL.")
            return

        r = requests.patch(url, json=data)
        if r.status_code == 200:
            messagebox.showinfo("Success", "Webhook updated.")
        else:
            messagebox.showerror("Error", f"Failed to update webhook. Status code: {r.status_code}")

    def get_info(self):
        url = self.url_entry.get().strip()
        r = requests.get(url)
        if r.status_code == 200:
            info = r.json()
            info_text = "\n".join(f"{k}: {v}" for k, v in info.items())
            messagebox.showinfo("Webhook Info", info_text)
        else:
            messagebox.showerror("Error", f"Failed to retrieve info. Status code: {r.status_code}")

    def delete_webhook(self):
        url = self.url_entry.get().strip()
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this webhook?"):
            r = requests.delete(url)
            if r.status_code == 204:
                messagebox.showinfo("Deleted", "Webhook deleted successfully.")
            else:
                messagebox.showerror("Error", f"Failed to delete. Status code: {r.status_code}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebhookTool(root)
    root.mainloop()
