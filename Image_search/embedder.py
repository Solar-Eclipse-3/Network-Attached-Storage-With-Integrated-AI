import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image
import requests
from io import BytesIO

# Load pre-trained ResNet50 model
_model = resnet50(weights=ResNet50_Weights.DEFAULT)
_model.eval()

# Remove the final classification layer to get feature embeddings
_model = torch.nn.Sequential(*list(_model.children())[:-1])

# Define image preprocessing steps
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def get_embedding(image_input) -> torch.Tensor:
    """
    Accepts a file path, BytesIO stream, or URL.
    """
    if isinstance(image_input, str):
        if image_input.startswith("http"):
            response = requests.get(image_input)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            img = Image.open(image_input).convert("RGB")
    else:
        img = Image.open(image_input).convert("RGB")

    tensor = _transform(img).unsqueeze(0)
    with torch.no_grad():
        embedding = _model(tensor).squeeze()
    return embedding.flatten()
