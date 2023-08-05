# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from dialogflow_v2beta1.proto import session_pb2 as google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2


class SessionsStub(object):
  """Manages user sessions.


  Custom methods.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.DetectIntent = channel.unary_unary(
        '/google.cloud.dialogflow.v2beta1.Sessions/DetectIntent',
        request_serializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.DetectIntentRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.DetectIntentResponse.FromString,
        )
    self.StreamingDetectIntent = channel.stream_stream(
        '/google.cloud.dialogflow.v2beta1.Sessions/StreamingDetectIntent',
        request_serializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.StreamingDetectIntentRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.StreamingDetectIntentResponse.FromString,
        )


class SessionsServicer(object):
  """Manages user sessions.


  Custom methods.
  """

  def DetectIntent(self, request, context):
    """Processes a natural language query and returns structured, actionable data
    as a result. This method is not idempotent, because it may cause contexts
    and session entity types to be updated, which in turn might affect
    results of future queries.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StreamingDetectIntent(self, request_iterator, context):
    """Processes a natural language query in audio format in a streaming fashion
    and returns structured, actionable data as a result. This method is only
    available via the gRPC API (not REST).
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_SessionsServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'DetectIntent': grpc.unary_unary_rpc_method_handler(
          servicer.DetectIntent,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.DetectIntentRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.DetectIntentResponse.SerializeToString,
      ),
      'StreamingDetectIntent': grpc.stream_stream_rpc_method_handler(
          servicer.StreamingDetectIntent,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.StreamingDetectIntentRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2beta1_dot_proto_dot_session__pb2.StreamingDetectIntentResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'google.cloud.dialogflow.v2beta1.Sessions', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
