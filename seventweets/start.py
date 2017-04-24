import argparse

from seventweets import init_db
from seventweets.server import Server


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''
                     starting db initialization and running servers ''')

    parser.add_argument('--dbname', dest='db_name', required=True,
                        help='name the db')
    parser.add_argument('--sname', dest='s_name', required=True,
                        help='name the server')

    subparsers = parser.add_subparsers(dest="subpar")

    init_parser = subparsers.add_parser('init_db')
    run_parser = subparsers.add_parser('run_server')

    run_parser.add_argument('--port', dest='port', required=True,
                            help='port on which server runs')
    run_parser.add_argument('--con', dest='con',
                            help='address of server to connect to')
    run_parser.add_argument('--my_addr', dest='my_address',
                            default='localhost')
    args = parser.parse_args()

    if args.subpar == 'init_db':
        init_db.init(server_name=args.s_name, database=args.db_name)
    elif args.subpar == 'run_server':
        server = Server(
            server_name=args.s_name,
            my_address=args.my_address,
            serving_at_port=args.port,
            database=args.db_name,
            connect_to=args.con
        )
        server.run()
    else:
        print('Invalid command')
