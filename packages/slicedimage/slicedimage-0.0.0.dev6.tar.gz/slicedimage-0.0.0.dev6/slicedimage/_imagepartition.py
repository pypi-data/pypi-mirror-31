from __future__ import absolute_import, division, print_function, unicode_literals


class ImagePartition(object):
    def __init__(self, dimensions, shape, default_tile_shape=None, default_tile_format=None, extras=None):
        self.dimensions = tuple(dimensions)
        self.shape = shape
        self.default_tile_shape = tuple(default_tile_shape)
        self.default_tile_format = None if default_tile_format is None else default_tile_format
        self.extras = {} if extras is None else extras
        self._tiles = []

        self._discrete_dimensions = set()

    def validate(self):
        pass

    def add_tile(self, tile):
        self._tiles.append(tile)

    def filter_tiles(self, filter_fn=None):
        if filter_fn is None:
            return self._tiles
        return [tile for tile in self._tiles if filter_fn(tile)]

    def get_dimension_shape(self, dimension_name):
        return self.shape[dimension_name]
