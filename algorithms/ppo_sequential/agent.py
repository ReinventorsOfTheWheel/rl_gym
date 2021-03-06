import numpy as np

np.seterr(all="raise")

import algorithms.ppo_sequential.params as params
from algorithms.ppo_sequential.brain import Brain
from algorithms.ppo_sequential.memory import Memory

import pygame
from moviepy.editor import ImageSequenceClip
import os

class Agent():
    def __init__(self,
                 brain: Brain,
                 shared_memory: Memory,
                 Env,
                 vis=False,
                 bookkeeping = False,
                 vis_fps = 20):

        self.env = Env()

        # a local memory, to store observations made by this agent
        # action 0 and reward 0 are between state 0 and 1
        self.seen_observations = []  # state of the environment
        self.seen_values = []  # corresponding estimated values (given by network)
        self.seen_policies = []  # policies predicted by the network
        self.seen_states = []  # state of the model
        self.seen_actions = []  # actions taken
        self.seen_rewards = []  # rewards given
        self.n_step_reward = 0  # reward for n consecutive steps

        # this is globally shared between agents
        # local observations will be successively pushed to the shared memory
        # as soon as we have enough for the N-step target
        self.brain = brain
        self.shared_memory = shared_memory

        self.num_episodes = 0
        self.stop = False

        self.vis = vis
        if self.vis:
            self.canvas_size = (500, 500)
            self.canvas = np.zeros([*self.canvas_size, 3])
            pygame.init()
            self.clock = pygame.time.Clock()
            self.window = pygame.display.set_mode(self.canvas_size)
            pygame.display.set_caption("Pygame cheat sheet")

            self.vis_fps = vis_fps
            self.frames = []

        self.bookkeeping = bookkeeping
        if self.bookkeeping:
            self.fails = 0
            self.wins = 0

    def reset(self):
        # clear all local memory
        self.seen_observations = []  # state of the environment
        self.seen_values = []  # corresponding estimated values (given by network)
        self.seen_policies = []  # policies predicted by the network
        self.seen_states = []  # state of the model
        self.seen_actions = []  # actions taken
        self.seen_rewards = []  # rewards given

        # reset n-step reward calculation
        self.n_step_reward = 0  # reward for n consecutive steps

        # reset environment
        self.observation = self.env.reset()
        self.observation = self.brain.preprocess(self.observation)
        self.seen_observations = [self.observation]

        # reset model
        self.state = self.brain.get_initial_state()
        self.seen_states = [self.state]

        self.total_reward = 0

        if self.vis:
            if len(self.frames)>0:
                clip = ImageSequenceClip(self.frames, fps=self.vis_fps)
                if os.path.exists(params.VIDEO_OUT_DIR):
                    clip.write_gif(params.VIDEO_OUT_DIR+"/"+str(self.num_episodes)+".gif")
                else:
                    print("video export directory not found")

            self.frames=[]

    def reset_metadata(self):
        self.num_episodes = 0
        self.episode_rewards = []

    def act(self, greedy = False):

        # show current state to network and get predicted policy
        policy, value, self.state = self.brain.predict(self.observation, self.state)

        # flatten the output
        policy = policy[0]
        if [] != self.state:
            self.state = self.state[0]
        value = value[0, 0]

        if greedy:
            action = np.argmax(policy)
        else:
            action = np.random.choice(params.NUM_ACTIONS, p=policy)

        new_observation, reward, done, _ = self.env.step(action)
        reward *= params.REWARD_SCALE

        if done:
            new_observation = np.zeros_like(self.observation)
        else:
            new_observation = self.brain.preprocess(new_observation)

        actions_onehot = np.zeros(params.NUM_ACTIONS)
        actions_onehot[action] = 1

        # append observations to local memory
        self.seen_values.append(value)
        self.seen_states.append(self.state)
        self.seen_policies.append(policy)
        self.seen_actions.append(actions_onehot)
        self.seen_rewards.append(reward)
        self.seen_observations.append(new_observation)
        self.n_step_reward = (self.n_step_reward + reward * params.GAMMA ** params.NUM_STEPS) / params.GAMMA

        assert len(self.seen_actions) <= params.NUM_STEPS, "as soon as N steps are reached, " \
                                                           "local memory must be moved to shared memory"

        # update state of agent
        self.observation = new_observation
        self.total_reward += reward

        # move local memory to shared memory
        if done:
            while len(self.seen_rewards) > 0:
                self.move_to_memory(done)
                self.n_step_reward /= params.GAMMA

        elif len(self.seen_actions) == params.NUM_STEPS:
            self.move_to_memory(done)

        # TODO: implement openai render() on custom envs
        if self.vis:
            self.canvas[:] = 0
            self.env.render_to_canvas(self.canvas)
            frame = (self.canvas * 255).astype(np.uint8)
            self.frames.append(np.transpose(frame, [1,0,2])) # numpy axes are not the same as moviepy or cv axes

            surf = pygame.surfarray.make_surface(frame)
            self.window.blit(surf, (0, 0))

            self.clock.tick(self.vis_fps)
            pygame.display.update()

        # print meta information if the agent was done
        # and reset
        if done:
            self.num_episodes += 1
            self.episode_rewards.append(self.total_reward)
            self.reset()

            if self.bookkeeping:
                if reward > 0:
                    self.wins += 1
                else:
                    self.fails += 1

                print("episode {} ended, {} wins, {} fails, {:.2f} overall positive rate".format(self.num_episodes, self.wins, self.fails, self.wins/(self.wins + self.fails)))


    def move_to_memory(self, terminal):
        # removes one set of observations from local memory
        # and pushes it to shared memory

        #  read the length first, before popping anything
        length = len(self.seen_actions)

        advantage_gae = self.compute_gae(np.array(self.seen_rewards), np.array(self.seen_values), terminal)

        from_observation = self.seen_observations.pop(0)
        from_state = self.seen_states.pop(0)
        to_observation = self.seen_observations[-1]
        to_state = self.seen_states[-1]
        action = self.seen_actions.pop(0)
        reward = self.seen_rewards.pop(0)
        pred_value = self.seen_values.pop(0)
        pred_policy = self.seen_policies.pop(0)

        batch = (
            from_observation, from_state, to_observation, to_state, pred_policy, pred_value, action, reward,
            advantage_gae,
            terminal, length)
        self.shared_memory.push(batch)

        self.n_step_reward = (self.n_step_reward - reward)

    def compute_gae(self, rewards, values, terminal):
        length = len(rewards)

        # delta functions are 1 step TD lambda
        padded_values = np.zeros((length + 1,))
        padded_values[:-1] = values
        padded_values[-1] = values[-1] * (1 - terminal)

        deltas = rewards + params.GAMMA * padded_values[1:] - padded_values[:-1]

        # gae advantage uses a weighted sum of deltas,
        # compare (16) in the gae paper
        discount_factor = params.GAMMA * params.LAMBDA
        weights = np.geomspace(1, discount_factor ** (len(deltas) - 1), len(deltas))
        weighted_series = deltas * weights
        advantage_gae = weighted_series.sum()

        return advantage_gae
