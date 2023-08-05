import pytest

# noinspection PyUnresolvedReferences
from ledger.test.conftest import tempdir, txn_serializer, hash_serializer  # noqa
from plenum.common.constants import LedgerState
from plenum.common.messages.node_messages import LedgerStatus

nodeCount = 7

ledger_id = 1


@pytest.yield_fixture(scope="function")
def restarted_pool(txnPoolNodeSet):
    '''
    Emulate restart of the pool
    '''
    for node in txnPoolNodeSet:
        node.viewNo = None
        node.master_replica.last_ordered_3pc = (0, 0)
        node.view_changer.set_defaults()
    return txnPoolNodeSet


@pytest.yield_fixture(scope="function")
def node_and_ledger_info(restarted_pool):
    '''
    Emulate restart of the pool (clean state)
    '''
    node = restarted_pool[0]
    ledger_manager = node.ledgerManager
    ledger_manager.last_caught_up_3PC = (0, 0)

    ledger_info = ledger_manager.getLedgerInfoByType(ledger_id)
    ledger_info.set_defaults()
    ledger_info.state = LedgerState.syncing
    ledger_info.canSync = True

    ledger_status = node.build_ledger_status(ledger_id)
    assert ledger_status.viewNo is None

    return node, ledger_manager, ledger_info, ledger_status


def test_same_ledger_status_quorum(restarted_pool,
                                   node_and_ledger_info):
    '''
    Check that we require at least n-f-1 (=4) same LedgerStatus msgs
    to finish CatchUp
    '''
    node, ledger_manager, ledger_info, ledger_status = node_and_ledger_info

    status_from = set()
    for i in range(3):
        node_name = restarted_pool[i + 1].name
        ledger_manager.processLedgerStatus(ledger_status, node_name)
        status_from = status_from.union({node_name})
        assert ledger_info.ledgerStatusOk == status_from
        assert ledger_info.canSync is True
        assert ledger_info.state == LedgerState.syncing

    node_name = restarted_pool[4].name
    ledger_manager.processLedgerStatus(ledger_status, node_name)

    assert ledger_info.ledgerStatusOk == set()
    assert ledger_info.canSync is False
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_same_3PC(restarted_pool,
                                                  node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs
    if all LedgerStatus msgs have the same not None 3PC keys
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info
    ledger_status_2_40 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      2, 20,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_manager.processLedgerStatus(ledger_status_2_40, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_2_40, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_2_40, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_2_40, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (2, 20)
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_same_None_3PC(restarted_pool,
                                                       node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs
    if all LedgerStatus msgs have the same None 3PC keys (like at the initial start of the pool)
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info

    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_one_not_none_3PC_last(restarted_pool,
                                                               node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs
    if all LedgerStatus msgs have the same None 3PC keys except the last one.
    The last msg contains not None 3PC, but it's not enough for setting last_ordered_3PC
    since the quorum is f+1 (=3)
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info

    ledger_status_3_40 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      3, 40,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_one_not_none_3PC_first(restarted_pool,
                                                                node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs
    if all LedgerStatus msgs have the same None 3PC keys except the first one.
    The first msg contains not None 3PC, but it's not enough for setting last_ordered_3PC
    since the quorum is f+1 (=3)
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info

    ledger_status_3_40 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      3, 40,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_not_none_3PC_quorum_with_none(restarted_pool,
                                                                       node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs
    if all LedgerStatus msgs have the same not None 3PC keys except the last one.
    The last msg contains None 3PC, but not None from the previous msgs is used
    since we have a quorum of f+1 (=3)
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info

    ledger_status_3_40 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      3, 40,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_none_3PC, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (3, 40)
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_not_none_3PC_quorum1(restarted_pool,
                                                              node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs
    if all LedgerStatus msgs have the same not None 3PC keys except the last one.
    The last msg contains a different not None 3PC, but 3PC from the previous msgs is used
    since we have a quorum of f+1 (=3)
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info

    ledger_status_1_10 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      1, 10,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_status_3_40 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      3, 40,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_manager.processLedgerStatus(ledger_status_1_10, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_1_10, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_1_10, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (1, 10)
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_not_none_3PC_quorum2(restarted_pool,
                                                              node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs
    if all LedgerStatus msgs have the same not None 3PC keys except the last one.
    The last msg contains a different not None 3PC, but 3PC from the previous msgs is used
    since we have a quorum of f+1 (=3)
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info

    ledger_status_1_10 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      1, 10,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_status_3_40 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      3, 40,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_1_10, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (3, 40)
    assert ledger_info.state == LedgerState.synced


def test_same_ledger_status_last_ordered_not_none_3PC_no_quorum_equal(restarted_pool,
                                                                      node_and_ledger_info):
    '''
    Check that last_ordered_3PC is set according to 3PC from LedgerStatus msgs.
    Check that if we have no quorum (2 different keys, but 3 is required ror quorum), then
    they are not used.
    '''
    node, ledger_manager, ledger_info, ledger_status_none_3PC = node_and_ledger_info

    ledger_status_1_10 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      1, 10,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_status_3_40 = LedgerStatus(ledger_status_none_3PC.ledgerId,
                                      ledger_status_none_3PC.txnSeqNo,
                                      3, 40,
                                      ledger_status_none_3PC.merkleRoot)

    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[1].name)
    ledger_manager.processLedgerStatus(ledger_status_3_40, restarted_pool[2].name)
    ledger_manager.processLedgerStatus(ledger_status_1_10, restarted_pool[3].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.syncing

    ledger_manager.processLedgerStatus(ledger_status_1_10, restarted_pool[4].name)
    assert node.master_last_ordered_3PC == (0, 0)
    assert ledger_info.state == LedgerState.synced
