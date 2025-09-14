from ultralytics import YOLO
import argparse
from pathlib import Path
import torch

def train_pill_detector(dataset_dir, output_file):
    """
    This function trains a YOLOv8 model on a custom pill dataset.
    """
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        raise ValueError(f"dataset_dir {dataset_dir} does not exist!")
    if not dataset_path.is_dir():
        raise ValueError(f"dataset_dir {dataset_dir} is not a directory!")
    data_yaml_path = dataset_path / "data.yaml"
    if not data_yaml_path.exists():
        raise ValueError(f"Could not find data.yaml in {dataset_dir}")

    if output_file is None:
        output_file = Path(".") / (dataset_path.name + ".pt")
    else:
        output_file = Path(output_file)

    if output_file.exists():
        raise ValueError(f"output_file {output_file} already exists! aborting.")

    # --- Step 1: Set up your training configuration ---

    # We need the dataset's .yaml file. That's data_yaml_path, defined above.

    # Define the number of epochs to train for.
    # An epoch is one full pass through the entire training dataset.
    # 50 is a good starting point. You can increase this for better accuracy,
    # but it will take longer.
    training_epochs = 50

    # Define the image size for training. 640 is a standard choice.
    image_size = 640

    # --- Step 2: Load a pre-trained model ---

    # We start with a model that is already pre-trained on the large COCO dataset.
    # This is called transfer learning and is much more effective than starting from scratch.
    # 'yolov8n.pt' is the smallest and fastest YOLOv8 model.
    model = YOLO('yolov8n.pt')

    # Check if a GPU is available and print the device name
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Training on device: {device}")

    # --- Step 3: Train the model ---

    print("Starting model training...")
    # The 'train' method will start the training process.
    # It will automatically save the best performing model and training logs.
    results = model.train(
        data=data_yaml_path,
        epochs=training_epochs,
        imgsz=image_size,
        device=device,
        project='runs/detect',  # Directory to save results
        name='pill_training'    # Sub-directory name for this specific run
    )

    print("Training complete!")
    print("Your trained model and results are saved in the 'runs/detect/pill_training' directory.")
    print("The best model is saved as 'best.pt' in the 'weights' subfolder.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="A tool to train a YOLOv8 model on a custom pill dataset.",
    )
    parser.add_argument(
        'dataset_dir',
        type=str,
        metavar='dataset-dir',
        help="A directory containing YOLOv8 model training data including a data.yaml file and subdirs test, train, and valid"
    )
    parser.add_argument(
        '-o', '--output',
        metavar="OUTPUT",
        type=str,
        default=None,
        help="The trained model .pt file. Defaults to the name of the training directory with .pt extension"
    )
    args = parser.parse_args()

    train_pill_detector(args.dataset_dir, args.output)

