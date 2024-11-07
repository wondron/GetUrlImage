import torch
import torch.nn as nn

class InvertedResidual(nn.Module):
    def __init__(self, in_channels, out_channels, stride, expand_ratio):
        super(InvertedResidual, self).__init__()
        hidden_dim = in_channels * expand_ratio
        self.use_res_connect = stride == 1 and in_channels == out_channels

        layers = []
        if expand_ratio != 1:
            layers.append(nn.Conv2d(in_channels, hidden_dim, 1, bias=False))
            layers.append(nn.BatchNorm2d(hidden_dim))
            layers.append(nn.ReLU6(inplace=True))
        
        layers.extend([
            nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False),
            nn.BatchNorm2d(hidden_dim),
            nn.ReLU6(inplace=True),
            nn.Conv2d(hidden_dim, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
        ])
        
        self.conv = nn.Sequential(*layers)

    def forward(self, x):
        if self.use_res_connect:
            return x + self.conv(x)
        else:
            return self.conv(x)

class MobileNetV2(nn.Module):
    def __init__(self, num_classes=1000, width_mult=1.0):
        super(MobileNetV2, self).__init__()
        block = InvertedResidual
        input_channel = 32
        feature_channel = 512
        last_channel = 1280
        
        # 定义网络结构
        inverted_residual_setting = [
            # t, c, n, s
            [1, 16, 1, 1],
            [6, 24, 2, 2],
            [6, 32, 3, 2],
            [6, 64, 4, 2],
            [6, 96, 3, 1],
            [6, 160, 3, 2],
            [6, 320, 1, 1],
        ]

        # 构建第一层
        self.features = [nn.Conv2d(3, input_channel, 3, stride=2, padding=1, bias=False),
                         nn.BatchNorm2d(input_channel),
                         nn.ReLU6(inplace=True)]
        
        # 构建中间的Inverted Residual块
        for t, c, n, s in inverted_residual_setting:
            output_channel = int(c * width_mult)
            for i in range(n):
                stride = s if i == 0 else 1
                self.features.append(block(input_channel, output_channel, stride, expand_ratio=t))
                input_channel = output_channel
        
        # 构建最后一层
        self.features.append(nn.Conv2d(input_channel, last_channel, 1, bias=False))
        self.features.append(nn.BatchNorm2d(last_channel))
        self.features.append(nn.ReLU6(inplace=True))
        
        self.features = nn.Sequential(*self.features)
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(last_channel, feature_channel),
            nn.Linear(feature_channel, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = x.mean([2, 3])  # 全局平均池化
        x = self.classifier(x)
        return x

# 创建MobileNetV2模型
model = MobileNetV2()
print(model)