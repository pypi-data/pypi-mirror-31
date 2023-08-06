import sys

import click
from terminaltables import AsciiTable

from ..utils import make_request


@click.group()
def job():
    """Jobs cli."""
    pass


@job.command('create', short_help='create a new job.')
@click.option('--description', '-d', help="Description", default=None)
@click.option('--blueprint', '-b', help="Blueprint to use", default=None)
@click.option('--machine', '-m', help="Machine type", default=None)
@click.option('--gpu', help="Add gpu", is_flag=True)
@click.option('--command', '-c', help="Command to run", default=None)
def create(description, blueprint, machine, gpu, command):
    """Create a new job."""
    if description is None:
        click.echo("A description is needed.")
        sys.exit(1)

    if blueprint is None:
        click.echo("You need to select a blueprint.")
        sys.exit(1)

    if machine is None:
        click.echo("You need to select a machine type.")
        sys.exit(1)

    if command is None:
        click.echo("You need to specify a command.")
        sys.exit(1)

    data = {
        "description": description,
        "blueprint": blueprint,
        "machine_type": machine,
        "gpu": gpu,
        "command": command,
    }
    response = make_request('/api/spawner/jobs', method='POST', data=data)

    click.echo(response.json()['message'])


@job.command()
def list():
    """List your jobs."""
    response = make_request('/api/spawner/jobs', method='GET')
    jobs = response.json()['jobs']
    data = []
    data.append(["", "Name", "Command", "Blueprint", "Status", "Machine/GPU"])
    for index, job in enumerate(jobs):

        gpu = "Y" if job['specs']['gpu'] else "N"
        data.append([
            index,
            job['name'],
            job['specs']['command'],
            f"{job['specs']['repository']}/{job['specs']['blueprint']}",
            job['status'],
            f"{job['specs']['machine_type']}/{gpu}",
        ])
    table = AsciiTable(data)
    table.inner_row_border = True
    click.echo(table.table)


@job.command()
@click.argument('name')
def remove(name):
    """Remove a job."""
    uri = '/api/spawner/jobs/{}'.format(name)
    response = make_request(uri, method='DELETE')

    click.echo(response.json()['message'])


@job.command()
@click.argument('name')
def logs(name):
    """Get logs of a job."""
    uri = '/api/spawner/jobs/logs/{}'.format(name)
    response = make_request(uri, method='GET')
    logs = response.json()['logs']

    for log in logs:
        click.echo(log)
