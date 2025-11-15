class SkeletonDataset:
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.skeletons = self.load_skeletons()

    def load_skeletons(self):
        # Load skeleton data from the processed directory
        skeletons_path = os.path.join(self.data_dir, 'processed', 'skeletons')
        skeleton_files = [f for f in os.listdir(skeletons_path) if f.endswith('.npy')]
        skeletons = []
        for file in skeleton_files:
            skeleton = np.load(os.path.join(skeletons_path, file))
            skeletons.append(skeleton)
        return skeletons

    def __len__(self):
        return len(self.skeletons)

    def __getitem__(self, idx):
        skeleton = self.skeletons[idx]
        if self.transform:
            skeleton = self.transform(skeleton)
        return skeleton