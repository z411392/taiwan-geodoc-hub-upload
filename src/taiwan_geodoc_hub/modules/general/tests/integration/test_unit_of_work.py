import pytest
from injector import Injector
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork,
    _ManuallyRollback,
    _UnitOfWorkManagerAlreadyInUseError,
)


@pytest.mark.skip(reason="")
class TestUnitOfWorkManager:
    @pytest.fixture
    def unit_of_work(self, injector: Injector):
        return injector.get(UnitOfWork)

    @pytest.mark.describe("正常提交事務")
    @pytest.mark.asyncio
    async def test_normal_commit(self, unit_of_work: FirestoreUnitOfWork):
        async with unit_of_work as unit_of_work:
            assert unit_of_work.transaction is not None
            # 在正常情況下，事務應該會被提交

        # 確認事務已清理
        assert unit_of_work.transaction is None
        assert unit_of_work._future is None
        assert unit_of_work._task is None

    @pytest.mark.describe("手動提交事務")
    @pytest.mark.asyncio
    async def test_manual_commit(self, unit_of_work: FirestoreUnitOfWork):
        async with unit_of_work as unit_of_work:
            transaction = unit_of_work.transaction
            assert transaction is not None

            # 手動提交
            unit_of_work.commit()

            # 再次提交不應該有問題
            unit_of_work.commit()

    @pytest.mark.describe("發生異常時自動回滾")
    @pytest.mark.asyncio
    async def test_auto_rollback_on_exception(self, unit_of_work: FirestoreUnitOfWork):
        test_exception = ValueError("測試異常")

        with pytest.raises(ValueError, match="測試異常"):
            async with unit_of_work as unit_of_work:
                assert unit_of_work.transaction is not None
                raise test_exception

        # 確認事務已清理
        assert unit_of_work.transaction is None
        assert unit_of_work._future is None
        assert unit_of_work._task is None

    @pytest.mark.describe("手動回滾事務")
    @pytest.mark.asyncio
    async def test_manual_rollback(self, unit_of_work: FirestoreUnitOfWork):
        test_exception = RuntimeError("手動回滾測試")

        with pytest.raises(RuntimeError, match="手動回滾測試"):
            async with unit_of_work as unit_of_work:
                assert unit_of_work.transaction is not None
                # 手動回滾
                unit_of_work.rollback(test_exception)

        # 確認事務已清理
        assert unit_of_work.transaction is None

    @pytest.mark.describe("手動回滾不傳入異常")
    @pytest.mark.asyncio
    async def test_manual_rollback_without_exception(
        self, unit_of_work: FirestoreUnitOfWork
    ):
        with pytest.raises(_ManuallyRollback):
            async with unit_of_work as unit_of_work:
                assert unit_of_work.transaction is not None
                # 手動回滾但不傳入異常
                unit_of_work.rollback()

    @pytest.mark.describe("重複使用 UnitOfWorkManager 應該拋出異常")
    @pytest.mark.asyncio
    async def test_already_in_use_error(self, unit_of_work: FirestoreUnitOfWork):
        async with unit_of_work:
            # 嘗試再次使用同一個 manager
            with pytest.raises(_UnitOfWorkManagerAlreadyInUseError):
                async with unit_of_work:
                    pass

    @pytest.mark.describe("在已提交的事務上再次提交不應該有問題")
    @pytest.mark.asyncio
    async def test_commit_after_commit(self, unit_of_work: FirestoreUnitOfWork):
        async with unit_of_work as unit_of_work:
            unit_of_work.commit()
            # 再次提交不應該有問題
            unit_of_work.commit()

    @pytest.mark.describe("在已提交的事務上回滾不應該有問題")
    @pytest.mark.asyncio
    async def test_rollback_after_commit(self, unit_of_work: FirestoreUnitOfWork):
        async with unit_of_work as unit_of_work:
            unit_of_work.commit()
            # 在已提交的事務上回滾不應該有問題
            unit_of_work.rollback()

    @pytest.mark.describe("在已回滾的事務上再次回滾不應該有問題")
    @pytest.mark.asyncio
    async def test_rollback_after_rollback(self, unit_of_work: FirestoreUnitOfWork):
        test_exception = RuntimeError("測試異常")

        with pytest.raises(RuntimeError):
            async with unit_of_work as unit_of_work:
                unit_of_work.rollback(test_exception)
                # 再次回滾不應該有問題
                unit_of_work.rollback()

    @pytest.mark.describe("事務初始狀態檢查")
    @pytest.mark.asyncio
    async def test_initial_state(self, unit_of_work: FirestoreUnitOfWork):
        assert unit_of_work.transaction is None
        assert unit_of_work._future is None
        assert unit_of_work._task is None

    @pytest.mark.describe("異常處理中的 traceback 保持")
    @pytest.mark.asyncio
    async def test_exception_traceback_preservation(
        self, unit_of_work: FirestoreUnitOfWork
    ):
        original_exception = ValueError("原始異常")

        try:
            async with unit_of_work as unit_of_work:
                try:
                    raise original_exception
                except ValueError as e:
                    # 手動回滾並傳入帶有 traceback 的異常
                    unit_of_work.rollback(e.with_traceback(e.__traceback__))
        except ValueError as caught_exception:
            # 驗證異常是同一個對象
            assert caught_exception is original_exception
            # 驗證 traceback 被保持
            assert caught_exception.__traceback__ is not None
