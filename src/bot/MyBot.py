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
            StoreGoal(),
            HarvestGoal()
        ]

    def get_name(self):
        return 'Mighty McMaster Power PengAIn'

    def turn(self, game_state, character_state, other_bots):
        super().turn(game_state, character_state, other_bots)

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
        if character_state['health'] < 15:
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
        if character_state['carrying'] <= 50 and len(listDeposits(game_state)) > 0:
            return True

    def action(self, bot, game_state, character_state, other_bots):
        if in_base(character_state) and character_state['carrying'] > 0:
            self.active = False
            return bot.commands.store()
        else:
            deposits = listDeposits(game_state)
            depoDists = []
            for depo in deposits:
                depoDists.append((distToGoal(game_state, character_state, other_bots, character_state['location'], depo), depo))

            depoDists.sort()
            goal = depoDists[0][1]

            direction = bot.pathfinder.get_next_direction(character_state['location'], goal)
            if direction:
                return bot.commands.move(direction)
            else:
                self.active = False
                return bot.commands.collect()


class InBaseGoal(Goal):
    def __init__(self):
        super().__init__()

    def condition(self, bot, game_state, character_state, other_bots):
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
        if character_state['carrying'] > 50:
            return True
        elif character_state['carrying'] > 10 and len(listDeposits(game_state)) == 0:
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

class AttackGoal(Goal): # Check in base
    def __init__(self):
        super().__init__()

    def condition(self, bot, game_state, character_state, other_bots):
        for nearBot in nearby_bots(5, game_state, character_state, other_bots):
            if nearBot['health'] < character_state['health']:
                return True

    def action(self, bot, game_state, character_state, other_bots):
        self.active = False
        return bot.commands.store()
        # Also heal?

def in_base(cs):
    return cs['location'] == cs['base']

def nearby_bots(dist, game_state, character_state, other_bots):
    bots = []
    for bot in other_bots:
        botDist = distToGoal(game_state, character_state, other_bots, character_state['location'], bot['location'])
        if botDist <= dist:
            bots.append(bot)
    return bots

def distToGoal(game_state, character_state, other_bots, location, potential_goal):
    return math.sqrt((location[0] - potential_goal[0])**2 + (location[1] - potential_goal[1])**2)
    """potential_Pathfinder = Pathfinder()
    potential_Pathfinder.set_game_state(game_state=game_state, players=(other_bots.append(character_state)))
    atGoal = False
    counter = 0
    local = location

    while (atGoal == False):
        graph = potential_Pathfinder.create_graph(potential_Pathfinder.game_map)
        path = astar_path(graph, local, potential_goal)
        direction = convert_node_to_direction(path)

        direc = potential_Pathfinder.convert_node_to_direction(path)

        if (direc == 'N'):
            local[1] += 1
        if (direc == 'S'):
            local[1] -= 1
        if (direc == 'E'):
            local[0] += 1
        if (direc == 'W'):
            local[0] -= 1

        counter += 1

        if (location == potential_goal):
            atGoal = True

    return counter

def convert_node_to_direction(path):
    if len(path) < 2:
        return None

    start = path[0]
    next = path[1]
    if start[1] == next[1] + 1:
        return 'W'

    elif start[1] == next[1] - 1:
        return 'E'

    elif start[0] == next[0] + 1:
        return 'N'

    else:
        return 'S'

"""
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
