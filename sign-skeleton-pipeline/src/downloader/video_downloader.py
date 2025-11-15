class VideoDownloader:
    def __init__(self, source_list, download_path):
        self.source_list = source_list
        self.download_path = download_path

    def download_video(self, url):
        import os
        import yt_dlp

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_all(self):
        for url in self.source_list:
            self.download_video(url)