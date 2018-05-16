from vector import BoundingBox, Vector


class World:
    def __init__(self, width, height, characters=None):
        self._width = width
        self._height = height
        self._characters = dict(characters or {})

    @classmethod
    def populated_by(cls, width, height, populator):
        world = World(width, height)
        for y in range(height):
            for x in range(width):
                character = next(populator)
                if character:
                    world = world.with_character((x, y), character)
        return world

    @property
    def rows(self):
        return [self._row(y) for y in range(self._height)]

    def _row(self, y):
        return [self._character_at((x, y)) for x in range(self._width)]

    def _character_at(self, position):
        return self._characters.get(position)

    @property
    def _character_positions(self):
        return self._characters.items()

    def with_character(self, position, character):
        if character is None:
            raise ValueError('Cannot add a null character')

        new_characters = dict([(pos, char) for (pos, char) in
                self._character_positions if char != character])
        if position in new_characters:
            message = 'Invalid move to occupied space {}'.format(position)
            raise ValueError(message)
        new_characters.update({position: character})
        return World(self._width, self._height, new_characters)

    def viewpoint(self, origin):
        return set([(self._offset(position, origin), character)
                    for position, character in self._character_positions])

    def _offset(self, position, origin):
        return Vector(position[0] - origin[0], position[1] - origin[1])

    def tick(self):
        world = self
        for (position, character) in self._character_positions:
            viewpoint = world.viewpoint(position)
            position_vector = Vector(*position)
            limits = BoundingBox(Vector.ZERO - position_vector,
                                 Vector(self._width, self._height) - position_vector)
            move = character.move(viewpoint, limits)
            world = world.with_character(
                    (position[0] + move.dx, position[1] + move.dy),
                    character
            )
        return world
