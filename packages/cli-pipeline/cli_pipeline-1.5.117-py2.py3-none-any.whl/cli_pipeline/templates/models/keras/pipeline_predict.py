import os
import numpy as np
import json
import logging

from pipeline_monitor import prometheus_monitor as monitor
from pipeline_logger import log

_logger = logging.getLogger('pipeline-logger')
_logger.setLevel(logging.INFO)
_logger_stream_handler = logging.StreamHandler()
_logger_stream_handler.setLevel(logging.INFO)
_logger.addHandler(_logger_stream_handler)


__all__ = ['predict']


_labels= {'model_runtime': '{{ PIPELINE_MODEL_RUNTIME}}',
          'model_type': '{{ PIPELINE_MODEL_TYPE }}',
          'model_name': '{{ PIPELINE_MODEL_NAME }}',
          'model_tag': '{{ PIPELINE_MODEL_TAG }}',
          'model_chip': '{{ PIPELINE_MODEL_CHIP }}',
         }


def _initialize_upon_import() -> TensorFlowServingModel:
    ''' Initialize / Restore Model Object.
    '''
    return TensorFlowServingModel(host='localhost',
                                  port=9000,
                                  model_name='{{ PIPELINE_MODEL_NAME }}',
                                  timeout=100)    


# This is called unconditionally at *module import time*...
_model = _initialize_upon_import()


@log(labels=_labels, logger=_logger)
def predict(request: bytes) -> bytes:
    '''Where the magic happens...'''

    with monitor(labels=_labels, name="transform_request"):
        transformed_request = _transform_request(request)

    with monitor(labels=_labels, name="predict"):
        predictions = _model.predict(transformed_request)

    with monitor(labels=_labels, name="transform_response"):
        transformed_response = _transform_response(predictions)

    return transformed_response


def _transform_request(request: bytes) -> dict:
    # Convert from bytes to tf.tensor, np.array, etc.
    pass


def _transform_response(response: dict) -> json:
    # Convert from tf.tensor, np.array, etc. to bytes
    pass
