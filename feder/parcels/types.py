from feder.parcels.models import IncomingParcelPost, OutgoingParcelPost
from feder.records.registry import record_type_registry
from feder.records.types import CommonRecordType

record_type_registry.registry(IncomingParcelPost, CommonRecordType(IncomingParcelPost))
record_type_registry.registry(OutgoingParcelPost, CommonRecordType(OutgoingParcelPost))
