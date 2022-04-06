from typing import TYPE_CHECKING, Any, List, Optional, TypeVar, cast
from pydantic import BaseModel, AnyHttpUrl
from pydantic.fields import ModelField, Undefined
from pydantic.validators import list_validator

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny

ItemT = TypeVar("ItemT")


class LenientList(List[ItemT]):
    """
    LenientList[T] is same as List[T], but will skip invalid items instead of raising error

    At some point this behaviour might be implemented in pydantic:
    https://github.com/samuelcolvin/pydantic/issues/2274
    """

    _item_field: ModelField

    def __class_getitem__(cls, type_):
        """
        Returned type must be subclass of LenientList for validation to work,
        But it also needs to smell like typing.List[T] for pydantic magic to work properly
        """
        if isinstance(type_, tuple):
            (type_,) = type_
        elif hasattr(cls, "_item_field"):
            raise TypeError(f"{cls.__name__} is already concrete")

        if isinstance(type_, TypeVar):
            pydantic_type = type(f"LenientList[{type_}]", (cls,), {})
        else:
            item_field = ModelField.infer(
                name="item",
                value=Undefined,
                annotation=type_,
                class_validators=None,
                config=BaseModel.__config__,
            )
            t_name = getattr(type_, "__name__", None) or type_.__class__.__name__
            pydantic_type = type(
                f"LenientList[{t_name}]", (cls,), {"_item_field": item_field}
            )

        generic_alias = super().__class_getitem__(type_)
        # this will enable support of GenericModel and json schema
        pydantic_type.__origin__ = generic_alias.__origin__
        pydantic_type.__parameters__ = generic_alias.__parameters__
        pydantic_type.__args__ = generic_alias.__args__
        return pydantic_type

    @classmethod
    def __get_validators__(cls):
        yield cls._list_validator

    @classmethod
    def _list_validator(
        cls, raw_value: Any, values: "DictStrAny", field: ModelField
    ) -> Optional[List[ItemT]]:
        if raw_value is None and not field.required:
            return None
        list_value: List[Any] = list_validator(raw_value)
        parsed: List[ItemT] = []
        for item in list_value:
            value, error = cls._item_field.validate(item, values, loc=())
            if error is None:
                parsed.append(cast(ItemT, value))
        return parsed


class Urls(BaseModel):
    target_url: AnyHttpUrl = None
    urls: LenientList[AnyHttpUrl] = []
    error: str = ""
