# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/cloud/dialogflow_v2beta1/proto/session_entity_type.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from dialogflow_v2beta1.proto import entity_type_pb2 as google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_entity__type__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import field_mask_pb2 as google_dot_protobuf_dot_field__mask__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='google/cloud/dialogflow_v2beta1/proto/session_entity_type.proto',
  package='google.cloud.dialogflow.v2beta1',
  syntax='proto3',
  serialized_pb=_b('\n?google/cloud/dialogflow_v2beta1/proto/session_entity_type.proto\x12\x1fgoogle.cloud.dialogflow.v2beta1\x1a\x1cgoogle/api/annotations.proto\x1a\x37google/cloud/dialogflow_v2beta1/proto/entity_type.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a google/protobuf/field_mask.proto\"\xd1\x02\n\x11SessionEntityType\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x63\n\x14\x65ntity_override_mode\x18\x02 \x01(\x0e\x32\x45.google.cloud.dialogflow.v2beta1.SessionEntityType.EntityOverrideMode\x12\x44\n\x08\x65ntities\x18\x03 \x03(\x0b\x32\x32.google.cloud.dialogflow.v2beta1.EntityType.Entity\"\x82\x01\n\x12\x45ntityOverrideMode\x12$\n ENTITY_OVERRIDE_MODE_UNSPECIFIED\x10\x00\x12!\n\x1d\x45NTITY_OVERRIDE_MODE_OVERRIDE\x10\x01\x12#\n\x1f\x45NTITY_OVERRIDE_MODE_SUPPLEMENT\x10\x02\"V\n\x1dListSessionEntityTypesRequest\x12\x0e\n\x06parent\x18\x01 \x01(\t\x12\x11\n\tpage_size\x18\x02 \x01(\x05\x12\x12\n\npage_token\x18\x03 \x01(\t\"\x8b\x01\n\x1eListSessionEntityTypesResponse\x12P\n\x14session_entity_types\x18\x01 \x03(\x0b\x32\x32.google.cloud.dialogflow.v2beta1.SessionEntityType\x12\x17\n\x0fnext_page_token\x18\x02 \x01(\t\"+\n\x1bGetSessionEntityTypeRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"\x81\x01\n\x1e\x43reateSessionEntityTypeRequest\x12\x0e\n\x06parent\x18\x01 \x01(\t\x12O\n\x13session_entity_type\x18\x02 \x01(\x0b\x32\x32.google.cloud.dialogflow.v2beta1.SessionEntityType\"\xa2\x01\n\x1eUpdateSessionEntityTypeRequest\x12O\n\x13session_entity_type\x18\x01 \x01(\x0b\x32\x32.google.cloud.dialogflow.v2beta1.SessionEntityType\x12/\n\x0bupdate_mask\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.FieldMask\".\n\x1e\x44\x65leteSessionEntityTypeRequest\x12\x0c\n\x04name\x18\x01 \x01(\t2\xdf\x08\n\x12SessionEntityTypes\x12\xdc\x01\n\x16ListSessionEntityTypes\x12>.google.cloud.dialogflow.v2beta1.ListSessionEntityTypesRequest\x1a?.google.cloud.dialogflow.v2beta1.ListSessionEntityTypesResponse\"A\x82\xd3\xe4\x93\x02;\x12\x39/v2beta1/{parent=projects/*/agent/sessions/*}/entityTypes\x12\xcb\x01\n\x14GetSessionEntityType\x12<.google.cloud.dialogflow.v2beta1.GetSessionEntityTypeRequest\x1a\x32.google.cloud.dialogflow.v2beta1.SessionEntityType\"A\x82\xd3\xe4\x93\x02;\x12\x39/v2beta1/{name=projects/*/agent/sessions/*/entityTypes/*}\x12\xe6\x01\n\x17\x43reateSessionEntityType\x12?.google.cloud.dialogflow.v2beta1.CreateSessionEntityTypeRequest\x1a\x32.google.cloud.dialogflow.v2beta1.SessionEntityType\"V\x82\xd3\xe4\x93\x02P\"9/v2beta1/{parent=projects/*/agent/sessions/*}/entityTypes:\x13session_entity_type\x12\xfa\x01\n\x17UpdateSessionEntityType\x12?.google.cloud.dialogflow.v2beta1.UpdateSessionEntityTypeRequest\x1a\x32.google.cloud.dialogflow.v2beta1.SessionEntityType\"j\x82\xd3\xe4\x93\x02\x64\x32M/v2beta1/{session_entity_type.name=projects/*/agent/sessions/*/entityTypes/*}:\x13session_entity_type\x12\xb5\x01\n\x17\x44\x65leteSessionEntityType\x12?.google.cloud.dialogflow.v2beta1.DeleteSessionEntityTypeRequest\x1a\x16.google.protobuf.Empty\"A\x82\xd3\xe4\x93\x02;*9/v2beta1/{name=projects/*/agent/sessions/*/entityTypes/*}B\xb4\x01\n#com.google.cloud.dialogflow.v2beta1B\x16SessionEntityTypeProtoP\x01ZIgoogle.golang.org/genproto/googleapis/cloud/dialogflow/v2beta1;dialogflow\xf8\x01\x01\xa2\x02\x02\x44\x46\xaa\x02\x1fGoogle.Cloud.Dialogflow.V2beta1b\x06proto3')
  ,
  dependencies=[google_dot_api_dot_annotations__pb2.DESCRIPTOR,google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_entity__type__pb2.DESCRIPTOR,google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,google_dot_protobuf_dot_field__mask__pb2.DESCRIPTOR,])



_SESSIONENTITYTYPE_ENTITYOVERRIDEMODE = _descriptor.EnumDescriptor(
  name='EntityOverrideMode',
  full_name='google.cloud.dialogflow.v2beta1.SessionEntityType.EntityOverrideMode',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ENTITY_OVERRIDE_MODE_UNSPECIFIED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENTITY_OVERRIDE_MODE_OVERRIDE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENTITY_OVERRIDE_MODE_SUPPLEMENT', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=458,
  serialized_end=588,
)
_sym_db.RegisterEnumDescriptor(_SESSIONENTITYTYPE_ENTITYOVERRIDEMODE)


_SESSIONENTITYTYPE = _descriptor.Descriptor(
  name='SessionEntityType',
  full_name='google.cloud.dialogflow.v2beta1.SessionEntityType',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='google.cloud.dialogflow.v2beta1.SessionEntityType.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='entity_override_mode', full_name='google.cloud.dialogflow.v2beta1.SessionEntityType.entity_override_mode', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='entities', full_name='google.cloud.dialogflow.v2beta1.SessionEntityType.entities', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SESSIONENTITYTYPE_ENTITYOVERRIDEMODE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=251,
  serialized_end=588,
)


_LISTSESSIONENTITYTYPESREQUEST = _descriptor.Descriptor(
  name='ListSessionEntityTypesRequest',
  full_name='google.cloud.dialogflow.v2beta1.ListSessionEntityTypesRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='parent', full_name='google.cloud.dialogflow.v2beta1.ListSessionEntityTypesRequest.parent', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='page_size', full_name='google.cloud.dialogflow.v2beta1.ListSessionEntityTypesRequest.page_size', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='page_token', full_name='google.cloud.dialogflow.v2beta1.ListSessionEntityTypesRequest.page_token', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=590,
  serialized_end=676,
)


_LISTSESSIONENTITYTYPESRESPONSE = _descriptor.Descriptor(
  name='ListSessionEntityTypesResponse',
  full_name='google.cloud.dialogflow.v2beta1.ListSessionEntityTypesResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session_entity_types', full_name='google.cloud.dialogflow.v2beta1.ListSessionEntityTypesResponse.session_entity_types', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='next_page_token', full_name='google.cloud.dialogflow.v2beta1.ListSessionEntityTypesResponse.next_page_token', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=679,
  serialized_end=818,
)


_GETSESSIONENTITYTYPEREQUEST = _descriptor.Descriptor(
  name='GetSessionEntityTypeRequest',
  full_name='google.cloud.dialogflow.v2beta1.GetSessionEntityTypeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='google.cloud.dialogflow.v2beta1.GetSessionEntityTypeRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=820,
  serialized_end=863,
)


_CREATESESSIONENTITYTYPEREQUEST = _descriptor.Descriptor(
  name='CreateSessionEntityTypeRequest',
  full_name='google.cloud.dialogflow.v2beta1.CreateSessionEntityTypeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='parent', full_name='google.cloud.dialogflow.v2beta1.CreateSessionEntityTypeRequest.parent', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session_entity_type', full_name='google.cloud.dialogflow.v2beta1.CreateSessionEntityTypeRequest.session_entity_type', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=866,
  serialized_end=995,
)


_UPDATESESSIONENTITYTYPEREQUEST = _descriptor.Descriptor(
  name='UpdateSessionEntityTypeRequest',
  full_name='google.cloud.dialogflow.v2beta1.UpdateSessionEntityTypeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='session_entity_type', full_name='google.cloud.dialogflow.v2beta1.UpdateSessionEntityTypeRequest.session_entity_type', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='update_mask', full_name='google.cloud.dialogflow.v2beta1.UpdateSessionEntityTypeRequest.update_mask', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=998,
  serialized_end=1160,
)


_DELETESESSIONENTITYTYPEREQUEST = _descriptor.Descriptor(
  name='DeleteSessionEntityTypeRequest',
  full_name='google.cloud.dialogflow.v2beta1.DeleteSessionEntityTypeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='google.cloud.dialogflow.v2beta1.DeleteSessionEntityTypeRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1162,
  serialized_end=1208,
)

_SESSIONENTITYTYPE.fields_by_name['entity_override_mode'].enum_type = _SESSIONENTITYTYPE_ENTITYOVERRIDEMODE
_SESSIONENTITYTYPE.fields_by_name['entities'].message_type = google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_entity__type__pb2._ENTITYTYPE_ENTITY
_SESSIONENTITYTYPE_ENTITYOVERRIDEMODE.containing_type = _SESSIONENTITYTYPE
_LISTSESSIONENTITYTYPESRESPONSE.fields_by_name['session_entity_types'].message_type = _SESSIONENTITYTYPE
_CREATESESSIONENTITYTYPEREQUEST.fields_by_name['session_entity_type'].message_type = _SESSIONENTITYTYPE
_UPDATESESSIONENTITYTYPEREQUEST.fields_by_name['session_entity_type'].message_type = _SESSIONENTITYTYPE
_UPDATESESSIONENTITYTYPEREQUEST.fields_by_name['update_mask'].message_type = google_dot_protobuf_dot_field__mask__pb2._FIELDMASK
DESCRIPTOR.message_types_by_name['SessionEntityType'] = _SESSIONENTITYTYPE
DESCRIPTOR.message_types_by_name['ListSessionEntityTypesRequest'] = _LISTSESSIONENTITYTYPESREQUEST
DESCRIPTOR.message_types_by_name['ListSessionEntityTypesResponse'] = _LISTSESSIONENTITYTYPESRESPONSE
DESCRIPTOR.message_types_by_name['GetSessionEntityTypeRequest'] = _GETSESSIONENTITYTYPEREQUEST
DESCRIPTOR.message_types_by_name['CreateSessionEntityTypeRequest'] = _CREATESESSIONENTITYTYPEREQUEST
DESCRIPTOR.message_types_by_name['UpdateSessionEntityTypeRequest'] = _UPDATESESSIONENTITYTYPEREQUEST
DESCRIPTOR.message_types_by_name['DeleteSessionEntityTypeRequest'] = _DELETESESSIONENTITYTYPEREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SessionEntityType = _reflection.GeneratedProtocolMessageType('SessionEntityType', (_message.Message,), dict(
  DESCRIPTOR = _SESSIONENTITYTYPE,
  __module__ = 'google.cloud.dialogflow_v2beta1.proto.session_entity_type_pb2'
  ,
  __doc__ = """Represents a session entity type.
  
  Extends or replaces a developer entity type at the user session level
  (we refer to the entity types defined at the agent level as "developer
  entity types").
  
  Note: session entity types apply to all queries, regardless of the
  language.
  
  
  Attributes:
      name:
          Required. The unique identifier of this session entity type.
          Format: ``projects/<Project ID>/agent/sessions/<Session
          ID>/entityTypes/<Entity Type Display Name>``.
      entity_override_mode:
          Required. Indicates whether the additional data should
          override or supplement the developer entity type definition.
      entities:
          Required. The collection of entities associated with this
          session entity type.
  """,
  # @@protoc_insertion_point(class_scope:google.cloud.dialogflow.v2beta1.SessionEntityType)
  ))
_sym_db.RegisterMessage(SessionEntityType)

ListSessionEntityTypesRequest = _reflection.GeneratedProtocolMessageType('ListSessionEntityTypesRequest', (_message.Message,), dict(
  DESCRIPTOR = _LISTSESSIONENTITYTYPESREQUEST,
  __module__ = 'google.cloud.dialogflow_v2beta1.proto.session_entity_type_pb2'
  ,
  __doc__ = """The request message for [SessionEntityTypes.ListSessionEntityTypes].
  
  
  Attributes:
      parent:
          Required. The session to list all session entity types from.
          Format: ``projects/<Project ID>/agent/sessions/<Session ID>``.
      page_size:
          Optional. The maximum number of items to return in a single
          page. By default 100 and at most 1000.
      page_token:
          Optional. The next\_page\_token value returned from a previous
          list request.
  """,
  # @@protoc_insertion_point(class_scope:google.cloud.dialogflow.v2beta1.ListSessionEntityTypesRequest)
  ))
_sym_db.RegisterMessage(ListSessionEntityTypesRequest)

ListSessionEntityTypesResponse = _reflection.GeneratedProtocolMessageType('ListSessionEntityTypesResponse', (_message.Message,), dict(
  DESCRIPTOR = _LISTSESSIONENTITYTYPESRESPONSE,
  __module__ = 'google.cloud.dialogflow_v2beta1.proto.session_entity_type_pb2'
  ,
  __doc__ = """The response message for [SessionEntityTypes.ListSessionEntityTypes].
  
  
  Attributes:
      session_entity_types:
          The list of session entity types. There will be a maximum
          number of items returned based on the page\_size field in the
          request.
      next_page_token:
          Token to retrieve the next page of results, or empty if there
          are no more results in the list.
  """,
  # @@protoc_insertion_point(class_scope:google.cloud.dialogflow.v2beta1.ListSessionEntityTypesResponse)
  ))
_sym_db.RegisterMessage(ListSessionEntityTypesResponse)

GetSessionEntityTypeRequest = _reflection.GeneratedProtocolMessageType('GetSessionEntityTypeRequest', (_message.Message,), dict(
  DESCRIPTOR = _GETSESSIONENTITYTYPEREQUEST,
  __module__ = 'google.cloud.dialogflow_v2beta1.proto.session_entity_type_pb2'
  ,
  __doc__ = """The request message for [SessionEntityTypes.GetSessionEntityType].
  
  
  Attributes:
      name:
          Required. The name of the session entity type. Format:
          ``projects/<Project ID>/agent/sessions/<Session
          ID>/entityTypes/<Entity Type Display Name>``.
  """,
  # @@protoc_insertion_point(class_scope:google.cloud.dialogflow.v2beta1.GetSessionEntityTypeRequest)
  ))
_sym_db.RegisterMessage(GetSessionEntityTypeRequest)

CreateSessionEntityTypeRequest = _reflection.GeneratedProtocolMessageType('CreateSessionEntityTypeRequest', (_message.Message,), dict(
  DESCRIPTOR = _CREATESESSIONENTITYTYPEREQUEST,
  __module__ = 'google.cloud.dialogflow_v2beta1.proto.session_entity_type_pb2'
  ,
  __doc__ = """The request message for [SessionEntityTypes.CreateSessionEntityType].
  
  
  Attributes:
      parent:
          Required. The session to create a session entity type for.
          Format: ``projects/<Project ID>/agent/sessions/<Session ID>``.
      session_entity_type:
          Required. The session entity type to create.
  """,
  # @@protoc_insertion_point(class_scope:google.cloud.dialogflow.v2beta1.CreateSessionEntityTypeRequest)
  ))
_sym_db.RegisterMessage(CreateSessionEntityTypeRequest)

UpdateSessionEntityTypeRequest = _reflection.GeneratedProtocolMessageType('UpdateSessionEntityTypeRequest', (_message.Message,), dict(
  DESCRIPTOR = _UPDATESESSIONENTITYTYPEREQUEST,
  __module__ = 'google.cloud.dialogflow_v2beta1.proto.session_entity_type_pb2'
  ,
  __doc__ = """The request message for [SessionEntityTypes.UpdateSessionEntityType].
  
  
  Attributes:
      session_entity_type:
          Required. The entity type to update. Format:
          ``projects/<Project ID>/agent/sessions/<Session
          ID>/entityTypes/<Entity Type Display Name>``.
      update_mask:
          Optional. The mask to control which fields get updated.
  """,
  # @@protoc_insertion_point(class_scope:google.cloud.dialogflow.v2beta1.UpdateSessionEntityTypeRequest)
  ))
_sym_db.RegisterMessage(UpdateSessionEntityTypeRequest)

DeleteSessionEntityTypeRequest = _reflection.GeneratedProtocolMessageType('DeleteSessionEntityTypeRequest', (_message.Message,), dict(
  DESCRIPTOR = _DELETESESSIONENTITYTYPEREQUEST,
  __module__ = 'google.cloud.dialogflow_v2beta1.proto.session_entity_type_pb2'
  ,
  __doc__ = """The request message for [SessionEntityTypes.DeleteSessionEntityType].
  
  
  Attributes:
      name:
          Required. The name of the entity type to delete. Format:
          ``projects/<Project ID>/agent/sessions/<Session
          ID>/entityTypes/<Entity Type Display Name>``.
  """,
  # @@protoc_insertion_point(class_scope:google.cloud.dialogflow.v2beta1.DeleteSessionEntityTypeRequest)
  ))
_sym_db.RegisterMessage(DeleteSessionEntityTypeRequest)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n#com.google.cloud.dialogflow.v2beta1B\026SessionEntityTypeProtoP\001ZIgoogle.golang.org/genproto/googleapis/cloud/dialogflow/v2beta1;dialogflow\370\001\001\242\002\002DF\252\002\037Google.Cloud.Dialogflow.V2beta1'))
try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities


  class SessionEntityTypesStub(object):
    """Manages session entity types.

    Session entity types can be redefined on a session level, allowing for
    specific concepts, like a user's playlists.


    Standard methods.
    """

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.ListSessionEntityTypes = channel.unary_unary(
          '/google.cloud.dialogflow.v2beta1.SessionEntityTypes/ListSessionEntityTypes',
          request_serializer=ListSessionEntityTypesRequest.SerializeToString,
          response_deserializer=ListSessionEntityTypesResponse.FromString,
          )
      self.GetSessionEntityType = channel.unary_unary(
          '/google.cloud.dialogflow.v2beta1.SessionEntityTypes/GetSessionEntityType',
          request_serializer=GetSessionEntityTypeRequest.SerializeToString,
          response_deserializer=SessionEntityType.FromString,
          )
      self.CreateSessionEntityType = channel.unary_unary(
          '/google.cloud.dialogflow.v2beta1.SessionEntityTypes/CreateSessionEntityType',
          request_serializer=CreateSessionEntityTypeRequest.SerializeToString,
          response_deserializer=SessionEntityType.FromString,
          )
      self.UpdateSessionEntityType = channel.unary_unary(
          '/google.cloud.dialogflow.v2beta1.SessionEntityTypes/UpdateSessionEntityType',
          request_serializer=UpdateSessionEntityTypeRequest.SerializeToString,
          response_deserializer=SessionEntityType.FromString,
          )
      self.DeleteSessionEntityType = channel.unary_unary(
          '/google.cloud.dialogflow.v2beta1.SessionEntityTypes/DeleteSessionEntityType',
          request_serializer=DeleteSessionEntityTypeRequest.SerializeToString,
          response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          )


  class SessionEntityTypesServicer(object):
    """Manages session entity types.

    Session entity types can be redefined on a session level, allowing for
    specific concepts, like a user's playlists.


    Standard methods.
    """

    def ListSessionEntityTypes(self, request, context):
      """Returns the list of all session entity types in the specified session.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def GetSessionEntityType(self, request, context):
      """Retrieves the specified session entity type.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def CreateSessionEntityType(self, request, context):
      """Creates a session entity type.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def UpdateSessionEntityType(self, request, context):
      """Updates the specified session entity type.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def DeleteSessionEntityType(self, request, context):
      """Deletes the specified session entity type.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_SessionEntityTypesServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'ListSessionEntityTypes': grpc.unary_unary_rpc_method_handler(
            servicer.ListSessionEntityTypes,
            request_deserializer=ListSessionEntityTypesRequest.FromString,
            response_serializer=ListSessionEntityTypesResponse.SerializeToString,
        ),
        'GetSessionEntityType': grpc.unary_unary_rpc_method_handler(
            servicer.GetSessionEntityType,
            request_deserializer=GetSessionEntityTypeRequest.FromString,
            response_serializer=SessionEntityType.SerializeToString,
        ),
        'CreateSessionEntityType': grpc.unary_unary_rpc_method_handler(
            servicer.CreateSessionEntityType,
            request_deserializer=CreateSessionEntityTypeRequest.FromString,
            response_serializer=SessionEntityType.SerializeToString,
        ),
        'UpdateSessionEntityType': grpc.unary_unary_rpc_method_handler(
            servicer.UpdateSessionEntityType,
            request_deserializer=UpdateSessionEntityTypeRequest.FromString,
            response_serializer=SessionEntityType.SerializeToString,
        ),
        'DeleteSessionEntityType': grpc.unary_unary_rpc_method_handler(
            servicer.DeleteSessionEntityType,
            request_deserializer=DeleteSessionEntityTypeRequest.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'google.cloud.dialogflow.v2beta1.SessionEntityTypes', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetaSessionEntityTypesServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """Manages session entity types.

    Session entity types can be redefined on a session level, allowing for
    specific concepts, like a user's playlists.


    Standard methods.
    """
    def ListSessionEntityTypes(self, request, context):
      """Returns the list of all session entity types in the specified session.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def GetSessionEntityType(self, request, context):
      """Retrieves the specified session entity type.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def CreateSessionEntityType(self, request, context):
      """Creates a session entity type.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def UpdateSessionEntityType(self, request, context):
      """Updates the specified session entity type.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def DeleteSessionEntityType(self, request, context):
      """Deletes the specified session entity type.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaSessionEntityTypesStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """Manages session entity types.

    Session entity types can be redefined on a session level, allowing for
    specific concepts, like a user's playlists.


    Standard methods.
    """
    def ListSessionEntityTypes(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Returns the list of all session entity types in the specified session.
      """
      raise NotImplementedError()
    ListSessionEntityTypes.future = None
    def GetSessionEntityType(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Retrieves the specified session entity type.
      """
      raise NotImplementedError()
    GetSessionEntityType.future = None
    def CreateSessionEntityType(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Creates a session entity type.
      """
      raise NotImplementedError()
    CreateSessionEntityType.future = None
    def UpdateSessionEntityType(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Updates the specified session entity type.
      """
      raise NotImplementedError()
    UpdateSessionEntityType.future = None
    def DeleteSessionEntityType(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Deletes the specified session entity type.
      """
      raise NotImplementedError()
    DeleteSessionEntityType.future = None


  def beta_create_SessionEntityTypes_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'CreateSessionEntityType'): CreateSessionEntityTypeRequest.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'DeleteSessionEntityType'): DeleteSessionEntityTypeRequest.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'GetSessionEntityType'): GetSessionEntityTypeRequest.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'ListSessionEntityTypes'): ListSessionEntityTypesRequest.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'UpdateSessionEntityType'): UpdateSessionEntityTypeRequest.FromString,
    }
    response_serializers = {
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'CreateSessionEntityType'): SessionEntityType.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'DeleteSessionEntityType'): google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'GetSessionEntityType'): SessionEntityType.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'ListSessionEntityTypes'): ListSessionEntityTypesResponse.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'UpdateSessionEntityType'): SessionEntityType.SerializeToString,
    }
    method_implementations = {
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'CreateSessionEntityType'): face_utilities.unary_unary_inline(servicer.CreateSessionEntityType),
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'DeleteSessionEntityType'): face_utilities.unary_unary_inline(servicer.DeleteSessionEntityType),
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'GetSessionEntityType'): face_utilities.unary_unary_inline(servicer.GetSessionEntityType),
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'ListSessionEntityTypes'): face_utilities.unary_unary_inline(servicer.ListSessionEntityTypes),
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'UpdateSessionEntityType'): face_utilities.unary_unary_inline(servicer.UpdateSessionEntityType),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_SessionEntityTypes_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'CreateSessionEntityType'): CreateSessionEntityTypeRequest.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'DeleteSessionEntityType'): DeleteSessionEntityTypeRequest.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'GetSessionEntityType'): GetSessionEntityTypeRequest.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'ListSessionEntityTypes'): ListSessionEntityTypesRequest.SerializeToString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'UpdateSessionEntityType'): UpdateSessionEntityTypeRequest.SerializeToString,
    }
    response_deserializers = {
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'CreateSessionEntityType'): SessionEntityType.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'DeleteSessionEntityType'): google_dot_protobuf_dot_empty__pb2.Empty.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'GetSessionEntityType'): SessionEntityType.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'ListSessionEntityTypes'): ListSessionEntityTypesResponse.FromString,
      ('google.cloud.dialogflow.v2beta1.SessionEntityTypes', 'UpdateSessionEntityType'): SessionEntityType.FromString,
    }
    cardinalities = {
      'CreateSessionEntityType': cardinality.Cardinality.UNARY_UNARY,
      'DeleteSessionEntityType': cardinality.Cardinality.UNARY_UNARY,
      'GetSessionEntityType': cardinality.Cardinality.UNARY_UNARY,
      'ListSessionEntityTypes': cardinality.Cardinality.UNARY_UNARY,
      'UpdateSessionEntityType': cardinality.Cardinality.UNARY_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'google.cloud.dialogflow.v2beta1.SessionEntityTypes', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)
