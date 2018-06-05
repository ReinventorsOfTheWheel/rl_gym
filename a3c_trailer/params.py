# parameters for the training setup
RUN_TIME = 12000000
NUM_EPISODES = 80000
AGENTS = 32
OPTIMIZERS = 2
WAIT_ON_ACTION = 0.001

# parameters for the agent
INITIAL_EXPLORATION = 1.0
FINAL_EXPLORATION = .1
FINAL_EXPLORATION_ACTION = 100000
EXPLORATION_STEP = (INITIAL_EXPLORATION - FINAL_EXPLORATION) / FINAL_EXPLORATION_ACTION

# parameters for the discount
NUM_STEPS = 20
GAMMA = 0.99
LAMBDA = 0.75
REWARD_SCALE = 1e-2

# parameters for the neural network
FRAME_SIZE = (128, 128)
INPUT_SHAPE = (*FRAME_SIZE, 3)
NUM_ACTIONS = 6
MIN_BATCH = 32
MAX_BATCH = 5 * MIN_BATCH

# parameters for the training
LEARNING_RATE = 1e-4
DECAY = 0.99
LOSS_VALUE = .5
LOSS_ENTROPY = .02
GRADIENT_NORM_CLIP = 25.

# parameters to control tensorflow behaviour (and logging)
TF_ALLOW_GROWTH = True
TF_LOG_DEVICE_PLACEMENT = False
