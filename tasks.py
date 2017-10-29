from invoke import task


@task()
def test(ctx, target):
    """
    Run tests for specified target
    """
    ctx.run('python -m pytest {}'.format(target))


@task()
def test_all(ctx):
    """
    Run tests for both database and kairatools
    """
    test(ctx, 'database')
    test(ctx, 'kairatools/backend')
