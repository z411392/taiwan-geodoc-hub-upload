from google.cloud.firestore import (
    AsyncClient,
    AsyncCollectionReference,
)
from taiwan_geodoc_hub.modules.general.enums.collection import (
    Collection,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.ocr_result_repository import (
    OCRResultRepository,
)
from injector import inject
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork as UnitOfWork,
)


class OCRResultFirestoreAdapter(OCRResultRepository[UnitOfWork]):
    _collection: AsyncCollectionReference

    @inject
    def __init__(self, /, db: AsyncClient):
        self._collection = db.collection(str(Collection.OCRResults))

    async def save(
        self,
        ocr_result_id: str,
        text: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        document = self._collection.document(ocr_result_id)
        data = dict(text=text)
        unit_of_work.transaction.set(document, data, merge=True)

    async def load(self, ocr_result_id: str, /, unit_of_work: UnitOfWork):
        document = self._collection.document(ocr_result_id)
        db: AsyncClient = unit_of_work.transaction._client
        document_snapshot = await anext(
            aiter(db.get_all([document], transaction=unit_of_work.transaction))
        )
        if not document_snapshot.exists:
            return None
        return document_snapshot.get("text")
