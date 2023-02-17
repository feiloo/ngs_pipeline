 #!/bin/bash
miniwdl run veppan.wdl sample=/data/vep_109/input/E12491.vcf cache=/data/vep_109/cache --verbose --cfg pancancer_vep.cfg
