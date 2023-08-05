pysc1 : The StarCraft I Learning Environment
============================================


This package is currently in enthusiastic development. Just wait a sec.
Meanwhile, refer to https://github.com/bboyseiok/pysc1-gym for now.

This project is also registered on pypi : https://pypi.org/project/pysc1/
I'll be waiting for the people who share the same interest and wants to build on the project!

Thank you.

Pysc1-gym
=========

Installing and managing Starcraft I learning environment can be tedious and full of errors. Here, I present to you packaged way of running a nice Starcraft I gym simulation in your laptop or some clusters.

I was using Windows 10 while making this work, so the instructions are made in reference to the Windows system. 

"OpenAI Gym" like code for Starcraft I
--------------------------------------

After the Environment is set, you can access the features of Starcraft I just like in OpenAI Gym:

.. code:: python

    env = sc.SingleBattleEnv(args.ip, args.port)
    env.seed(777)
    agent = RandomAgent(env.action_space)
    
    episodes = 0
    while episodes < 100:
        obs = env._reset()
        done = False
        while not done:
            action = agent.act()
            obs, reward, done, info = env._step(action)
        episodes += 1
    
    env.close()

