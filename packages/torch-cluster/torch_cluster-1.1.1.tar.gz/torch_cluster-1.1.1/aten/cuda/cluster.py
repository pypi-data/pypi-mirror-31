import torch
import cluster_cuda

device = torch.device("cuda:0")


def grid_cluster(pos, size, start=None, end=None):
    start = pos.t().min(dim=1)[0] if start is None else start
    end = pos.t().max(dim=1)[0] if end is None else end
    return cluster_cuda.grid(pos, size, start, end)


pos = torch.tensor([[1, 1], [3, 3], [5, 5], [7, 7]], device=device)
size = torch.tensor([2, 2], device=device)
print('pos', pos.tolist())
print('size', size.tolist())
cluster = grid_cluster(pos, size)
print('result', cluster.tolist())
