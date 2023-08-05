import time

from functools import wraps


def retry(Except, retries=5, delay=0, logger=None, level='info', multiple=1):

    def deco_retry(function):

        @wraps(function)
        def f_retry(*args, **kwargs):
            tries = 1
            mdelay = delay
            while tries < retries:
                try:
                    return function(*args, **kwargs)
                except Except as e:
                    msg = '{e}, Retrying {tries} of {retries}'.format(
                        e=e,
                        tries=tries,
                        retries=retries
                    )
                    if mdelay:
                        msg = ' '.join([msg, 'in {} seconds...'.format(mdelay)])
                    if logger:
                        getattr(logger, level)(msg)
                    time.sleep(mdelay)
                    mdelay *= multiple
                    tries += 1
            return function(*args, **kwargs)
        return f_retry
    return deco_retry
