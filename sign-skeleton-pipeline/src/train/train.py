import os
import yaml
import torch
from torch.utils.data import DataLoader
from src.datasets.skeleton_dataset import SkeletonDataset
from src.models.skeleton_model import SkeletonModel

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    # Load configuration
    config = load_config('configs/default.yaml')
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Initialize dataset
    train_dataset = SkeletonDataset(config['dataset']['train_data_path'])
    train_loader = DataLoader(train_dataset, batch_size=config['training']['batch_size'], shuffle=True)
    
    # Initialize model
    model = SkeletonModel(config['model']).to(device)
    
    # Define loss function and optimizer
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config['training']['learning_rate'])
    
    # Training loop
    for epoch in range(config['training']['num_epochs']):
        model.train()
        for batch in train_loader:
            inputs, labels = batch['skeletons'].to(device), batch['labels'].to(device)
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        print(f'Epoch [{epoch+1}/{config["training"]["num_epochs"]}], Loss: {loss.item():.4f}')
    
    # Save the trained model
    os.makedirs('models', exist_ok=True)
    torch.save(model.state_dict(), 'models/skeleton_model.pth')

if __name__ == '__main__':
    main()