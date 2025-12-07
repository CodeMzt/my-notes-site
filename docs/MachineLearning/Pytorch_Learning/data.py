from torch.utils.data import Dataset
from PIL import Image
import os

class MyDataset(Dataset):
    def __init__(self, root_dir,label_dir):
        """初始化方法，用于设置数据集参数和加载数据"""
        super().__init__()
        # 初始化代码
        self.root_dir = root_dir
        self.label_dir = label_dir
        self.path = os.path.join(self.root_dir,self.label_dir)
        self.img_path = os.listdir(self.path)

    def __len__(self):
        """返回数据集的大小"""
        return len(self.img_path)

    def __getitem__(self, idx):
        """根据索引返回一个样本"""
        img_name = self.img_path[idx]
        img_item_path = os.path.join(self.root_dir,self.label_dir, img_name)
        img = Image.open(img_item_path)
        label = self.label_dir
        return img, label

# 取数据集
ants_dataset = MyDataset('dataset/train',"ants")
bees_dataset = MyDataset('dataset/train',"bees")

train_dataset = ants_dataset + bees_dataset