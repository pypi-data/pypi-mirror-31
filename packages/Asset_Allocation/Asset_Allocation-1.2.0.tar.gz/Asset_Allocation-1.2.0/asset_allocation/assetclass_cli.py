"""
CLI for dealing with Asset Classes
"""
import sys
from decimal import Decimal

import click

from asset_allocation.app import AppAggregate
from asset_allocation.dal import AssetClass


@click.group()
def ac():
    """ Operates the Asset Class records """
    pass


@click.command()
# , prompt="Asset Class name") # help="Name of the Asset Class"
@click.argument("name", "-n")
def add(name):
    """ Add new Asset Class """
    item = AssetClass()
    item.name = name
    app = AppAggregate()
    app.create_asset_class(item)

    print(f"Asset class {name} created.")


@click.command()
@click.argument("id", type=int)
def delete(id):
    """ Deletes asset class record """
    app = AppAggregate()
    app.delete(id)


@click.command()
@click.argument("id", type=int)
@click.option("--parent", "-p", type=int, help="Set the parent")
@click.option("--alloc", "-a", type=Decimal)
def edit(id: int, parent: int, alloc: Decimal):
    """ Edit asset class """
    saved = False

    # load
    app = AppAggregate()
    item = app.get(id)
    if not item:
        raise KeyError("Asset Class with id %s not found.", id)

    if parent:
        assert parent != id, "Parent can not be set to self."

        # TODO check if parent exists?

        item.parentid = parent
        saved = True
        # click.echo(f"parent set to {parent}")

    if alloc:
        assert alloc != Decimal(0)

        item.allocation = alloc
        saved = True

    app.save()
    if saved:
        click.echo("Data saved.")
    else:
        click.echo("No data modified. Use --help to see possible parameters.")


@click.command("list")
def my_list():
    """ Lists all asset classes """
    session = AppAggregate().open_session()
    classes = session.query(AssetClass).all()
    for item in classes:
        print(item)


@click.command("import")
#, help="The path to the CSV file to import. The first row must contain column names."
@click.argument("file")
def my_import(file):
    """ Import Asset Class(es) from a .csv file """
    lines = ""
    with open(file) as csv_file:
        lines = csv_file.readlines()

    # Header, the first line.
    header = lines[0]
    lines.remove(header)
    header = header.rstrip()
    # print(f"header: {header}")

    # Parse records from a csv row.
    counter = 0
    app = AppAggregate()
    app.open_session()
    for line in lines:
        # Create insert statements
        line = line.rstrip()
        command = f"insert into AssetClass ({header}) values ({line});"
        # insert records
        app.session.execute(command)
        try:
            app.save()
        except:
            print(f"error: ", sys.exc_info()[0])
            app.session.close()
        counter += 1
    print(f"Data imported. {counter} rows created.")


ac.add_command(add)
ac.add_command(delete)
ac.add_command(edit)
ac.add_command(my_import)
ac.add_command(my_list)
