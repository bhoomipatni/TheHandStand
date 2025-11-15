import unittest
from src.downloader.video_downloader import VideoDownloader

class TestVideoDownloader(unittest.TestCase):

    def setUp(self):
        self.downloader = VideoDownloader()

    def test_download_video(self):
        url = "https://example.com/video.mp4"
        output_path = "data/raw/video.mp4"
        result = self.downloader.download_video(url, output_path)
        self.assertTrue(result)
        # Check if the file exists
        self.assertTrue(os.path.exists(output_path))

    def test_download_invalid_url(self):
        url = "https://invalid-url.com/video.mp4"
        output_path = "data/raw/invalid_video.mp4"
        result = self.downloader.download_video(url, output_path)
        self.assertFalse(result)

    def test_download_multiple_videos(self):
        urls = [
            "https://example.com/video1.mp4",
            "https://example.com/video2.mp4"
        ]
        output_paths = [
            "data/raw/video1.mp4",
            "data/raw/video2.mp4"
        ]
        results = self.downloader.download_multiple_videos(urls, output_paths)
        self.assertEqual(len(results), len(urls))
        self.assertTrue(all(results))

if __name__ == '__main__':
    unittest.main()