from space import BoundingBox, UnlimitedBoundingBox, Vector


def shortest(vectors):
    return min(vectors, key=lambda v: v.distance)


class TargetVectors:
    def __init__(self, viewpoint):
        self._viewpoint = viewpoint

    @property
    def nearest_human(self):
        return self._viewpoint.nearest(undead=False, living=True)

    @property
    def nearest_zombie(self):
        return self._viewpoint.nearest(undead=True)

    def from_offset(self, offset):
        return TargetVectors(self._viewpoint.from_offset(offset))


class Obstacles:
    def __init__(self, viewpoint):
        self._viewpoint = viewpoint

    def __contains__(self, vector):
        if vector == Vector.ZERO:
            return False
        return self._viewpoint.character_at(vector) is not None


class Living:

    living = True
    undead = False
    movement_range = BoundingBox.range(2)
    next_state = None

    def attack(self, target_vectors):
        return None

    def best_move(self, target_vectors, available_moves):
        if target_vectors.nearest_zombie is not None:

            def move_rank(move):
                return (
                    -target_vectors.from_offset(move).nearest_zombie.distance,
                    move.distance,
                )

            return min(available_moves, key=move_rank)
        else:
            return shortest(available_moves)


class Dead:
    def __init__(self, age=0):
        self._age = age

    living = False
    undead = False
    movement_range = [Vector.ZERO]

    _resurrection_age = 20

    def attack(self, target_vectors):
        return None

    def best_move(self, target_vectors, available_moves):
        if Vector.ZERO not in available_moves:
            raise ValueError("Zero move unavailable for dead character")
        return Vector.ZERO

    @property
    def next_state(self):
        if self._age >= self._resurrection_age:
            return Undead()
        else:
            return Dead(self._age + 1)

    def __eq__(self, other):
        return isinstance(other, Dead) and self._age == other._age


class Undead:

    living = False
    undead = True
    movement_range = BoundingBox.range(1)
    attack_range = BoundingBox.range(1)
    next_state = None

    def attack(self, target_vectors):
        nearest_human = target_vectors.nearest_human
        if nearest_human is not None and nearest_human in self.attack_range:
            return nearest_human

    def best_move(self, target_vectors, available_moves):
        nearest_human = target_vectors.nearest_human
        if nearest_human:

            def move_rank(move):
                return ((nearest_human - move).distance, move.distance)

            return min(available_moves, key=move_rank)
        else:
            return shortest(available_moves)

    def __eq__(self, other):
        return isinstance(other, Undead)


class Character:
    def __init__(self, state):
        self._state = state

    @property
    def living(self):
        return self._state.living

    @property
    def undead(self):
        return self._state.undead

    def next_action(self, environment, limits, actions):
        new_state = self._state.next_state
        if new_state:
            return actions.change_state(new_state)
        target_vector = self.attack(environment)
        if target_vector:
            return actions.attack(target_vector)
        move = self.move(environment, limits)
        return actions.move(move)

    def move(self, environment, limits=UnlimitedBoundingBox()):
        """Choose where to move next.

        Arguments:
            environment: the character's current environment. This is currently
                passed in as a Viewpoint instance, supporting the
                `character_at`, `nearest` and `from_offset` methods.
            limits: any limits on the character's movement provided by the
                edges of the world. This can be anything that reponds to the
                `in` operator.

        Return a Vector object representing this character's intended move. If
        the character does not intend to (or cannot) move, return a zero
        vector.
        """
        target_vectors = TargetVectors(environment)
        obstacles = Obstacles(environment)

        moves = self._available_moves(limits, obstacles)
        return self._state.best_move(target_vectors, moves)

    def _available_moves(self, limits, obstacles):
        moves = [
            m for m in self._state.movement_range if m in limits and m not in obstacles
        ]
        return moves

    def attack(self, environment):
        return self._state.attack(TargetVectors(environment))

    def with_state(self, new_state):
        return Character(state=new_state)

    def attacked(self):
        return self.with_state(Dead())


def default_human():
    return Character(state=Living())


def default_zombie():
    return Character(state=Undead())
