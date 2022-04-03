import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, padding,
                 use_activation=True,
                use_instance_norm=True):
        
        super().__init__()
        self.conv_block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, padding_mode='reflect'),
            nn.InstanceNorm2d(out_channels, affine=True) if use_instance_norm else nn.Identity(),
            nn.ReLU() if use_activation else nn.Identity()
        
        )
        
    def forward(self, x):
        return self.conv_block(x)
        
        

class ResBlock(nn.Module):
    def __init__(self, in_channels, kernel_size, stride, padding):
        super().__init__()
        self.res_block = nn.Sequential(
        ConvBlock(in_channels, in_channels, kernel_size, stride, padding),
        ConvBlock(in_channels, in_channels, kernel_size, stride, padding, use_activation=False)    
        
        )
        
    def forward(self, x):
        return x + self.res_block(x)
        


class TransformerNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            
            ConvBlock(3, 32, (9, 9), 1, 4), #32x256x256
            ConvBlock(32, 64, (3, 3), 2, 1), #64x128x128
            ConvBlock(64, 128, (3, 3), 2, 1), #128x64x64
            
            *[ResBlock(128, (3, 3), 1, 1) for i in range(5)], #128x64x64
            
            nn.Upsample(scale_factor=2), #128x128x128
            ConvBlock(128, 64, (3, 3), 1, 1), #64x128x128
 
            nn.Upsample(scale_factor=2), #64x256x256
            ConvBlock(64, 32, (3, 3), 1, 1), #32x256x256
            
            ConvBlock(32, 3, (9, 9), 1,  4, use_activation=False, use_instance_norm=False), #3x256x256
            
        
        )
        
    def forward(self, x):
        return self.model(x)