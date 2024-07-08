import torch
import torch.nn.init

# CNN Model
class CNN(torch.nn.Module):

    def __init__(self):
        super(CNN, self).__init__()
        self.keep_prob = 0.5
        # L1 ImgIn shape=(?, 28, 28, 1)
        #    Conv     -> (?, 28, 28, 32)
        #    Pool     -> (?, 14, 14, 32)
        self.layer1 = torch.nn.Sequential(
            torch.nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            torch.nn.PReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))
        # L2 ImgIn shape=(?, 14, 14, 32)
        #    Conv      ->(?, 14, 14, 64)
        #    Pool      ->(?, 7, 7, 64)
        self.layer2 = torch.nn.Sequential(
            torch.nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            torch.nn.PReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))
        # L3 ImgIn shape=(?, 7, 7, 64)
        #    Conv      ->(?, 7, 7, 128)
        #    Pool      ->(?, 4, 4, 128)
        self.layer3 = torch.nn.Sequential(
            torch.nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            torch.nn.PReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2, padding=1))

        # L4 FC 4x4x128 inputs -> 625 outputs
        # self.fc1 = torch.nn.Linear(4 * 4 * 128, 625, bias=True)
        self.fc1 = torch.nn.Linear(256*483, 625, bias=True)
        torch.nn.init.xavier_uniform_(self.fc1.weight)
        self.layer4 = torch.nn.Sequential(
            self.fc1,
            torch.nn.PReLU(),
            torch.nn.Dropout(p=1 - self.keep_prob))
        # L5 Final FC 625 inputs -> 10 outputs
        self.fc2 = torch.nn.Linear(625, 2, bias=True)
        torch.nn.init.xavier_uniform_(self.fc2.weight)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.view(out.size(0), -1)   # Flatten them for FC
        out = self.layer4(out)
        out = self.fc2(out)
        return out
    
class MyLoss(torch.nn.Module):
    def __init__(self):
        super(MyLoss, self).__init__()
    
    def get_loss(self, pos_raw, pos_predict):
        if abs(pos_raw[0]-pos_predict[0])<=20 and abs(pos_raw[1]-pos_predict[1])<=20:
            return 0
        else:
            return abs(pos_raw[0]-pos_predict[0])+abs(pos_raw[1]-pos_predict[1])+100

    def forward(self, pos_raw, pos_predict):
        loss = 0
        for a,b in zip(pos_raw, pos_predict):
            loss = loss + self.get_loss(a, b)
        return torch.tensor(float(loss),requires_grad=True)
    
def evaluate(pos_raw_s, pos_predict_s):
    judge = []
    for pos_raw, pos_predict in zip(pos_raw_s, pos_predict_s):
        if abs(pos_raw[0]-pos_predict[0])<=20 and abs(pos_raw[1]-pos_predict[1])<=20:
            judge.append(1)
        else:
            judge.append(0)
    return torch.Tensor(judge)

def init_weights(layer):
    # 如果为卷积层，使用正态分布初始化
    if type(layer) == torch.nn.Conv2d:
        torch.nn.init.normal_(layer.weight, mean=0, std=0.5)
    # 如果为全连接层，权重使用均匀分布初始化，偏置初始化为0.1
    elif type(layer) == torch.nn.Linear:
        torch.nn.init.uniform_(layer.weight, a=-0.1, b=0.1)
        torch.nn.init.constant_(layer.bias, 0.1)