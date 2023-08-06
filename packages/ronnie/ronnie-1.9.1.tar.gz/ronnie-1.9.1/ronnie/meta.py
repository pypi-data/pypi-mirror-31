#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# LICENSE 	   : MIT
# Version      : 1.9.x
class Meta:
	PROJECT_PATH		= "PROJECT_PATH"
	SYS					= "SYS"
	DATA_IMGXs			= "DATA_IMGXS"
	DATA_INPUTXs		= "DATA_INPUTXs"
	DATA_LABELYs		= "DATA_LABELYS"
	DATA_IMGX_WIDTH		= "DATA_IMGX_WIDTH"
	DATA_IMGX_HEIGHT	= "DATA_IMGX_HEIGHT"
	DATA_IMGX_CHANNEL	= "DATA_IMGX_CHANNEL"
	DATA_LABELY_CLASSs	= "DATA_LABELY_CLASSs"
	
	BASIC_CONFIG		= "BASIC_CONFIG"
	DATA_CONFIG			= "DATA_CONFIG"
	TRAIN_CONFIG		= "TRAIN_CONFIG"
	EVAL_CONFIG			= "EVAL_CONFIG"
	
	TOWER_TYPE			= "TOWER_TYPE"

	CONV_LAYERs			= "CONVOLUTIONLAYERs"
	CONV_LAYER			= "CONVOLUTIONLAYER"
	CON_KERNAL 			= "CON_KERNAL"
	CON_FILTER 			= "CON1_FILTER"
	CON_PADDING 		= "PADDING"
	CON_STRIDE			= "CON_STRIDE"
	
	POOL_TYPE			= "POOL_TYPE"
	POOL_MAX			= "POOL_MAX"
	POOL_AVG			= "POOL_AVG"
	POOL_LAYERs			= "POOLAYERs"
	POOL_LAYER			= "POOLAYER"
	POOL_KERNAL			= "POOL_KERNAL"
	POOL_STRIDE 		= "POOL_STRIDE"
	
	INCEPT_LAYER		= "INCEPT_LAYER"
	RESNET_LAYER		= "RESNET_LAYER"
	
	BATCHNORM_LAYER     = "BATCHNORM_LAYER"
	MOMENTUM			= "MOMENTUM"
	EPSILON				= "EPSILON"
	CENTER				= "CENTER"
	SCALE				= "SCALE"
	FUSED				= "FUSED"
	AXIS				= "AXIS"
	
	INCEPT_TOWER		= "INCEPT_TOWER"
	RES_TOWER			= "RES_TOWER"
	
	TOWER_BLOCKS		= "TOWER_BLOCKS"
	INCEPTIONV1			= "GoogLeNet-INCEPTIONV1"

	
	PADDING_TYPE		= "PADDING_TYPE"
	PADDING_SAME		= "same"
	PADDING_VALID		= "valid"
	
	DENSE_LAYERs 		= "DENSE_LAYERs" 
	DENSE_LAYER 		= "DENSE_LAYER" 
	MODEL_LEARNRATE 	= "LEARNRATE"
	MODEL_DROPOUTRATE 	= "DROPOUTRATE"
	MODEL_NEURON 		= "NEURON"
	MODEL				= "MODEL"
	MODEL_NAME			= "MODEL_NAME"
	MODEL_PATH			= "MODEL_PATH"
	MODEL_EXPORT_FILE 	= "MODEL_EXPORT_FILE" 
	MODEL_EXPORT_ENCODE	= "MODEL_EXPORT_ENCODE"
	
	MODEL_ACT 			= "ACTIVATION"
	MODEL_ACT_RELU 		= "RELU"
	MODEL_ACT_SIGMOID 	= "SIGMOID"
	MODEL_ACT_TANH 		= "TANH"
	
	MERGE_TYPE			= "MERGE_TYPE"
	MERGE_ADD			= "MERGE_ADD"
	MERGE_CONCATE		= "MERGE_CONCATE"
	
	
	CONCATE_BLOCKS		= "CONCATE_BLOCKS"
	CONCATE_BLOCK		= "CONCATE_BLOCK"
	
	LAYER_LINKs			= "LAYER_LINKS"
	LAYER_TYPE			= "LAYER_TYPE"
	LAYER_SPEC			= "LAYER_SPEC"
	LAYER_BRICKS		= "LAYER_BRICKS"
	LAYER_BRICK			= "LAYER_BRICK"
	
	SHUFFLE 			= "SHUFFLE" 
	
	OPTIMIZER			= "OPTIMIZER"
	OPTIMIZER_ADAM		= "OPTIMIZER_ADAM"
	OPTIMIZER_GD		= "OPTIMIZER_GD"
	
	LOG_LEVEL_CRITICAL 	= "CRITICAL"
	LOG_LEVEL_ERROR 	= "ERROR"
	LOG_LEVEL_WARNING 	= "WARNING"
	LOG_LEVEL_INFO 		= "INFO"
	LOG_LEVEL_DEBUG 	= "DEBUG"
	LOG_LEVEL_NOTSET 	= "NOTSET"
	
	
	def __init__(self):
		return
	
	class MetaError(TypeError) : pass
	class MetaCaseError(MetaError):pass
	
	def __setattr__(self, name, value):
		if name in self.__dict__:
			raise(self.MetaError, "It is a Constant CLASS")
		else:
			raise(self.MetaError, "It is a Constant CLASS")
		
		#if not name.isupper():
		#    raise self.ConstCaseError, 'const "%s" is not all letters are capitalized' %name
		#self.__dict__[name] = value
	
	
	def __delattr__(self, name):
		if self.__dict__.has_key(name):
			raise(self.MetaError, "WARN: It's is a Constant" % name)
	
import sys
sys.modules[__name__] = Meta()
