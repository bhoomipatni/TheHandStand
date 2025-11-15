import unittest
from src.extractor.keypoint_extractor import KeypointExtractor

class TestKeypointExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = KeypointExtractor()

    def test_extract_keypoints(self):
        video_path = 'data/videos/sample_video.mp4'
        keypoints = self.extractor.extract(video_path)
        self.assertIsNotNone(keypoints)
        self.assertTrue(len(keypoints) > 0)

    def test_invalid_video_path(self):
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract('data/videos/non_existent_video.mp4')

    def test_keypoints_shape(self):
        video_path = 'data/videos/sample_video.mp4'
        keypoints = self.extractor.extract(video_path)
        # Assuming keypoints are in the shape (num_frames, num_keypoints, 2)
        self.assertEqual(len(keypoints.shape), 3)
        self.assertGreater(keypoints.shape[1], 0)  # Ensure there are keypoints

if __name__ == '__main__':
    unittest.main()