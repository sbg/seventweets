import json

import pg8000

from seventweets.exceptions import BadRequest, Forbidden


class Registry:
    """
    Manages registration and removal of servers
    """

    def __init__(self, name, address):
        """
        Initialize Registry and servers dict
        :param name: Server name
        :param address: Server address
        """
        self.servers = dict()
        self.servers[name] = address

    def register(self, name, address):
        """
        Adds server to servers dict
        :param name: Server name.
        :param address: Server address.
        :return: Dict of registered servers.
        """
        if self.servers.get(name):
            raise BadRequest('Username already exists')
        else:
            self.servers[name] = address
            return json.dumps(self.servers)

    def unregister(self, name, ip):
        """
        Remove server from servers dict
        :param name: Server name
        :param ip: ip address of server sending request
        :return: json with status
        """
        ip_address = (self.servers[name]).split(':')[0]
        if ip_address == ip:
            del self.servers[name]
            return json.dumps({'status': 'ok'})
        else:
            raise Forbidden('You are not authorized for this action')


class QueryArgs:
    """
    Holds search params as attributes
    """

    def __init__(self, content, name, from_time,
                 to_time, per_page, last_creation_time):
        """
        Initialize object with search query parameters
        :param content:
        :param name:
        :param from_time:
        :param to_time:
        :param per_page:
        :param last_creation_time:
        """
        self.content = content
        self.name = name
        self.from_time = from_time
        self.to_time = to_time
        self.per_page = per_page
        self.last_creation_time = last_creation_time

    def to_dict(self):
        """
        Make dict from object attributes
        :return: Object attributes as dict
        """
        return {
            'content': self.content,
            'name': self.name,
            'from_time': self.from_time,
            'to_time': self.to_time,
            'per_page': self.per_page,
            'last_creation_time': self.last_creation_time,
        }

    def query_creator(self, retweet, start_time=None):
        """
        Create query string and list of params from object arguments
        :param retweet: tweet type (original, retweet)
        :param start_time: offset in query
        :return: query string and params list
        """
        params = []
        query = '''SELECT id,name,tweet,creation_time,type,reference
                   FROM tweets WHERE '''
        if not retweet:
            query += 'reference is NULL'
            if self.content:
                query += ' AND tweet LIKE %s'
                params.append('%'+self.content+'%')
            if self.last_creation_time:
                query += ' AND creation_time > %s'
                params.append(self.last_creation_time)
            elif self.from_time:
                query += ' AND creation_time >= %s '
                params.append(self.from_time)
            if self.to_time:
                query += ' AND creation_time <= %s '
                params.append(self.to_time)
            if self.per_page:
                query += ' ORDER BY creation_time LIMIT %s'
                params.append(self.per_page)
        else:
            query += ' reference is NOT NULL'
            if start_time:
                query += ' AND creation_time > %s'
                params.append(start_time)
            if self.from_time:
                query += ' AND creation_time >= %s'
                params.append(self.from_time)
            if self.to_time:
                query += ' AND creation_time <= %s '
                params.append(self.to_time)
            if self.per_page:
                query += ' ORDER BY creation_time LIMIT %s'
                params.append(self.per_page)
        return query, params


class Database:
    """
    Manages db connection and query execution
    """

    def __init__(self, user, database, host='localhost', unix_sock=None,
                 port=5432, password=None, ssl=False, timeout=None):
        """
        Initialize class with db parameters
        :param user:
        :param database:
        :param host:
        :param unix_sock:
        :param port:
        :param password:
        :param ssl:
        :param timeout:
        """
        self.db_con = None
        self.user = user
        self.database = database
        self.host = host
        self.unix_sock = unix_sock
        self.port = port
        self.password = password
        self.ssl = ssl
        self.timeout = timeout

    def get_db(self):
        """
        Get connection to db
        :return: db connection
        """
        db = self.db_con
        if db is None:
            db = self.db_con = pg8000.connect(
                user=self.user,
                database=self.database,
                host=self.host,
                unix_sock=self.unix_sock,
                port=self.port,
                password=self.password,
                ssl=self.ssl,
                timeout=self.timeout
            )
        return db

    def close_connection(self):
        """
        Closes connection to db
        """
        db = self.db_con
        if db is not None:
            db.close()

    def query_execute(self, query, args=()):
        """
        Execute query with params
        :param query: sql string to execute
        :param args: params for query
        :return: rows as result
        """
        db = self.get_db()
        cur = db.cursor()
        cur.execute(query, args)
        result = cur.fetchall()
        db.commit()
        cur.close()
        return result

