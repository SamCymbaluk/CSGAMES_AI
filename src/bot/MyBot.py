from src.bot.Bot import Bot

from src.utils.Pathfinder import Pathfinder
from networkx.algorithms.shortest_paths import astar_path
import math

class MyBot(Bot):

    def __init__(self):
        super().__init__()

        self.goals = [
            InBaseGoal(),
            HealthGoal(),
            DefendDepositGoal(),
            StoreGoal(),
            HarvestGoal()
        ]

        self.turn_num = 0
    def get_name(self):
        return 'Mighty McMaster Power PengAIn'

    def turn(self, game_state, character_state, other_bots):
        super().turn(game_state, character_state, other_bots)
        self.turn_num += 1

        print('TURN', self.turn_num)
        print('GS', game_state)
        print('CS', character_state)
        print('OB', other_bots)

        for goal in self.goals:
            if goal.predicate(self, game_state, character_state, other_bots):
                print(goal)
                return goal.action(self, game_state, character_state, other_bots)

        return self.commands.idle()



class Goal:
    def __init__(self):
        self.active = False

    def condition(self, bot, game_state, character_state, other_bots):
        return False

    def predicate(self, bot, game_state, character_state, other_bots):
        cond = self.condition(bot, game_state, character_state, other_bots)
        self.active = cond
        return cond

    def action(self, bot, game_state, character_state, other_bots):
        return bot.commands.idle()

class HealthGoal(Goal):
    def __init__(self):
        super().__init__()

    def condition(self, bot, game_state, character_state, other_bots):
        if self.active:
            return True
        if character_state['health'] < 30:
            return True

    def action(self, bot, game_state, character_state, other_bots):
        if in_base(character_state):
            if character_state['health'] < 100:
                return bot.commands.rest()
            else:
                self.active = False
                return bot.commands.idle()
        else:
            goal = character_state['base']
            direction = bot.pathfinder.get_next_direction(character_state['location'], goal)
            if direction:
                return bot.commands.move(direction)
            else:
                self.active = False
                return bot.commands.idle()


class HarvestGoal(Goal):
    def __init__(self):
        super().__init__()

    def condition(self, bot, game_state, character_state, other_bots):
        if self.active:
            return True
        if character_state['carrying'] <= 1000 and len(nearby_bots(3, game_state, character_state, other_bots)) == 0:
            return True
        elif character_state['carrying'] <= 100:
            return True

        return False

    def action(self, bot, game_state, character_state, other_bots):
        if in_base(character_state) and character_state['carrying'] > 0:
            self.active = False
            return bot.commands.store()
        else:
            goal = closestDeposit(character_state, game_state)

            direction = bot.pathfinder.get_next_direction(character_state['location'], goal)
            print(bot, direction)
            if direction:
                return bot.commands.move(direction)
            else:
                self.active = False
                return bot.commands.collect()


class InBaseGoal(Goal):
    def __init__(self):
        super().__init__()

    def condition(self, bot, game_state, character_state, other_bots):
        if self.active:
            return True
        if in_base(character_state) and character_state['carrying'] > 0:
            return True

    def action(self, bot, game_state, character_state, other_bots):
        self.active = False
        return bot.commands.store()
        # Also heal?


class StoreGoal(Goal):
    def __init__(self):
        super().__init__()

    def condition(self, bot, game_state, character_state, other_bots):
        if self.active:
            return True
        if character_state['carrying'] > 100 and len(nearby_bots(3, game_state, character_state, other_bots)) > 0:
            return True
        elif character_state['carrying'] > 1000:
            return True


    def action(self, bot, game_state, character_state, other_bots):
        if in_base(character_state):
            self.active = False
            return bot.commands.store()
        else:
            goal = character_state['base']
            direction = bot.pathfinder.get_next_direction(character_state['location'], goal)
            if direction:
                return bot.commands.move(direction)
            else:
                self.active = False
                return bot.commands.idle()

class DefendDepositGoal(Goal): # Check in base
    def __init__(self):
        super().__init__()

    def condition(self, bot, game_state, character_state, other_bots):
        for nearBot in nearby_bots(5, game_state, character_state, other_bots):
            print('NEARBOT', nearBot)
            if character_state['health'] > 20 and nearBot['location'] == closestDeposit(character_state, game_state):
                return True

    def action(self, bot, game_state, character_state, other_bots):
        print("DefendDepositGoal")
        for nearBot in nearby_bots(5, game_state, character_state, other_bots):
            if nearBot['location'] == closestDeposit(character_state, game_state):
                goal = nearBot['location']
                direction = bot.pathfinder.get_next_direction(character_state['location'], goal)

                if direction and (not is_beside(character_state['location'], goal)):
                    return bot.commands.move(direction)
                elif direction:
                    return bot.commands.attack(direction)
                else:
                    return bot.commands.idle()


def in_base(cs):
    return cs['location'] == cs['base']

def nearby_bots(dist, game_state, character_state, other_bots):
    bots = []
    for bot in other_bots:
        botDist = distToGoal(character_state['location'], bot['location'])
        if botDist <= dist:
            bots.append(bot)
    return bots

def distToGoal(location, potential_goal):
    return math.sqrt((location[0] - potential_goal[0])**2 + (location[1] - potential_goal[1])**2)

def listDeposits(game_state):
    map = game_state.split('\n')
    mineral_Locations = []

    x = 0
    for row in map:
        y = 0
        for char in row:
            if char == 'J':
                mineral_Locations.append((x,y))
            y += 1
        x += 1

    return mineral_Locations

def closestDeposit(character_state, game_state):
    deposits = listDeposits(game_state)
    depoDists = []
    for depo in deposits:
        depoDists.append((distToGoal(character_state['location'], depo), depo))

    depoDists.sort()
    return depoDists[0][1]

def is_beside(location1, location2):
    dx = int(math.fabs(location1[0] - location2[0]))
    dy = int(math.fabs(location1[1] - location2[1]))

    return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)


