import torch
import torch.nn as nn
import bm3d
import numpy as np

def tensor2array(img):
    img = img.cpu().detach().numpy()
    img = np.transpose(img, (1, 2, 0))
    return img

def array2tensor(img):
    return torch.from_numpy(img).permute(2, 0, 1)

class Denoiser(nn.Module):
    def __init__(self, denoiser_name, device, n_channels=3, ckpt_path=None):
        '''
        '''
        super(Denoiser, self).__init__()
        self.denoiser_name = denoiser_name
        self.device = device
        if self.denoiser_name == 'drunet':
            from deepinv.diffops.models.drunet import UNetRes
            self.model = UNetRes(in_channels=n_channels+1, out_channels=n_channels)
            self.model.load_state_dict(torch.load(ckpt_path), strict=True)
            self.model.eval()
            for _, v in self.model.named_parameters():
                v.requires_grad = False
            self.model = self.model.to(device)
        
    def forward(self, x, sigma):
        if self.denoiser_name == 'BM3D':            #x = torch.cat((x, torch.tensor([sigma]).to(self.device).repeat(1, 1, x.shape[2], x.shape[3])), dim=1)
            return torch.cat([array2tensor(bm3d.bm3d(tensor2array(xi), sigma)) for xi in x])
        elif self.denoiser_name == 'drunet':
            noise_level_map = torch.FloatTensor(x.size(0), 1, x.size(2), x.size(3)).fill_(sigma).to(self.device)
            x = torch.cat((x, noise_level_map), 1)
            x = self.model(x)
            return x
        else: 
            raise Exception("The denoiser chosen doesn't exist")