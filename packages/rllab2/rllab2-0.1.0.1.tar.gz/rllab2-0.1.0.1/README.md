[![Docs](https://readthedocs.org/projects/rllab2/badge)](http://rllab2.readthedocs.org/en/latest/)
[![Circle CI](https://circleci.com/gh/rllab2/rllab2.svg?style=shield)](https://circleci.com/gh/rllab2/rllab2)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/rllab2/rllab2/blob/master/LICENSE)
[![Join the chat at https://gitter.im/rllab2/rllab2](https://badges.gitter.im/rllab2/rllab2.svg)](https://gitter.im/rllab2/rllab2?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# rllab2

rllab2 is a framework for developing and evaluating reinforcement learning algorithms. It includes a wide range of continuous control tasks plus implementations of the following algorithms:


- [REINFORCE](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/vpg.py)
- [Truncated Natural Policy Gradient](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/tnpg.py)
- [Reward-Weighted Regression](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/erwr.py)
- [Relative Entropy Policy Search](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/reps.py)
- [Trust Region Policy Optimization](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/trpo.py)
- [Cross Entropy Method](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/cem.py)
- [Covariance Matrix Adaption Evolution Strategy](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/cma_es.py)
- [Deep Deterministic Policy Gradient](https://github.com/rllab2/rllab2/blob/master/rllab2/algos/ddpg.py)

rllab2 is fully compatible with [OpenAI Gym](https://gym.openai.com/). See [here](http://rllab2.readthedocs.io/en/latest/user/gym_integration.html) for instructions and examples.

rllab2 only officially supports Python 3.5+. For an older snapshot of rllab2 sitting on Python 2, please use the [py2 branch](https://github.com/rllab2/rllab2/tree/py2).

rllab2 comes with support for running reinforcement learning experiments on an EC2 cluster, and tools for visualizing the results. See the [documentation](https://rllab2.readthedocs.io/en/latest/user/cluster.html) for details.

The main modules use [Theano](http://deeplearning.net/software/theano/) as the underlying framework, and we have support for TensorFlow under [sandbox/rocky/tf](https://github.com/openai/rllab2/tree/master/sandbox/rocky/tf).

# Documentation

Documentation is available online: [https://rllab2.readthedocs.org/en/latest/](https://rllab2.readthedocs.org/en/latest/).

# Citing rllab2

If you use rllab2 for academic research, you are highly encouraged to cite the following paper:

- Yan Duan, Xi Chen, Rein Houthooft, John Schulman, Pieter Abbeel. "[Benchmarking Deep Reinforcement Learning for Continuous Control](http://arxiv.org/abs/1604.06778)". _Proceedings of the 33rd International Conference on Machine Learning (ICML), 2016._

# Credits

rllab2 was originally developed by Rocky Duan (UC Berkeley / OpenAI), Peter Chen (UC Berkeley), Rein Houthooft (UC Berkeley / OpenAI), John Schulman (UC Berkeley / OpenAI), and Pieter Abbeel (UC Berkeley / OpenAI). The library is continued to be jointly developed by people at OpenAI and UC Berkeley.

# Slides

Slides presented at ICML 2016: https://www.dropbox.com/s/rqtpp1jv2jtzxeg/ICML2016_benchmarking_slides.pdf?dl=0
