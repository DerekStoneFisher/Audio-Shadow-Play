

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

    def updateSoundboardState(self, keys_down):
        if set(keys_down) == self.hold_to_play_combination:
            self.hold_to_play = not self.hold_to_play # toggle hold_to_play on or off
        elif set(keys_down) == self.restart_after_stopping_combination:
            self.restart_after_stopping = False # for 1 key press, disable the restart after stopping
        elif set(keys_down) == self.mark_frame_index_of_last_sound_combination:
            self.mark_frame_index_of_last_sound = True # toggle on to true. It will be toggled off elsewhere (within SoundEntry)
        elif set(keys_down) == self.jump_to_frame_index_of_last_sound_combination:
            self.jump_to_frame_index_of_last_sound = True
        elif set(keys_down) == self.move_marked_frame_forward_combination:
            self.move_marked_frame_forward = True
        elif set(keys_down) == self.move_marked_frame_backward_combination:
            self.move_marked_frame_forward = True



class KeyPressManager:
    def __init__(self, soundBoardState):
        self.soundBoardState = soundBoardState
        self._key_state_queue = [[],[],[],[],[]]

        self.modifier_key_set = {"lcontrol", "lalt", "lmenu"}
        self.keys_to_ignore = []
        self.key_state_changed = False

    def processKeyEvent(self, key_event):
        key = str(key_event.Key).lower()
        keys_down = self.getKeysDown()

        if "down" in key_event.MessageName and key not in keys_down:
            keys_down.append(key)
        if "up" in key_event.MessageName and key not in self.keys_to_ignore:
            keys_down.remove(key)

        self.soundBoardState.updateSoundboardState(keys_down)

        if keys_down != self.getKeysDown():
            self.key_state_changed = True
            self._key_state_queue.append(keys_down)
            if len(self._key_state_queue) > KEY_STATE_QUEUE_MAX_SIZE:
                del(self._key_state_queue[0])
            print self._key_state_queue
        else:
            self.key_state_changed = False

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