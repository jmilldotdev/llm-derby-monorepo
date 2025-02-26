from typing import Dict, List, Optional, Tuple

import textarena as ta
from textarena import Agent, Env, Info, Wrapper
from derby.strategies import StrategyProvider
from derby.types import WagerDecision


class BaseWagerWrapper(Wrapper):
    def __init__(self, env: Env, agents: Dict[int, Agent]):
        """
        Initializes the LLMObservationWrapper.

        Args:
            env (Env): The environment to wrap.
        """
        super().__init__(env)
        self.state = self.env.state
        self.agents = agents

    def step(self, action: str) -> Tuple[bool, Optional[Info]]:
        print("Resolving single bet waging step...")
        return self.state.step(action)


class SingleBetWagerWrapper(BaseWagerWrapper):
    def __init__(self, env: Env, agents: Dict[int, Agent]):
        """
        Initializes the LLMObservationWrapper.

        Args:
            env (Env): The environment to wrap.
        """
        super().__init__(env, agents)

    def step(self, action: str) -> Tuple[bool, Optional[Info]]:
        observation = self.env.get_observation()
        active_player = self.state.current_player_id
        nonactive_player = 1 if active_player == 0 else 0
        pot = 0
        resolved = False

        # First make the game move
        done, info = self.env.step(action)

        # If game is already done, return without wagering
        if done:
            return done, info

        # Handle wagering after the move
        while not resolved:
            decision = self.agents[active_player].get_wager_decision(
                observation=observation,
                valid_options=[WagerDecision.CHECK, WagerDecision.RAISE],
            )
            if decision == WagerDecision.CHECK:
                resolved = True
            elif decision == WagerDecision.RAISE:
                pot += 1
                decision = self.agents[nonactive_player].get_wager_decision(
                    observation=observation,
                    valid_options=[WagerDecision.CALL, WagerDecision.FOLD],
                )
                if decision == WagerDecision.CALL:
                    pot += 1
                    resolved = True
                elif decision == WagerDecision.FOLD:
                    resolved = True
                    self.state.set_winners(
                        player_ids=[active_player],
                        reason=f"Player {active_player} wins by opponent folding.",
                    )
                else:
                    print("Invalid decision")
                    resolved = True
            else:
                print("Invalid decision")
                resolved = True

        # Return the game state after both move and wagering
        return self.state.done, self.state.info


class HoldEmWagerWrapper(BaseWagerWrapper):
    def __init__(self, env: Env):
        """
        Initializes the LLMObservationWrapper.

        Args:
            env (Env): The environment to wrap.
        """
        super().__init__(env)
        self.state = self.env.state

    def step(self, action: str) -> Tuple[bool, Optional[Info]]:
        print("Resolving holdem waging step...")
        return self.state.step(action)


class WagerAgentWrapper(ta.Agent):
    def __init__(self, agent: ta.Agent, strategy_provider: StrategyProvider) -> None:
        super().__init__()
        self.agent = agent
        self.strategy_provider = strategy_provider

    def get_wager_decision(
        self, observation: str, valid_options: List[WagerDecision]
    ) -> WagerDecision:
        return self.strategy_provider.get_wager_decision(
            observation=observation, valid_options=valid_options
        )

    def __call__(self, observation: str) -> str:
        return self.agent(observation)
