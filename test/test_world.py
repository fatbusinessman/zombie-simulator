from hypothesis import example, given
from hypothesis import strategies as st

import pytest

from space import Point, Vector
from world import World, WorldBuilder


world_dimensions = st.integers(min_value=0, max_value=50)


class TestWorld:

    @given(width=world_dimensions, height=world_dimensions)
    @example(0, 0)
    @example(1, 1)
    def test_world_dimensions(self, width, height):
        world = World(width, height, characters={})
        assert world.rows == [[None] * width] * height

    def test_explicitly_empty_world(self):
        assert World(2, 2, {}).rows == [[None, None], [None, None]]

    def test_world_with_character(self):
        character = object()
        world = World(2, 2, {(1, 1): character})
        assert world.rows == [[None, None], [None, character]]

    def test_character_out_of_bounds(self):
        with pytest.raises(ValueError):
            World(2, 2, {(2, 2): object()})

    def test_empty_viewpoint(self):
        world = World(2, 2, characters={})
        assert len(world.viewpoint((1, 1))) == 0

    def test_viewpoint_single_character(self):
        character = object()
        world = World(2, 2, {(1, 1): character})
        viewpoint = world.viewpoint((1, 1))
        assert len(viewpoint) == 1
        assert (Vector.ZERO, character) in viewpoint

    def test_viewpoint_multiple_characters(self):
        char1, char2 = object(), object()
        world = World(3, 3, {(1, 1): char1, (2, 0): char2})
        viewpoint = world.viewpoint((0, 1))
        assert len(viewpoint) == 2
        assert (Vector(1, 0), char1) in viewpoint
        assert (Vector(2, -1), char2) in viewpoint


class TestWorldBuilder:

    def test_populated_world(self):
        population = iter(['foo', 'bar', 'baz', 'boop'])
        builder = WorldBuilder(2, 2, population)
        assert builder.world.rows == [['foo', 'bar'], ['baz', 'boop']]

    @given(st.iterables(elements=st.one_of(st.integers(), st.just(None)),
                        min_size=25,
                        unique=True))
    def test_integer_population(self, population):
        builder = WorldBuilder(5, 5, population)
