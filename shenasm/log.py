

def verbose_on(*args, **kwargs):
    """
    dumb wrapper for print, see verbose_off and verbose
    """
    print(*args, **kwargs)


def verbose_off(*args, **kwargs):
    """
    dummy function provides alternative to verbose_off
    """
    _ = args, kwargs


# dumb way of doing optional verbose output, see verbose_on and verbose_off
verbose = verbose_off
