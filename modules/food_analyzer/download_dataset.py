"""
Food-101 Dataset Downloader and Preprocessor
Downloads the Food-101 dataset and prepares it for training

Dataset info:
- 101 food categories
- 1000 images per category 
- Total: 101,000 images
- Size: ~5GB

Usage:
    python download_dataset.py
"""
import os
import tarfile
import shutil
from pathlib import Path
import urllib.request
import sys

# Food-101 dataset URL
DATASET_URL = "http://data.vision.ee.ethz.ch/cvl/food-101.tar.gz"
DATASET_DIR = Path(__file__).parent.parent.parent / "data" / "food101"
ARCHIVE_PATH = DATASET_DIR / "food-101.tar.gz"


def download_with_progress(url: str, filepath: Path):
    """Download file with progress bar"""
    print(f"Downloading from {url}")
    print(f"Saving to {filepath}")
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, downloaded * 100 // total_size)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        sys.stdout.write(f"\rProgress: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, filepath, progress_hook)
    print("\nDownload complete!")


def extract_archive(archive_path: Path, extract_to: Path):
    """Extract tar.gz archive"""
    print(f"Extracting {archive_path}...")
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(extract_to)
    print("Extraction complete!")


def organize_dataset(dataset_dir: Path):
    """Organize dataset into train/test structure for PyTorch ImageFolder"""
    source_dir = dataset_dir / "food-101"
    images_dir = source_dir / "images"
    
    if not images_dir.exists():
        print(f"Images directory not found at {images_dir}")
        return
    
    # Read train/test splits
    meta_dir = source_dir / "meta"
    
    train_dir = dataset_dir / "train"
    test_dir = dataset_dir / "test"
    
    # Create directories
    train_dir.mkdir(exist_ok=True)
    test_dir.mkdir(exist_ok=True)
    
    # Read train.txt
    train_files = set()
    with open(meta_dir / "train.txt", "r") as f:
        for line in f:
            train_files.add(line.strip())
    
    # Read test.txt
    test_files = set()
    with open(meta_dir / "test.txt", "r") as f:
        for line in f:
            test_files.add(line.strip())
    
    print(f"Train images: {len(train_files)}")
    print(f"Test images: {len(test_files)}")
    
    # Copy images to train/test directories
    print("Organizing dataset...")
    
    for category in os.listdir(images_dir):
        category_path = images_dir / category
        if not category_path.is_dir():
            continue
        
        # Create category subdirectories
        (train_dir / category).mkdir(exist_ok=True)
        (test_dir / category).mkdir(exist_ok=True)
        
        for img_file in os.listdir(category_path):
            img_name = f"{category}/{img_file.replace('.jpg', '')}"
            src_path = category_path / img_file
            
            if img_name in train_files:
                dst_path = train_dir / category / img_file
            elif img_name in test_files:
                dst_path = test_dir / category / img_file
            else:
                continue
            
            if not dst_path.exists():
                shutil.copy2(src_path, dst_path)
    
    print("Dataset organized!")
    print(f"Train directory: {train_dir}")
    print(f"Test directory: {test_dir}")


def main():
    """Main function to download and prepare dataset"""
    print("=" * 50)
    print("Food-101 Dataset Downloader")
    print("=" * 50)
    
    # Create directories
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if already downloaded
    if (DATASET_DIR / "train").exists() and (DATASET_DIR / "test").exists():
        print("Dataset already downloaded and organized!")
        return
    
    # Download if archive doesn't exist
    if not ARCHIVE_PATH.exists():
        print(f"\nDownloading Food-101 dataset (~5GB)...")
        download_with_progress(DATASET_URL, ARCHIVE_PATH)
    else:
        print(f"Archive already exists at {ARCHIVE_PATH}")
    
    # Extract archive
    if not (DATASET_DIR / "food-101").exists():
        extract_archive(ARCHIVE_PATH, DATASET_DIR)
    
    # Organize into train/test
    organize_dataset(DATASET_DIR)
    
    print("\n" + "=" * 50)
    print("Dataset ready for training!")
    print("=" * 50)


if __name__ == "__main__":
    main()
