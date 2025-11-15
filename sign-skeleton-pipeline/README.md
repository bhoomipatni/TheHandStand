# sign-skeleton-pipeline

This project is designed to download videos, extract keypoints, and train models on skeleton sequences derived from those keypoints. The pipeline consists of several components that work together to facilitate the entire process from video acquisition to model training.

## Project Structure

- **data/**: Contains all data-related directories.
  - **raw/**: Original downloaded videos.
  - **videos/**: Processed video files after downloading.
  - **processed/**: Holds the outputs of the processing steps.
    - **keypoints/**: Extracted keypoints from the videos.
    - **skeletons/**: Skeleton sequences generated from the keypoints.

- **src/**: Source code for the project.
  - **downloader/**: Module for downloading videos.
    - **video_downloader.py**: Contains the `VideoDownloader` class.
  - **extractor/**: Module for extracting keypoints.
    - **keypoint_extractor.py**: Contains the `KeypointExtractor` class.
  - **datasets/**: Module for handling datasets.
    - **skeleton_dataset.py**: Contains the `SkeletonDataset` class.
  - **models/**: Module for model definitions.
    - **skeleton_model.py**: Contains the `SkeletonModel` class.
  - **train/**: Module for training scripts.
    - **train.py**: Main training script.
  - **eval/**: Module for evaluation scripts.
    - **evaluate.py**: Evaluation script for assessing model performance.
  - **utils/**: Utility functions for I/O operations.
    - **io.py**: Contains utility functions for loading and saving data.

- **scripts/**: Shell scripts for automating processes.
  - **download.sh**: Automates the video downloading process.
  - **extract_keypoints.sh**: Automates the keypoint extraction process.
  - **train.sh**: Automates the training process.

- **configs/**: Configuration files for the project.
  - **default.yaml**: Default settings for the project.
  - **dataset.yaml**: Dataset-specific settings.

- **notebooks/**: Jupyter notebooks for exploratory data analysis.
  - **exploration.ipynb**: Notebook for data exploration and visualization.

- **tests/**: Unit tests for the project.
  - **test_downloader.py**: Tests for the video downloader functionality.
  - **test_extractor.py**: Tests for the keypoint extractor functionality.

- **requirements.txt**: Lists the Python dependencies required for the project.

- **setup.py**: Used for packaging the project and managing dependencies.

- **.gitignore**: Specifies files and directories to be ignored by Git.

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd sign-skeleton-pipeline
pip install -r requirements.txt
```

## Usage

1. **Download Videos**: Run the download script to fetch videos.
   ```bash
   bash scripts/download.sh
   ```

2. **Extract Keypoints**: After downloading, extract keypoints from the videos.
   ```bash
   bash scripts/extract_keypoints.sh
   ```

3. **Train Model**: Finally, train the model using the extracted keypoints.
   ```bash
   bash scripts/train.sh
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.