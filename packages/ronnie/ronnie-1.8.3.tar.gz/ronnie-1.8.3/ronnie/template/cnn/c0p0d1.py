import ronnie.meta 					as meta

conLyrs = [
			]
poolLyrs = [
			]
denseLyrs = [
			{	#2nd Dense Layer
				meta.LAYER_TYPE			: meta.DENSE_LAYER,
				meta.MODEL_NEURON		:10,
				meta.MODEL_ACT			:'',
				meta.MODEL_DROPOUTRATE	:0.4},
			]
#build tuple encoder/decoder to convert the tuple					
modelTower =(     #call LAYER_BLOCK sounds more better, reconsider the naming
				{	meta.LAYER_SPEC		: denseLyrs[0],
					meta.LAYER_BRICK	: "",
				},
			)
	
modelDef = {    meta.MODEL_NAME			: "",
				meta.MODEL				: "",
				meta.BASIC_CONFIG		: "", 
				meta.DATA_CONFIG		: "",
				meta.TRAIN_CONFIG 		: "",
				meta.EVAL_CONFIG 		: "",
			}