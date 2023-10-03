#!/bin/bash
#SBATCH --account=vision
#SBATCH --partition=svl --qos=normal
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=30G
#SBATCH --gres=gpu:1

#SBATCH --job-name="mini_bh_prelim"
#SBATCH --output=logs/mini_bh_train_slurm_%A.out
#SBATCH --error=logs/mini_bh_train_slurm_%A.err
####SBATCH --mail-user=emilyjin@stanford.edu
####SBATCH --mail-type=ALL

# list out some useful information (optional)
echo "SLURM_JOBID="$SLURM_JOBID
echo "SLURM_JOB_NODELIST"=$SLURM_JOB_NODELIST
echo "SLURM_NNODES"=$SLURM_NNODES
echo "SLURMTMPDIR="$SLURMTMPDIR
echo "working directory = "$SLURM_SUBMIT_DIR


##########################################
# Setting up virtualenv / conda / docker #
##########################################
module load anaconda3
source activate behavior
echo "conda env activated"


##############################################################
# Setting up LD_LIBRARY_PATH or other env variable if needed #
##############################################################
export LD_LIBRARY_PATH=/usr/local/cuda-9.1/lib64:/usr/lib/x86_64-linux-gnu
echo "Working with the LD_LIBRARY_PATH: "$LD_LIBRARY_PATH


cd /vision/u/emilyjin/mini_behavior/

echo "running command: python train_rl_agent.py --task InstallingAPrinter"
python train_rl_agent.py --task InstallingAPrinter

echo "running command: python train_rl_agent.py --task PuttingAwayDishesAfterCleaning"
python train_rl_agent.py --task PuttingAwayDishesAfterCleaning

echo "running command: python train_rl_agent.py --task WashingPotsAndPans"
python train_rl_agent.py --task WashingPotsAndPans

echo "Done"
