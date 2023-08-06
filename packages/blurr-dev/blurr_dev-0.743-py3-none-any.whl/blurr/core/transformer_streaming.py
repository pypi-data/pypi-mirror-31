from datetime import datetime

from blurr.core.base import Expression
from blurr.core.errors import IdentityError, TimeError
from blurr.core.evaluation import Context, EvaluationContext
from blurr.core.record import Record
from blurr.core.schema_loader import SchemaLoader
from blurr.core.transformer import Transformer, TransformerSchema


class StreamingTransformerSchema(TransformerSchema):
    """
    Represents the schema for processing streaming data.  Handles the streaming specific attributes of the schema
    """

    ATTRIBUTE_IDENTITY = 'Identity'
    ATTRIBUTE_TIME = 'Time'

    def __init__(self, fully_qualified_name: str, schema_loader: SchemaLoader) -> None:
        super().__init__(fully_qualified_name, schema_loader)

        self.identity = Expression(self._spec[self.ATTRIBUTE_IDENTITY])
        self.time = Expression(self._spec[self.ATTRIBUTE_TIME])

    def get_identity(self, record: Record) -> str:
        """
        Evaluates and returns the identity as specified in the schema.
        :param record: Record which is used to determine the identity.
        :return: The evaluated identity
        :raises: IdentityError if identity cannot be determined.
        """
        context = self.schema_context.context
        context.add_record(record)
        identity = self.identity.evaluate(context)
        if not identity:
            raise IdentityError('Could not determine identity using {}. Record is {}'.format(
                self.identity.code_string, record))
        context.remove_record()
        return identity

    def get_time(self, record: Record) -> datetime:
        context = self.schema_context.context
        context.add_record(record)
        time = self.time.evaluate(context)
        if not time or not isinstance(time, datetime):
            raise TimeError('Could not determine time using {}.  Record is {}'.format(
                self.time.code_string, record))
        context.remove_record()
        return time


class StreamingTransformer(Transformer):
    def __init__(self, schema: TransformerSchema, identity: str) -> None:
        super().__init__(schema, identity)
        self._evaluation_context.global_add('identity', self._identity)

    def evaluate(self, record: Record):
        """
        Evaluates and updates data in the StreamingTransformer.
        :param record: The 'source' record used for the update.
        :raises: IdentityError if identity is different from the one used during
        initialization.
        """
        record_identity = self._schema.get_identity(record)
        if self._identity != record_identity:
            raise IdentityError(
                'Identity in transformer ({}) and new record ({}) do not match'.format(
                    self._identity, record_identity))

        # Add source record and time to the global context
        self._evaluation_context.add_record(record)
        self._evaluation_context.global_add('time',
                                            self._schema.time.evaluate(self._evaluation_context))
        super().evaluate()

        # Cleanup source and time form the context
        self._evaluation_context.remove_record()
        self._evaluation_context.global_remove('time')
