"""Small semantic-segmentation network shared by lesion training and inference.

It is intentionally a project-local research model.  A checkpoint is never
treated as lesion evidence unless its accompanying manifest and test report
show that it was trained on real pixel annotations.
"""

from __future__ import annotations

import torch
from torch import nn


class _ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return self.layers(value)


class LesionSegmentationNet(nn.Module):
    """Compact U-Net-style multi-label segmentation model.

    Each output channel corresponds to one explicitly annotated lesion class;
    this is not a classifier CAM or a generated heatmap.
    """

    architecture = "lesion-unet-lite-v1"

    def __init__(self, num_classes: int, base_channels: int = 24) -> None:
        super().__init__()
        if num_classes < 1:
            raise ValueError("病灶分割模型至少需要一个标签类别。")
        self.encoder1 = _ConvBlock(3, base_channels)
        self.pool1 = nn.MaxPool2d(2)
        self.encoder2 = _ConvBlock(base_channels, base_channels * 2)
        self.pool2 = nn.MaxPool2d(2)
        self.bottleneck = _ConvBlock(base_channels * 2, base_channels * 4)
        self.up2 = nn.ConvTranspose2d(base_channels * 4, base_channels * 2, kernel_size=2, stride=2)
        self.decoder2 = _ConvBlock(base_channels * 4, base_channels * 2)
        self.up1 = nn.ConvTranspose2d(base_channels * 2, base_channels, kernel_size=2, stride=2)
        self.decoder1 = _ConvBlock(base_channels * 2, base_channels)
        self.head = nn.Conv2d(base_channels, num_classes, kernel_size=1)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        encoder1 = self.encoder1(images)
        encoder2 = self.encoder2(self.pool1(encoder1))
        bottleneck = self.bottleneck(self.pool2(encoder2))
        decoder2 = self.decoder2(torch.cat((self.up2(bottleneck), encoder2), dim=1))
        decoder1 = self.decoder1(torch.cat((self.up1(decoder2), encoder1), dim=1))
        return self.head(decoder1)
