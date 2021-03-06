The algorithms in this repository can be applied to a wide range of problems.
Very popular is the openai atari environment, there is also vizdoom.
And I'm starting to work on homebrew environments.

vizdoom and openai have different interfaces.
I prefer the openai version, which exposes these methods:
 - reset()
 - render()
 - step()

For vizdoom, there is a small adapter,
homebrew environments should follow this directly.

The environment should also expose the possible actions,
as well as a method to sample from them.
OpenAI has the action_space property, which has their own datatype.
Here the adapter differs from openai:
 - num_actions
 - sample_action()
 
For now, all actions are represented by a number. 
This is not well suited for a control setting and will probably be refactored later on.
The method sample_action() seems pretty useless, 
I'm keeping it, since for control, sampling might become more complex.