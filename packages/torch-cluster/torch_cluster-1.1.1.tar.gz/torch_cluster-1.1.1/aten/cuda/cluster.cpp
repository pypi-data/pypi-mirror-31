#include <torch/torch.h>

#define CHECK_CUDA(x) AT_ASSERT(x.type().is_cuda(), #x "must be a CUDA tensor")

at::Tensor grid(at::Tensor pos, at::Tensor size, at::Tensor start, at::Tensor end) {
  CHECK_CUDA(pos); CHECK_CUDA(size); CHECK_CUDA(start); CHECK_CUDA(end);

  return pos;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
  m.def("grid", &grid, "Grid (CUDA)");
}
