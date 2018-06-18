# parameters for the training setup
ENV_NAME = 'CartPole-v0'
RUN_TIME = 120
AGENTS = 8
OPTIMIZERS = 2
WAIT_ON_ACTION = 0.001

# parameters for the agent
INITIAL_EXPLORATION = 0.4
FINAL_EXPLORATION = .15
FINAL_EXPLORATION_ACTION = 75000
EXPLORATION_STEP = (INITIAL_EXPLORATION - FINAL_EXPLORATION) / FINAL_EXPLORATION_ACTION

# parameters for the discount
GAMMA = 0.99
NUM_STEPS = 8
GAMMA_N = GAMMA ** NUM_STEPS

# parameters for the neural network
NUM_STATE = 4
INPUT_SHAPE = (NUM_STATE,)
NUM_ACTIONS = 2
MIN_BATCH = 32
MAX_BATCH = 5 * MIN_BATCH

# parameters for the training
LEARNING_RATE = 5e-3
DECAY = 0.99
LOSS_VALUE = .5
LOSS_ENTROPY = .01

# parameters to control tensorflow behaviour (and logging)
TF_ALLOW_GROWTH = True
TF_LOG_DEVICE_PLACEMENT = False
