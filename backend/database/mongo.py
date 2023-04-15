"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: mongo.py
 @DateTime: 2023/4/8 14:12
 @SoftWare: PyCharm
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure, CollectionInvalid

from config import mongo_settings
from log import database_logger
import pymongo

logger = database_logger


MONGO_URI_DEFAULT = 'mongodb://localhost:27017/'
URI_CLIENT_DICT = {} 	# a dictionary hold all client with uri as key


class DBManager:
    """A safe and simple pymongo packaging class ensuring existing database and collection.
    Operations:
    MongoClient level operations: https://api.mongodb.com/python/current/api/pymongo/mongo_client.html
    Database level operations: https://api.mongodb.com/python/current/api/pymongo/database.html
    Collection level operations: https://api.mongodb.com/python/current/api/pymongo/collection.html
    """
    __default_uri = f"mongodb://{mongo_settings.get('host', '127.0.0.1')}:{mongo_settings.get('port', '27017')}/"
    __default_db_name = mongo_settings.get('db_name', 'chat2Bili')
    # __default_coll_name = 'test'

    def __init__(self, uri=__default_uri, db_name=__default_db_name, *, coll_name, **kwargs):
        self.__uri = uri
        self.__db_name = db_name
        self.__coll_name = coll_name
        self.__client = get_mongo_client(uri, **kwargs)
        self.__db = get_existing_db(self.__client, db_name)
        self.__coll = get_existing_coll(self.__db, coll_name)

    def __str__(self):
        return u'uri: {}, db_name: {}, coll_name: {}, id_client: {}, client: {}, db: {}, coll: {}'.format(
            self.uri, self.db_name, self.coll_name, id(self.client), self.client, self.db, self.coll)

    @classmethod
    def create(cls, coll_name):
        dbm = cls(coll_name=coll_name)
        dbm.db_name = dbm.__db_name
        dbm.coll_name = dbm.coll_name
        return dbm

    @property
    def uri(self):
        return self.__uri

    @property
    def db_name(self):
        return self.__db_name

    @property
    def coll_name(self):
        return self.__coll_name

    @db_name.setter
    def db_name(self, db_name):
        self.__db_name = db_name
        self.__db = get_existing_db(self.__client, db_name)

    @coll_name.setter
    def coll_name(self, coll_name):
        self.__coll_name = coll_name
        self.__coll = get_existing_coll(self.__db, coll_name)

    @property
    def client(self):
        return self.__client

    @property
    def db(self):
        return self.__db

    @property
    def coll(self):
        # always use the current instance self.__db
        self.__coll = get_existing_coll(self.__db, self.__coll_name)
        return self.__coll

    def create_coll(self, db_name, coll_name):
        """Create new collection with new or existing database"""
        if self.__client is None:
            return None
        try:
            return self.__client.get_database(db_name).create_collection(coll_name)
        except CollectionInvalid:
            logger.error('collection {} already exists in database {}'.format(coll_name, db_name))
            return None

    def session_pipeline(self, pipeline):
        if self.__client is None:
            logger.error('client is None in session_pipeline: {}'.format(self.__client))
            return None
        with self.__client.start_session(causal_consistency=True) as session:
            result = []
            for operation in pipeline:
                try:
                    if operation.level == 'client':
                        target = self.__client
                    elif operation.level == 'db':
                        target = self.__db
                    elif operation.level == 'coll':
                        target = self.__coll
                    operation_name = operation.operation_name
                    args = operation.args
                    kwargs = operation.kwargs
                    operator = getattr(target, operation_name)
                    if type(args) == tuple:
                        ops_rst = operator(*args, session=session, **kwargs)
                    else:
                        ops_rst = operator(args, session=session, **kwargs)
                    if operation.callback is not None:
                        operation.out = operation.callback(ops_rst)
                    else:
                        operation.out = ops_rst
                except Exception as e:
                    logger.error('{} {} Exception, session_pipeline args: {}, kwargs: {}'.format(
                        target, operation, args, kwargs))
                    logger.error('session_pipeline Exception: {}'.format(repr(e)))
                result.append(operation)
            return result

    # https://api.mongodb.com/python/current/api/pymongo/client_session.html#transactions
    def transaction_pipeline(self, pipeline):
        if self.__client is None:
            logger.error('client is None in transaction_pipeline: {}'.format(self.__client))
            return None
        with self.__client.start_session(causal_consistency=True) as session:
            with session.start_transaction():
                result = []
                for operation in pipeline:
                    try:
                        if operation.level == 'client':
                            target = self.__client
                        elif operation.level == 'db':
                            target = self.__db
                        elif operation.level == 'coll':
                            target = self.__coll
                        operation_name = operation.operation_name
                        args = operation.args
                        kwargs = operation.kwargs
                        operator = getattr(target, operation_name)
                        if type(args) == tuple:
                            ops_rst = operator(*args, session=session, **kwargs)
                        else:
                            ops_rst = operator(args, session=session, **kwargs)
                        if operation.callback is not None:
                            operation.out = operation.callback(ops_rst)
                        else:
                            operation.out = ops_rst
                    except Exception as e:
                        logger.error('{} {} Exception, transaction_pipeline args: {}, kwargs: {}'.format(
                            target, operation, args, kwargs))
                        logger.error('transaction_pipeline Exception: {}'.format(repr(e)))
                        raise Exception(repr(e))
                    result.append(operation)
                return result


def new_mongo_client(uri, **kwargs):
    """Create new pymongo.mongo_client.MongoClient instance. DO NOT USE IT DIRECTLY."""
    try:
        client = MongoClient(uri, maxPoolSize=1024, **kwargs)
        client.admin.command('ismaster')  # The ismaster command is cheap and does not require auth.
    except ConnectionFailure:
        logger.error("new_mongo_client(): Server not available, Please check you uri: {}".format(uri))
        return None
    else:
        return client


def get_mongo_client(uri=MONGO_URI_DEFAULT, fork=False, **kwargs):
    """Get pymongo.mongo_client.MongoClient instance. One mongodb uri, one client.
    @:param uri: mongodb uri
    @:param fork: for fork-safe in multiprocess case, if fork=True, return a new MongoClient instance, default False.
    @:param kwargs: refer to pymongo.mongo_client.MongoClient kwargs
    """
    if fork:
        return new_mongo_client(uri, **kwargs)
    global URI_CLIENT_DICT
    matched_client = URI_CLIENT_DICT.get(uri)
    if matched_client is None:  # no matched client
        new_client = new_mongo_client(uri, **kwargs)
        if new_client is not None:
            URI_CLIENT_DICT[uri] = new_client
        return new_client
    return matched_client


def get_existing_db(client, db_name):
    """Get existing pymongo.database.Database instance.
    @:param client: pymongo.mongo_client.MongoClient instance
    @:param db_name: database name wanted
    """
    if client is None:
        logger.error('client {} is None'.format(client))
        return None
    try:
        db_available_list = client.list_database_names()
    except PyMongoError as e:
        logger.error('client: {}, db_name: {}, client.list_database_names() error: {}'.
                      format(client, db_name, repr(e)))
    else:
        if db_name not in db_available_list:
            logger.error('client {} has no db named {}'.format(client, db_name))
            return None
    db = client.get_database(db_name)
    return db


def get_existing_coll(db, coll_name):
    """Get existing pymongo.collection.Collection instance.
    @:param client: pymongo.mongo_client.MongoClient instance
    @:param coll_name: collection name wanted
    """
    if db is None:
        logger.error('db {} is None'.format(db))
        return None
    try:
        coll_available_list = db.list_collection_names()
    except PyMongoError as e:
        logger.error('db: {}, coll_name: {}, db.list_collection_names() error: {}'.
                      format(db, coll_name, repr(e)))
    else:
        if coll_name not in coll_available_list:
            logger.error('db {} has no collection named {}'.format(db, coll_name))
            return None
    coll = db.get_collection(coll_name)
    return coll