from .codeepneat_module_densedropout import CoDeepNEATModuleDenseDropout
from .codeepneat_module_conv2dmaxpool2ddropout import CoDeepNEATModuleConv2DMaxPool2DDropout

MODULES = {
    'DenseDropout': CoDeepNEATModuleDenseDropout,
    'Conv2DMaxPool2DDropout': CoDeepNEATModuleConv2DMaxPool2DDropout
}
