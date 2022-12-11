import torch
from mmaction.apis import init_recognizer, inference_recognizer
import sys

def predict(video_p):
	config_file = '/home/student/mmaction2/configs/recognition/tsn/tsn_r50_video_inference_1x1x3_100e_kinetics400_rgb.py'
	# download the checkpoint from model zoo and put it in `checkpoints/`
	checkpoint_file = '/home/student/Downloads/tsn_r50_1x1x3_100e_kinetics400_rgb_20200614-e508be42.pth'

	# assign the desired device.
	device = 'cpu' # or 'cpu'
	device = torch.device(device)

	 # build the model from a config file and a checkpoint file
	model = init_recognizer(config_file, checkpoint_file, device=device)

	# test a single video and show the result:
	video = video_p
	label = '/home/student/mmaction2/tools/data/kinetics/label_map_k400.txt'
	print(video)
	results = inference_recognizer(model, video)


	labels = open(label).readlines()
	labels = [x.strip() for x in labels]
	results = [(labels[k[0]], k[1]) for k in results]

	print(results)


predict(sys.argv[1])
