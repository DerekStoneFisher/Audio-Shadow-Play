

KEY_STATE_QUEUE_MAX_SIZE = 5



class SoundBoardState:
    def __init__(self):
        self.hold_to_play = False
        self.hold_to_play_combination = {"1", "2", "3"}

        self.restart_after_stopping = True
        self.restart_after_stopping_combination = {"tab"}

        self.mark_frame_index_of_last_sound = False
        self.mark_frame_index_of_last_sound_combination = {"1", "3"}

        self.jump_to_frame_index_of_last_sound = False
        self.jump_to_frame_index_of_last_sound_combination = {"1", "4"}

        self.move_marked_frame_forward = False
        self.move_marked_frame_forward_combination = {"up"}

        self.move_marked_frame_backward = False
        self.move_marked_frame_backward_combination = {"down"}

        self.complete_combination_list = \
            tuple([self.hold_to_play_combination, self.restart_after_stopping_combination,
             self.mark_frame_index_of_last_sound_combination, self.jump_to_frame_index_of_last_sound_combination,
             self.move_marked_frame_forward_combination, self.move_marked_frame_backward_combination])




class KeyPressManager:
    def __init__(self, soundBoardState):
        self.soundBoardState = soundBoardState
        self._key_state_queue = [[],[],[],[],[]]
        self.keys_to_ignore = []
        self.key_state_changed = False

    def processKeyEvent(self, key_event):
        key = str(key_event.Key).lower()
        keys_down = self.getKeysDown()

        if "down" in key_event.MessageName and key not in keys_down:
            keys_down.append(key)
        if "up" in key_event.MessageName and key not in self.soundBoardState.complete_combination_list:
            keys_down.remove(key)

        self.updateSoundboardState()
        #regular_keys, config_keys = self.extractConfigKeysFromKeyPressCombination(keys_down)

        if keys_down != self.getKeysDown():
            self.key_state_changed = True
            self._key_state_queue.append(keys_down)
            if len(self._key_state_queue) > KEY_STATE_QUEUE_MAX_SIZE:
                del(self._key_state_queue[0])
            print self._key_state_queue
        else:
            self.key_state_changed = False


    def updateSoundboardState(self):
        if self.combinationPressed(self.soundBoardState.hold_to_play_combination):
            self.soundBoardState.hold_to_play = not self.soundBoardState.hold_to_play # toggle hold_to_play on or off
        elif self.combinationPressed(self.soundBoardState.restart_after_stopping_combination):
            self.soundBoardState.restart_after_stopping = False # for 1 key press, disable the restart after stopping
        elif self.combinationPressed(self.soundBoardState.mark_frame_index_of_last_sound_combination):
            self.soundBoardState.mark_frame_index_of_last_sound = True # toggle on to true. It will be toggled off elsewhere (within SoundEntry)
        elif self.combinationPressed(self.soundBoardState.jump_to_frame_index_of_last_sound_combination):
            self.soundBoardState.jump_to_frame_index_of_last_sound = True
        elif self.combinationPressed(self.soundBoardState.move_marked_frame_forward_combination):
            self.soundBoardState.move_marked_frame_forward = True
        elif self.combinationPressed(self.soundBoardState.move_marked_frame_backward_combination):
            self.soundBoardState.move_marked_frame_forward = True

    def combinationPressed(self, key_combination):
        possible_modifiers = []
        keys_down = list(self.getKeysDown())
        while len(keys_down) > 0:
            if key_combination == set(keys_down):
                return True
            else:
                possible_modifiers.append(keys_down)
                keys_down = keys_down[1:]
        return False


    #
    #
    # def extractConfigKeysFromKeyPressCombination(self, keys_down):
    #     ending_config_key_combination = list(keys_down)
    #     starting_regular_key_combination = []
    #     while len(ending_config_key_combination) > 0:
    #         if set(ending_config_key_combination) in self.soundBoardState.complete_combination_list:
    #             break
    #         else:
    #             print "appending ", ending_config_key_combination[0], " to regular key combination"
    #             starting_regular_key_combination.append(ending_config_key_combination[0])
    #             print "deleteing [0] from ", ending_config_key_combination
    #             del(ending_config_key_combination[0])
    #         print "=x=", starting_regular_key_combination, ending_config_key_combination, "=x="
    #         print "checking to see if ", ending_config_key_combination, "is equal to {1, 3}"
    #     print "=x=", starting_regular_key_combination, ending_config_key_combination, "=x="
    #     return starting_regular_key_combination, ending_config_key_combination


    # def _updateModifierKeyState(self, keys_down):
    #     modifier_keys_down = set()
    #     activation_keys_down = set()
    #
    #     for key in keys_down:
    #         if key in self.modifier_key_set:
    #             modifier_keys_down.add(key)
    #         else:
    #             activation_keys_down.add(key)




    def getKeysDown(self):
        return list(self._key_state_queue[-1])

    def getLastKeysDown(self):
        return list(self._key_state_queue[-2])



    # def getModifierKeysDown(self):
    #     return set([key for key in self.getKeysDown() if key in self.modifier_key_set])
    #
    # def getActivationKeysDown(self):
    #     return set([key for key in self.getKeysDown() if key not in self.modifier_key_set])