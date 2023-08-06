from guillotina.commands import Command
from guillotina.commands.utils import change_transaction_strategy
from guillotina.component import getUtility
from guillotina.db.reader import reader
from guillotina.interfaces import ICatalogUtility
from guillotina.utils import get_containers
from guillotina_elasticsearch.migration import Migrator
from lru import LRU  # pylint: disable=E0611

import aioes
import asyncio
import json
import logging


try:
    from guillotina.utils import clear_conn_statement_cache
except ImportError:
    def clear_conn_statement_cache(conn):
        pass

logger = logging.getLogger('guillotina_elasticsearch_vacuum')


SELECT_BY_KEYS = '''SELECT zoid from objects where zoid = ANY($1)'''
BATCHED_GET_CHILDREN_BY_PARENT = """
SELECT zoid
FROM objects
WHERE of is NULL AND parent_id = ANY($1)
ORDER BY parent_id
LIMIT $2::int
OFFSET $3::int
"""


PAGE_SIZE = 500


class Vacuum:

    def __init__(self, txn, tm, request, container):
        self.txn = txn
        self.tm = tm
        self.request = request
        self.container = container
        self.orphaned = []
        self.missing = []
        self.utility = getUtility(ICatalogUtility)
        self.migrator = Migrator(
            self.utility, self.container, full=True, bulk_size=10)
        self.cache = LRU(200)

    async def iter_batched_es_keys(self):
        index_name = await self.utility.get_index_name(self.container)
        result = await self.utility.conn.search(
            index=index_name,
            scroll='15m',
            size=PAGE_SIZE,
            _source=False,
            body={
                "sort": ["_doc"]
            })
        yield [r['_id'] for r in result['hits']['hits']]
        scroll_id = result['_scroll_id']
        while scroll_id:
            try:
                result = await self.utility.conn.scroll(
                    scroll_id=scroll_id,
                    scroll='5m'
                )
            except aioes.exception.TransportError:
                # no results
                break
            if len(result['hits']['hits']) == 0:
                break
            yield [r['_id'] for r in result['hits']['hits']]
            scroll_id = result['_scroll_id']

    async def get_db_page_of_keys(self, oids, page=1, page_size=PAGE_SIZE):
        conn = await self.txn.get_connection()
        clear_conn_statement_cache(conn)
        keys = []
        async with self.txn._lock:
            for record in await conn.fetch(
                    BATCHED_GET_CHILDREN_BY_PARENT, oids,
                    page_size, (page - 1) * page_size):
                keys.append(record['zoid'])
        return keys

    async def iter_paged_db_keys(self, oids):
        page_num = 1
        page = await self.get_db_page_of_keys(oids, page_num)
        while page:
            yield page
            async for sub_page in self.iter_paged_db_keys(page):
                yield sub_page
            page_num += 1
            page = await self.get_db_page_of_keys(oids, page_num)

    async def get_object(self, oid):
        if oid in self.cache:
            return self.cache[oid]

        try:
            result = self.txn._manager._hard_cache.get(oid, None)
        except AttributeError:
            from guillotina.db.transaction import HARD_CACHE  # pylint: disable=E0611
            result = HARD_CACHE.get(oid, None)
        if result is None:
            clear_conn_statement_cache(await self.txn.get_connection())
            result = await self.txn._cache.get(oid=oid)

        if result is None:
            result = await self.tm._storage.load(self.txn, oid)

        obj = reader(result)
        obj._p_jar = self.txn
        if result['parent_id']:
            obj.__parent__ = await self.get_object(result['parent_id'])
        return obj

    async def process_missing(self, oid, full=True):
        # need to fill in parents in order for indexing to work...
        logger.warning(f'Index missing {oid}')
        try:
            obj = await self.get_object(oid)
        except (KeyError, AttributeError, TypeError):
            logger.warning(f'Could not find {oid}')
            return  # object or parent of object was removed, ignore
        await self.migrator.index_object(obj, full=full)

    async def __call__(self):
        # how we're doing this...
        # 1) iterate through all es keys
        # 2) batch check obs exist in db
        # 3) iterate through all db keys
        # 4) batch check they are in elasticsearch
        # WHY this way?
        #   - uses less memory rather than getting all keys in both.
        #   - this way should allow us handle VERY large datasets

        self.index_name = await self.utility.get_index_name(self.container)
        self.migrator.work_index_name = self.index_name
        logger.warning('Running vacuum...')
        await asyncio.gather(self.check_orphans(), self.check_missing())

    async def check_orphans(self):
        conn = await self.txn.get_connection()
        checked = 0
        async for es_batch in self.iter_batched_es_keys():
            checked += len(es_batch)
            clear_conn_statement_cache(conn)
            async with self.txn._lock:
                records = await conn.fetch(SELECT_BY_KEYS, es_batch)
            db_batch = set()
            for record in records:
                db_batch.add(record['zoid'])
            orphaned = [k for k in set(es_batch) - db_batch]
            if checked % 10000 == 0:
                logger.warning(f'Checked ophans: {checked}')
            if orphaned:
                # these are keys that are in ES but not in DB so we should
                # remove them..
                self.orphaned.extend(orphaned)
                logger.warning(f'deleting orphaned {len(orphaned)}')
                conn_es = await self.utility.conn.transport.get_connection()
                # delete by query for orphaned keys...
                await conn_es._session.post(
                    '{}{}/_delete_by_query'.format(
                        conn_es._base_url.human_repr(),
                        self.index_name),
                    data=json.dumps({
                        'query': {
                            'terms': {
                                'uuid': orphaned
                            }
                        }
                    }))

    async def check_missing(self):
        checked = 0
        async for batch in self.iter_paged_db_keys([self.container._p_oid]):
            es_batch = []
            results = await self.utility.conn.search(
                self.index_name, body={
                    'query': {
                        'terms': {
                            'uuid': batch
                        }
                    }
                },
                _source=False,
                size=PAGE_SIZE)
            for result in results['hits']['hits']:
                es_batch.append(result['_id'])
            missing = [k for k in set(batch) - set(es_batch)]
            checked += len(batch)
            if missing:
                logger.warning(
                    f'indexing missing: {len(missing)}, total checked: {checked}')
                # these are keys that are in DB but not in ES so we
                # should index them..
                self.missing.extend(missing)
                for oid in missing:
                    await self.process_missing(oid)

        await self.migrator.flush()
        await self.migrator.join_futures()


class VacuumCommand(Command):
    description = 'Run vacuum on elasticearch'
    vacuum_klass = Vacuum

    def get_parser(self):
        parser = super(VacuumCommand, self).get_parser()
        parser.add_argument(
            '--continuous', help='Continuously vacuum', action='store_true')
        parser.add_argument('--sleep', help='Time in seconds to sleep',
                            default=10 * 60, type=int)
        return parser

    async def run(self, arguments, settings, app):
        change_transaction_strategy('none')
        self.request._db_write_enabled = True
        self.request._message.headers['Host'] = 'localhost'
        first_run = True
        while arguments.continuous or first_run:
            if not first_run:
                await asyncio.sleep(arguments.sleep)
            else:
                first_run = False
            async for txn, tm, container in get_containers(self.request):
                logger.warning(f'Vacuuming container {container.id}', extra={
                    'account': container.id
                })
                try:
                    vacuum = self.vacuum_klass(
                        txn, tm, self.request, container)
                    await vacuum()
                    logger.warning(f'''Finished vacuuming with results:
Orphaned cleaned: {len(vacuum.orphaned)}
Missing added: {len(vacuum.missing)}
''')
                except Exception:
                    logger.error('Error vacuuming', exc_info=True)
                finally:
                    await tm.abort(txn=txn)
