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
            print keys_down
        if "up" in key_event.MessageName:
            keys_down.remove(key)


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

    def getKeysDown(self):
        return list(self._key_state_queue[-1])

    def getLastKeysDown(self):
        return list(self._key_state_queue[-2])


    def endingKeysEqual(self, ending_keys):
        keys_down = list(self.getKeysDown())
        if len(keys_down) < len(ending_keys):
            return False
        else: # check to see if last n keys of keys_down are equal to equal_keys where n is the length of ending_keys
            return set(keys_down[-len(ending_keys):]) == set(ending_keys)

