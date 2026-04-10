import copy
import math
from data.presets import LOG, RULES

RECALL_COST_MULTIPLIER = RULES["recall_cost_multiplier"]
RECALL_STAT_VALUE = RULES["recall_stat_value"]

class RecallSystem:
    def __init__(
            self,
            user_data: dict
            ) -> None:
        self.user_data = user_data

    def recall_stat(self, stat: str) -> dict:
        recall_log = copy.deepcopy(LOG["recall_log_template"])
        recall_log["stat"] = stat

        global_recalls = self.user_data["global_recalls"]
        stat_recall_cost = global_recalls["recall_cost"][stat]
        if global_recalls["memory_fragments"] >= stat_recall_cost:
            recall_log["action"] = "recall"

            global_recalls["memory_fragments"] -= stat_recall_cost

            recall_log["memory_fragments_delta"] = stat_recall_cost

            global_recalls["recall_cost"][stat] *= RECALL_COST_MULTIPLIER[stat]
            global_recalls[f"plus_{stat}"] += RECALL_STAT_VALUE[stat]

            global_recalls["recall_cost"][stat] = math.ceil(global_recalls["recall_cost"][stat])

            return recall_log

        return recall_log
