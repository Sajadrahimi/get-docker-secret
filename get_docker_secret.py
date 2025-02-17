import os

root = os.path.abspath(os.sep)


def get_docker_secret(name, default=None, cast_to=str, autocast_name=True, getenv=True, env_name=None, safe=True,
                      secrets_dir=os.path.join(root, 'var', 'run', 'secrets')):
    """This function fetches a docker secret

    :param name: the name of the docker secret
    :param default: the default value if no secret found
    :param cast_to: casts the value to the given type
    :param autocast_name: whether the name should be lowercase for secrets and upper case for environment
    :param getenv: if environment variable should be fetched as fallback
    :param env_name: this name will be used to get variable from env, default will be the same as name
    :param safe: Whether the function should raise exceptions
    :param secrets_dir: the directory where the secrets are stored
    :returns: docker secret or environment variable depending on params
    :raises TypeError: if cast fails due to wrong type (None)
    :raises ValueError: if casts fails due to Value
    """

    # cast name if autocast enabled
    name_secret = name.lower() if autocast_name else name
    if getenv:
        if not env_name:
            env_name = name
        env_name = env_name.upper() if autocast_name else env_name

    # initialize value
    value = None

    # try to read from secret file
    try:
        with open(os.path.join(secrets_dir, name_secret), 'r') as secret_file:
            value = secret_file.read().rstrip('\n')
    except IOError as e:
        # try to read from env if enabled
        if getenv:
            value = os.environ.get(env_name)
        elif safe:
            return value
        else:
            raise e

    # set default value if no value found
    if value is None:
        return default

    # try to cast
    try:
        # special case bool
        if cast_to == bool:
            if value not in ('True', 'true', 'False', 'false', '1', 1):
                raise ValueError('value %s not of type bool' % value)
            value = 1 if value in ('True', 'true') else 0

        # try to cast
        return cast_to(value)

    except (TypeError, ValueError) as e:
        # whether exception should be thrown
        if safe:
            return value
        raise e
