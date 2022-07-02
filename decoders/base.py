import torch
from torch import nn
from torch.nn import functional


__all__ = [
    'DecoderSimpleBlock',
    'DecoderBasicBlock',
    'DecoderBottleneckBlock'
]


class DecoderSimpleBlock(nn.Module):
    def __init__(self, in_channels, out_channels, scale_factor=2, mode='nearest'):
        super(DecoderSimpleBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=(1, 1), bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )
        self.scale_factor = scale_factor
        self.mode = mode

    def forward(self, x, skip=None):
        # x = functional.interpolate(x, scale_factor=self.scale_factor, mode=self.mode)
        x = self.block(x)
        return x


class DecoderBasicBlock(nn.Module):
    def __init__(self, in_channels, skip_channels, out_channels, scale_factor=2, mode='nearest'):
        super(DecoderBasicBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels + skip_channels, out_channels, kernel_size=(3, 3), padding=(1, 1), bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=(3, 3), padding=(1, 1), bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )
        self.scale_factor = scale_factor
        self.mode = mode

    def forward(self, x, skip=None):
        x = functional.interpolate(x, scale_factor=self.scale_factor, mode=self.mode)
        if skip is not None:
            x = torch.cat(tensors=(x, skip), dim=1)
        x = self.block(x)
        return x


class DecoderBottleneckBlock(nn.Module):
    def __init__(self, in_channels, skip_channels, out_channels, scale_factor=2, mode='nearest'):
        super(DecoderBottleneckBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels + skip_channels, out_channels // 2, kernel_size=(1, 1), padding=(0, 0), bias=False),
            nn.BatchNorm2d(out_channels // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels // 2, out_channels // 2, kernel_size=(3, 3), padding=(1, 1), bias=False),
            nn.BatchNorm2d(out_channels // 2),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels // 2, out_channels, kernel_size=(3, 3), padding=(1, 1), bias=False),
            nn.BatchNorm2d(out_channels),
        )
        self.relu = nn.ReLU(inplace=True)
        self.scale_factor = scale_factor
        self.mode = mode

    def forward(self, x, skip=None):
        x = functional.interpolate(x, scale_factor=self.scale_factor, mode=self.mode)
        if skip is not None:
            x = torch.cat(tensors=(x, skip), dim=1)
        x = self.block(x) + x
        x = self.relu(x)
        return x