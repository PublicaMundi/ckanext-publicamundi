'''Import into our namespace a set of commonly used classes/interfaces 
from zope.schema-related modules.
'''

import zope.interface
import zope.schema
import zope.schema.interfaces
import z3c.schema.email

__all__ = [
    
    # field interfaces
    
    'IField',
    'ITextField',
    'ITextLineField',
    'INativeStringField',
    'IStringField',
    'INativeStringLineField',
    'IStringLineField',
    'IChoiceField',
    'IURIField',
    'IPasswordField',
    'IDottedNameField',
    'IIdField',
    'IDatetimeField',
    'IDateField',
    'ITimeField',
    'ITimedeltaField',
    'IBoolField',
    'IIntField',
    'IFloatField',
    'IDecimalField',
    'ICollectionField',
    'IContainerField',
    'ISequenceField',
    'IListField',
    'IDictField',
    'ITupleField',
    'IObjectField',
    'IEmailAddressField',
    
    # fields
    
    'TextField',
    'TextLineField',
    'NativeStringField',
    'StringField',
    'NativeStringLineField',
    'StringLineField',
    'ChoiceField',
    'URIField',
    'PasswordField',
    'DottedNameField',
    'IdField',
    'DatetimeField',
    'DateField',
    'TimeField',
    'TimedeltaField',
    'BoolField',
    'IntField',
    'FloatField',
    'DecimalField',
    'ListField',
    'DictField',
    'TupleField',
    'ObjectField',
    'EmailAddressField',

]

from zope.schema.interfaces import (
    IField,
    IText as ITextField,
    ITextLine as ITextLineField,
    INativeString as INativeStringField,
    INativeString as IStringField,
    INativeStringLine as INativeStringLineField,
    INativeStringLine as IStringLineField,
    IChoice as IChoiceField,
    IURI as IURIField,
    IPassword as IPasswordField,
    IDottedName as IDottedNameField,
    IId as IIdField,
    IDatetime as IDatetimeField,
    IDate as IDateField,
    ITime as ITimeField,
    ITimedelta as ITimedeltaField,
    IBool as IBoolField,
    IInt as IIntField,
    IFloat as IFloatField,
    IDecimal as IDecimalField,
    ICollection as ICollectionField,
    IContainer as IContainerField,
    ISequence as ISequenceField,
    IList as IListField,
    IDict as IDictField,
    ITuple as ITupleField,
    IObject as IObjectField,)

from zope.schema.interfaces import (
    ConstraintNotSatisfied,
    InvalidValue,
    NotUnique,
    RequiredMissing,
    SchemaNotFullyImplemented,
    SchemaNotProvided,
    StopValidation,
    TooBig,
    TooLong,
    TooShort,
    TooSmall,
    Unbound,
    ValidationError,
    WrongContainedType,
    WrongType,)

from z3c.schema.email.interfaces import (
    IRFC822MailAddress as IEmailAddressField,)

from zope.schema import (
    Text as TextField,
    TextLine as TextLineField,
    NativeString as NativeStringField,
    NativeString as StringField,
    NativeStringLine as NativeStringLineField,
    NativeStringLine as StringLineField,
    Choice as ChoiceField,
    URI as URIField,
    Password as PasswordField,
    DottedName as DottedNameField,
    Id as IdField,
    Datetime as DatetimeField,
    Date as DateField,
    Time as TimeField,
    Timedelta as TimedeltaField,
    Bool as BoolField,
    Int as IntField,
    Float as FloatField,
    Decimal as DecimalField,
    List as ListField,
    Dict as DictField,
    Tuple as TupleField,
    Object as ObjectField,)

from z3c.schema.email import (
    RFC822MailAddress as EmailAddressField,)

