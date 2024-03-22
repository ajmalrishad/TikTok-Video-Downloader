import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import aiohttp
import asyncio
from io import BytesIO
from PIL import Image, ImageTk
import requests
from tiktokapipy.async_api import AsyncTikTokAPI

class TikTokDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("TikTok Video Downloader")

        # Load TikTok logo image
        self.tiktok_logo = Image.open("tiktok_logo.png")
        self.tiktok_logo_tk = ImageTk.PhotoImage(self.tiktok_logo.resize((50, 50)))

        # Create label for TikTok logo
        self.tiktok_logo_label = tk.Label(master, image=self.tiktok_logo_tk)
        self.tiktok_logo_label.pack(pady=50)

        self.link_label = tk.Label(master, text="Paste TikTok Video Link:")
        self.link_label.pack()

        self.link_entry = tk.Entry(master, width=50)
        self.link_entry.pack(padx=10,pady=10)
        self.link_entry.bind("<Button-3>", self.show_menu)

        self.process_button = tk.Button(master, text="PROCESS", bg="#3b71ca", fg="white", command=self.process_video, font=('Helvetica', 10))
        self.process_button.pack()
        self.downloading = False  

    def show_menu(self, event):
        # Create a right-click context menu
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.link_entry.event_generate('<<Paste>>'))
        menu.tk_popup(event.x_root, event.y_root)

    def process_video(self):
        video_link = self.link_entry.get()
        if video_link and video_link.startswith('https://www.tiktok.com/'):
            if not self.downloading:  # Check if URL is valid and no download in progress
                self.master.withdraw()  # Hide the main window
                self.show_success_page(video_link)
            else:
                messagebox.showinfo("Download in Progress", "A download is already in progress. Please wait until it completes.")
        else:
            messagebox.showerror("Error", "Please enter a valid video URL.")

    # Success_page 
    def show_success_page(self, video_link):
        success_window = tk.Toplevel(self.master)
        success_window.geometry(self.master.geometry())
        
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Fetch video information
        loop.run_until_complete(self.fetch_video_info(video_link, success_window))

        # Download button
        download_button = tk.Button(success_window, text="Download", bg="green", fg="white", command=lambda: self.download_video(video_link, success_window))
        download_button.pack(padx=20,pady=20)


    async def fetch_video_info(self, video_link, success_window):
        async with AsyncTikTokAPI() as api:
            try:
                video = await api.video(video_link)
                title = video.desc
                thumbnail = video.video.cover
                response = requests.get(thumbnail)
                img = Image.open(BytesIO(response.content))
                img = img.resize((300, 300), Image.LANCZOS)
                thumbnail_image = ImageTk.PhotoImage(img)
                self.show_video_info(success_window, title, thumbnail_image)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch video information: {str(e)}")
                self.thumbnail = tk.Label(success_window, text="Thumbnail: Not available")
                self.thumbnail.pack(pady=20)
                retry = tk.Button(success_window, text="Retry", bg="red", fg="white", command=lambda: self.retry(success_window))
                retry.pack()

    def show_video_info(self, success_window, title, thumbnail_image):
        # Display video thumbnail image
        thumbnail_label = tk.Label(success_window, image=thumbnail_image)
        thumbnail_label.pack(pady=10)
        # Display video title
        title_label = tk.Label(success_window, text="Video Title : "f'{title}')
        title_label.pack(pady=10)

    def retry(self, success_window):
        success_window.destroy()  # Close the success window
        self.master.deiconify()   # Show the master window


    async def save_video(self, video, api,success_window):
        async with aiohttp.ClientSession(cookies={cookie["name"]: cookie["value"] for cookie in await api.context.cookies() if cookie["name"] == "tt_chain_token"}) as session:
            async with session.get(video.video.download_addr, headers={"referer": "https://www.tiktok.com/"}) as resp:
                if resp.status == 200:
                    filename = f"{video.id}.mp4"
                    script_path = os.path.dirname(__file__)
                    filepath = os.path.join(script_path, filename)
                    self.downloadstatus = tk.Label(success_window, fg="green", text="Downloading...")
                    self.downloadstatus.pack(pady=10)

                    # Create progress bar
                    self.progress_bar = ttk.Progressbar(success_window, mode='determinate')
                    self.progress_bar.pack()

                    self.progress_bar.start()  # Start the progress bar
                    with open(filepath, "wb") as f:
                        f.write(await resp.read())
                    self.master.deiconify()  # Show the main window again after download
                    self.process_button.config(state='normal')
                    # Hide the success window and destroy it
                    success_window.destroy()
                    messagebox.showinfo("Success", f"Video downloaded and saved as {filepath}")
                else:
                    messagebox.showerror("Error", f"Failed to download video: {resp.status} - {resp.reason}")
                    self.master.deiconify()  # Show the main window again after download
                    # Hide the success window and destroy it
                    success_window.destroy()

    async def download_video_async(self, link, success_window):
        async with AsyncTikTokAPI() as api:
            try:
                video = await api.video(link)
                await self.save_video(video, api,success_window)
                success_window.destroy()
                self.master.deiconify()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download video: {str(e)}")
                retry = tk.Button(success_window, text="Retry", bg="red", fg="white", command=lambda: self.retry(success_window))
                retry.pack()
            finally:
                self.downloading = False
                self.process_button.config(state='normal')
                success_window.destroy()
                self.master.deiconify()


    def download_video(self, link, success_window):
        self.downloading = True  # Set downloading flag to True
        self.process_button.config(state='disabled')  # Disable the download button
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.download_video_async(link, success_window))


def main():
    root = tk.Tk()
    root.iconbitmap(r'favicon.ico')
    root.minsize(500, 500)
    app = TikTokDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
