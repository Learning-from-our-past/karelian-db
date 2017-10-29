from invoke import task
import os


@task()
def test(ctx):
    os.chdir('../')
    ctx.run('python -m pytest database')

