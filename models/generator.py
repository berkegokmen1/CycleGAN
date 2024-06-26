# import torch
# import torch.nn as nn

from util.constants import Constants


# # c7sn - k-  a 7×7Convolution-InstanceNormReLU layer with k filters and stride n
# class Conv7StrNBlock(nn.Module):
#     def __init__(self, in_channels, out_channels, stride, **kwargs):
#         super().__init__()
#         self.conv = nn.Sequential(
#             nn.Conv2d(
#                 in_channels,
#                 out_channels,
#                 kernel_size=7,
#                 padding=3,
#                 stride=stride,
#                 padding_mode=Constants.PADDING_MODE,
#                 **kwargs
#             ),
#             nn.InstanceNorm2d(out_channels),
#             nn.ReLU(inplace=True),
#         )

#     def forward(self, x):
#         return self.conv(x)


# # d-k block -- a 3×3 Convolution-InstanceNorm-ReLU layer with k filters and stride 2
# class DownConvBlock(nn.Module):
#     def __init__(self, in_channels, out_channels, use_act=True, **kwargs):
#         super().__init__()
#         self.conv = nn.Sequential(
#             nn.Conv2d(in_channels, out_channels, padding_mode=Constants.PADDING_MODE, **kwargs),
#             nn.InstanceNorm2d(out_channels),
#             nn.ReLU(inplace=True) if use_act else nn.Identity(),
#         )

#     def forward(self, x):
#         return self.conv(x)


# # uk denotes a 3×3 fractional-strided-Convolution InstanceNorm-ReLUlayer with k filters and stride 1/2.
# class UpConvBlock(nn.Module):
#     def __init__(self, in_channels, out_channels, use_act=True, **kwargs):
#         super().__init__()
#         self.conv = nn.Sequential(
#             # We have tried to try other padding modes but only zeros is supported...
#             nn.ConvTranspose2d(in_channels, out_channels, padding_mode="zeros", **kwargs),
#             nn.InstanceNorm2d(out_channels),
#             nn.ReLU(inplace=True) if use_act else nn.Identity(),
#         )

#     def forward(self, x):
#         return self.conv(x)


# # R-k Block denotes a residual block that contains two 3×3 convolutional layers with the same number of filters on both layer.
# class ResidualBlock(nn.Module):
#     def __init__(self, channels):
#         super().__init__()
#         self.block = nn.Sequential(
#             DownConvBlock(channels, channels, kernel_size=3, padding=1),
#             DownConvBlock(channels, channels, use_act=False, kernel_size=3, padding=1),
#         )

#     def forward(self, x):
#         return x + self.block(x)


# # Generator, with 9 default residual block
# class Generator(nn.Module):
#     def __init__(self, img_channels, num_features=64, num_residuals=Constants.NUMBER_OF_RESIDUALS):
#         super().__init__()

#         # c7s1-64
#         self.initial = Conv7StrNBlock(img_channels, num_features, stride=1)

#         down_blocks = []

#         # d128
#         down_blocks.append(DownConvBlock(num_features, num_features * 2, kernel_size=3, stride=2, padding=1))

#         # d256
#         down_blocks.append(
#             DownConvBlock(
#                 num_features * 2,
#                 num_features * 4,
#                 kernel_size=3,
#                 stride=2,
#                 padding=1,
#             )
#         )
#         self.down_blocks = nn.ModuleList(down_blocks)

#         residual_blocks = []
#         for _ in range(num_residuals):
#             residual_blocks.append(ResidualBlock(num_features * 4))  # R256

#         # R256 * num_residuals
#         self.res_blocks = nn.Sequential(*residual_blocks)

#         up_blocks = []

#         # u128
#         up_blocks.append(
#             UpConvBlock(
#                 num_features * 4,
#                 num_features * 2,
#                 kernel_size=3,
#                 stride=2,
#                 padding=1,
#                 output_padding=1,
#             )
#         )

#         # u64
#         up_blocks.append(
#             UpConvBlock(
#                 num_features * 2,
#                 num_features * 1,
#                 kernel_size=3,
#                 stride=2,
#                 padding=1,
#                 output_padding=1,
#             )
#         )

#         self.up_blocks = nn.ModuleList(up_blocks)

#         # c7s1-3
#         self.last = Conv7StrNBlock(num_features * 1, img_channels, stride=1)

#     def forward(self, x):
#         x = self.initial(x)
#         for layer in self.down_blocks:
#             x = layer(x)
#         x = self.res_blocks(x)
#         for layer in self.up_blocks:
#             x = layer(x)
#         return torch.tanh(self.last(x))


# if __name__ == "__main__":
#     x = torch.randn((1, 3, 256, 256))
#     model = Generator(img_channels=3)
#     print(model(x).shape)


import torch
import torch.nn as nn

    

class DownSamplingConvolutionalBlock(nn.Module):
    def __init__(self, 
                in_channels: int,
                out_channels: int,
                add_activation: bool = True,
                *args,
                **kwargs,
            ):
        
        super().__init__()
        self.conv = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, padding_mode=Constants.PADDING_MODE, **kwargs),
                nn.InstanceNorm2d(out_channels),
                nn.ReLU(inplace=True) if add_activation else nn.Identity(),
            )
        
    def forward(self, x):
        return self.conv(x)
    


class UpSamplingConvolutionalBlock(nn.Module):
    def __init__(self, 
                in_channels: int,
                out_channels: int,
                add_activation: bool = True,
                *args,
                **kwargs,
            ):
        
        super().__init__()

        self.conv = nn.Sequential(
                nn.ConvTranspose2d(in_channels, out_channels, **kwargs),
                nn.InstanceNorm2d(out_channels),
                nn.ReLU(inplace=True) if add_activation else nn.Identity(),
            )
        
    def forward(self, x):
        return self.conv(x)


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.block = nn.Sequential(
            DownSamplingConvolutionalBlock(channels, channels, add_activation=True, kernel_size=3, padding=1),
            DownSamplingConvolutionalBlock(channels, channels, add_activation=False, kernel_size=3, padding=1),
        )

    def forward(self, x):
        return x + self.block(x)


class Generator(nn.Module):
    def __init__(
        self, img_channels: int, num_features: int = 64, num_residuals: int = 6
    ):
        """
        Generator consists of 2 layers of downsampling/encoding layer, 
        followed by 6 residual blocks for 128 × 128 training images 
        and then 3 upsampling/decoding layer. 
        
        The network with 6 residual blocks can be written as: 
        c7s1–64, d128, d256, R256, R256, R256, R256, R256, R256, u128, u64, and c7s1–3.
        """
        super().__init__()
        self.initial_layer = nn.Sequential(
            nn.Conv2d(
                img_channels,
                num_features,
                kernel_size=7,
                stride=1,
                padding=3,
                padding_mode="reflect",
            ),
            nn.InstanceNorm2d(num_features),
            nn.ReLU(inplace=True),
        )

        self.downsampling_layers = nn.ModuleList(
            [
                DownSamplingConvolutionalBlock(
                    num_features, 
                    num_features * 2,
                    kernel_size=3, 
                    stride=2, 
                    padding=1,
                ),
                DownSamplingConvolutionalBlock(
                    num_features * 2,
                    num_features * 4,
                    kernel_size=3,
                    stride=2,
                    padding=1,
                ),
            ]
        )

        self.residual_layers = nn.Sequential(
            *[ResidualBlock(num_features * 4) for _ in range(num_residuals)]
        )

        self.upsampling_layers = nn.ModuleList(
            [
                UpSamplingConvolutionalBlock(
                    num_features * 4,
                    num_features * 2,
                    kernel_size=3,
                    stride=2,
                    padding=1,
                    output_padding=1,
                ),
                UpSamplingConvolutionalBlock(
                    num_features * 2,
                    num_features * 1,
                    kernel_size=3,
                    stride=2,
                    padding=1,
                    output_padding=1,
                ),
            ]
        )

        self.last_layer = nn.Conv2d(
            num_features * 1,
            img_channels,
            kernel_size=7,
            stride=1,
            padding=3,
            padding_mode=Constants.PADDING_MODE,
        )

    def forward(self, x):
        x = self.initial_layer(x)

        for layer in self.downsampling_layers:
            x = layer(x)

        x = self.residual_layers(x)

        for layer in self.upsampling_layers:
            x = layer(x)

        return torch.tanh(self.last_layer(x))