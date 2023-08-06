# -*- coding: utf-8 -*-
"""CLI for prance."""

__author__ = 'Jens Finkhaeuser'
__copyright__ = 'Copyright (c) 2016-2017 Jens Finkhaeuser'
__license__ = 'MIT +no-false-attribs'
__all__ = ()


import click

import prance


def __write_to_file(filename, specs):  # noqa: N802
  """
  Write specs to the given filename.

  This takes into account file name extensions as per `fs.write_file`.
  """
  from prance.util import fs, formats
  contents = formats.serialize_spec(specs, filename)
  fs.write_file(filename, contents)


@click.group()
@click.version_option(version = prance.__version__)
def cli():
  pass  # pragma: no cover


@click.command()
@click.option(
    '--resolve/--no-resolve',
    default = True,
    help = 'Resolve external references before validation. The default is to '
           'do so.'
)
@click.option(
    '--backend',
    default = 'flex',
    metavar = 'BACKEND',
    nargs = 1,
    help = 'The validation backend to use. One of "flex" or '
           '"swagger-spec-validator".'
)
@click.option(
    '--strict/--no-strict',
    default = True,
    help = 'Be strict or lenient in validating specs. Strict validation '
           'rejects non-string spec keys, for example in response codes. '
           'Only applies to the "swagger-spec-validator" backend.'
)
@click.option(
    '--output-file', '-o',
    type = click.Path(exists = False),
    default = None,
    metavar = 'FILENAME',
    nargs = 1,
    help = 'If given, write the validated specs to this file. Together with '
           'the --resolve option, the output file will be a resolved version '
           'of the input file.'
)
@click.argument(
    'urls',
    type = click.Path(exists = False),
    nargs = -1,
)
def validate(resolve, backend, strict, output_file, urls):
  """
  Validate the given spec or specs.

  If the --resolve option is set, references will be resolved before
  validation.

  Note that this merges referenced objects into the main specs. Validation
  backends used by prance cannot validate referenced objects, so resolving
  the references before validation allows for full spec validation.

  If the --output-file option is given, the validated spec is written to that
  file. Please note that with that option given, only one input file may be
  specified. Using this option together with --resolve effectively creates
  a compiled and validated spec with no further external references.
  """
  # Ensure that when an output file is given, only one input file exists.
  if output_file and len(urls) > 1:
    raise click.UsageError('If --output-file is given, only one input URL '
        'is allowed!')

  import os.path
  from prance.util import fs
  # Process files
  for url in urls:
    formatted = click.format_filename(url)
    click.echo('Processing "%s"...' % (formatted, ))
    fsurl = fs.abspath(url)
    if os.path.exists(fs.from_posix(fsurl)):
      url = fsurl

    # Create parser to use
    if resolve:
      click.echo(' -> Resolving external references.')
      parser = prance.ResolvingParser(url, lazy = True, backend = backend,
              strict = strict)
    else:
      click.echo(' -> Not resolving external references.')
      parser = prance.BaseParser(url, lazy = True, backend = backend,
              strict = strict)

    # Try parsing
    from prance.util.url import ResolutionError
    from prance import SwaggerValidationError
    try:
      parser.parse()
    except (ResolutionError, SwaggerValidationError) as err:
      msg = 'ERROR in "%s" [%s]: %s' % (formatted, type(err).__name__,
          str(err))
      click.secho(msg, err = True, fg = 'red')
      import sys
      sys.exit(1)

    # All good, next file.
    click.echo('Validates OK as Swagger/OpenAPI 2.0!')

    # If an output file is given, write the specs to it.
    if output_file:
      __write_to_file(output_file, parser.specification)


cli.add_command(validate)
