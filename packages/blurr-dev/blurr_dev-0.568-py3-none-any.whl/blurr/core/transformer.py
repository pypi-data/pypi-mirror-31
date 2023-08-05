from typing import Dict, Type

from abc import ABC

from blurr.core.base import BaseItemCollection, BaseSchemaCollection, BaseItem
from blurr.core.aggregate import Aggregate
from blurr.core.errors import MissingAttributeError, IdentityError
from blurr.core.evaluation import Context, EvaluationContext, Expression
from blurr.core.loader import TypeLoader
from blurr.core.schema_loader import SchemaLoader
from blurr.core.store import Store


class TransformerSchema(BaseSchemaCollection, ABC):
    """
    All Transformer Schema inherit from this base.  Adds support for handling
    the required attributes of a schema.
    """

    ATTRIBUTE_VERSION = 'Version'
    ATTRIBUTE_STORES = 'Stores'
    ATTRIBUTE_AGGREGATES = 'Aggregates'

    def __init__(self, fully_qualified_name: str, schema_loader: SchemaLoader) -> None:
        super().__init__(fully_qualified_name, schema_loader, self.ATTRIBUTE_AGGREGATES)

        # Load the schema specific attributes
        self.version = self._spec[self.ATTRIBUTE_VERSION]

        # Load list of stores from the schema
        self.stores: Dict[str, Type[Store]] = {
            schema_spec[self.ATTRIBUTE_NAME]: self.schema_loader.get_nested_schema_object(
                self.fully_qualified_name, schema_spec[self.ATTRIBUTE_NAME])
            for schema_spec in self._spec.get(self.ATTRIBUTE_STORES, [])
        }

        # Load nested schema items
        self.nested_schema: Dict[str, Type[Aggregate]] = {
            schema_spec[self.ATTRIBUTE_NAME]: self.schema_loader.get_nested_schema_object(
                self.fully_qualified_name, schema_spec[self.ATTRIBUTE_NAME])
            for schema_spec in self._spec[self._nested_item_attribute]
        }


class Transformer(BaseItemCollection, ABC):
    """
    All transformers inherit from this base.  Adds the current transformer
    to the context
    """

    def __init__(self, schema: TransformerSchema, identity: str, context: Context) -> None:
        super().__init__(schema, EvaluationContext(global_context=context))
        # Load the nested items into the item
        self._aggregates: Dict[str, Aggregate] = {
            name: TypeLoader.load_item(item_schema.type)(item_schema, identity,
                                                         self._evaluation_context)
            for name, item_schema in schema.nested_schema.items()
        }
        self._identity = identity
        self._evaluation_context.global_add('identity', self._identity)
        self._evaluation_context.global_context.merge(self._nested_items)

    @property
    def _nested_items(self) -> Dict[str, Aggregate]:
        """
        Dictionary of nested data groups
        """
        return self._aggregates

    def finalize(self) -> None:
        """
        Iteratively finalizes all data groups in its transformer
        """
        for item in self._nested_items.values():
            item.finalize()

    def __getattr__(self, item: str) -> Aggregate:
        """
        Makes the value of the nested items available as properties
        of the collection object.  This is used for retrieving data groups
        for dynamic execution.
        :param item: Data group requested
        """
        return self.__getitem__(item)

    def __getitem__(self, item) -> Aggregate:
        """
        Makes the nested items available though the square bracket notation.
        :raises KeyError: When a requested item is not found in nested items
        """
        if item not in self._nested_items:
            raise MissingAttributeError('{item} not defined in {name}'.format(
                item=item, name=self._name))

        return self._nested_items[item]
