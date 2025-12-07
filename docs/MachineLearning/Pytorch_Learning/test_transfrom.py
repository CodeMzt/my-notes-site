from PIL import Image
from torchvision import transforms

img_path = 'dataset/train/ants/0013035.jpg'
img = Image.open(img_path)
print(type(img))


tensor_trans = transforms.ToTensor()
img_tensor = tensor_trans(img)
print(type(img_tensor))