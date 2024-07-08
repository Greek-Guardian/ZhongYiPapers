import os.path
from PIL import Image
import torchvision.transforms as standard_transforms
import torch
from torch.utils.data import Dataset  # Dataset是个抽象类，只能用于继承
from torch.utils.data import DataLoader # DataLoader需实例化，用于加载数据


class MyDataset(Dataset):   # 继承Dataset类
    def __init__(self, batch_size, device):
        # 数据集图片的路径
        dataset_dir_path = r"/home/liangzida/workspace/Python/ZhongYi/chaoxin/dataset"
        paths = os.listdir(dataset_dir_path)
        # PIL Image 转 Tensor
        transform = standard_transforms.ToTensor()
        dataset = []
        labelset = []
        for index in range(len(paths)):
            # 从 paths[] 中的文件名中提取出坐标
            tmp = paths[index][0:-4].split('_')
            labelset.append(torch.tensor([int(tmp[1]), int(tmp[2])]))
            # 将图片转化为 tensor
            image = Image.open(dataset_dir_path+"/"+paths[index])
            image_tensor = transform(image)
            dataset.append(image_tensor)
        # 合并两个 list 为 Tensor
        dataset = torch.stack(dataset).to(device)
        labelset = torch.stack(labelset).to(device)
        
        # 数据和标签
        self.x_data = dataset
        self.y_data = labelset
        # 数据集的长度
        self.length = len(self.y_data)
        
        
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]
    
    def __len__(self): 
        return self.length

def get_dataloader(batch_size, shuffle=True, num_workers=0, device='cuda'):
    # 实例化
    my_dataset = MyDataset(batch_size, device) 
    data_loader = DataLoader(dataset=my_dataset, # 要传递的数据集
                            batch_size=batch_size, #一个小批量数据的大小是多少
                            shuffle=shuffle, # 数据集顺序是否要打乱，一般是要的。测试数据集一般没必要
                            num_workers=num_workers) # 需要几个进程来一次性读取这个小批量数据，默认0，一般用0就够了，多了有时会出一些底层错误。
    return data_loader
