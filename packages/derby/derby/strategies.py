from abc import ABC, abstractmethod
import random
from typing import List, Optional
import re

import textarena as ta
from derby.types import WagerDecision


class StrategyProvider(ABC):
    def __init__(self, agent: ta.Agent):
        self.agent = agent

    @abstractmethod
    def get_wager_decision(
        self, observation: str, valid_options: List[WagerDecision]
    ) -> WagerDecision:
        pass


class RandomStrategyProvider(StrategyProvider):
    def __init__(self, agent: ta.Agent):
        super().__init__(agent)

    def get_wager_decision(
        self, observation: str, valid_options: List[WagerDecision]
    ) -> WagerDecision:
        return random.choice(valid_options)


class LLMStrategyProvider(StrategyProvider):
    def __init__(self, agent: ta.Agent, strategy_prompt: Optional[str] = None):
        super().__init__(agent)
        self.strategy_prompt = strategy_prompt

    def construct_wager_prompt(
        self, observation: str, valid_options: List[WagerDecision]
    ) -> str:
        prompt = f"""
        Observation: {observation}

        You are currently in the betting round.
        The valid options are:
        {valid_options}

        You must respond with the name of the option you choose in square brackets, e.g. '[raise]', '[call]', '[check]', '[fold]'. Your choice must be one of the valid options. You must only choose a single option.
        """

        if self.strategy_prompt:
            prompt += f"YOUR PREFERRED STRATEGY:\n\n{self.strategy_prompt}"

        return prompt

    def parse_wager_response(
        self, response: str, valid_options: List[WagerDecision]
    ) -> WagerDecision:
        # Find the first text in square brackets
        match = re.search(r"\[(.*?)\]", response)
        if not match:
            raise ValueError(
                f"No decision found in square brackets in response: {response}"
            )

        decision = match.group(1).lower().strip()

        try:
            wager_decision = WagerDecision(decision)
            if wager_decision not in valid_options:
                raise ValueError(
                    f"Decision '{decision}' not in valid options: {valid_options}"
                )
            return wager_decision
        except ValueError as e:
            raise ValueError(
                f"Invalid decision '{decision}'. Must be one of: {valid_options}"
            )

    def get_wager_decision(
        self, observation: str, valid_options: List[WagerDecision]
    ) -> WagerDecision:
        prompt = self.construct_wager_prompt(observation, valid_options)
        print(f"Wager prompt: {prompt}")
        response = self.agent(prompt)
        print(f"Wager response: {response}")
        return self.parse_wager_response(response, valid_options)
