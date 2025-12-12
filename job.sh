#!/bin/bash

#SBATCH --partition={{ partition }}          # Partition (job queue)

#SBATCH --requeue                 # Return job to the queue if preempted

#SBATCH --job-name={{ filename }}       # Assign a short name to your job

#SBATCH --nodes={{ nodes }}                 # Number of nodes you require

#SBATCH --ntasks={{ tasks }}                # Total # of tasks across all nodes

#SBATCH --cpus-per-task={{ cpus }}         # Cores per task (>1 if multithread tasks)

#SBATCH --mem={{ mem }}                # Real memory (RAM) required (MB)

#SBATCH --time={{ time }}           # Total run time limit (HH:MM:SS)

#SBATCH --output={{ filename }}.out  # STDOUT output file

#SBATCH --error={{ filename }}.err   # STDERR output file (optional)

cd /scratch/$USER

chmod u+x ./main.sh

srun ./main.sh {{ filename }}
