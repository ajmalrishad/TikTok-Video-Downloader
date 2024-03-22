import asyncio
import io
import os
import tkinter as tk
from tkinter import messagebox
import aiohttp

from tiktokapipy.async_api import AsyncTikTokAPI

class TikTokDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Downloader")

        self.link_label = tk.Label(root, text="Paste TikTok Video Link:")
        self.link_label.pack()

        self.link_entry = tk.Entry(root, width=50)
        self.link_entry.pack()

        self.download_button = tk.Button(root, text="Download", command=self.download_video)
        self.download_button.pack()

    async def save_video(self, video, api):
        async with aiohttp.ClientSession(cookies={cookie["name"]: cookie["value"] for cookie in await api.context.cookies() if cookie["name"] == "tt_chain_token"}) as session:
            async with session.get(video.video.download_addr, headers={"referer": "https://www.tiktok.com/"}) as resp:
                if resp.status == 200:
                    filename = f"{video.id}.mp4"
                    filepath = os.path.join("C:\\Users\\INFOLITZ\\Downloads", filename)
                    with open(filepath, "wb") as f:
                        f.write(await resp.read())
                    messagebox.showinfo("Success", f"Video downloaded and saved as {filepath}")
                else:
                    messagebox.showerror("Error", f"Failed to download video: {resp.status} - {resp.reason}")

    async def download_video_async(self):
        link = self.link_entry.get()
        if not link:
            messagebox.showerror("Error", "Please paste a TikTok video link.")
            return

        async with AsyncTikTokAPI() as api:
            try:
                video = await api.video(link)
                await self.save_video(video, api)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download video: {str(e)}")

    def download_video(self):
        asyncio.run(self.download_video_async())

def main():
    root = tk.Tk()
    app = TikTokDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
