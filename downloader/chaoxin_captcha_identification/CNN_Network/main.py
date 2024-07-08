import torch
import torch.nn.init
from dataloader import get_dataloader
from model import CNN, MyLoss, evaluate, init_weights
import time
import os

device = 'cuda:1'# if torch.cuda.is_available() else 'cpu'

# for reproducibility
torch.manual_seed(777)
if device == 'cuda:1':
    torch.cuda.manual_seed_all(777)
    torch.cuda.set_device('cuda:1')
    device = torch.device('cuda:1')

# parameters
learning_rate = 0.001
training_epochs = 500000
batch_size = 100

# dataset loader
print("Loading dataset...")
dataloader = get_dataloader(batch_size, shuffle=True, num_workers=0, device=device)
print("Dataset loaded, size ", len(dataloader), ".")

# 加载或初始化模型
load_or_not = False
if load_or_not:
    try:
        model = torch.load(r"/home/liangzida/workspace/Python/ZhongYi/chaoxin/CNN_Network/CNN.pth", map_location=device)
        print("Previous model read.")
    except:
        model = CNN().to(device)
        model.apply(init_weights)
        print("New model created.")
else:
    # instantiate CNN model
    model = CNN().to(device)
    model.apply(init_weights)
    print("New model created.")

# define cost/loss & optimizer
# criterion = MyLoss().to(device)
criterion = torch.nn.PoissonNLLLoss().to(device)
# criterion = torch.nn.CrossEntropyLoss().to(device)    # Softmax is internally computed.
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# train my model
total_batch = len(dataloader)
model.train()    # set the model to train mode (dropout=True)
print('Learning started. It takes sometime.')

start_time = time.time()
for epoch in range(training_epochs):
    avg_cost = 0

    for X, Y in dataloader:
        X = X.to(device)
        Y = Y.to(device)

        optimizer.zero_grad()
        hypothesis = model(X)
        cost = criterion(hypothesis, Y)
        cost.backward()
        optimizer.step()

        avg_cost += cost / total_batch

    print('[Epoch: {:>4}] cost = {:>.9}'.format(epoch + 1, avg_cost), ". Time consumption: ", time.time()-start_time)
    torch.save(model, r"/home/liangzida/workspace/Python/ZhongYi/chaoxin/CNN_Network/CNN.pth")
    start_time = time.time()

torch.save(model, r"/home/liangzida/workspace/Python/ZhongYi/chaoxin/CNN_Network/CNN.pth")
print('Learning Finished!')

# Test model and check accuracy
with torch.no_grad():
    model.eval()    # set the model to evaluation mode (dropout=False)

    # 获取100个测试图像
    for x, y in dataloader:
        x_data = x
        y_data = y
        break
    # 这里不对
    X_test = x_data.view(len(x_data), 1, 360, 160).float().to(device)
    Y_test = y_data.to(device)

    prediction = model(X_test)
    # correct_prediction = torch.argmax(prediction, 1) == Y_test
    correct_prediction = evaluate(prediction, Y_test)
    accuracy = correct_prediction.float().mean()
    print('Accuracy:', accuracy.item())