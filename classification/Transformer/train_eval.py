# coding: UTF-8
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn import metrics
import time
from utils import get_time_dif
from tensorboardX import SummaryWriter

def train(config, model, vocab, loss_weight, train_iter, dev_iter, test_iter, train_iter_labeled, dev_iter_labeled, test_iter_labeled):
    start_time = time.time()
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)

    # 学习率指数衰减，每次epoch：学习率 = gamma * 学习率
    # scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9)
    total_batch = 0  # 记录进行到多少batch
    dev_best_loss = float('inf')
    last_improve = 0  # 记录上次验证集loss下降的batch数
    flag = False  # 记录是否很久没有效果提升
    writer = SummaryWriter(log_dir=config.log_path + '/' + time.strftime('%m-%d_%H.%M', time.localtime()))
    for epoch in range(config.num_epochs):
        print('Epoch [{}/{}]'.format(epoch + 1, config.num_epochs))
        # scheduler.step() # 学习率衰减
        for _, (trains, _) in enumerate(train_iter):
            input, Y, cover = generate_cover(trains[0], vocab, config)

            outputs = model(input, cover=cover)
            model.zero_grad()
            loss = F.cross_entropy(outputs, Y, weight=loss_weight)
            loss.backward()
            optimizer.step()
            if total_batch % 100 == 0:
                # 每多少轮输出在训练集和验证集上的效果
                true = Y.data.cpu()
                predic = torch.max(outputs.data, 1)[1].cpu()
                train_acc = metrics.accuracy_score(true, predic)
                dev_acc, dev_loss = evaluate(config, model, vocab, dev_iter, config.vocab_list, loss_weight)
                if dev_loss < dev_best_loss:
                    dev_best_loss = dev_loss
                    # torch.save(model.state_dict(), config.save_path+'_Dacc_'+str(int(dev_acc*100))+'_'+str(epoch)+'_'+str(total_batch)+'.ckpt')
                    torch.save(model, config.save_path+'_Dacc_'+str(int(dev_acc*100))+'_'+str(epoch)+'_'+str(total_batch)+'.pth')
                    improve = '*'
                    last_improve = total_batch
                else:
                    improve = ''
                time_dif = get_time_dif(start_time)
                print('RecvIter: ', total_batch, \
                      ', Train Loss: ', round(loss.item(), 4), \
                      ', Train Acc: ', round(train_acc, 3), \
                      ', Val Loss: ',  round(dev_loss, 4), \
                      ', Val Acc: ', round(dev_acc, 3), \
                      ', Time: ', time_dif, improve)
                # msg = 'Iter: {0:>6},  Train Loss: {1:>5.2},  Train Acc: {2:>6.2%},  Val Loss: {3:>5.2},  Val Acc: {4:>6.2%},  Time: {5} {6}'
                # print(msg.format(total_batch, loss.item(), train_acc, dev_loss, dev_acc, time_dif, improve))
                writer.add_scalar("loss/train", loss.item(), total_batch)
                writer.add_scalar("loss/dev", dev_loss, total_batch)
                writer.add_scalar("acc/train", train_acc, total_batch)
                writer.add_scalar("acc/dev", dev_acc, total_batch)
                model.train()
            if total_batch % 100 == 0:
                avg_acc = 0
                sum = 0
                for _, (trains, Y) in enumerate(train_iter_labeled):
                    outputs = model(trains[0], recover_or_classify='classify')
                    model.zero_grad()
                    loss = F.cross_entropy(outputs, Y)
                    loss.backward()
                    optimizer.step()
                    Y = Y.data.cpu().numpy()
                    predic = torch.max(outputs.data, 1)[1].cpu()
                    train_acc = metrics.accuracy_score(Y, predic)
                    avg_acc += train_acc
                    sum += 1
                # print('Train classification mean accuracy:', avg_acc/sum)
                test_acc, test_loss = evaluate(config, model, vocab, dev_iter_labeled, config.class_list)
                # print('Validation classification mean accuracy:', test_acc)
                print('ClsfIter: ', total_batch, \
                      ', Train Loss: ', round(loss.item(), 4), \
                      ', Train Acc: ', round(avg_acc/sum, 3), \
                      ', Val Loss: ',  round(test_loss, 4), \
                      ', Val Acc: ', round(test_acc, 3), \
                      ', Time: ', time_dif, improve)
                writer.add_scalar("loss_clf/train", loss.item(), total_batch)
                writer.add_scalar("loss_clf/dev", test_loss, total_batch)
                writer.add_scalar("acc_clf/train", train_acc, total_batch)
                writer.add_scalar("acc_clf/dev", test_acc, total_batch)
            total_batch += 1
            if total_batch - last_improve > config.require_improvement:
                # 验证集loss超过1000batch没下降，结束训练
                print("No optimization for a long time, auto-stopping...")
                flag = True
                break
        if flag:
            break
    writer.close()
    test(config, model, vocab, test_iter, loss_weight, config.vocab_list)


def test(config, model, vocab, test_iter, loss_weight, class_list):
    # test
    # model.load_state_dict(torch.load(config.save_path))
    model.eval()
    start_time = time.time()
    test_acc, test_loss, test_report, test_confusion = evaluate(config, model, vocab, test_iter, class_list, loss_weight, test=True)
    msg = 'Test Loss: {0:>5.2},  Test Acc: {1:>6.2%}'
    print(msg.format(test_loss, test_acc))
    # print("Precision, Recall and F1-Score...")
    # print(test_report)
    print("Confusion Matrix...")
    print(test_confusion)
    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)


def evaluate(config, model, vocab, data_iter, class_list, loss_weight=None, test=False):
    model.eval()
    loss_total = 0
    predict_all = np.array([], dtype=int)
    labels_all = np.array([], dtype=int)
    with torch.no_grad():
        for _, (texts, Y) in enumerate(data_iter):
            if len(class_list)!=2:
                input, Y, cover = generate_cover(texts[0], vocab, config)
                outputs = model(input, cover=cover)
                loss = F.cross_entropy(outputs, Y, weight=loss_weight)
            else:
                outputs = model(texts[0], recover_or_classify='classify')
                loss = F.cross_entropy(outputs, Y)
            loss_total += loss.item()
            Y = Y.data.cpu().numpy()
            predic = torch.max(outputs.data, 1)[1].cpu().numpy()
            labels_all = np.append(labels_all, Y)
            predict_all = np.append(predict_all, predic)

    acc = metrics.accuracy_score(labels_all, predict_all)
    if test:
        report = metrics.classification_report(labels_all, predict_all, labels=range(len(class_list)), target_names=class_list, digits=4, zero_division=0)
        confusion = metrics.confusion_matrix(labels_all, predict_all)
        return acc, loss_total / len(data_iter), report, confusion
    return acc, loss_total / len(data_iter)

def generate_cover(raw_input, vocab, config):
    cover = torch.zeros(raw_input.size(0), raw_input.size(1), device=config.device, requires_grad=False)
    cover[:,0] = 1
    for i in range(raw_input.size(0)):
        cover[i,:] = cover[i,torch.randperm(cover.size(1))]
    input = (raw_input * (1-cover)).long()
    input = input + (cover*vocab['<MASK>']).long()
    choose = torch.nonzero(cover).to(config.device)
    Y = raw_input[choose[:,0], choose[:,1]].long()
    return input, Y, cover
