All contributions by Kevin Lok:
Copyright (c) 2018 - 2018, Kevin Lok Ka Wing.All rights reserved.
Licensed under the MIT

Version 1.9.x:
1) Add Major Model Architecture templates:
1.1) Alexnet
1.2) VGG
1.3) GoogLeNet
1.4) Resnet

2) Add logs to each models

IMPORTANT:
Changes of Input argurements at collector.buildFromDF
FROM collector.buildFromDF(orgDF, batchNum=1, batchSize=20000) TO collector.buildFromDF(orgDF,cfg.dataCfg, batchNum=1, batchSize=20000)
will result to error while excute the py after you upgrade from 1.8.x to 1.9.x only.

