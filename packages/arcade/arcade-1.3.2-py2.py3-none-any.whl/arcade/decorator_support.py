from inspect import signature

from arcade.arcade_types import Color

import arcade


class ArcadeWindow(arcade.Window):
    def __init__(self, registry: dict, width: int, height: int,
                 title='Arcade Window',
                 background_color=None):
        super().__init__(width, height, title=title)

        self.registry = registry
        self.width = width
        self.height = height
        if background_color:
            arcade.set_background_color(background_color)

    def setup(self):
        game = self.registry.get('game')
        for func in self.registry['setup']:
            if game is not None:
                # Pass game instance as self
                func(game)
            else:
                sig = signature(func)
                if 'window' in sig.parameters:
                    func(self)
                else:
                    func()

    def on_draw(self):
        arcade.start_render()

        # Process any deferred imperative drawing
        for drawing in self.registry['deferred_drawing']:
            this_cmd = getattr(arcade, drawing['cmd'])
            this_args = drawing['args']
            this_kwargs = drawing['kwargs']
            this_cmd(*this_args, **this_kwargs)

        # Now run registered handlers
        game = self.registry.get('game')
        for func in self.registry['draw']:
            if game is not None:
                # Pass game instance as self
                func(game)
            else:
                sig = signature(func)
                if 'window' in sig.parameters:
                    func(self.registry['window'])
                else:
                    func()

    def update(self, delta_time):
        game = self.registry.get('game')
        for func in self.registry['update']:
            if game is not None:
                # Pass game instance as self
                func(game, delta_time)
            else:
                sig = signature(func)
                if 'window' in sig.parameters:
                    func(self.registry['window'], delta_time)
                else:
                    func(delta_time)

    def on_key_press(self, key, key_modifiers):
        game = self.registry.get('game')
        for func in self.registry['key_press']:
            if game is not None:
                # Pass game instance as self
                func(game, key, key_modifiers)
            else:
                sig = signature(func)
                if 'window' in sig.parameters:
                    func(self.registry['window'], key, key_modifiers)
                else:
                    func(key, key_modifiers)


class decorator(arcade.Window):
    """
    >>> import arcade
    >>> my_decorator = decorator()
    >>> def f():
    ...    pass
    >>> my_decorator.init(f) == f
    True
    >>> my_decorator.draw(f) == f
    True
    >>> my_decorator.setup(800, 600, "Test Window", arcade.color.WHITE)
    """

    registry = dict(
        setup=[],
        update=[],
        key_press=[],
        draw=[],
        game_class=None,
        game=None,  # Class-based games register a game, we store instance
        window=None,  # This will pyglet window as "global"
        deferred_drawing=[]
    )

    # The decorators
    @classmethod
    def init(cls, original_function):
        cls.registry['setup'].append(original_function)
        return original_function

    @classmethod
    def draw(cls, original_function):
        cls.registry['draw'].append(original_function)
        return original_function

    @classmethod
    def animate(cls, original_function):
        cls.registry['update'].append(original_function)
        return original_function

    @classmethod
    def key_press(cls, original_function):
        cls.registry['key_press'].append(original_function)
        return original_function

    @classmethod
    def game(cls, original_game):
        cls.registry['game_class'] = original_game

    # Now re-implement the arcade drawing methods, to avoid use of
    # global window (for now, faking the re-implementation)
    color = arcade.color
    key = arcade.key

    """
    @classmethod
    def draw_text(cls, *args, **kwargs):
        # Imperative mode means no event-handler functions, simplest
        # possible mode. Detect this by seeing if run has been called. If
        # not, then defer this drawing.
        if cls.registry['window'] is None:
            cls.registry['deferred_drawing'].append(
                dict(cmd='draw_text', args=args, kwargs=kwargs)
            )
        else:
            arcade.draw_text(*args, **kwargs)

    @classmethod
    def draw_circle_filled(cls, *args, **kwargs):
        if cls.registry['window'] is None:
            cls.registry['deferred_drawing'].append(
                dict(cmd='draw_circle_filled', args=args, kwargs=kwargs)
            )
        else:
            arcade.draw_circle_filled(*args, **kwargs)
    """

    @classmethod
    def setup(cls, width: int, height: int,
              title: str,
              background_color: Color):
        cls.registry['window'] = ArcadeWindow(
            cls.registry, width, height,
            title=title,
            background_color=background_color)

        # If a game is registered, instantiate it
        game_class = cls.registry.get('game_class')
        if game_class:
            cls.registry['game'] = game_class(cls.registry['window'])
            cls.registry['window'].setup()

    @classmethod
    def run(cls, width: int = 600, height: int = 400,
            title: str = 'Arcade Demo',
            background_color: Color = arcade.color.WHEAT):
        cls.setup(width, height, title, background_color)
        arcade.run()
