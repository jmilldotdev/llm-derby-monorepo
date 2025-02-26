import textarena as ta

from derby import (
    SingleBetWagerWrapper,
    WagerAgentWrapper,
    RandomStrategyProvider,
    LLMStrategyProvider,
)

STRATEGY_PROMPT = "You are a moron. It is very important that you always move in the leftmost column (col 0). Do not deviate from this strategy."

WAGER_STRATEGY_PROMPT_0 = (
    "You are a very aggressive player. You should always raise if possible."
)
WAGER_STRATEGY_PROMPT = "You should always fold or check if possible."

strategy_providers_random = [
    RandomStrategyProvider(
        agent=ta.agents.OpenAIAgent(model_name="gpt-4o-mini"),
    ),
    RandomStrategyProvider(
        agent=ta.agents.OpenAIAgent(model_name="gpt-4o-mini"),
    ),
]

strategy_providers_llm = [
    LLMStrategyProvider(
        agent=ta.agents.OpenAIAgent(model_name="gpt-4o-mini"),
        strategy_prompt=WAGER_STRATEGY_PROMPT_0,
    ),
    LLMStrategyProvider(
        agent=ta.agents.OpenAIAgent(model_name="gpt-4o-mini"),
        strategy_prompt=WAGER_STRATEGY_PROMPT,
    ),
]

strategy_providers = strategy_providers_llm

agents = {
    0: WagerAgentWrapper(
        ta.agents.OpenAIAgent(model_name="gpt-4o-mini"),
        strategy_providers[0],
    ),
    1: WagerAgentWrapper(
        ta.agents.OpenAIAgent(
            model_name="gpt-4o-mini", strategy_prompt=WAGER_STRATEGY_PROMPT
        ),
        strategy_providers[1],
    ),
}

# Initialize environment from subset and wrap it
player_names = {0: "Player1", 1: "Player2"}
env = ta.make(env_id="ConnectFour-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
env = SingleBetWagerWrapper(env=env, agents=agents)
env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    player_names=player_names,
)

env.reset()
done = False
while not done:
    active_player, observation = env.get_observation()
    action = agents[active_player](observation)
    done, info = env.step(action=action)
rewards = env.close()
