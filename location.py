import inspect


def auto_repr(cls):
    members = vars(cls)

    if "__repr__" in members:
        raise TypeError(f"{cls.__name__} already defines __repr__")

    if "__init__" not in members:
        raise TypeError(f"{cls.__name__} does not override __init__")

    sig = inspect.signature(cls.__init__)
    parameters_name = list(sig.parameters)[1:]

    if not all(
        isinstance(members.get(name, None),property)
        for name in parameters_name
    ):
        raise TypeError(f"Cannot apply auto_repr to {cls.__name__} because not all"
                        f"__init__ parameters matching all properties"
                        )

    def synthesized_repr(self):
        return "{typename}({args})".format(
            typename = typename(self),
            args=".".join(
                "{name}={value!r}".format(
                    name=name,
                    value=getattr(name)
                ) for name in parameters_name
            )
        )

    setattr(cls, "__repr__", synthesized_repr)

    return cls


@auto_repr
class Position:

    def __init__(self, latitude, longitude):
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude {latitude} out of range")

        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude {longitude} out of range")

        self._latitude = latitude
        self._longitude = longitude

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def latitude_hemisphere(self):
        return "N" if self.latitude > 0 else "S"

    def longitude_hemisphere(self):
        return "E" if self.longitude > 0 else "W"

    def __str__(self):
        return (
            f"{abs(self.latitude)}° {self.latitude_hemisphere}, "
            f"{abs(self.longitude)}° {self.longitude_hemisphere()}"
        )

    def __format__(self, format_spec):
        component_format_spec = ".2f"
        prefix, dot, suffix = format_spec.partition(".")
        if dot:
            number_decimal_places = int(suffix)
            component_format_spec = f".{number_decimal_places}f"
        latitude = format(abs(self.latitude), component_format_spec)
        longitude = format(abs(self.longitude), component_format_spec)
        return (
            f"{latitude}° {self.latitude_hemisphere}, "
            f"{longitude}° {self.longitude_hemisphere()}"
        )


class EarthPosition(Position):
    pass


class MarsPosition(Position):
    pass


def typename(obj):
    return type(obj).__name__
