import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from tf_agents.agents import tf_agent
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.drivers.dynamic_step_driver import DynamicStepDriver
from tf_agents.environments import tf_py_environment
from tf_agents.metrics import tf_metrics
from tf_agents.networks import q_network
from tf_agents.policies.q_policy import QPolicy
from tf_agents.replay_buffers import tf_uniform_replay_buffer

from sumobasesimulation.verify import SumoBaseSimulation

def main():
    tf_env = tf_py_environment.TFPyEnvironment( SumoBaseSimulation())
    r = tf_env.reset()
    q_net = q_network.QNetwork(
        tf_env.time_step_spec().observation,
        tf_env.action_spec(),
        fc_layer_params=(100,))

    agent = dqn_agent.DqnAgent(
        tf_env.time_step_spec(),
        tf_env.action_spec(),
        q_network=q_net,
        optimizer=tf.compat.v1.train.AdamOptimizer(0.001))
    agent.initialize()
    my_q_policy = QPolicy(
        tf_env.time_step_spec(),
        tf_env.action_spec(),
        q_network=q_net)

    replay_buffer_capacity = 1000
    replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
        agent.collect_data_spec,
        batch_size=tf_env.batch_size,
        max_length=replay_buffer_capacity)

    # Add an observer that adds to the replay buffer:
    replay_observer = [replay_buffer.add_batch]

    collect_steps_per_iteration = 10
    collect_op = DynamicStepDriver(
      tf_env,
      my_q_policy,
      observers=replay_observer,
      num_steps=collect_steps_per_iteration).run()

    dataset = replay_buffer.as_dataset(
        num_parallel_calls=3,
        sample_batch_size=tf_env.batch_size,
        num_steps=2).prefetch(3)

    iterator = iter(dataset)

    train_metrics = [
        tf_metrics.NumberOfEpisodes(),
        tf_metrics.EnvironmentSteps(),
        tf_metrics.AverageReturnMetric(),
        tf_metrics.AverageEpisodeLengthMetric(),
    ]

    driver = dynamic_step_driver.DynamicStepDriver(
        tf_env,
        my_q_policy,
        observers=replay_observer + train_metrics,
        num_steps=1)

    episode_len = []

    final_time_step, policy_state = driver.run()

    for i in range(1000):
        final_time_step, _ = driver.run(final_time_step, policy_state)

        experience, _ = next(iterator)
        train_loss = agent.train(experience=experience)
        step = agent.train_step_counter.numpy()

        if step % 10 == 0:
            print('step = {0}: loss = {1}'.format(step, train_loss.loss))
            episode_len.append(train_metrics[3].result().numpy())
            print('Average episode length: {}'.format(train_metrics[3].result().numpy()))


    plt.plot(episode_len)
    plt.show()
if __name__ == '__main__':
    main()