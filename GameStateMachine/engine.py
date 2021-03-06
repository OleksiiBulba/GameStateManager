# game state machine - provides a game management based on a game state
# Copyright (C) 2020  Oleksii Bulba
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Oleksii Bulba
# oleksii.bulba@gmail.com

import copy
import sys

import logging
from typing import Union

from GameStateMachine.clock import Clock
from GameStateMachine.states import BaseGameState


class GameEngine(object):
    """
    Basic Game Engine class. It manages all game states.
    """

    def __init__(self, clock: Clock, initial_state_name: str, fps: int = 60, fps_max: int = 120):
        self.clock = clock
        self.fps = fps
        self.time_delta_min = fps_max / 1000.0

        self.states = {}
        self.active_state: Union[BaseGameState, None] = None
        self.init_states()
        self.set_initial_state(initial_state_name)

    def init_states(self) -> None:
        """
        Initializes states, return nothing
        :return: None
        """
        raise NotImplementedError("init_states method should be implemented in child classes")

    def set_initial_state(self, state_name):
        if state_name in self.states.keys():
            self.active_state = self.states[state_name]
            self.active_state.start()
        else:
            raise NameError("State name {} not found. Did you forget to init it?".format(state_name))

    def register_state(self, state: BaseGameState):
        if state.name not in self.states:
            self.states[state.name] = state
        else:
            raise NameError("State {} already exists".format(state.name))

    def run(self):
        while True:
            frame_time = self.clock.tick(self.fps)
            time_delta = min(frame_time / 1000.0, self.time_delta_min)

            if self.active_state is None:
                raise ValueError

            self.active_state.run(time_delta)

            if self.active_state.time_to_quit_app:
                break

            if self.active_state.time_to_transition:
                self.transition()

        self.exit()

    def transition(self):
        logging.info('Transition: {} -> {}'.format(self.active_state.name, self.active_state.target_state_name))
        self.active_state.time_to_transition = False
        new_state_name = self.active_state.target_state_name
        # TODO refactor using return and params for transition data between states
        self.active_state.end()
        outgoing_data_copy = copy.deepcopy(self.active_state.outgoing_transition_data)
        self.active_state = self.states[new_state_name]
        self.active_state.incoming_transition_data = outgoing_data_copy
        self.active_state.start()

    def exit(self):
        self.active_state.end()
        sys.exit()
