from collections import Counter

from space import Area, Point


class World:

    def __init__(self, width, height, characters):
        self._area = Area(Point(0, 0), Point(width, height))
        self._width = width
        self._height = height
        self._roster = Roster.for_value(characters)

        bad_positions = [p for p, _ in self._roster if p not in self._area]
        if bad_positions:
            raise ValueError('Off-world characters at '
                             '{}'.format(bad_positions))

    def __repr__(self):
        return 'World({}, {}, {})'.format(self._width, self._height, self._roster)

    @property
    def rows(self):
        return [self._row(y) for y in range(self._height)]

    def _row(self, y):
        return [self._roster.character_at((x, y)) for x in range(self._width)]

    def viewpoint(self, origin):
        return set([(position - origin, character)
                    for position, character in self._roster])

    def _next_action(self, character, viewpoint, limits):
        target = character.attack(viewpoint)
        if target:
            return Attack(character, target)
        else:
            move_vector = character.move(viewpoint, limits)
            return Move(character, move_vector)

    def tick(self):
        world = self
        for (position, character) in self._roster:
            if character not in world._roster:
                continue
            viewpoint = world.viewpoint(position)
            limits = self._area.from_origin(position)
            action = self._next_action(character, viewpoint, limits)
            new_roster = action.next_roster(world._roster)
            world = World(self._width, self._height, new_roster)
        return world


class Move:

    def __init__(self, character, move_vector):
        self._character = character
        self._move_vector = move_vector

    def next_roster(self, roster):
        if not self._move_vector:
            return roster

        character = self._character

        if character not in roster:
            raise ValueError('Attempt to move non-existent character '
                             '{}'.format(character))

        new_positions = [(pos + self._move_vector if char == character else pos, char)
                         for (pos, char) in roster]
        return Roster(new_positions)


class Attack:

    def __init__(self, attacker, target):
        self._attacker = attacker
        self._target = target

    def next_roster(self, roster):
        attacker = self._attacker
        target = self._target

        if attacker not in roster:
            raise ValueError('Attack by non-existent character '
                             '{}'.format(attacker))
        if target not in roster:
            raise ValueError('Attack on non-existent character '
                             '{}'.format(target))

        new_positions = [(pos, char.attacked() if char == target else char)
                         for (pos, char) in roster]
        return Roster(new_positions)


class Roster:

    @classmethod
    def for_value(cls, value):
        if isinstance(value, Roster):
            return value
        if hasattr(value, 'items'):
            return Roster(value.items())
        if value is None:
            return Roster([])

        return Roster(value)

    def __init__(self, character_positions):
        self._positions = [(Point(*position), character)
                           for position, character in character_positions]
        position_counts = Counter(p[0] for p in self._positions)

        self._check_unique((p[0] for p in self._positions),
                           'Multiply-occupied points in roster')

        self._check_unique((p[1] for p in self._positions),
                           'Characters in multiple places')

    def _check_unique(self, collection, message):
        duplicates = [item for item, count in Counter(collection).items()
                      if count > 1]
        if duplicates:
            raise ValueError('{}: {}'.format(message, duplicates))

    def character_at(self, position):
        for p, char in self._positions:
            if p == position:
                return char
        else:
            return None

    def __contains__(self, character):
        return any(c == character for _, c in self._positions)

    def __iter__(self):
        return iter(self._positions)

    def __repr__(self):
        return 'Roster({})'.format(self._positions)

    def __eq__(self, other):
        return sorted(self._positions) == sorted(other._positions)


class WorldBuilder:

    def __init__(self, width, height, population):
        grid = self._grid(width, height)

        starting_positions = [(point, character)
                              for point, character in zip(grid, population)
                              if character is not None]

        self._world = World(width, height, starting_positions)

    def _grid(self, width, height):
        for y in range(height):
            for x in range(width):
                yield Point(x, y)

    @property
    def world(self):
        return self._world
