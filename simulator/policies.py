import query


def raiblocks_yolo_policy(self, time, step_nr):
    if step_nr == 0:
        self.market.buy(self, "raiblocks", self.funds)
