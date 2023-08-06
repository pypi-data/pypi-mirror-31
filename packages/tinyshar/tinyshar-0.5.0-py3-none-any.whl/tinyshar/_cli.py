import argparse
import contextlib
import os
import shlex
import sys
import tinyshar


def _dest_path(src, dest):
    if dest == '' or dest.endswith('/'):
        return dest + os.path.basename(src)

    return dest


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="create a self-extracting shell archive",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + tinyshar.__version__
    )
    parser.add_argument(
        "-o",
        metavar="<file>",
        help="write output to <file> instead of stdout"
    )
    parser.add_argument(
        "-a",
        metavar="<dir>",
        action='append',
        default=[],
        help="directory containing files to be extracted to root. Can be specified multiple times"
    )
    parser.add_argument(
        "-f",
        metavar="<src:dest[:mode]>",
        action='append',
        default=[],
        help='add a single file "src" to be extracted to "dest". '
             'If "dest" ends with "/" it is treated as a directory name. Can be specified multiple times'
    )
    parser.add_argument(
        "-r",
        metavar="<dir>",
        action='append',
        default=[],
        help="directory containing files to be extracted to arena. Can be specified multiple times"
    )
    parser.add_argument(
        "-p",
        metavar="<cmd>",
        action='append',
        default=[],
        help="command to execute before file extraction. Can be specified multiple times"
    )
    parser.add_argument(
        "-c",
        metavar="<cmd>",
        action='append',
        default=[],
        help="command to execute after file extraction. Can be specified multiple times"
    )
    parser.add_argument(
        "-L",
        action='store_true',
        default=False,
        help="follow directory symlinks"
    )
    parser.add_argument(
        "--no-shellcheck",
        action='store_true',
        help="do not check resulting archive with shellcheck"
    )
    parser.add_argument(
        "--no-tee",
        action='store_true',
        help="do tee stdout and stderr of extractor to file"
    )

    args = parser.parse_args(args=argv)

    shar = tinyshar.SharCreator()

    for i in args.a:
        shar.add_dir(i, '/', follow_symlinks=args.L)

    for i in args.r:
        shar.add_dir(i, '', follow_symlinks=args.L)

    for i in args.p:
        shar.add_pre(i)

    for i in args.f:
        def add_file(desc):
            desc = desc.split(':', 2)
            src, dest = desc[:2]
            dest_path = _dest_path(src, dest)
            print(src, dest_path)
            shar.add_file(dest_path, lambda: open(src, 'rb'))

            if len(desc) > 2:
                mode = desc[2]
                shar.add_post("chmod %s %s" % (mode, shlex.quote(dest_path)))

        add_file(i)

    for i in args.c:
        shar.add_post(i)

    with contextlib.ExitStack() as exit_stack:
        if args.o:
            out_stm = exit_stack.enter_context(open(args.o, 'wb'))
        else:
            out_stm = sys.stdout.buffer

        try:
            shar.render(
                out_stm=out_stm,
                build_validators=[] if args.no_shellcheck else [tinyshar.ShellcheckValidator()],
                tee_to_file=not args.no_tee
            )
        except tinyshar.ValidatorError as e:
            sys.exit(str(e))
