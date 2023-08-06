from guillotina import app_settings
from guillotina.component import getUtility
from guillotina.event import notify
from guillotina.events import ObjectRemovedEvent
from guillotina.interfaces import IAnnotations
from guillotina.interfaces import ICatalogUtility
from guillotina.registry import REGISTRY_DATA_KEY
from guillotina.tests.utils import create_content
from guillotina.transactions import managed_transaction
from guillotina.utils import get_content_path
from guillotina_elasticsearch.interfaces import DOC_TYPE
from guillotina_elasticsearch.manager import DEFAULT_SETTINGS
from guillotina_elasticsearch.migration import Migrator
from guillotina_elasticsearch.schema import get_mappings
from guillotina_elasticsearch.tests.utils import add_content
from guillotina_elasticsearch.tests.utils import run_with_retries
from guillotina_elasticsearch.tests.utils import setup_txn_on_container

import aioelasticsearch
import aiotask_context
import asyncio
import pytest
import random


@pytest.mark.flaky(reruns=5)
async def _test_migrate_while_content_getting_added(es_requester):
    async with es_requester as requester:
        add_count = await add_content(requester)

        container, request, txn, tm = await setup_txn_on_container(requester)

        search = getUtility(ICatalogUtility)
        await search.refresh(container)
        await asyncio.sleep(3)

        assert add_count == await search.get_doc_count(container)

        migrator = Migrator(search, container, force=True)
        add_content_task1 = asyncio.ensure_future(add_content(requester, base_id='foo1-'))
        add_content_task2 = asyncio.ensure_future(add_content(requester, base_id='foo2-'))
        reindex_task = asyncio.ensure_future(migrator.run_migration())

        await asyncio.wait([add_content_task1, reindex_task, add_content_task2])
        await search.refresh(container)
        await asyncio.sleep(3)

        idx_count = await search.get_doc_count(container)
        # +1 here because container ob now indexed and it isn't by default in tests
        assert (add_count * 3) + 1 == idx_count

        await tm.abort(txn=txn)


async def test_migrate_get_all_uids(es_requester):
    async with es_requester as requester:
        await add_content(requester)

        container, request, txn, tm = await setup_txn_on_container(requester)

        search = getUtility(ICatalogUtility)
        await asyncio.sleep(1)
        await search.refresh(container)
        await asyncio.sleep(1)

        current_count = await search.get_doc_count(container)

        migrator = Migrator(search, container, force=True)
        uids = await migrator.get_all_uids()

        assert len(uids) == current_count

        await tm.abort(txn=txn)


@pytest.mark.flaky(reruns=5)
async def test_removes_orphans(es_requester):
    async with es_requester as requester:
        container, request, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)
        await search.index(container, {
            'foobar': {
                'title': 'foobar',
                'type_name': 'Item'
            }
        })
        # foobar here is an orphaned object because it doesn't reference an object

        index_name = await search.get_index_name(container)  # alias

        doc = await search.conn.get(
            index=index_name, doc_type=DOC_TYPE, id='foobar')
        assert doc['found']

        migrator = Migrator(search, container, force=True)
        await migrator.run_migration()

        async def _test():
            with pytest.raises(aioelasticsearch.exceptions.NotFoundError):
                await search.conn.get(
                    index=index_name, doc_type=DOC_TYPE, id='foobar')

            assert len(migrator.orphaned) == 1
            assert migrator.orphaned[0] == 'foobar'

        await run_with_retries(_test, requester)


@pytest.mark.flaky(reruns=5)
async def test_fixes_missing(es_requester):
    async with es_requester as requester:
        await add_content(requester, 2, 2)
        container, request, txn, tm = await setup_txn_on_container(requester)

        search = getUtility(ICatalogUtility)
        await asyncio.sleep(1)
        await search.refresh(container)
        await asyncio.sleep(1)
        original_count = await search.get_doc_count(container)

        keys = await container.async_keys()
        key = random.choice(keys)
        ob = await container.async_get(key)
        await search.remove(container, [(
            ob._p_oid, ob.type_name, get_content_path(ob)
        )], request=request)

        await asyncio.sleep(1)
        await search.refresh(container)
        await asyncio.sleep(1)
        assert original_count != await search.get_doc_count(container)
        old_index_name = await search.get_real_index_name(container)

        migrator = Migrator(search, container, force=True, request=request)
        await migrator.run_migration()

        await asyncio.sleep(1)
        await search.refresh(container)
        await asyncio.sleep(1)
        # new index should fix missing one, old index still has it missing
        num_docs = await search.get_doc_count(container, migrator.work_index_name)
        # it's + 1 here because reindexing also adds container object which
        # in these tests is not there by default.
        assert num_docs == (original_count + 1)
        assert old_index_name != await search.get_real_index_name(container)


@pytest.mark.flaky(reruns=5)
async def test_updates_index_data(es_requester):
    async with es_requester as requester:
        container, request, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)

        migrator = Migrator(search, container, force=True, request=request)
        version, new_index_name = await migrator.create_next_index()
        migrator.work_index_name = new_index_name
        await search.install_mappings_on_index(new_index_name)

        ob = create_content()
        ob.title = 'foobar'
        await migrator.index_object(ob, full=True)
        assert len(migrator.batch) == 1
        assert [v for v in migrator.batch.values()][0]['action'] == 'index'

        await migrator.flush()
        assert len(migrator.batch) == 0
        await migrator.join_futures()
        await asyncio.sleep(1)
        await search.refresh(container, new_index_name)
        await asyncio.sleep(1)
        assert await search.get_doc_count(container, new_index_name) == 1

        # test updating doc
        migrator.mapping_diff = {
            'Item': {
                'title': {}
            }
        }
        ob.title = 'foobar-new'
        await migrator.index_object(ob, full=False)
        assert len(migrator.batch) == 1
        assert [v for v in migrator.batch.values()][0]['action'] == 'update'

        assert len([v for v in migrator.batch.values()][0]['data']) == 2
        assert [v for v in migrator.batch.values()][0]['data']['title'] == 'foobar-new'

        await migrator.flush()
        assert len(migrator.batch) == 0
        await migrator.join_futures()
        await asyncio.sleep(1)
        await search.refresh(container, new_index_name)
        await asyncio.sleep(1)
        doc = await search.conn.get(
            index=new_index_name, doc_type=DOC_TYPE, id=ob._p_oid)
        assert doc['_source']['title'] == 'foobar-new'


async def test_calculate_mapping_diff(es_requester):
    async with es_requester as requester:
        container, request, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)

        migrator = Migrator(search, container, force=True, request=request)
        version, new_index_name = await migrator.create_next_index()
        migrator.work_index_name = new_index_name

        mappings = get_mappings()
        index_settings = DEFAULT_SETTINGS.copy()
        index_settings.update(app_settings.get('index', {}))

        # tweak mappings so we can get the diff...
        if 'creators' in mappings['properties']:
            mappings['properties']['creators']['type'] = 'text'
        mappings['properties']['foobar'] = {'type': 'keyword', 'index': True}

        await search.conn.indices.close(new_index_name)
        await search.conn.indices.put_settings(
            body=index_settings, index=new_index_name)
        await search.conn.indices.put_mapping(
            index=new_index_name, doc_type=DOC_TYPE, body=mappings)
        await search.conn.indices.open(new_index_name)

        diff = await migrator.calculate_mapping_diff()
        assert len(diff[DOC_TYPE]) == 2


async def test_updates_index_name(es_requester):
    async with es_requester as requester:
        container, request, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)
        existing_index = await search.get_real_index_name(container)
        assert await search.conn.indices.exists(existing_index)
        migrator = Migrator(search, container, force=True, request=request)
        await migrator.run_migration()
        assert not await search.conn.indices.exists(existing_index)
        assert await search.conn.indices.exists(migrator.work_index_name)
        assert await search.get_real_index_name(container) == migrator.work_index_name


async def test_moves_docs_over(es_requester):
    async with es_requester as requester:
        await add_content(requester)
        container, request, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)

        await asyncio.sleep(1)
        await search.refresh(container)
        await asyncio.sleep(1)
        current_count = await search.get_doc_count(container)

        migrator = Migrator(search, container, force=True, request=request)
        await migrator.run_migration()

        assert await search.get_real_index_name(container) == migrator.work_index_name
        await asyncio.sleep(1)
        await search.refresh(container)
        await asyncio.sleep(1)
        # adds container to index(+ 1)
        assert await search.get_doc_count(container) == (current_count + 1)


async def test_create_next_index(es_requester):
    async with es_requester as requester:
        container, request, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)
        migrator = Migrator(search, container, force=True, request=request)
        version, name = await migrator.create_next_index()
        assert version == 2
        assert name == 'guillotina-guillotina_2'


async def test_unindex_during_next_index(es_requester):
    async with es_requester as requester:
        await add_content(requester, 2)
        container, request, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)
        migrator = Migrator(search, container, force=True, request=request)
        next_index_version, work_index_name = await migrator.create_next_index()
        await search.install_mappings_on_index(work_index_name)
        await search.activate_next_index(
            container, next_index_version, request=request)
        await tm.commit(txn=txn)
        container, request, txn, tm = await setup_txn_on_container(requester)
        keys = await container.async_keys()
        item = await container.async_get(keys[0])
        aiotask_context.set('request', request)
        await notify(ObjectRemovedEvent(item, container, item.id))
        request.execute_futures()
        await asyncio.sleep(1)


async def test_apply_next_index_does_not_cause_conflict_error(es_requester):
    async with es_requester as requester:
        container, req, txn, tm = await setup_txn_on_container(requester)
        search = getUtility(ICatalogUtility)
        migrator = Migrator(search, container, force=True, request=req)
        await migrator.setup_next_index()
        assert migrator.next_index_version == 2
        assert migrator.work_index_name == 'guillotina-guillotina_2'

        container, req, txn, tm = await setup_txn_on_container(requester)
        annotations_container = IAnnotations(container)
        container_settings = await annotations_container.async_get(REGISTRY_DATA_KEY)
        container_settings['foo'] = 'bar'
        await tm.commit(txn=txn)

        async with managed_transaction(migrator.request, write=True,
                                       adopt_parent_txn=True) as txn:
            await migrator.utility.apply_next_index(migrator.container,
                                                    migrator.request)
