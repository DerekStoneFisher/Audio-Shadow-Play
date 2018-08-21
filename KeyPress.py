from Audio_Proj_Const import NAME_OVERRIDE_LIST

KEY_STATE_QUEUE_MAX_SIZE = 5

class KeyPressManager:
    def __init__(self, soundCollection):
        self.soundCollection = soundCollection
        self._key_state_queue = [[],[],[],[],[]]
        self.keys_to_ignore = []
        self.key_state_changed = False

    def processKeyEvent(self, key_event):
        key = str(key_event.Key).lower()
        if key in NAME_OVERRIDE_LIST:
            key = NAME_OVERRIDE_LIST[key]



        keys_down = list(self.getKeysDown())

        if "down" in key_event.MessageName and key not in keys_down:
            keys_down.append(key)
        if "up" in key_event.MessageName:
            keys_down.remove(key)


        # regular_keys, config_keys = self.splitKeysDownIntoRegularAndConfig(keys_down)

        #if len(config_keys) > 0:
        #    print "regualr and config -------> ", regular_keys, config_keys

        if keys_down != self.getKeysDown():
            self.key_state_changed = True
            self._key_state_queue.append(keys_down)
            if len(self._key_state_queue) > KEY_STATE_QUEUE_MAX_SIZE:
                del(self._key_state_queue[0])
            #print self._key_state_queue
        else:
            self.key_state_changed = False

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

    # def splitKeysDownIntoRegularAndConfig(self, keys_down):
    #     first_half = [] # ['o', '1', '2', '3'] -> ['o']
    #     second_half = list(keys_down) # ['o', '1', '2', '3'] -> ['1', '2', '3']
    #     while len(second_half) > 0 and set(second_half) not in self.soundBoardState.complete_combination_list:
    #         first_half.append(second_half[0])
    #         del(second_half[0])
    #     return first_half, second_half




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

    # def getRegularKeysDown(self):
    #     regular_keys, control_keys = self.splitKeysDownIntoRegularAndConfig(self.getKeysDown())
    #     return regular_keys

    def getLastKeysDown(self):
        return list(self._key_state_queue[-2])



    # def getModifierKeysDown(self):
    #     return set([key for key in self.getKeysDown() if key in self.modifier_key_set])
    #
    # def getActivationKeysDown(self):
    #     return set([key for key in self.getKeysDown() if key not in self.modifier_key_set])

    def endingKeysEqual(self, ending_keys):
        keys_down = list(self.getKeysDown())
        if len(keys_down) < len(ending_keys):
            return False
        else: # check to see if last n keys of keys_down are equal to equal_keys where n is the length of ending_keys
            return set(keys_down[-len(ending_keys):]) == set(ending_keys)


    def getScoresForKeyPresses(self):
        pass

    def calculateKeyPressMatchScore(self, key_combination):
        keys_down = self.getKeysDown()
        score = 0
        for key in keys_down:
            if key in key_combination:
                score += 1
        return score