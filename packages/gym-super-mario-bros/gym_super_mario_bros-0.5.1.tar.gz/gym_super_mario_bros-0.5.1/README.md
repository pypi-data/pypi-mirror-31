# OpenAI Gym - Super Mario Bros

![smb](https://user-images.githubusercontent.com/2184469/39209488-854e960c-47cb-11e8-9e66-ddadcb0d7874.png)

An [OpenAI Gym](https://github.com/openai/gym) environment for the original
Super Mario Bros. game on the Nintendo Entertainment System (NES).

# Installation

The preferred installation of `gym-super-mario-bros` is from `pip`:

```shell
pip install gym-super-mario-bros
```

## NES Emulator

NESGym uses [FCEUX](http://www.fceux.com/web/home.html) to emulate NES games.
Make sure it's installed and in your `$PATH`.

### Unix

```shell
sudo apt-get install fceux
```

### Mac

```shell
brew install fceux
```

# Usage

```python
import gym_super_mario_bros
env = gym_super_mario_bros.make('SuperMarioBros-v0')

done = True
for step in range(5000):
    if done:
        state = env.reset()
    state, reward, done, info = env.step(env.action_space.sample())

env.close()
```

**NOTE:** `gym_super_mario_bros.make` is just an alias to `gym.make` for
convenience.

# Environments

The following environments play the game as a human would. The agent has
three lives to make it through the 32 levels of the game. The agent is
configured to _only_ see reward-able game-play frames. No cut-scenes, loading
screens, etc. are shown to the agent.

| Environment                    | Description                                      |
|:-------------------------------|:-------------------------------------------------|
| `SuperMarioBros-v0`            | 4 frames per action, standard ROM                |
| `SuperMarioBros-v1`            | 4 frames per action, custom down-sampled ROM     |
| `SuperMarioBrosNoFrameskip-v0` | 1 frame per action, standard ROM                 |
| `SuperMarioBrosNoFrameskip-v1` | 1 frame per action, custom down-sampled ROM      |
