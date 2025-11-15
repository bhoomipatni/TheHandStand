import os
import json
import numpy as np
from src.datasets.skeleton_dataset import SkeletonDataset
from src.models.skeleton_model import SkeletonModel

def evaluate_model(model, dataset):
    model.eval()
    total_loss = 0
    correct_predictions = 0

    with torch.no_grad():
        for data in dataset:
            inputs, targets = data
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            total_loss += loss.item()
            predictions = outputs.argmax(dim=1)
            correct_predictions += (predictions == targets).sum().item()

    accuracy = correct_predictions / len(dataset)
    return total_loss, accuracy

def main():
    # Load configuration
    with open('configs/default.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Initialize dataset and model
    dataset = SkeletonDataset(config['dataset'])
    model = SkeletonModel(config['model'])

    # Load trained model weights
    model.load_state_dict(torch.load(config['model']['weights_path']))

    # Evaluate the model
    loss, accuracy = evaluate_model(model, dataset)

    # Print evaluation results
    print(f'Evaluation Loss: {loss:.4f}')
    print(f'Evaluation Accuracy: {accuracy:.4f}')

if __name__ == '__main__':
    main()