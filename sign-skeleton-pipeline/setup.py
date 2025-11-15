from setuptools import setup, find_packages

setup(
    name='sign-skeleton-pipeline',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A pipeline for downloading videos, extracting keypoints, and training on skeleton sequences for sign language recognition.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'opencv-python',
        'torch',
        'torchvision',
        'scikit-learn',
        'pandas',
        'PyYAML',
        'matplotlib',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'download-videos=scripts.download:main',
            'extract-keypoints=scripts.extract_keypoints:main',
            'train-model=scripts.train:main',
        ],
    },
)