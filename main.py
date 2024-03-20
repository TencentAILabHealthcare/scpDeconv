import os
import sys
# sys.path.append('/apdcephfs/private_gelseywang/scDeconvolution/scpDeconv')
# os.chdir('/apdcephfs/private_gelseywang/scDeconvolution/Script/git/scpDeconv')
import argparse
import options
from model.refer_mixup import *
from model.AEimpute_model import *
from model.DANN_model import *
from model.utils import *

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, default='murine_cellline', help='The name of benchmarking datasets')
args = parser.parse_args()

def main():
	dataset = args.dataset
	### Start Running scpDeconv ###
	print("------Start Running scpDeconv------")
	opt = options.get_option_list(dataset = dataset)

	### Run Stage 1 ###
	print("------Start Running Stage 1 : Mixup reference------")
	model_mx = ReferMixup(opt)
	source_data, target_data = model_mx.mixup()
	print("The dim of source data is :")
	print(source_data.shape)
	print("The dim of target data is :")
	print(target_data.shape)
	print("Stage 1 : Mixup finished!")

	### Run Stage 2 ###
	print("------Start Running Stage 2 : Training AEimpute model------")
	model_im = AEimpute(opt)
	source_recon_data = model_im.train(source_data, target_data)
	print("Stage 2 : AEimpute model training finished!")

	### Run Stage 3 ###
	print("------Start Running Stage 3 : Training DANN model------")
	model_da = DANN(opt)
	model_da.train(source_recon_data, target_data) 
	print("Stage 3 : DANN model training finished!")

	### Run Stage 4 ###
	print("------Start Running Stage 4 : Inference for target data------")
	if opt['target_type'] == "simulated":
	    final_preds_target, ground_truth_target = model_da.prediction()
	    SavePredPlot(opt['SaveResultsDir'], final_preds_target, ground_truth_target)
	    final_preds_target.to_csv(os.path.join(opt['SaveResultsDir'], "target_predicted_fractions.csv"))

	elif opt['target_type'] == "real":
	    final_preds_target, _ = model_da.prediction()
	    final_preds_target.to_csv(os.path.join(opt['SaveResultsDir'], "target_predicted_fraction.csv"))
	print("Stage 4 : Inference for target data finished!")

if __name__ == "__main__":
    main()
