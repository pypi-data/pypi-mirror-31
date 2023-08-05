# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from stylelens_color.grpc import color_extract_pb2 as color__extract__pb2


class ExtractStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetColor = channel.unary_unary(
        '/extractcolor.Extract/GetColor',
        request_serializer=color__extract__pb2.ColorRequest.SerializeToString,
        response_deserializer=color__extract__pb2.ColorReply.FromString,
        )


class ExtractServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetColor(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ExtractServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetColor': grpc.unary_unary_rpc_method_handler(
          servicer.GetColor,
          request_deserializer=color__extract__pb2.ColorRequest.FromString,
          response_serializer=color__extract__pb2.ColorReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'extractcolor.Extract', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
