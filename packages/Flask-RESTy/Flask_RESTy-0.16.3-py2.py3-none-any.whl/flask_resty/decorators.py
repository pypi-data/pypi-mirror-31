import functools

# -----------------------------------------------------------------------------


def get_item_or_404(func=None, **decorator_kwargs):
    # Allow using this as either a decorator or a decorator factory.
    if func is None:
        return functools.partial(get_item_or_404, **decorator_kwargs)

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        id = self.get_data_id(kwargs)
        item = self.get_item_or_404(id, **decorator_kwargs)

        # No longer need these; just the item is enough.
        for id_field in self.id_fields:
            del kwargs[id_field]

        return func(self, item, *args, **kwargs)

    return wrapped
