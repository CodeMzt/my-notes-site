from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("logs")

# 实例 y = x
for i in range(100):
    writer.add_scalar(tag='y=2x',scalar_value=2*i,global_step=i)

from PIL import Image
import numpy as np
image_path = 'hymenoptera_data/hymenoptera_data/train/ants/0013035.jpg'
img = Image.open(image_path)
img = np.array(img)
print(img.shape) # note : 默认是 3*H*W 这里3却在最后。因此我们需要额外设置格式
writer.add_image('image',img,global_step=2,dataformats='HWC')

writer.close()