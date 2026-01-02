"""
Food Classification Model Training Script
Trains MobileNetV2 on Food-101 dataset using transfer learning

Requirements:
- PyTorch with CUDA (for GPU training)
- Food-101 dataset (run download_dataset.py first)

Usage:
    python train_model.py

For Google Colab, upload this file and run:
    !python train_model.py --epochs 10 --batch_size 32
"""
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.optim.lr_scheduler import StepLR

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent.parent / "data" / "food101"
MODEL_DIR = SCRIPT_DIR / "trained_models"
MODEL_DIR.mkdir(exist_ok=True)


def get_transforms():
    """Get data augmentation and normalization transforms"""
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    return train_transform, test_transform


def create_model(num_classes: int, pretrained: bool = True):
    """Create MobileNetV2 model with custom classifier"""
    print(f"Creating MobileNetV2 model for {num_classes} classes...")
    
    if pretrained:
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    else:
        model = models.mobilenet_v2(weights=None)
    
    # Freeze early layers for transfer learning
    for param in model.features[:14].parameters():
        param.requires_grad = False
    
    # Replace classifier
    num_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, num_classes)
    )
    
    return model


def train_epoch(model, train_loader, criterion, optimizer, device, epoch):
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = output.max(1)
        total += target.size(0)
        correct += predicted.eq(target).sum().item()
        
        if batch_idx % 50 == 0:
            print(f"  Batch {batch_idx}/{len(train_loader)} | "
                  f"Loss: {loss.item():.4f} | "
                  f"Acc: {100.*correct/total:.2f}%")
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc


def evaluate(model, test_loader, criterion, device):
    """Evaluate model on test set"""
    model.eval()
    test_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
    
    test_loss /= len(test_loader)
    accuracy = 100. * correct / total
    return test_loss, accuracy


def save_model(model, class_names, save_path):
    """Save model with class names"""
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'class_names': class_names,
        'num_classes': len(class_names)
    }
    torch.save(checkpoint, save_path)
    print(f"Model saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description='Train Food Classification Model')
    parser.add_argument('--epochs', type=int, default=15, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--resume', type=str, default=None, help='Path to checkpoint to resume')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Food Classification Model Training")
    print("=" * 60)
    
    # Check CUDA
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    if device.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("WARNING: Training on CPU will be very slow!")
        print("Consider using Google Colab with GPU runtime.")
    
    # Check dataset
    train_dir = DATA_DIR / "train"
    test_dir = DATA_DIR / "test"
    
    if not train_dir.exists():
        print(f"\nDataset not found at {DATA_DIR}")
        print("Please run download_dataset.py first!")
        sys.exit(1)
    
    # Load data
    print("\nLoading dataset...")
    train_transform, test_transform = get_transforms()
    
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    test_dataset = datasets.ImageFolder(test_dir, transform=test_transform)
    
    class_names = train_dataset.classes
    num_classes = len(class_names)
    
    print(f"Classes: {num_classes}")
    print(f"Train images: {len(train_dataset)}")
    print(f"Test images: {len(test_dataset)}")
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=args.batch_size, 
        shuffle=True, 
        num_workers=4,
        pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset, 
        batch_size=args.batch_size, 
        shuffle=False, 
        num_workers=4,
        pin_memory=True
    )
    
    # Create model
    model = create_model(num_classes, pretrained=True)
    model = model.to(device)
    
    # Resume from checkpoint
    start_epoch = 0
    if args.resume and os.path.exists(args.resume):
        print(f"Resuming from {args.resume}")
        checkpoint = torch.load(args.resume)
        model.load_state_dict(checkpoint['model_state_dict'])
        start_epoch = checkpoint.get('epoch', 0)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr
    )
    scheduler = StepLR(optimizer, step_size=5, gamma=0.1)
    
    # Training loop
    print("\nStarting training...")
    print("-" * 60)
    
    best_acc = 0.0
    training_start = time.time()
    
    for epoch in range(start_epoch, args.epochs):
        epoch_start = time.time()
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        
        # Train
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        
        # Evaluate
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)
        
        # Update scheduler
        scheduler.step()
        
        epoch_time = time.time() - epoch_start
        
        print(f"\n  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Test Loss:  {test_loss:.4f} | Test Acc:  {test_acc:.2f}%")
        print(f"  Time: {epoch_time:.1f}s | LR: {scheduler.get_last_lr()[0]:.6f}")
        
        # Save best model
        if test_acc > best_acc:
            best_acc = test_acc
            save_path = MODEL_DIR / "food_classifier_best.pth"
            save_model(model, class_names, save_path)
            print(f"  New best accuracy: {best_acc:.2f}%")
        
        # Save checkpoint
        checkpoint_path = MODEL_DIR / f"checkpoint_epoch_{epoch+1}.pth"
        torch.save({
            'epoch': epoch + 1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_loss': train_loss,
            'test_acc': test_acc,
            'class_names': class_names
        }, checkpoint_path)
    
    total_time = time.time() - training_start
    print("\n" + "=" * 60)
    print("Training Complete!")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Best accuracy: {best_acc:.2f}%")
    print(f"Model saved to: {MODEL_DIR / 'food_classifier_best.pth'}")
    print("=" * 60)
    
    # Save final model for bot
    final_path = SCRIPT_DIR / "food_model.pth"
    save_model(model, class_names, final_path)
    print(f"\nFinal model ready for bot: {final_path}")


if __name__ == "__main__":
    main()
