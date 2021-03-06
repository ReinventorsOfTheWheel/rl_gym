# parameters for the training setup
# the parameters exposed here are taken from the deepmind paper
# but their values are changed
# do not assume that this is an optimal setup

RETRAIN = True

# parameters for the structure of the neural network
NUM_ACTIONS = 4
FRAME_STACK = 2  # number of consecutive frames to stack as input for the network
BATCH_SIZE = 32

# parameters for the reinforcement process
GAMMA = 0.99  # discount factor for future updates
REWARD_SCALE = 1

# parameters for the optimizer
LEARNING_RATE = 0.00025
RHO = 0.95
EPSILON = 0.01
GRADIENT_NORM_CLIP = None  # switched off
L2_REG_CONV = 0  # 1e-3
L2_REG_FULLY = 0  # 1e-3

# parameters for the training
TOTAL_INTERACTIONS = int(3e6)  # after this many interactions, the training stops
TRAIN_SKIPS = 2  # interact with the environment X times, update the network once

TARGET_NETWORK_UPDATE_FREQ = 1e4  # update the target network every X training steps
SAVE_NETWORK_FREQ = 5  # save every Xth version of the target network

# parameters for interacting with the environment
INITIAL_EXPLORATION = 1.0  # initial chance of sampling a random action
FINAL_EXPLORATION = 0.1  # final chance
FINAL_EXPLORATION_FRAME = int(TOTAL_INTERACTIONS // 2)  # frame at which final value is reached
EXPLORATION_STEP = (INITIAL_EXPLORATION - FINAL_EXPLORATION) / FINAL_EXPLORATION_FRAME

REPEAT_ACTION_MAX = 10  # maximum number of repeated actions before sampling random action

# parameters for the memory
REPLAY_MEMORY_SIZE = int(2 ** 20)
REPLAY_START_SIZE = int(5e4)
MEMORY_MAPPED = True
ERROR_BIAS = 0.05
ERROR_POW = 0.7
DEFAULT_PRIO = 1

# parameters for the behaviour of tensorflow
TF_ALLOW_GROWTH = True
TF_LOG_DEVICE_PLACEMENT = False
