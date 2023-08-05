#-*- coding: utf-8 -*-

__version__ = "1.5.117"

import warnings as _warnings
import requests as _requests
import fire as _fire
import tarfile as _tarfile
import os as _os
import sys as _sys
import kubernetes.client as _kubeclient
import kubernetes.config as _kubeconfig
import json as _json
from pprint import pprint as _pprint
import subprocess as _subprocess
import jinja2 as _jinja2
import boto3 as _boto3
from botocore.exceptions import ClientError as _ClientError
import base64 as _base64
import binascii as _binascii
from flask import Flask as _Flask, Response as _Response, jsonify as _jsonify, url_for as _url_for, redirect as _redirect, request as _request, send_file as _send_file, stream_with_context as _stream_with_context
from flask_cors import CORS as _CORS, cross_origin as _cross_origin
from shelljob import proc as _proc
from inspect import getmembers as _getmembers, isfunction as _isfunction
import shutil as _shutil
import time

app = _Flask(__name__)

_CORS(app, resources=r'/*')

_http_mode = True 
_model_base_path = '.'

if _sys.version_info.major == 3:
    from urllib3 import disable_warnings as _disable_warnings
    _disable_warnings()

# Deprecated
_kube_deploy_registry = {'jupyter': (['jupyterhub-deploy.yaml'], []),
                        'jupyterhub': (['jupyterhub-deploy.yaml'], []),
                        'spark': (['spark-master-deploy.yaml'], ['spark-worker', 'metastore']),
                        'spark-worker': (['spark-worker-deploy.yaml'], []),
                        'metastore': (['metastore-deploy.yaml'], ['mysql']),
                        'hdfs': (['namenode-deploy.yaml'], []),
                        'redis': (['redis-master-deploy.yaml'], []),
                        'presto': (['presto-master-deploy.yaml',
                                    'presto-worker-deploy.yaml'], ['metastore']),
                        'presto-ui': (['presto-ui-deploy.yaml'], ['presto']),
                        'airflow': (['airflow-deploy.yaml'], ['mysql', 'redis']),
                        'mysql': (['mysql-master-deploy.yaml'], []),
                        #'web-home': (['web/home-deploy.yaml'], []),
                        'zeppelin': (['zeppelin-deploy.yaml'], []),
                        #'zookeeper': (['zookeeper-deploy.yaml'], []),
                        'elasticsearch': (['elasticsearch-2-3-0-deploy.yaml'], []),
                        'kibana': (['kibana-4-5-0-deploy.yaml'], ['elasticsearch'], []), 
                        #'kafka': (['stream/kafka-0.11-deploy.yaml'], ['zookeeper']),
                        'cassandra': (['cassandra-deploy.yaml'], []),
                        'jenkins': (['jenkins-deploy.yaml'], []),
                        #'turbine': (['dashboard/turbine-deploy.yaml'], []),
                        #'hystrix': (['dashboard/hystrix-deploy.yaml'], []),
                       }

# Deprecated
_kube_svc_registry = {'jupyter': (['jupyterhub-svc.yaml'], []),
                     'jupyterhub': (['jupyterhub-svc.yaml'], []),
                     'spark': (['spark-master-svc.yaml'], ['spark-worker', 'metastore']), 
                     'spark-worker': (['spark-worker-svc.yaml'], []),
                     'metastore': (['metastore-svc.yaml'], ['mysql']),
                     'hdfs': (['namenode-svc.yaml'], []),
                     'redis': (['redis-master-svc.yaml'], []),
                     'presto': (['presto-master-svc.yaml',
                                 'presto-worker-svc.yaml'], ['metastore']),
                     'presto-ui': (['presto-ui-svc.yaml'], ['presto']),
                     'airflow': (['airflow-svc.yaml'], ['mysql', 'redis']),
                     'mysql': (['mysql-master-svc.yaml'], []),
                     #'web-home': (['web/home-svc.yaml'], []),
                     'zeppelin': (['zeppelin-svc.yaml'], []),
                     #'zookeeper': (['zookeeper/zookeeper-svc.yaml'], []),
                     'elasticsearch': (['elasticsearch-2-3-0-svc.yaml'], []),
                     'kibana': (['kibana-4-5-0-svc.yaml'], ['elasticsearch'], []),
                     #'kafka': (['stream/kafka-0.11-svc.yaml'], ['zookeeper']),
                     'cassandra': (['cassandra-svc.yaml'], []),
                     #'jenkins': (['jenkins-svc.yaml'], []),
                     #'turbine': (['dashboard/turbine-svc.yaml'], []),
                     #'hystrix': (['dashboard/hystrix-svc.yaml'], []),
                    }

_Dockerfile_template_registry = {
                                 'predict-server': (['docker/predict-server-local-dockerfile.template'], []),
                                 'train-server': (['docker/train-server-local-dockerfile.template'], []),
                                }

_kube_router_deploy_template_registry = {'predict-router-split': (['yaml/predict-deploy.yaml.template'], []),
                                         'predict-router-gpu-split': (['yaml/predict-gpu-deploy.yaml.template'], [])}

_kube_router_ingress_template_registry = {'predict-router-split': (['yaml/predict-ingress.yaml.template'], [])}
_kube_router_svc_template_registry = {'predict-router-split': (['yaml/predict-svc.yaml.template'], [])}
_kube_router_routerules_template_registry = {'predict-router': (['yaml/predict-routerules.yaml.template'], [])}
_kube_router_autoscale_template_registry = {'predict-router-split': (['yaml/predict-autoscale.yaml.template'], [])}

_kube_stream_deploy_template_registry = {'stream': (['yaml/stream-deploy.yaml.template'], [])}
_kube_stream_svc_template_registry = {'stream': (['yaml/stream-svc.yaml.template'], [])}
_kube_stream_ingress_template_registry = {'stream': (['yaml/stream-ingress.yaml.template'], [])}
_kube_stream_routerules_template_registry = {'stream': (['yaml/stream-routerules.yaml.template'], [])}

_train_kube_template_registry = {'train-cluster': (['yaml/train-cluster.yaml.template'], []),
                                 'train-gpu-cluster': (['yaml/train-gpu-cluster.yaml.template'], [])}

_pipeline_api_version = 'v1'

_default_pipeline_templates_path = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), 'templates'))
_default_pipeline_services_path = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), 'services'))

_default_image_registry_url = 'docker.io'
_default_image_registry_repo = 'pipelineai'
_default_image_registry_train_namespace = 'train'
_default_image_registry_predict_namespace = 'predict' 
_default_image_registry_stream_namespace = 'stream'
_default_image_registry_base_tag = '1.5.0'

_default_model_chip = 'cpu'

_default_build_type = 'docker'
_default_build_context_path = '.'

_default_namespace = 'default'


####################
# TF Serving Utils #
####################
# Note:  This requires tensorflow to be installed
@app.route("/predict-tensorflow-describe/<string:model_path>/", methods=['GET'])
def _predict_tensorflow_describe(model_path):
    # saved_model_cli show --dir $(find $PIPELINE_MODEL_PATH/pipeline_tfserving -mindepth 1 -maxdepth 1 -type d) --all
    cmd = "saved_model_cli show --dir $(find %s/pipeline_tfserving -mindepth 1 -maxdepth 1 -type d) --all" % model_path
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


# TODO: Create app.route to accept a checkpoint file and create saved_model format
def _convert_tf_export_format_to_savedmodel_format(checkpoint_prefix,
                                                   saved_model_path,
                                                   inputs,
                                                   outputs):
  """Writes SavedModel to disk.
  Args:
    saved_model_path: Path to write SavedModel.
    trained_checkpoint_prefix: path to trained_checkpoint_prefix (old tf export format).
    inputs: The input tensors to use for prediction.
    outputs: A tensor dictionary containing the outputs of a prediction
  """
  saver = tf.train.Saver()
  with session.Session() as sess:
    saver.restore(sess, trained_checkpoint_prefix)
    builder = tf.saved_model.builder.SavedModelBuilder(saved_model_path)

    tensor_info_inputs = {
          'inputs': tf.saved_model.utils.build_tensor_info(inputs)}
    tensor_info_outputs = {}
    for k, v in outputs.items():
      tensor_info_outputs[k] = tf.saved_model.utils.build_tensor_info(v)

    signature = (
        tf.saved_model.signature_def_utils.build_signature_def(
              inputs=tensor_info_inputs,
              outputs=tensor_info_outputs,
              method_name=signature_constants.PREDICT_METHOD_NAME))

    builder.add_meta_graph_and_variables(
          sess, [tf.saved_model.tag_constants.SERVING],
          signature_def_map={
              'default':
                  signature,
              signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                  signature,
          },
      )
    builder.save()


def help():
    print("Available commands:")
    this_module = _sys.modules[__name__]
    functions = [o[0] for o in _getmembers(this_module) if _isfunction(o[1])]
    functions = [function.replace('_', '-') for function in functions if not function.startswith('_')]
    functions = sorted(functions)
    print("\n".join(functions))


def version():
    print('')
    print('CLI version: %s' % __version__)
    print('API version: %s' % _pipeline_api_version)
    print('')
    print('Default build type: %s' % _default_build_type)

    build_context_path = _os.path.expandvars(_default_build_context_path)
    build_context_path = _os.path.expanduser(build_context_path)
    build_context_path = _os.path.abspath(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)

    print('Default build context path: %s => %s' % (_default_build_context_path, build_context_path))
    print('')
    print('Default train base image: %s/%s/%s-%s:%s' % (_default_image_registry_url, _default_image_registry_repo, _default_image_registry_train_namespace, _default_model_chip, _default_image_registry_base_tag))
    print('Default predict base image: %s/%s/%s-%s:%s' % (_default_image_registry_url, _default_image_registry_repo, _default_image_registry_predict_namespace, _default_model_chip, _default_image_registry_base_tag))
    print('')


def _templates_path():
    print("")
    print("Templates path: %s" % _default_pipeline_templates_path)
    print("")

    return _default_pipeline_templates_path


def _get_default_model_runtime(model_type):
    model_runtime = 'python'

    if model_type in ['keras', 'python', 'scikit', 'pytorch']:
       model_runtime = 'python'
     
    if model_type in ['java', 'pmml', 'spark', 'xgboost']:
       model_runtime = 'jvm'

    if model_type in ['tensorflow']:
       model_runtime = 'tfserving'
     
    if model_type in ['caffe']:
       model_runtime = 'cpp'

    return model_runtime


# TODO:  Make sure model_tag is DNS compliant since this may be used as a DNS hostname.
#        We might also want to remove '-' and '_', etc.
def _validate_and_prep_model_tag(model_tag):
    if type(model_tag) != str:
        model_tag = str(model_tag)
    model_tag = model_tag.lower()

    return model_tag


def _validate_and_prep_model_split_tag_and_weight_dict(model_split_tag_and_weight_dict):
    model_weight_total = 0
    for tag, _ in model_split_tag_and_weight_dict.items():
        model_weight = int(model_split_tag_and_weight_dict[tag])
        model_weight_total += model_weight

    if model_weight_total != 100:
        raise ValueError("Total of '%s' for weights '%s' does not equal 100 as expected." % (model_weight_total, model_split_tag_and_weight_dict))
        
    return 


@app.route("/predict-kube-endpoint/<string:model_name>/", methods=['GET'])
def predict_kube_endpoint(model_name,
                          namespace=None,
                          image_registry_namespace=None):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        endpoint_url = _get_model_kube_endpoint(model_name=model_name, 
                                                namespace=namespace,
                                                image_registry_namespace=image_registry_namespace)

        response = kubeclient_v1_beta1.list_namespaced_deployment(namespace=namespace,
                                                                  include_uninitialized=True,
                                                                  watch=False,
                                                                  limit=1000,
                                                                  pretty=False)

        deployments = response.items
        model_variant_list = [deployment.metadata.name for deployment in deployments
                               if '%s-%s' % (image_registry_namespace, model_name) in deployment.metadata.name]

    return_dict = {"endpoint_url": endpoint_url,
                   "model_variants": model_variant_list}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


@app.route("/predict-kube-endpoints/", methods=['GET'])
def predict_kube_endpoints(namespace=None,
                           image_registry_namespace=None):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    endpoint_list = []
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")

        endpoint_list = _get_all_model_endpoints(namespace=namespace,
                                                 image_registry_namespace=image_registry_namespace)

        return_dict = {"endpoints": endpoint_list}

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict


def _get_sage_endpoint_url(model_name,
                           model_region,
                           image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    return 'https://runtime.sagemaker.%s.amazonaws.com/endpoints/%s-%s/invocations' % (model_region, image_registry_namespace, model_name)


def _jupyter_kube_start(namespace=None,
                        image_registry_namespace=None):
    pass


def _dashboard_kube_start(namespace=None,
                         image_registry_namespace=None):
    pass


def predict_kube_connect(model_name,
                         model_tag,
                         local_port=None,
                         service_port=None,
                         namespace=None,
                         image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_connect(service_name=service_name,
                     namespace=namespace,
                     local_port=local_port,
                     service_port=service_port)


def _service_connect(service_name,
                     namespace=None,
                     local_port=None,
                     service_port=None):

    if not namespace:
        namespace = _default_namespace

    pod = _get_pod_by_service_name(service_name=service_name)
    if not pod:
        print("")
        print("Service '%s' is not running." % service_name)
        print("")
        return
    if not service_port:
        svc = _get_svc_by_service_name(service_name=service_name)
        if not svc:
            print("")
            print("Service '%s' proxy port cannot be found." % service_name)
            print("")
            return
        service_port = svc.spec.ports[0].target_port

    if not local_port:
        print("")
        print("Proxying local port '<randomly-chosen>' to app '%s' port '%s' using pod '%s' in namespace '%s'." % (service_port, service_name, pod.metadata.name, namespace))
        print("")
        print("If you break out of this terminal, your proxy session will end.")
        print("")
        print("Use 'http://127.0.0.1:<randomly-chosen>' to access app '%s' on port '%s' in namespace '%s'." % (service_name, service_port, namespace))
        print("")
        cmd = 'kubectl port-forward %s :%s --namespace=%s' % (pod.metadata.name, service_port, namespace)
        print(cmd)
        print("")
    else:
        print("")
        print("Proxying local port '%s' to app '%s' port '%s' using pod '%s' in namespace '%s'." % (local_port, service_port, service_name, pod.metadata.name, namespace))
        print("")
        print("If you break out of this terminal, your proxy session will end.")
        print("")
        print("Use 'http://127.0.0.1:%s' to access app '%s' on port '%s' in namespace '%s'." % (local_port, service_name, service_port, namespace))
        print("")
        cmd = 'kubectl port-forward %s %s:%s --namespace=%s' % (pod.metadata.name, local_port, service_port, namespace)
        print(cmd)
        print("")

    _subprocess.call(cmd, shell=True)
    print("")


def _environment_resources():
    _subprocess.call("kubectl top node", shell=True)

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                          pretty=True)
        deployments = response.items
        for deployment in deployments:
            _service_resources(deployment.metadata.name)


def _service_resources(service_name,
                       namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()
    
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                             pretty=True)
        pods = response.items
        for pod in pods: 
            if (service_name in pod.metadata.name):
                _subprocess.call('kubectl top pod %s --namespace=%s' % (pod.metadata.name, namespace), shell=True)
    print("")


def _create_predict_server_Dockerfile(model_name,
                                      model_tag,
                                      model_path,
                                      model_type,
                                      model_runtime,
                                      model_chip,
                                      http_proxy,
                                      https_proxy,
                                      stream_logger_url,
                                      stream_logger_topic,
                                      stream_input_url,
                                      stream_input_topic,
                                      stream_output_url,
                                      stream_output_topic,
                                      image_registry_url,
                                      image_registry_repo,
                                      image_registry_namespace,
                                      image_registry_base_tag,
                                      image_registry_base_chip,
                                      pipeline_templates_path,
                                      build_context_path):

    model_tag = _validate_and_prep_model_tag(model_tag)

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_MODEL_PATH': model_path,
               'PIPELINE_MODEL_TYPE': model_type,
               'PIPELINE_MODEL_RUNTIME': model_runtime,
               'PIPELINE_MODEL_CHIP': model_chip,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
              }

    model_predict_cpu_Dockerfile_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _Dockerfile_template_registry['predict-server'][0][0]))
    path, filename = _os.path.split(model_predict_cpu_Dockerfile_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_Dockerfile = _os.path.normpath('%s/.pipeline-generated-%s-%s-%s-%s-%s-%s-Dockerfile' % (build_context_path, image_registry_namespace, model_name, model_tag, model_type, model_runtime, model_chip))
    with open(rendered_Dockerfile, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'." % (filename, rendered_Dockerfile))

    return rendered_Dockerfile


def _predict_server_describe(model_name,
                             model_tag):
    pass        


def _is_base64_encoded(data):
    try:
        data = data.encode('utf-8')
    except Exception:
        pass

    try:
        if _base64.b64encode(_base64.b64decode(data)) == data:
            return True
    except Exception:
        pass

    return False


def _decode_base64(data):
    return _base64.b64decode(data).decode('utf-8')


#  Note:  model_path must contain the pipeline_conda_environment.yml file
def env_conda_activate(model_name,
                       model_tag,
                       model_path='.'):

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)

    # TODO:  Check if exists.  If so, warn the user as new packages in pipeline_conda_environment.yml
    #        will not be picked up after the initial environment creation.
    cmd = 'source activate root && conda env update --name %s-%s -f %s/pipeline_conda_environment.yml --prune --verbose' % (model_name, model_tag, model_path)
    print(cmd)
    process = _subprocess.call(cmd, shell=True)
    print("")
    cmd = 'Please run "source activate %s-%s" before you continue.' % (model_name, model_tag)
    print("")
    return cmd


@app.route("/predict-server-init/<string:model_name>/<string:model_tag>/<string:model_type>/<string:new_model_path>/<string:model_runtime>/<string:model_chip>/", methods=['GET'])
def predict_server_init(model_name,
                        model_tag,
                        model_type,
                        new_model_path=None, # must be empty and relative to pwd 
                        model_runtime=None,
                        model_chip=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_chip:
        model_chip = _default_model_chip

    if not model_runtime:
        model_runtime = _get_default_model_runtime(model_type)

    if not new_model_path:
        new_model_path = _os.path.normpath('%s/%s/%s-%s/' % (_model_base_path, model_type, model_name, model_tag))
    else:
        if _is_base64_encoded(new_model_path):
            new_model_path = _decode_base64(new_model_path)
 
    new_model_path = _os.path.expandvars(new_model_path)
    new_model_path = _os.path.expanduser(new_model_path)
    new_model_path = _os.path.abspath(new_model_path)
    new_model_path = _os.path.normpath(new_model_path)

    if _os.path.exists(new_model_path):
        return_dict = {"status": "incomplete",
                       "error_message": "Model path '%s' already exists. Please specify a different path." % new_model_path,
                       "model_name": model_name,
                       "model_tag": model_tag,
                       "model_type": model_type,
                       "model_runtime": model_runtime,
                       "model_chip": model_chip,
                       "new_model_path": new_model_path,
                      }

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_MODEL_TYPE': model_type,
               'PIPELINE_MODEL_RUNTIME': model_runtime,
               'PIPELINE_MODEL_CHIP': model_chip,
              }

    templates_base_path = _os.path.normpath('%s/models/%s' % (_templates_path(), model_type))

    templates_list = _jinja2.Environment(loader=_jinja2.FileSystemLoader(templates_base_path)).list_templates()
    rendered_filenames = []
    for template in templates_list:
        rendered_content = _jinja2.Environment(loader=_jinja2.FileSystemLoader(templates_base_path)).get_template(template).render(context)
        rendered_filename = _os.path.normpath('%s/%s' % (new_model_path, template))
        rendered_path, _ = _os.path.split(rendered_filename)
        #rendered_path = _os.path.join(rendered_path, 'model')
        # TODO: Refactor this
        if not _os.path.exists(rendered_path):
            _os.makedirs(rendered_path)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered_content)
            print("'%s' => '%s'." % (template, rendered_filename))

        rendered_filenames += [rendered_filename]

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "model_type": model_type,
                   "model_runtime": model_runtime,
                   "model_chip": model_chip,                 
                   "new_model_path": new_model_path,
                   "new_filename_list": rendered_filenames,
                  }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


## TODO:  train_server_init


# ie. http://localhost:6970/predict-server-build/mnist/gpu/tensorflow/tfserving/gpu/dGVuc29yZmxvdy9tbmlzdC1ncHUvbW9kZWwv/docker.io/pipelineai/predict/
#
# model_name: mnist
# model_tag: gpu
# model_path: tensorflow/mnist-gpu/model/
# model_type: tensorflow
# model_runtime: tfserving
# model_chip: gpu
#
@app.route("/predict-server-build/<string:model_name>/<string:model_tag>/<string:model_type>/<string:model_runtime>/<string:model_chip>/<string:model_path>/<string:image_registry_url>/<string:image_registry_repo>/<string:image_registry_namespace>/", methods=['GET'])
def predict_server_build(model_name,
                         model_tag,
                         model_type,
                         model_path, # relative to models/ ie. ./tensorflow/mnist/
                         model_runtime=None,
                         model_chip=None,
                         squash=False,
                         no_cache=False,
                         http_proxy=None,
                         https_proxy=None,
                         stream_logger_url=None,
                         stream_logger_topic=None,
                         stream_input_url=None,
                         stream_input_topic=None,
                         stream_output_url=None,
                         stream_output_topic=None,
                         build_type=None,
                         build_context_path=None,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None,
                         image_registry_base_tag=None,
                         image_registry_base_chip=None,
                         pipeline_templates_path=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_chip:
        model_chip = _default_model_chip

    if not model_runtime:
        model_runtime = _get_default_model_runtime(model_type)

    if not build_type:
        build_type = _default_build_type

    if not build_context_path: 
        build_context_path = _default_build_context_path

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    build_context_path = _os.path.expandvars(build_context_path)
    build_context_path = _os.path.expanduser(build_context_path)
    build_context_path = _os.path.abspath(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)

    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    pipeline_templates_path = _os.path.relpath(pipeline_templates_path, build_context_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)

    if _is_base64_encoded(model_path):
        model_path = _decode_base64(model_path)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)
    model_path = _os.path.relpath(model_path, build_context_path)
    model_path = _os.path.normpath(model_path)

    print("expanded model_path: '%s'" % model_path)

    if build_type == 'docker':
        generated_Dockerfile = _create_predict_server_Dockerfile(model_name=model_name,
                                                                 model_tag=model_tag,
                                                                 model_path=model_path,
                                                                 model_type=model_type, 
                                                                 model_runtime=model_runtime,
                                                                 model_chip=model_chip,
                                                                 http_proxy=http_proxy,
                                                                 https_proxy=https_proxy,
                                                                 stream_logger_url=stream_logger_url,
                                                                 stream_logger_topic=stream_logger_topic,
                                                                 stream_input_url=stream_input_url,
                                                                 stream_input_topic=stream_input_topic,
                                                                 stream_output_url=stream_output_url,
                                                                 stream_output_topic=stream_output_topic,
                                                                 image_registry_url=image_registry_url,
                                                                 image_registry_repo=image_registry_repo,
                                                                 image_registry_namespace=image_registry_namespace,
                                                                 image_registry_base_tag=image_registry_base_tag,
                                                                 image_registry_base_chip=image_registry_base_chip,
                                                                 pipeline_templates_path=pipeline_templates_path,
                                                                 build_context_path=build_context_path)

        if http_proxy:
           http_proxy_build_arg_snippet = '--build-arg HTTP_PROXY=%s' % http_proxy
        else:
           http_proxy_build_arg_snippet = ''

        if https_proxy:
           https_proxy_build_arg_snippet = '--build-arg HTTPS_PROXY=%s' % https_proxy
        else:
           https_proxy_build_arg_snippet = ''

        if no_cache:
           no_cache = '--no-cache'
        else:
           no_cache = ''

        if squash:
           squash = '--squash'
        else:
           squash = ''

        print("")
        # TODO: Narrow the build_context_path (difference between model_path and current path?) 
        cmd = 'docker build %s %s %s %s -t %s/%s/%s-%s:%s -f %s %s' % (no_cache, squash, http_proxy_build_arg_snippet, https_proxy_build_arg_snippet, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag, generated_Dockerfile, build_context_path)

        print(cmd)
        print("")
        process = _subprocess.call(cmd, shell=True)
    else:
        return_dict = {"status": "incomplete",
                       "error_message": "Build type '%s' not found" % build_type}

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict

    return_dict = {"status": "complete",
                   "cmd": "%s" % cmd,
                   "model_variant": "%s-%s-%s" % (image_registry_namespace, model_name, model_tag),
                   "image": "%s/%s/%s-%s:%s" % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag),
                   "model_path": model_path}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def _create_predict_kube_Kubernetes_yaml(model_name,
                                         model_tag,
                                         model_chip=None,
                                         namespace=None,
                                         stream_logger_url=None,
                                         stream_logger_topic=None,
                                         stream_input_url=None,
                                         stream_input_topic=None,
                                         stream_output_url=None,
                                         stream_output_topic=None,
                                         memory_limit='2Gi',
                                         core_limit='1000m',
                                         target_core_util_percentage='50',
                                         min_replicas='1',
                                         max_replicas='2',
                                         image_registry_url=None,
                                         image_registry_repo=None,
                                         image_registry_namespace=None,
                                         image_registry_base_tag=None,
                                         image_registry_base_chip=None,
                                         pipeline_templates_path=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not model_chip:
        model_chip = _default_model_chip
    
    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_NAMESPACE': namespace,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_CORE_LIMIT': core_limit,
               'PIPELINE_MEMORY_LIMIT': memory_limit,
               'PIPELINE_TARGET_CORE_UTIL_PERCENTAGE': target_core_util_percentage,
               'PIPELINE_MIN_REPLICAS': min_replicas,
               'PIPELINE_MAX_REPLICAS': max_replicas,
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
              }

    rendered_filenames = []

    if model_chip == 'gpu':
        model_router_deploy_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_deploy_template_registry['predict-router-gpu-split'][0][0]))
        path, filename = _os.path.split(model_router_deploy_yaml_templates_path)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s-deploy.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'" % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]
    else:
        model_router_deploy_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_deploy_template_registry['predict-router-split'][0][0]))
        path, filename = _os.path.split(model_router_deploy_yaml_templates_path)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s-deploy.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'" % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]

    model_router_ingress_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_ingress_template_registry['predict-router-split'][0][0]))
    path, filename = _os.path.split(model_router_ingress_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-ingress.yaml' % (image_registry_namespace, model_name))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    model_router_svc_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_svc_template_registry['predict-router-split'][0][0]))
    path, filename = _os.path.split(model_router_svc_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-svc.yaml' % (image_registry_namespace, model_name))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    model_router_autoscale_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_autoscale_template_registry['predict-router-split'][0][0]))
    path, filename = _os.path.split(model_router_autoscale_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-autoscale.yaml' % (image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    return rendered_filenames


# This function is kinda silly.
# pipeline _local --cmd="<my-command>" --args="<my-args>"
def _local(cmd, args):
    cmd = '%s %s' % (cmd, args)
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def _create_stream_kube_Kubernetes_yaml(model_name,
                                        model_tag,
                                        model_chip,
                                        stream_logger_topic,
                                        stream_input_topic,
                                        stream_output_topic,
                                        stream_enable_mqtt,
                                        stream_enable_kafka_rest_api,
                                        namespace,
                                        image_registry_url,
                                        image_registry_repo,
                                        image_registry_namespace,
                                        image_registry_base_tag,
                                        image_registry_base_chip,
                                        pipeline_templates_path):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_NAMESPACE': namespace,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_STREAM_ENABLE_MQTT': stream_enable_mqtt,
               'PIPELINE_STREAM_ENABLE_KAFKA_REST_API': stream_enable_kafka_rest_api,
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
              }

    rendered_filenames = []

    model_stream_svc_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_stream_svc_template_registry['stream'][0][0]))
    path, filename = _os.path.split(model_stream_svc_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-svc.yaml' % (image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    model_stream_deploy_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_stream_deploy_template_registry['stream'][0][0]))
    path, filename = _os.path.split(model_stream_deploy_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-deploy.yaml' % (image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    model_stream_ingress_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_stream_ingress_template_registry['stream'][0][0]))
    path, filename = _os.path.split(model_stream_ingress_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-ingress.yaml' % (image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    model_stream_routerules_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_stream_routerules_template_registry['stream'][0][0]))
    path, filename = _os.path.split(model_stream_routerules_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-routerules.yaml' % (image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    return rendered_filenames


def predict_server_shell(model_name,
                         model_tag,
                         image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = 'docker exec -it %s bash' % container_name 
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)


# http://localhost:6970/predict-server-register/mnist/a/docker.io/pipelineai
@app.route("/predict-server-register/<string:model_name>/<string:model_tag>/<string:image_registry_url>/<string:image_registry_repo>/", methods=['GET'])
def predict_server_register(model_name,
                            model_tag,
                            image_registry_url=None,
                            image_registry_repo=None,
                            image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    registry_type = "docker"
    registry_coordinates = '%s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)

    cmd = 'docker push %s' % registry_coordinates 
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "image_registry_url": image_registry_url,
                   "image_registry_repo": image_registry_repo,
                   "image_registry_namespace": image_registry_namespace,
                   "registry_type": registry_type,
                   "registry_coordinates": registry_coordinates
                  }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_server_pull(model_name,
                        model_tag,
                        image_registry_url=None,
                        image_registry_repo=None,
                        image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    cmd = 'docker pull %s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)


def predict_server_start(model_name,
                         model_tag,
                         stream_logger_url=None,
                         stream_logger_topic=None,
                         stream_input_url=None,
                         stream_input_topic=None,
                         stream_output_url=None,
                         stream_output_topic=None,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None,
                         predict_port='8080',
                         prometheus_port='9090',
                         grafana_port='3000',
                         memory_limit='2G',
                         start_cmd='docker'):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    if not stream_logger_topic:
        stream_logger_topic = '%s-%s-logger' % (model_name, model_tag)

    if not stream_input_topic:
        stream_input_topic = '%s-%s-input' % (model_name, model_tag)

    if not stream_output_topic:
        stream_output_topic = '%s-%s-output' % (model_name, model_tag)      

    # Note: We added `serve` to mimic AWS SageMaker and encourage ENTRYPOINT vs CMD as detailed here:  
    #       https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html
    cmd = '%s run -itd -p %s:8080 -p %s:9090 -p %s:3000 -e PIPELINE_LOCAL_MODE=true -e PIPELINE_STREAM_LOGGER_URL=%s -e PIPELINE_STREAM_LOGGER_TOPIC=%s -e PIPELINE_STREAM_INPUT_URL=%s -e PIPELINE_STREAM_INPUT_TOPIC=%s -e PIPELINE_STREAM_OUTPUT_URL=%s -e PIPELINE_STREAM_OUTPUT_TOPIC=%s --name=%s -m %s %s/%s/%s-%s:%s serve' % (start_cmd, predict_port, prometheus_port, grafana_port, stream_logger_url, stream_logger_topic, stream_input_url, stream_input_topic, stream_output_url, stream_output_topic, container_name, memory_limit, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)
    print("")
    print("container name: '%s'" % container_name)
    print("predict port: '%s'" % predict_port)
    print("prometheus port: '%s'" % prometheus_port)
    print("grafana port: '%s'" % grafana_port)
    print("")


def predict_server_stop(model_name,
                        model_tag,
                        image_registry_namespace=None,
                        stop_cmd='docker'): 

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = '%s rm -f %s' % (stop_cmd, container_name)
    print(cmd)
    print("")

    process = _subprocess.call(cmd, shell=True)


def predict_server_logs(model_name,
                        model_tag,
                        image_registry_namespace=None,
                        logs_cmd='docker'):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = '%s logs -f %s' % (logs_cmd, container_name)
    print(cmd)
    print("")

    process = _subprocess.call(cmd, shell=True)


def _service_rollout(service_name,
                     service_image,
                     service_tag):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                          pretty=True)
        found = False
        deployments = response.items
        for deployment in deployments:
            if service_name in deployment.metadata.name:
                found = True
                break
        if found:
            print("")
            print("Upgrading service '%s' using Docker image '%s:%s'." % (deployment.metadata.name, service_image, service_tag))
            print("")
            cmd = "kubectl set image deploy %s %s=%s:%s" % (deployment.metadata.name, deployment.metadata.name, service_image, service_tag)
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
            cmd = "kubectl rollout status deploy %s" % deployment.metadata.name
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
            cmd = "kubectl rollout history deploy %s" % deployment.metadata.name
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("")


def _service_history(service_name):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                          pretty=True)
        found = False
        deployments = response.items
        for deployment in deployments:
            if service_name in deployment.metadata.name:
                found = True
                break
        if found:
            print("")
            cmd = "kubectl rollout status deploy %s" % deployment.metadata.name
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
            cmd = "kubectl rollout history deploy %s" % deployment.metadata.name
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("")


def _service_rollback(service_name,
                      revision=None):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                          pretty=True)
        found = False
        deployments = response.items
        for deployment in deployments:
            if service_name in deployment.metadata.name:
                found = True
                break
        if found:
            print("")
            if revision:
                print("Rolling back app '%s' to revision '%s'." % deployment.metadata.name, revision)
                cmd = "kubectl rollout undo deploy %s --to-revision=%s" % (deployment.metadata.name, revision)
            else:
                print("Rolling back app '%s'." % deployment.metadata.name)
                cmd = "kubectl rollout undo deploy %s" % deployment.metadata.name
            print("")
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
            cmd = "kubectl rollout status deploy %s" % deployment.metadata.name
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
            cmd = "kubectl rollout history deploy %s" % deployment.metadata.name
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("")


def _filter_tar(tarinfo):
    ignore_list = []
    for ignore in ignore_list:
        if ignore in tarinfo.name:
            return None

    return tarinfo


def predict_server_tar(model_name,
                       model_tag,
                       model_path,
                       tar_path='.',
                       filemode='w',
                       compression='gz'):
    return _tar(model_name=model_name,
                model_tag=model_tag,
                model_path=model_path,
                filemode=filemode,
                compression=compression)


def _tar(model_name,
         model_tag,
         model_path,
         tar_path='.',
         filemode='w',
         compression='gz'):

    model_tag = _validate_and_prep_model_tag(model_tag)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)

    tar_path = _os.path.expandvars(tar_path)
    tar_path = _os.path.expanduser(tar_path)
    tar_path = _os.path.abspath(tar_path)
    tar_path = _os.path.normpath(tar_path)

    tar_filename = '%s-%s.tar.gz' % (model_name, model_tag)
    tar_path = _os.path.join(tar_path, tar_filename) 

    #print("")
    #print("Compressing model_path '%s' into tar_path '%s'." % (model_path, tar_path))

    with _tarfile.open(tar_path, '%s:%s' % (filemode, compression)) as tar:
        tar.add(model_path, arcname='.', filter=_filter_tar)
    
    return tar_path


def predict_server_untar(model_name,
                         model_tag,
                         model_path,
                         untar_path='.',
                         untar_filename=None,
                         filemode='w',
                         compression='gz'):

    return _untar(model_name=model_name,
                  model_tag=model_tag,
                  model_path=model_path,
                  untar_path=untar_path,
                  untar_filename=untar_filename,
                  filemode=filemode,
                  compression=compression)


def _untar(model_name,
           model_tag,
           model_path,
           untar_path='.',
           untar_filename=None,
           filemode='r',
           compression='gz'):

    model_tag = _validate_and_prep_model_tag(model_tag)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)

    untar_path = _os.path.expandvars(untar_path)
    untar_path = _os.path.expanduser(untar_path)
    untar_path = _os.path.abspath(untar_path)
    untar_path = _os.path.normpath(untar_path)
    
    #print("Untar_path: %s" % untar_path)
    if not untar_filename:
       untar_filename = '%s-%s.tar.gz' % (model_name, model_tag)

    full_untar_path = _os.path.join(untar_path, untar_filename)

    with _tarfile.open(full_untar_path, '%s:%s' % (filemode, compression)) as tar:
        tar.extractall(model_path)

    return untar_path


from werkzeug.utils import secure_filename as _secure_filename
# TODO:  LOCK THIS DOWN TO '.tar.gz'
_ALLOWED_EXTENSIONS = set(['tar', 'gz', 'tar.gz'])

def _allowed_file(filename):
# TODO: 
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in _ALLOWED_EXTENSIONS


def predict_server_tarupload(model_name,
                             model_tag,
                             model_type,
                             model_path,
                             model_runtime=None,
                             model_chip=None,
                             tar_path='.',
                             filemode='w',
                             compression='gz',
                             new_model_path=None,# defaults to ./<model-type>/<model-name>-<model-tag>/
                             upload_url=None,
                             upload_file_path=None,
                             timeout_seconds=1200):

    upload_file_path = _tar(model_name=model_name,
                            model_tag=model_tag,
                            model_path=model_path,
                            tar_path=tar_path,
                            filemode=filemode,
                            compression=compression)

    return predict_server_upload(model_name=model_name,
                                 model_tag=model_tag,
                                 model_type=model_type,
                                 model_runtime=model_runtime,
                                 model_chip=model_chip,
                                 new_model_path=new_model_path,# defaults to ./<model-type>/<model-name>-<model-tag>/
                                 upload_url=upload_url,
                                 upload_file_path=upload_file_path,
                                 timeout_seconds=timeout_seconds)


# Test:
#   cd ./models
#
#   pipeline predict-server-init --model-name=pasta --model-tag=boo --model-type=python
#   pipeline predict-server-tar --model-name=pasta --model-tag=boo --model-path=./python/pasta-boo/model
#   curl -F 'file=@pasta-boo.tar.gz' http://localhost:6970/predict-server-upload/pasta/boo/python/python/cpu/
# NOTE:  MAKE SURE YOU ADD THE TRAILING SLASH TO THE URL ABOVE!
#
# pipeline predict-server-upload --model-name=pasta --model-tag=boo --model-type=python --upload-url=http://localhost:6970/predict-server-upload/pasta/boo/python/python/cpu/ --upload-file-path=./pasta-boo.tar.gz
# NOTE:  MAKE SURE YOU ADD THE TRAILING SLASH TO THE URL ABOVE!
# 
# path: ./models/models/python/pasta-boo/
# file: ./pasta-boo.tar.gz <-- This can be anything, but usually matches <model-name>-<model-tag>.tar.gz if you're using pipeline-server-tar 
#
# Notes:  
#  * If you see weird things with 301 redirects from POST -> GET, this is likely because the user specified an `upload_url` without a trailing slash!  
#  * You must have a trailing slash!
#  * When using the `predict-server-upload` CLI command with `--upload_url` and `--upload_file_path`, the `--model_name` and `--model_tag` passed into the CLI will be ignored in favor of those specified in the URL
@app.route("/predict-server-upload/<string:model_name>/<string:model_tag>/<string:model_type>/<string:model_runtime>/<string:model_chip>/", methods=['POST'])
def predict_server_upload(model_name,
                          model_tag,
                          model_type,
                          model_runtime=None,
                          model_chip=None,
                          new_model_path=None, # defaults to ./<model-type>/<model-name>-<model-tag>/
                          upload_url=None,
                          upload_file_path=None,
                          timeout_seconds=1200):

    if upload_url and upload_file_path:
        files = {'file': open(upload_file_path, 'rb')}

        # make sure there is a trailing slash!
        upload_url = upload_url.rstrip('/')
        upload_url = upload_url + '/'
        response = _requests.post(url=upload_url,
                                  files=files,
                                  timeout=timeout_seconds)

        return response.text
    else:
        model_tag = _validate_and_prep_model_tag(model_tag)

        if not model_chip:
            model_chip = _default_model_chip

        if not model_runtime:
            model_runtime = _get_default_model_runtime(model_type)

        if not new_model_path:
            new_model_path = _os.path.normpath('%s/%s/%s-%s/model/' % (_model_base_path, model_type, model_name, model_tag))
        else:
            if _is_base64_encoded(new_model_path):
                new_model_path = _decode_base64(new_model_path)

        # TODO:  Check if path is secure using securefile or some such (saw it somewhere)
        new_model_path = _os.path.expandvars(new_model_path)
        new_model_path = _os.path.expanduser(new_model_path)
        new_model_path = _os.path.abspath(new_model_path)
        new_model_path = _os.path.normpath(new_model_path)

        if _os.path.exists(new_model_path):
            return_dict = {"status": "incomplete",
                           "error_message": "Model path '%s' already exists." % new_model_path,
                           "model_name": model_name,
                           "model_tag": model_tag,
                           "model_type": model_type,
                           "model_runtime": model_runtime,
                           "model_chip": model_chip,
                           "new_model_path": new_model_path,
                          }

            if _http_mode:
                return _jsonify(return_dict)
            else:
                return return_dict

        if _request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in _request.files:
                return_dict = {"status": "incomplete",
                               "error_message": "File is required.",
                               "model_name": model_name,
                               "model_tag": model_tag,
                               "model_type": model_type,
                               "model_runtime": model_runtime,
                               "model_chip": model_chip,
                               "new_model_path": new_model_path}

                if _http_mode:
                    return _jsonify(return_dict)
                else:
                    return return_dict

            f = _request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if f.filename == '':
                return_dict = {"status": "incomplete",
                               "error_message": "Filename is invalid/empty.",
                               "model_name": model_name,
                               "model_tag": model_tag,
                               "model_type": model_type,
                               "model_runtime": model_runtime,
                               "model_chip": model_chip,
                               "new_model_path": new_model_path}
    
                if _http_mode:
                    return _jsonify(return_dict)
                else:
                    return return_dict

            if f and _allowed_file(f.filename):
                filename = _secure_filename(f.filename)
                # TODO:  Support subdirectories after /uploads
                if not _os.path.exists(new_model_path):
                    _os.makedirs(new_model_path)
                full_path = _os.path.join(new_model_path, filename)
                print('Writing to "%s"' % full_path)
                f.save(full_path)
    
                # TODO:  Return the results of the untar
                _untar(model_name=model_name, 
                       model_tag=model_tag,
                       model_path='%s/..' % full_path,
                       untar_path=new_model_path,
                       untar_filename=filename)

                return_dict = {"status": "complete",
                               "model_name": model_name,
                               "model_tag": model_tag,
                               "model_type": model_type,
                               "model_runtime": model_runtime,
                               "model_chip": model_chip,
                               "new_model_path": new_model_path}

                if _http_mode:
                    return _jsonify(return_dict)
                else:
                    return return_dict

        return_dict = {"status": "incomplete",
                       "error_message": "POST method is required.",
                       "model_name": model_name,
                       "model_tag": model_tag,
                       "model_type": model_type,
                       "model_runtime": model_runtime,
                       "model_chip": model_chip,
                       "new_model_path": new_model_path}

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict


# ie. http://localhost:6970/predict-kube-start/mnist/a/
@app.route("/predict-kube-start/<string:model_name>/<string:model_tag>/", methods=['GET'])
def predict_kube_start(model_name,
                       model_tag,
                       model_chip=None,
                       namespace=None,
                       stream_logger_url=None,
                       stream_logger_topic=None,
                       stream_input_url=None,
                       stream_input_topic=None,
                       stream_output_url=None,
                       stream_output_topic=None,
                       memory_limit='2Gi',
                       core_limit='1000m',
                       target_core_util_percentage='50',
                       min_replicas='1',
                       max_replicas='2',
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       image_registry_base_tag=None,
                       image_registry_base_chip=None,
                       pipeline_templates_path=None,
                       timeout_seconds=1200):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not model_chip:
        model_chip = _default_model_chip

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    rendered_yamls = _create_predict_kube_Kubernetes_yaml(
                                      model_name=model_name,
                                      model_tag=model_tag,
                                      model_chip=model_chip,        
                                      namespace=namespace,
                                      stream_logger_url=stream_logger_url,
                                      stream_logger_topic=stream_logger_topic,
                                      stream_input_url=stream_input_url,
                                      stream_input_topic=stream_input_topic,
                                      stream_output_url=stream_output_url,
                                      stream_output_topic=stream_output_topic,
                                      memory_limit=memory_limit,
                                      core_limit=core_limit,
                                      target_core_util_percentage=target_core_util_percentage,
                                      min_replicas=min_replicas,
                                      max_replicas=max_replicas,
                                      image_registry_url=image_registry_url,
                                      image_registry_repo=image_registry_repo,
                                      image_registry_namespace=image_registry_namespace,
                                      image_registry_base_tag=image_registry_base_tag,
                                      image_registry_base_chip=image_registry_base_chip,
                                      pipeline_templates_path=pipeline_templates_path)

    for rendered_yaml in rendered_yamls:
        # For now, only handle '-deploy' and '-svc' and '-ingress' (not autoscale or routerules)
        if ('-stream-deploy' not in rendered_yaml and '-stream-svc' not in rendered_yaml) and ('-deploy' in rendered_yaml or '-svc' in rendered_yaml or '-ingress' in rendered_yaml):
            _istio_apply(yaml_path=rendered_yaml,
                         namespace=namespace)

    endpoint_url = _get_model_kube_endpoint(model_name=model_name, 
                                            namespace=namespace,
                                            image_registry_namespace=image_registry_namespace)

    endpoint_url = endpoint_url.rstrip('/')

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "endpoint_url": endpoint_url,
                   "comments": "The `endpoint_url` is an internal IP to the ingress controller. No traffic will be allowed until you enable traffic to this endpoint using `pipeline predict-kube-route`. This extra routing step is intentional."}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


@app.route("/stream-kube-start/<string:model_name>/<string:model_tag>/", methods=['GET'])
def stream_kube_start(model_name,
                      model_tag,
                      model_chip=None,
                      stream_logger_topic=None,
                      stream_input_topic=None,
                      stream_output_topic=None,
                      stream_enable_mqtt=True,
                      stream_enable_kafka_rest_api=True,
                      namespace=None,
                      image_registry_url=None,
                      image_registry_repo=None,
                      image_registry_namespace=None,
                      image_registry_base_tag=None,
                      image_registry_base_chip=None,
                      pipeline_templates_path=None,
                      timeout_seconds=1200):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_chip:
        model_chip = _default_model_chip

    if not namespace:
        namespace = _default_namespace

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    if not stream_logger_topic:
        stream_logger_topic = '%s-%s-logger' % (model_name, model_tag)

    if not stream_input_topic:
        stream_input_topic = '%s-%s-input' % (model_name, model_tag)

    if not stream_output_topic:
        stream_output_topic = '%s-%s-output' % (model_name, model_tag)

    rendered_yamls = _create_stream_kube_Kubernetes_yaml(model_name=model_name,
                                                         model_tag=model_tag,
                                                         model_chip=model_chip,
                                                         stream_logger_topic=stream_logger_topic,
                                                         stream_input_topic=stream_input_topic,
                                                         stream_output_topic=stream_output_topic,
                                                         stream_enable_mqtt=stream_enable_mqtt,
                                                         stream_enable_kafka_rest_api=stream_enable_kafka_rest_api,
                                                         namespace=namespace,
                                                         image_registry_url=image_registry_url,
                                                         image_registry_repo=image_registry_repo,
                                                         image_registry_namespace=image_registry_namespace,
                                                         image_registry_base_tag=image_registry_base_tag,
                                                         image_registry_base_chip=image_registry_base_chip,
                                                         pipeline_templates_path=pipeline_templates_path)

    for rendered_yaml in rendered_yamls:
        _kube_apply(yaml_path=rendered_yaml,
                    namespace=namespace)

    service_name = "%s-%s-%s" % (image_registry_namespace, model_name, model_tag)
    stream_url = _get_cluster_service(service_name=service_name,
                                      namespace=namespace)

    stream_url = stream_url.rstrip('/')

    stream_url = 'http://%s/stream/%s/%s' % (stream_url, model_name, model_tag)

    endpoint_url = '%s/topics' % stream_url

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "model_chip": model_chip,
                   "stream_url": stream_url,
                   "stream_logger_topic": stream_logger_topic,
                   "stream_input_topic": stream_input_topic,
                   "stream_output_topic": stream_output_topic,
                   "endpoint_url": endpoint_url 
                  }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def stream_http_describe(stream_url,
                         stream_topic=None,
                         namespace=None,
                         image_registry_namespace=None,
                         timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    stream_url = stream_url.rstrip('/')
   
    if stream_topic:
        endpoint_url = '%s/topics/%s' % (stream_url, stream_topic)
        endpoint_url = endpoint_url.rstrip('/')
        print("")
        print("Describing stream_url '%s' and stream_topic '%s' at endpoint_url '%s'." % (stream_url, stream_topic, endpoint_url))
    else:
        endpoint_url = '%s/topics' % stream_url
        endpoint_url = endpoint_url.rstrip('/')
        print("")
        print("Describing stream_url '%s' at endpoint_url '%s'." % (stream_url, endpoint_url))

    response = _requests.get(url=endpoint_url,
                             timeout=timeout_seconds)

    return_dict = {"status": "complete",
                   "stream_url": stream_url,
                   "endpoint_url": endpoint_url,
                   "stream_topic": stream_topic,
                   "response": response.text
                  }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def stream_kube_describe(model_name,
                         model_tag,
                         stream_topic=None,
                         namespace=None,
                         image_registry_namespace=None,
                         timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    service_name = "%s-%s-%s" % (image_registry_namespace, model_name, model_tag)
    stream_url = _get_cluster_service(service_name=service_name,
                                      namespace=namespace)

    stream_url = 'http://%s/stream/%s/%s' % (stream_url, model_name, model_tag)

    # TODO:  The following method returns json.  
    #        Enrich this json response with `model_name` and `model_tag`
    return stream_http_describe(stream_url=stream_url,
                                stream_topic=stream_topic,
                                namespace=namespace,
                                image_registry_namespace=image_registry_namespace,
                                timeout_seconds=timeout_seconds)


def stream_http_consume(stream_url,
                        stream_topic,
                        stream_consumer_name=None,
                        stream_offset=None,
                        namespace=None,
                        image_registry_namespace=None,
                        timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not stream_offset:
        stream_offset = "earliest"

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    if not stream_consumer_name:
        stream_consumer_name = '%s' % stream_topic

    stream_url = stream_url.rstrip('/')

    endpoint_url = '%s/consumers/%s' % (stream_url, stream_consumer_name)
    endpoint_url = endpoint_url.rstrip('/')

    print("")
    print("Consuming stream topic '%s' at '%s' as consumer id '%s'." % (stream_topic, endpoint_url, stream_consumer_name))
    print("")

    # Register consumer
    content_type_headers = {"Content-Type": "application/vnd.kafka.json.v2+json"}
    accept_headers = {"Accept": "application/vnd.kafka.json.v2+json"}

    body = '{"name": "%s", "format": "json", "auto.offset.reset": "%s"}' % (stream_consumer_name, stream_offset)
    print(endpoint_url)
    response = _requests.post(url=endpoint_url,
                              headers=content_type_headers,
                              data=body.encode('utf-8'),
                              timeout=timeout_seconds)

    if response.text:
        print("")
        _pprint(response.text)


    # Subscribe consumer to topic
    body = '{"topics": ["%s"]}' % stream_topic
    endpoint_url = '%s/consumers/%s/instances/%s/subscription' % (stream_url, stream_consumer_name, stream_consumer_name)
    print(endpoint_url)
    response = _requests.post(url=endpoint_url,
                              headers=content_type_headers,
                              data=body.encode('utf-8'),
                              timeout=timeout_seconds)

    if response.text:
        print("")
        _pprint(response.text)

    # Get consumer topic subscription
    endpoint_url = '%s/consumers/%s/instances/%s/subscription' % (stream_url, stream_consumer_name, stream_consumer_name)
    print(endpoint_url)
    response = _requests.get(url=endpoint_url,
                             headers=accept_headers,
                             timeout=timeout_seconds)

    if response.text:
        print("")
        _pprint(response.text)

    # Consume messages from topic
    endpoint_url = '%s/consumers/%s/instances/%s/records' % (stream_url, stream_consumer_name, stream_consumer_name)
    print(endpoint_url)
    response = _requests.get(url=endpoint_url,
                             headers=accept_headers,
                             timeout=timeout_seconds)

    messages = response.text

    if response.text:
        print("")
        _pprint(response.text)

    # Remove consumer subscription from topic
    endpoint_url = '%s/consumers/%s/instances/%s' % (stream_url, stream_consumer_name, stream_consumer_name)
    endpoint_url = endpoint_url.rstrip('/')
    print(endpoint_url)
    response = _requests.delete(url=endpoint_url,
                                headers=content_type_headers,
                                timeout=timeout_seconds)

    if response.text:
        print("")
        _pprint(response.text)

    return messages


@app.route("/stream-kube-consume/<string:model_name>/<string:model_tag>/<string:stream_topic>/", methods=['GET'])
def stream_kube_consume(model_name,
                        model_tag,
                        stream_topic,
                        stream_consumer_name=None,
                        stream_offset=None,
                        namespace=None,
                        image_registry_namespace=None,
                        timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not stream_offset:
        stream_offset = "earliest"

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    service_name = "%s-%s-%s" % (image_registry_namespace, model_name, model_tag)
    stream_url = _get_cluster_service(service_name=service_name,
                                      namespace=namespace)

    stream_url = stream_url.rstrip('/')

    stream_url = 'http://%s/stream/%s/%s' % (stream_url, model_name, model_tag)

    if not stream_consumer_name:
        stream_consumer_name = '%s-%s-%s' % (model_name, model_tag, stream_topic)

    stream_http_consume(stream_url=stream_url,
                        stream_topic=stream_topic,
                        stream_consumer_name=stream_consumer_name,
                        stream_offset=stream_offset,
                        namespace=namespace,
                        image_registry_namespace=image_registry_namespace,
                        timeout_seconds=timeout_seconds)


def predict_stream_test(model_name,
                        model_tag,
                        test_request_path,
                        stream_input_topic=None,
                        namespace=None,
                        image_registry_namespace=None,
                        test_request_concurrency=1,
                        test_request_mime_type='application/json',
                        test_response_mime_type='application/json',
                        test_request_timeout_seconds=1200):

    stream_kube_produce(model_name=model_name,
                        model_tag=model_tag,
                        test_request_path=test_request_path,
                        stream_input_topic=stream_input_topic,
                        namespace=namespace,
                        image_registry_namespace=image_registry_namespace,
                        test_request_concurrency=test_request_concurrency,
                        test_request_mime_type=test_request_mime_type,
                        test_response_mime_type=test_response_mime_type,
                        test_request_timeout_seconds=test_request_timeout_seconds)


def stream_http_produce(endpoint_url,
                        test_request_path,
                        test_request_concurrency=1,
                        test_request_mime_type='application/json',
                        test_response_mime_type='application/json',
                        test_request_timeout_seconds=1200):

    endpoint_url = endpoint_url.rstrip('/')

    print("")
    print("Producing messages for endpoint_url '%s'." % endpoint_url)
    print("")

    accept_and_content_type_headers = {"Accept": "application/vnd.kafka.v2+json", "Content-Type": "application/vnd.kafka.json.v2+json"}

    with open(test_request_path, 'rt') as fh:
        model_input_text = fh.read()

    body = '{"records": [{"value":%s}]}' % model_input_text

    response = _requests.post(url=endpoint_url,
                              headers=accept_and_content_type_headers,
                              data=body.encode('utf-8'),
                              timeout=test_request_timeout_seconds)

    return_dict = {"status": "complete",
                   "endpoint_url": endpoint_url,
                   "headers": accept_and_content_type_headers,
                   "timeout": test_request_timeout_seconds,
                   "test_request_path": test_request_path,
                   "test_request_concurrency": test_request_concurrency,
                   "body": body,
                   "response": response,
                  }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def stream_kube_produce(model_name,
                        model_tag,
                        test_request_path,
                        stream_topic=None,
                        namespace=None,
                        image_registry_namespace=None,
                        test_request_concurrency=1,
                        test_request_mime_type='application/json',
                        test_response_mime_type='application/json',
                        test_request_timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    if not stream_topic:
        stream_topic = '%s-%s-input' % (model_name, model_tag)

    service_name = "%s-%s-%s" % (image_registry_namespace, model_name, model_tag)

    stream_url = _get_cluster_service(service_name=service_name,
                                      namespace=namespace)

    stream_url = stream_url.rstrip('/')

    stream_url = 'http://%s/stream/%s/%s' % (stream_url, model_name, model_tag)

    stream_url = stream_url.rstrip('/')

    endpoint_url = '%s/topics/%s' % (stream_url, stream_topic)

    endpoint_url = endpoint_url.rstrip('/')

    # TODO: Enrich return_dict with model_name and model_tag and stream_url and stream_topic
    # TODO:  The following method returns json.
    #        Enrich this json response with `model_name`, `model_tag`, `stream_url`, and `stream_topic`
    return stream_http_produce(endpoint_url=endpoint_url,
                               test_request_path=test_request_path,
                               test_request_concurrency=test_request_concurrency,
                               test_request_mime_type=test_request_mime_type,
                               test_response_mime_type=test_response_mime_type,
                               test_request_timeout_seconds=test_request_timeout_seconds)


def _optimize_predict(model_name,
                      model_tag,
                      model_type,
                      model_runtime,
                      model_chip,
                      model_path,
                      input_host_path,
                      output_host_path,
                      optimize_type,
                      optimize_params):

    model_tag = _validate_and_prep_model_tag(model_tag)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)


def _optimize_train(
             model_name,
             model_tag,
             model_type,
             model_runtime,
             model_chip,
             model_path,
             input_host_path,
             output_host_path,
             optimize_type,
             optimize_params):

    model_tag = _validate_and_prep_model_tag(model_tag)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)


def predict_server_test(endpoint_url,
                        test_request_path,
                        test_request_concurrency=1,
                        test_request_mime_type='application/json',
                        test_response_mime_type='application/json',
                        test_request_timeout_seconds=1200):

    from concurrent.futures import ThreadPoolExecutor, as_completed

    endpoint_url = endpoint_url.rstrip('/')

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_predict_http_test(endpoint_url=endpoint_url,
                                               test_request_path=test_request_path,
                                               test_request_mime_type=test_request_mime_type,
                                               test_response_mime_type=test_response_mime_type,
                                               test_request_timeout_seconds=test_request_timeout_seconds))


def predict_kube_test(model_name,
                      test_request_path,
                      image_registry_namespace=None,
                      namespace=None,
                      test_request_concurrency=1,
                      test_request_mime_type='application/json',
                      test_response_mime_type='application/json',
                      test_request_timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if _is_base64_encoded(test_request_path):
        test_request_path = _decode_base64(test_request_path)

    endpoint_url = _get_model_kube_endpoint(model_name=model_name,
                                            namespace=namespace,
                                            image_registry_namespace=image_registry_namespace)

    endpoint_url = endpoint_url.rstrip('/')

    # This is required to get around the limitation of istio managing only 1 load balancer
    # See here for more details: https://github.com/istio/istio/issues/1752
    # If this gets fixed, we can relax the -routerules.yaml and -ingress.yaml in the templates dir
    #   (we'll no longer need to scope by model_name)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_predict_http_test(endpoint_url=endpoint_url,
                                               test_request_path=test_request_path,
                                               test_request_mime_type=test_request_mime_type,
                                               test_response_mime_type=test_response_mime_type,
                                               test_request_timeout_seconds=test_request_timeout_seconds))
    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "endpoint_url": endpoint_url,
                   "test_request_path": test_request_path,
                   "test_request_concurrency": test_request_concurrency}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_http_test(endpoint_url,
                      test_request_path,
                      test_request_concurrency=1,
                      test_request_mime_type='application/json',
                      test_response_mime_type='application/json',
                      test_request_timeout_seconds=1200):

    from concurrent.futures import ThreadPoolExecutor, as_completed

    endpoint_url = endpoint_url.rstrip('/')

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_predict_http_test(endpoint_url=endpoint_url,
                                               test_request_path=test_request_path,
                                               test_request_mime_type=test_request_mime_type,
                                               test_response_mime_type=test_response_mime_type,
                                               test_request_timeout_seconds=test_request_timeout_seconds))


def _predict_http_test(endpoint_url,
                       test_request_path,
                       test_request_mime_type='application/json',
                       test_response_mime_type='application/json',
                       test_request_timeout_seconds=1200):

    test_request_path = _os.path.expandvars(test_request_path)
    test_request_path = _os.path.expanduser(test_request_path)
    test_request_path = _os.path.abspath(test_request_path)
    test_request_path = _os.path.normpath(test_request_path)

    full_endpoint_url = endpoint_url.rstrip('/')
    print("")
    print("Predicting with file '%s' using '%s'" % (test_request_path, full_endpoint_url))
    print("")

    with open(test_request_path, 'rb') as fh:
        model_input_binary = fh.read()

    headers = {'Content-type': test_request_mime_type, 'Accept': test_response_mime_type} 
    from datetime import datetime 

    begin_time = datetime.now()
    response = _requests.post(url=full_endpoint_url, 
                              headers=headers, 
                              data=model_input_binary, 
                              timeout=test_request_timeout_seconds)
    end_time = datetime.now()

    if response.text:
        print("")
        _pprint(response.text)

    if response.status_code == _requests.codes.ok:
        print("")
        print("Success!")
    else:
        print(response.status_code)

    total_time = end_time - begin_time
    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return_dict = {"status": "complete",
                   "endpoint_url": full_endpoint_url,
                   "test_request_path": test_request_path}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_sage_test(model_name,
                      test_request_path,
                      image_registry_namespace=None,
                      test_request_concurrency=1,
                      test_request_mime_type='application/json',
                      test_response_mime_type='application/json',
                      test_request_timeout_seconds=1200):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_test_single_prediction_sage(
                                          model_name=model_name,
                                          test_request_path=test_request_path,
                                          image_registry_namespace=image_registry_namespace,
                                          test_request_mime_type=test_request_mime_type,
                                          test_response_mime_type=test_response_mime_type,
                                          test_request_timeout_seconds=test_request_timeout_seconds))


def _test_single_prediction_sage(model_name,
                                 test_request_path,
                                 image_registry_namespace,
                                 test_request_mime_type='application/json',
                                 test_response_mime_type='application/json',
                                 test_request_timeout_seconds=1200):

    test_request_path = _os.path.expandvars(test_request_path)
    test_request_path = _os.path.expanduser(test_request_path)
    test_request_path = _os.path.abspath(test_request_path)
    test_request_path = _os.path.normpath(test_request_path)

    print("")
    print("Predicting with file '%s' using endpoint '%s-%s'" % (test_request_path, image_registry_namespace, model_name))

    with open(test_request_path, 'rb') as fh:
        model_input_binary = fh.read()

    from datetime import datetime

    begin_time = datetime.now()
    body = model_input_binary.decode('utf-8')

    sagemaker_client = _boto3.client('runtime.sagemaker')
    response = sagemaker_client.invoke_endpoint(
                                          EndpointName='%s-%s' % (image_registry_namespace, model_name),
                                          Body=model_input_binary,
                                          ContentType=test_request_mime_type,
                                          Accept=test_response_mime_type)
    end_time = datetime.now()

    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("")
        print("Variant: '%s'" % response['InvokedProductionVariant'])
        print("")
        _pprint(response['Body'].read().decode('utf-8'))
   
        print("")
    else:
        return 

    total_time = end_time - begin_time
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")


def predict_sage_stop(model_name,
                      image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    from datetime import datetime

    sagemaker_client = _boto3.client('sagemaker')

    # Remove Endpoint
    try:
        begin_time = datetime.now()
        response = sagemaker_client.delete_endpoint(EndpointName='%s-%s' % (image_registry_namespace, model_name))
        end_time = datetime.now()

#        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        total_time = end_time - begin_time
        print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
        print("")
    except _ClientError as ce:
        pass

    print("Stopped endpoint '%s-%s'" % (image_registry_namespace, model_name))

    # Remove Endpoint Config
    try:
        begin_time = datetime.now()
        response = sagemaker_client.delete_endpoint_config(EndpointConfigName='%s-%s' % (image_registry_namespace, model_name))
        end_time = datetime.now()

#        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        total_time = end_time - begin_time
        print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
        print("")
    except _ClientError as ce:
        pass

    print("Stopped endpoint config '%s-%s'" % (image_registry_namespace, model_name))
    print("")


def predict_sage_describe(model_name,
                          image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    from datetime import datetime

    begin_time = datetime.now()
    sagemaker_client = _boto3.client('sagemaker')
    response = sagemaker_client.describe_endpoint(EndpointName='%s-%s' % (image_registry_namespace, model_name))
    end_time = datetime.now()

    total_time = end_time - begin_time
    model_region = 'UNKNOWN_REGION'
    print("")
    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        status = response['EndpointStatus']
        print("Endpoint Status: '%s'" % status)

        endpoint_arn = response['EndpointArn']
        print("")
        print("EndpointArn: '%s'" % endpoint_arn)
        model_region = endpoint_arn.split(':')[3]
        endpoint_url = _get_sage_endpoint_url(model_name=model_name,
                                              model_region=model_region,
                                              image_registry_namespace=image_registry_namespace)
        print("Endpoint Url: '%s'" % endpoint_url)
        print("")
        print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
        print("")


#def train_kube_status():
#    _cluster_status()


#def predict_kube_status():
#    _cluster_status()


def _cluster_status():
    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    print("")
    print("Versions")
    print("********")
    version()

    print("")
    print("Nodes")
    print("*****")
    _get_all_nodes()

    _environment_volumes()

    print("")
    print("Environment Resources")
    print("*********************")        
    _environment_resources()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_service_for_all_namespaces(watch=False,
                                                                 pretty=True)
        services = response.items
        for svc in services:
            _service_resources(service_name=svc.metadata.name)

    print("")
    print("Service Descriptions")
    print("********************")
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_service_for_all_namespaces(watch=False,
                                                                 pretty=True)
        services = response.items
        for svc in services:
            _service_describe(service_name=svc.metadata.name)

    print("")
    print("DNS Internal (Public)")
    print("*********************")
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_service_for_all_namespaces(watch=False, 
                                                                 pretty=True)
        services = response.items
        for svc in services:
            ingress = 'Not public' 
            if svc.status.load_balancer.ingress and len(svc.status.load_balancer.ingress) > 0:
                if (svc.status.load_balancer.ingress[0].hostname):
                    ingress = svc.status.load_balancer.ingress[0].hostname
                if (svc.status.load_balancer.ingress[0].ip):
                    ingress = svc.status.load_balancer.ingress[0].ip               
            print("%s (%s)" % (svc.metadata.name, ingress))

    print("")
    print("Deployments")
    print("***********")
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                          pretty=True)
        deployments = response.items
        for deployment in deployments:
            print("%s (Available Replicas: %s)" % (deployment.metadata.name, deployment.status.available_replicas))

    print("")
    print("Pods")
    print("****")
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                             pretty=True)
        pods = response.items
        for pod in pods:
            print("%s (%s)" % (pod.metadata.name, pod.status.phase))

    print("")
    print("Note:  If you are using Minikube, use 'minikube service list'.")
    print("")

    predict_kube_describe()


def _get_pod_by_service_name(service_name):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    found = False 
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, pretty=True)
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                found = True
                break
    if found:
        return pod
    else:
        return None


def _get_svc_by_service_name(service_name):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    found = False
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_service_for_all_namespaces(watch=False, 
                                                                 pretty=True)
        services = response.items
        for svc in services:
            if service_name in svc.metadata.name:
                found = True
                break
    if found:
        return svc 
    else:
        return None


def _get_all_available_services():

    available_services = list(_kube_deploy_registry.keys())
    available_services.sort()
    for service in available_services:
        print(service)


def _get_all_nodes():

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_node(watch=False, pretty=True)
        nodes = response.items
        for node in nodes:
            print("%s" % node.metadata.labels['kubernetes.io/hostname'])


def predict_kube_shell(model_name,
                       model_tag,
                       namespace=None,
                       image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    container_name = '%s-%s' % (image_registry_namespace, model_name)

    _service_shell(service_name=service_name,
                   container_name=container_name,
                   namespace=namespace)


def _service_shell(service_name,
                   container_name=None,
                   namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                             pretty=True)
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                break
        print("")
        print("Connecting to '%s'" % pod.metadata.name)      
        print("")

        if container_name:
            cmd = "kubectl exec -it %s -c %s bash" % (pod.metadata.name, container_name)
        else:
            cmd = "kubectl exec -it %s bash" % pod.metadata.name

        _subprocess.call(cmd, shell=True)

        print("")


def predict_kube_logs(model_name,
                      model_tag,
                      namespace=None,
                      image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    container_name = '%s-%s' % (image_registry_namespace, model_name)

    _service_logs(service_name=service_name,
                  container_name=container_name,
                  namespace=namespace)


def _service_logs(service_name,
                  container_name=None,
                  namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                             pretty=True)
        found = False
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                found = True
                break
        if found:
            print("")
            print("Tailing logs on '%s'." % pod.metadata.name)
            print("")
            if container_name:
                cmd = "kubectl logs -f %s -c %s --namespace=%s" % (pod.metadata.name, container_name, namespace)
            else:
                cmd = "kubectl logs -f %s --namespace=%s" % (pod.metadata.name, namespace)
            print(cmd)
            print("")      
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("")


def _service_describe(service_name,
                      namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False,
                                                             pretty=True)
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                break
        print("")
        print("Connecting to '%s'" % pod.metadata.name)
        print("")
        _subprocess.call("kubectl describe pod %s --namespace=%s" % (pod.metadata.name, namespace), shell=True)
    print("")

@app.route("/predict-kube-scale/<string:model_name>/<string:model_tag>/<int:replicas>/", methods=['GET'])
def predict_kube_scale(model_name,
                       model_tag,
                       replicas,
                       namespace=None,
                       image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_scale(service_name=service_name,
                   replicas=replicas,
                   namespace=namespace)

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "replicas": replicas}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


# TODO:  See https://github.com/istio/istio/tree/master/samples/helloworld
#             for more details on how istio + autoscaling work
@app.route("/predict-kube-autoscale/<string:model_name>/<string:model_tag>/<int:cpu_percent>/<int:min_replicas>/<int:max_replicas>/", methods=['GET'])
def predict_kube_autoscale(model_name,
                           model_tag,
                           cpu_percent,
                           min_replicas,
                           max_replicas,
                           namespace=None,
                           image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    # TODO:  make sure resources/requests/cpu has been set to something in the yaml
    #        ie. istioctl kube-inject -f helloworld.yaml -o helloworld-istio.yaml
    #        then manually edit as follows:
    #
    #  resources:
    #    limits:
    #      cpu: 1000m
    #    requests:
    #      cpu: 100m

    cmd = "kubectl autoscale deployment %s-%s-%s --cpu-percent=%s --min=%s --max=%s --namespace=%s" % (image_registry_namespace, model_name, model_tag, cpu_percent, min_replicas, max_replicas, namespace)
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    cmd = "kubectl get hpa"
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "cpu_percent": cpu_percent,
                   "min_replcias": min_replicas,
                   "max_replicas": max_replicas}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def spark_kube_scale(replicas,
                     namespace=None):

    if not namespace:
        namespace = _default_namespace

    service_name = 'spark-worker'

    _service_scale(service_name=service_name,
                   replicas=replicas,
                   namespace=namespace)

    return_dict = {"status": "complete",
                   "service": "spark-worker-2-1-0",
                   "replicas": replicas,
                  }


def _service_scale(service_name,
                   replicas,
                   namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    # TODO:  Filter by given `namespace`
    #        I believe there is a new method list_deployment_for_namespace() or some such
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False, 
                                                                          pretty=True)
        found = False
        deployments = response.items
        for deploy in deployments:
            if service_name in deploy.metadata.name:
                found = True
                break
        if found:
            print("")
            print("Scaling service '%s' to '%s' replicas." % (deploy.metadata.name, replicas))
            print("")
            cmd = "kubectl scale deploy %s --replicas=%s --namespace=%s" % (deploy.metadata.name, replicas, namespace)
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("") 


def _environment_volumes():

    print("")
    print("Volumes")
    print("*******")
    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_persistent_volume(watch=False,
                                                        pretty=True)
        claims = response.items
        for claim in claims:
            print("%s" % (claim.metadata.name))

    print("")
    print("Volume Claims")
    print("*************")
    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_persistent_volume_claim_for_all_namespaces(watch=False,
                                                                                 pretty=True)
        claims = response.items
        for claim in claims:
            print("%s" % (claim.metadata.name))


def _get_deploy_yamls(service_name):
    try:
        (deploy_yamls, dependencies) = _kube_deploy_registry[service_name]
    except:
        dependencies = []
        deploy_yamls = []

    if len(dependencies) > 0:
        for dependency in dependencies:
            deploy_yamls = deploy_yamls + _get_deploy_yamls(service_name=dependency)

    return deploy_yamls 


def _get_svc_yamls(service_name):
    try:
        (svc_yamls, dependencies) = _kube_svc_registry[service_name]
    except:
        dependencies = []
        svc_yamls = []
   
    if len(dependencies) > 0:
        for dependency_service_name in dependencies:
            svc_yamls = svc_yamls + _get_svc_yamls(service_name=dependency_service_name)

    return svc_yamls


def _kube_apply(yaml_path,
                namespace=None):

    if not namespace:
        namespace = _default_namespace

    yaml_path = _os.path.normpath(yaml_path)

    cmd = "kubectl apply --namespace %s -f %s" % (namespace, yaml_path)
    _kube(cmd=cmd)


def _kube_create(yaml_path,
                 namespace=None):

    if not namespace:
        namespace = _default_namespace

    yaml_path = _os.path.normpath(yaml_path)

    cmd = "kubectl create --namespace %s -f %s --save-config --record" % (namespace, yaml_path)
    _kube(cmd=cmd)


def _kube_delete(yaml_path,
                 namespace=None):

    yaml_path = _os.path.normpath(yaml_path)

    if not namespace:
        namespace = _default_namespace

    cmd = "kubectl delete --namespace %s -f %s" % (namespace, yaml_path)
    _kube(cmd=cmd) 


def _kube( cmd):
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")


def predict_kube_describe(model_name=None,
                          namespace=None,
                          image_registry_namespace=None):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if model_name:
        print("")
        print("Endpoint")
        print(predict_kube_endpoint(model_name=model_name,
                                    namespace=namespace,
                                    image_registry_namespace=image_registry_namespace))
    else:
        print("")
        print("Endpoints")
        print(predict_kube_endpoints(namespace=namespace,
                                     image_registry_namespace=image_registry_namespace))

    print("")
    print("Routes")
    print(predict_kube_routes(model_name=model_name,
                              namespace=namespace,
                              image_registry_namespace=image_registry_namespace))


def predict_kube_routes(model_name=None,
                        namespace=None,
                        image_registry_namespace=None):

    route_context = ''
    if model_name:
        if not image_registry_namespace:
            image_registry_namespace = _default_image_registry_predict_namespace
        route_context = '%s-%s' % (image_registry_namespace, model_name)

    if not namespace:
        namespace = _default_namespace

    print("")
    print("Traffic Ingress")
    print("***************")
    cmd = "kubectl get ingress -o wide --namespace=%s" % namespace
    _subprocess.call(cmd, shell=True)

    # TODO:  if model_name is passed in, filter by model_name
    print("")
    print("Traffic Route Rules")
    print("********************")
    cmd = "kubectl get routerules -o wide --namespace=%s" % namespace
    _subprocess.call(cmd, shell=True)

    print("")
    cmd = "kubectl describe routerules --namespace=%s" % namespace
    _subprocess.call(cmd, shell=True)
    print("")


def _get_model_kube_endpoint(model_name,
                             namespace,
                             image_registry_namespace):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    ingress_name = '%s-%s' % (image_registry_namespace, model_name)
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        ingress = kubeclient_v1_beta1.read_namespaced_ingress(name=ingress_name, 
                                                              namespace=namespace)

        endpoint = None
        if ingress.status.load_balancer.ingress and len(ingress.status.load_balancer.ingress) > 0:
            if (ingress.status.load_balancer.ingress[0].hostname):
                endpoint = ingress.status.load_balancer.ingress[0].hostname
            if (ingress.status.load_balancer.ingress[0].ip):
                endpoint = ingress.status.load_balancer.ingress[0].ip

        if not endpoint:
            try:
                istio_ingress_nodeport = _get_istio_ingress_nodeport()
            except Exception:
                istio_ingress_nodeport = '<ingress-controller-nodeport>'
    
            try:
                istio_ingress_ip = _get_istio_ingress_ip()
            except Exception:
                istio_ingress_ip = '<ingress-controller-ip>'

            endpoint = '%s:%s' % (istio_ingress_ip, istio_ingress_nodeport)

        path = ingress.spec.rules[0].http.paths[0].path

        endpoint = 'http://%s%s' % (endpoint, path)
        endpoint = endpoint.replace(".*", "invocations")

        return endpoint


def _get_istio_ingress_nodeport():
    cmd = "kubectl get svc -n istio-system istio-ingress -o jsonpath='{.spec.ports[0].nodePort}'"
    istio_ingress_nodeport_bytes = _subprocess.check_output(cmd, shell=True)
    return istio_ingress_nodeport_bytes.decode('utf-8') 


def _get_istio_ingress_ip():
    cmd = "kubectl -n istio-system get po -l istio=ingress -o jsonpath='{.items[0].status.hostIP}'"
    istio_ingress_nodeport_bytes = _subprocess.check_output(cmd, shell=True)
    return istio_ingress_nodeport_bytes.decode('utf-8')


# TODO: Filter ingresses using image_registry_namespace ('predict-')
def _get_all_model_endpoints(namespace,
                             image_registry_namespace):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    endpoint_list = []
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        ingresses = kubeclient_v1_beta1.list_namespaced_ingress(namespace=namespace)
        for ingress in ingresses.items:
            endpoint = None
            if ingress.status.load_balancer.ingress and len(ingress.status.load_balancer.ingress) > 0:
                if (ingress.status.load_balancer.ingress[0].hostname):
                    endpoint = ingress.status.load_balancer.ingress[0].hostname
                if (ingress.status.load_balancer.ingress[0].ip):
                    endpoint = ingress.status.load_balancer.ingress[0].ip

            if not endpoint:
                try:
                    istio_ingress_nodeport = _get_istio_ingress_nodeport()
                except Exception:
                    istio_ingress_nodeport = '<ingress-controller-nodeport>'

                try:
                    istio_ingress_ip = _get_istio_ingress_ip()
                except Exception:
                    istio_ingress_ip = '<ingress-controller-ip>'

                endpoint = '%s:%s' % (istio_ingress_ip, istio_ingress_nodeport)

            path = ingress.spec.rules[0].http.paths[0].path
            endpoint = 'http://%s%s' % (endpoint, path)
            endpoint = endpoint.replace(".*", "invocations")
            endpoint_list += [endpoint]

    return endpoint_list


def _get_cluster_service(service_name,
                         namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    endpoint = None
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        service = kubeclient_v1.read_namespaced_service(name=service_name,
                                                        namespace=namespace)

        # TODO: What about port? defaults to 80 for ingress controller, but what about non-ingress-controller?
        if service.status.load_balancer.ingress and len(service.status.load_balancer.ingress) > 0:
            if (service.status.load_balancer.ingress[0].hostname):
                endpoint = service.status.load_balancer.ingress[0].hostname
            if (service.status.load_balancer.ingress[0].ip):
                endpoint = service.status.load_balancer.ingress[0].ip

        if not endpoint:
            try:
                istio_ingress_nodeport = _get_istio_ingress_nodeport()
            except Exception:
                istio_ingress_nodeport = '<ingress-controller-nodeport>'

            try:
                istio_ingress_ip = _get_istio_ingress_ip()
            except Exception:
                istio_ingress_ip = '<ingress-controller-ip>'

            endpoint = '%s:%s' % (istio_ingress_ip, istio_ingress_nodeport)

    return endpoint


def _istio_apply(yaml_path,
                 namespace=None):

    if not namespace:
        namespace = _default_namespace

    yaml_path = _os.path.normpath(yaml_path)

    cmd = "istioctl kube-inject -f %s" % yaml_path
    print("")
    print("Running '%s'." % cmd)
    print("")
    new_yaml_bytes = _subprocess.check_output(cmd, shell=True)
    new_yaml_path = '%s-istio' % yaml_path
    with open(new_yaml_path, 'wt') as fh:
        fh.write(new_yaml_bytes.decode('utf-8'))
        print("'%s' => '%s'" % (yaml_path, new_yaml_path))
    print("")

    cmd = "kubectl apply --namespace %s -f %s" % (namespace, new_yaml_path)
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")


# {"cpu":50, "gpu":50}: eyJjcHUiOjUwLCAiZ3B1Ijo1MH0=
# {"cpu":1, "gpu":99}: eyJjcHUiOjEsICJncHUiOjk5fQ==
# {"025":99, "050":1}: eyIwMjUiOjk5LCAiMDUwIjoxfQ==
# {"025":50, "050":50}: eyIwMjUiOjUwLCAiMDUwIjo1MH0=
# {"025":1, "050":99}: eyIwMjUiOjEsICIwNTAiOjk5fQ==
# split: {"a":100, "b":0}: eyJhIjoxMDAsICJiIjowfQ==
# shadow: ["b"]: WyJiIl0=
# ie. http://localhost:6970/predict-kube-route/mnist/eyJhIjoxMDAsICJiIjowfQ==/WyJiIl0=
@app.route("/predict-kube-route/<string:model_name>/<string:model_split_tag_and_weight_dict>/<string:model_shadow_tag_list>/", methods=['GET'])
def predict_kube_route(model_name,
                       model_split_tag_and_weight_dict, # '{"a":100, "b":0, "c":0}'
                       model_shadow_tag_list, # '[b,c]' Note: must set b and c to traffic split 0 above
                       pipeline_templates_path=None,
                       image_registry_namespace=None,
                       namespace=None):
    
    if type(model_split_tag_and_weight_dict) is str:
        model_split_tag_and_weight_dict = _base64.b64decode(model_split_tag_and_weight_dict) 
        model_split_tag_and_weight_dict = _json.loads(model_split_tag_and_weight_dict)

    if type(model_shadow_tag_list) is str:
        model_shadow_tag_list = _base64.b64decode(model_shadow_tag_list)
        # strip '[' and ']' and split on comma
        model_shadow_tag_list = model_shadow_tag_list.decode('utf-8')
        model_shadow_tag_list = model_shadow_tag_list.strip()
        model_shadow_tag_list = model_shadow_tag_list.lstrip('[')
        model_shadow_tag_list = model_shadow_tag_list.rstrip(']')
        if ',' in model_shadow_tag_list:
            model_shadow_tag_list = model_shadow_tag_list.split(',')
            model_shadow_tag_list = [ tag.strip() for tag in model_shadow_tag_list ]
            model_shadow_tag_list = [ tag.strip("\"") for tag in model_shadow_tag_list ]
        else:
            model_shadow_tag_list = model_shadow_tag_list.strip("\"")
            if model_shadow_tag_list:
                model_shadow_tag_list = [model_shadow_tag_list]
            else:
                model_shadow_tag_list = []

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    try:
        _validate_and_prep_model_split_tag_and_weight_dict(model_split_tag_and_weight_dict)
    except ValueError as ve:
        return_dict = {"status": "incomplete",
                       "error_message": ve}

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict
    
    for model_tag in model_shadow_tag_list:
        try:
            if int(model_split_tag_and_weight_dict[model_tag]) != 0:
                error_message = 'Model variants targeted for traffic-shadow must also exist in --model_split_tag_and_weight_dict with 0 percent traffic-split as follows: --model-split-tag-and-weight-dict=\'{"%s":0,...}\'.' % model_tag
                return_dict = {"status": "incomplete",
                               "error_message": error_message}
                if _http_mode:
                    return _jsonify(return_dict)
                else:
                    return return_dict
        except KeyError:
            error_message = 'Model variants targeted for traffic-shadow must also exist in --model_split_tag_and_weight_dict with 0 percent traffic-split as follows: --model-split-tag-and-weight-dict=\'{"%s":0,...}\'.' % model_tag
            return_dict = {"status": "incomplete",
                           "error_message": error_message}
            if _http_mode:
                return _jsonify(return_dict)
            else:
                return return_dict

    model_shadow_tag_list = [ _validate_and_prep_model_tag(model_tag) for model_tag in model_shadow_tag_list ]
    model_split_tag_list = [ _validate_and_prep_model_tag(model_tag) for model_tag in model_split_tag_and_weight_dict.keys() ]
    model_split_weight_list = list(model_split_tag_and_weight_dict.values())
    context = {'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_SPLIT_TAG_LIST': model_split_tag_list,
               'PIPELINE_MODEL_SPLIT_WEIGHT_LIST': model_split_weight_list,
               'PIPELINE_MODEL_NUM_SPLIT_TAGS_AND_WEIGHTS': len(model_split_tag_list),
               'PIPELINE_MODEL_SHADOW_TAG_LIST': model_shadow_tag_list,
               'PIPELINE_MODEL_NUM_SHADOW_TAGS': len(model_shadow_tag_list)}

    model_router_routerules_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_routerules_template_registry['predict-router'][0][0]))
    path, filename = _os.path.split(model_router_routerules_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    split_tag_weight_filename_snippet = 'split' 
    for idx in range(len(model_split_tag_list)):
        split_tag_weight_filename_snippet = '%s-%s-%s' % (split_tag_weight_filename_snippet, model_split_tag_list[idx], model_split_weight_list[idx])

    split_tag_weight_filename_snippet = split_tag_weight_filename_snippet.lstrip('-')
    split_tag_weight_filename_snippet = split_tag_weight_filename_snippet.rstrip('-')

    shadow_tag_filename_snippet = 'shadow'
    for idx in range(len(model_shadow_tag_list)):
        shadow_tag_filename_snippet = '%s-%s' % (shadow_tag_filename_snippet, model_shadow_tag_list[idx])

    shadow_tag_filename_snippet = shadow_tag_filename_snippet.lstrip('-')
    shadow_tag_filename_snippet = shadow_tag_filename_snippet.rstrip('-')
   
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s-router-routerules.yaml' % (image_registry_namespace, model_name, split_tag_weight_filename_snippet, shadow_tag_filename_snippet))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'." % (filename, rendered_filename))
    _kube_apply(rendered_filename, namespace)

    return_dict = {"status": "complete",
                   "new_traffic_split_routes": model_split_tag_and_weight_dict,
                   "new_traffic_shadow_routes": model_shadow_tag_list}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def _service_start(service_name,
                   pipeline_services_path=None,
                   namespace=None):

    if not pipeline_services_path:
        pipeline_services_path = _default_pipeline_services_path

    if not namespace:
        namespace = _default_namespace

    deploy_yaml_filenames = []
    svc_yaml_filenames = []

    deploy_yaml_filenames = deploy_yaml_filenames + _get_deploy_yamls(service_name=service_name)
    deploy_yaml_filenames = ['%s/%s' % (pipeline_services_path, deploy_yaml_filename) for deploy_yaml_filename in deploy_yaml_filenames]
    print("Using '%s'" % deploy_yaml_filenames)

    svc_yaml_filenames = svc_yaml_filenames + _get_svc_yamls(service_name=service_name)
    svc_yaml_filenames = ['%s/%s' % (pipeline_services_path, svc_yaml_filename) for svc_yaml_filename in svc_yaml_filenames]
    print("Using '%s'" % svc_yaml_filenames)

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    print("")
    print("Starting service '%s'." % service_name)
    print("")
    print("Kubernetes Deployments:")
    print("")
    for deploy_yaml_filename in deploy_yaml_filenames:
        deploy_yaml_filename = _os.path.normpath(deploy_yaml_filename)
        cmd = "kubectl apply -f %s" % deploy_yaml_filename
        print("Running '%s'." % cmd)
        print("")
        _subprocess.call(cmd, shell=True)
        print("")
    print("")
    print("Kubernetes Services:")
    print("")
    for svc_yaml_filename in svc_yaml_filenames:
        svc_yaml_filename = _os.path.normpath(svc_yaml_filename)
        cmd = "kubectl apply -f %s" % svc_yaml_filename
        print("Running '%s'." % cmd)
        print("")
        _subprocess.call(cmd, shell=True)
        print("")
    print("")


# ie. http://localhost:6970/predict-kube-stop/mnist/a

@app.route("/predict-kube-stop/<string:model_name>/<string:model_tag>/", methods=['GET'])
def predict_kube_stop(model_name,
                      model_tag,
                      namespace=None,
                      image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    _service_stop(service_name=service_name, 
                  namespace=namespace)

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def _service_stop(service_name,
                  namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False, pretty=True)
        found = False
        deployments = response.items
        for deploy in deployments:
            if service_name in deploy.metadata.name:
                found = True
                break
        if found:
            print("")
            print("Deleting service '%s'." % deploy.metadata.name)
            print("")
            cmd = "kubectl delete deploy %s --namespace %s" % (deploy.metadata.name, namespace)
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("")


def train_server_pull(model_name,
                      model_tag,
                      image_registry_url=None,
                      image_registry_repo=None,
                      image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    cmd = 'docker pull %s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)


def train_server_register(model_name,
                          model_tag,
                          image_registry_url=None,
                          image_registry_repo=None,
                          image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    cmd = 'docker push %s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)


def train_server_logs(model_name,
                      model_tag,
                      image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = 'docker logs -f %s' % container_name
    print(cmd)
    print("")

    process = _subprocess.call(cmd, shell=True)


def train_server_shell(model_name,
                       model_tag,
                       image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = 'docker exec -it %s bash' % container_name 
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)


def _create_train_server_Dockerfile(model_name,
                                    model_tag,
                                    model_path,
                                    model_type,
                                    model_runtime,
                                    model_chip,
                                    http_proxy,
                                    https_proxy,
                                    stream_logger_url,
                                    stream_logger_topic,
                                    stream_input_url,
                                    stream_input_topic,
                                    stream_output_url,
                                    stream_output_topic,
                                    build_context_path,
                                    image_registry_url,
                                    image_registry_repo,
                                    image_registry_namespace,
                                    image_registry_base_tag,
                                    image_registry_base_chip,
                                    pipeline_templates_path):

    model_tag = _validate_and_prep_model_tag(model_tag)

    print("")
    print("Using templates in '%s'." % pipeline_templates_path)
    print("(Specify --pipeline-templates-path if the templates live elsewhere.)")
    print("")

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_MODEL_PATH': model_path,
               'PIPELINE_MODEL_TYPE': model_type,
               'PIPELINE_MODEL_RUNTIME': model_runtime,
               'PIPELINE_MODEL_CHIP': model_chip,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
              }

    model_train_cpu_Dockerfile_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _Dockerfile_template_registry['train-server'][0][0]))
    path, filename = _os.path.split(model_train_cpu_Dockerfile_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('%s/.pipeline-generated-%s-%s-%s-Dockerfile' % (build_context_path, image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'." % (filename, rendered_filename))

    return rendered_filename


# ie. http://localhost:6970/train-server-build/mnist/gpu/tensorflow/tfserving/gpu/dGVuc29yZmxvdy9tbmlzdC1ncHUvbW9kZWwv/docker.io/pipelineai/train/
#
# model_name: mnist
# model_tag: gpu
# model_path: tensorflow/mnist-gpu/model/
# model_type: tensorflow
# model_runtime: tfserving
# model_chip: gpu
#
@app.route("/train-server-build/<string:model_name>/<string:model_tag>/<string:model_type>/<string:model_runtime>/<string:model_chip>/<string:model_path>/<string:image_registry_url>/<string:image_registry_repo>/<string:image_registry_namespace>/", methods=['GET'])
def train_server_build(model_name,
                       model_tag,
                       model_path,
                       model_type,
                       model_runtime=None,
                       model_chip=None,
                       http_proxy=None,
                       https_proxy=None,
                       stream_logger_url=None,
                       stream_logger_topic=None,
                       stream_input_url=None,
                       stream_input_topic=None,
                       stream_output_url=None,
                       stream_output_topic=None,
                       build_type=None,
                       build_context_path=None,
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       image_registry_base_tag=None,
                       image_registry_base_chip=None,
                       pipeline_templates_path=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_runtime:
        model_runtime = _get_default_model_runtime(model_type)

    if not model_chip: 
        model_chip = _default_model_chip

    if not build_type:
        build_type = _default_build_type

    if not build_context_path:
        build_context_path = _default_build_context_path

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    build_context_path = _os.path.normpath(build_context_path)
    build_context_path = _os.path.expandvars(build_context_path)
    build_context_path = _os.path.expanduser(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)
    build_context_path = _os.path.abspath(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)
    print(build_context_path)

    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    pipeline_templates_path = _os.path.relpath(pipeline_templates_path, build_context_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    print(pipeline_templates_path)

    model_path = _os.path.normpath(model_path)
    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)
    model_path = _os.path.relpath(model_path, build_context_path)
    model_path = _os.path.normpath(model_path)
    print(model_path)

    if build_type == 'docker':
        generated_Dockerfile = _create_train_server_Dockerfile(model_name=model_name,
                                                               model_tag=model_tag,
                                                               model_path=model_path,
                                                               model_type=model_type,
                                                               model_runtime=model_runtime,
                                                               model_chip=model_chip,
                                                               http_proxy=http_proxy,
                                                               https_proxy=https_proxy,
                                                               stream_logger_url=stream_logger_url,
                                                               stream_logger_topic=stream_logger_topic,
                                                               stream_input_url=stream_input_url,
                                                               stream_input_topic=stream_input_topic,
                                                               stream_output_url=stream_output_url,
                                                               stream_output_topic=stream_output_topic,
                                                               build_context_path=build_context_path,
                                                               image_registry_url=image_registry_url,
                                                               image_registry_repo=image_registry_repo,
                                                               image_registry_namespace=image_registry_namespace,
                                                               image_registry_base_tag=image_registry_base_tag,
                                                               image_registry_base_chip=image_registry_base_chip,
                                                               pipeline_templates_path=pipeline_templates_path)

        if http_proxy:
           http_proxy_build_arg_snippet = '--build-arg HTTP_PROXY=%s' % http_proxy
        else:
           http_proxy_build_arg_snippet = ''

        if https_proxy:
           https_proxy_build_arg_snippet = '--build-arg HTTPS_PROXY=%s' % https_proxy
        else:
           https_proxy_build_arg_snippet = ''

        cmd = 'docker build %s %s -t %s/%s/%s-%s:%s -f %s %s' % (http_proxy_build_arg_snippet, https_proxy_build_arg_snippet, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag, generated_Dockerfile, build_context_path)

        print(cmd)
        print("")
        process = _subprocess.call(cmd, shell=True)
    else:
        print("Build type '%s' not found." % build_type)


# HACK: This is a blend of the separate "build" and "start" phases - and without a Docker image to distribute.
#       This is a hack that will train the model inside the admin server container.
#       Hence the name "local" (vs. "server" or "kube")
#       This is not ideal, but good enough for the initial demos.
#
# ie. http://localhost:6970/train-local-start/mnist/v1/L3Jvb3QvbW9kZWxzL21vZGVscy90ZW5zb3JmbG93L21uaXN0LXYxL21vZGVs 
@app.route("/train-local-start/<string:model_name>/<string:model_tag>/<string:model_path>/", methods=['GET'])
def _train_local_start(model_name,
                       model_tag,
                       model_path,
#                      model_type,
#                      model_runtime,
#                      model_chip,
#                      input_host_path=None,
#                      output_host_path=None,
#                      train_args='',
#                       stream_logger_url=None,
#                       stream_logger_topic=None,
#                       stream_input_url=None,
#                       stream_input_topic=None,
#                       stream_output_url=None,
#                       stream_output_topic=None,
#                       memory_limit='2G',
#                       core_limit='2000m',
#                       image_registry_url=None,
#                       image_registry_repo=None,
#                       image_registry_namespace=None,
#                       start_cmd='docker'
                       ):

    if _is_base64_encoded(model_path):
        model_path = _decode_base64(model_path)

    cmd = "cd %s && guild train -y" % model_path

    _local(cmd, args)


def train_server_start(model_name,
                       model_tag,
                       input_host_path=None,
                       output_host_path=None,
                       train_args='',
                       stream_logger_url=None,
                       stream_logger_topic=None,
                       stream_input_url=None,
                       stream_input_topic=None,
                       stream_output_url=None,
                       stream_output_topic=None,
                       memory_limit='2G',
#                       core_limit='2000m',
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       start_cmd='docker'):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if input_host_path:
        input_host_path = _os.path.expandvars(input_host_path)
        input_host_path = _os.path.expanduser(input_host_path)
        input_host_path = _os.path.abspath(input_host_path)
        input_host_path = _os.path.normpath(input_host_path)

    if output_host_path:
        output_host_path = _os.path.expandvars(output_host_path)
        output_host_path = _os.path.expanduser(output_host_path)
        output_host_path = _os.path.abspath(output_host_path)
        output_host_path = _os.path.normpath(output_host_path)

    # Used for samples ./models
    current_path = _os.path.dirname(_os.path.realpath(__file__))
    current_path = _os.path.abspath(current_path)
    current_path = _os.path.normpath(current_path)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    # environment == local, task type == worker, and no cluster definition
    tf_config_local_run = '\'{\"environment\": \"local\", \"task\":{\"type\": \"worker\"}}\''

    # Note:  We added `train` to mimic AWS SageMaker and encourage ENTRYPOINT vs CMD per https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo.html
    # /opt/ml/input/data/{training|validation|testing} per https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo.html

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = '%s run -itd -p 2222:2222 -p 6006:6006 -e PIPELINE_LOCAL_MODEL=true -e PIPELINE_STREAM_LOGGER_URL=%s -e PIPELINE_STREAM_LOGGER_TOPIC=%s -e PIPELINE_STREAM_INPUT_URL=%s -e PIPELINE_STREAM_INPUT_TOPIC=%s -e PIPELINE_STREAM_OUTPUT_URL=%s -e PIPELINE_STREAM_OUTPUT_TOPIC=%s -e TF_CONFIG=%s -e PIPELINE_TRAIN_ARGS="%s" -v %s:/opt/ml/input/samples/models/ -v %s:/opt/ml/input/ -v %s:/opt/ml/output/ --name=%s -m %s %s/%s/%s-%s:%s train' % (start_cmd, stream_logger_url, stream_logger_topic, stream_input_url, stream_input_topic, stream_output_url, stream_output_topic, tf_config_local_run, train_args, current_path, input_host_path, output_host_path, container_name, memory_limit, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)

    print("")
    print("container name: '%s'" % container_name)


def train_server_stop(model_name,
                      model_tag,
                      image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = 'docker rm -f %s' % container_name 

    print(cmd)
    print("")

    process = _subprocess.call(cmd, shell=True)


def _create_train_kube_yaml(model_name,
                            model_tag,
                            input_host_path,
                            output_host_path,
                            model_chip,
                            train_args,
                            stream_logger_url,
                            stream_logger_topic,
                            stream_input_url,
                            stream_input_topic,
                            stream_output_url,
                            stream_output_topic,
                            master_replicas,
                            ps_replicas,
                            worker_replicas,
                            image_registry_url,
                            image_registry_repo,
                            image_registry_namespace,
                            image_registry_base_tag,
                            image_registry_base_chip,
                            pipeline_templates_path,
                            namespace,
                            worker_memory_limit,
                            worker_core_limit):

    model_tag = _validate_and_prep_model_tag(model_tag)

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_MODEL_CHIP': model_chip,
               'PIPELINE_TRAIN_ARGS': train_args,
               'PIPELINE_INPUT_HOST_PATH': input_host_path,
               'PIPELINE_OUTPUT_HOST_PATH': output_host_path,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_WORKER_CORE_LIMIT': worker_core_limit,
               'PIPELINE_WORKER_MEMORY_LIMIT': worker_memory_limit,
               'PIPELINE_MASTER_REPLICAS': int(master_replicas),
               'PIPELINE_PS_REPLICAS': int(ps_replicas),
               'PIPELINE_WORKER_REPLICAS': int(worker_replicas),
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
               }

    if model_chip == 'gpu':
        predict_clustered_template = _os.path.normpath(_os.path.join(pipeline_templates_path, _train_kube_template_registry['train-gpu-cluster'][0][0]))
        path, filename = _os.path.split(predict_clustered_template)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
    else:
        predict_clustered_template = _os.path.normpath(_os.path.join(pipeline_templates_path, _train_kube_template_registry['train-cluster'][0][0]))
        path, filename = _os.path.split(predict_clustered_template)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)

    print("'%s' => '%s'." % (filename, rendered_filename))

    return rendered_filename


def train_kube_connect(model_name,
                       model_tag,
                       local_port=None,
                       service_port=None,
                       namespace=None,
                       image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_connect(service_name=service_name,
                     namespace=namespace,
                     local_port=local_port,
                     service_port=service_port)


def train_kube_describe(model_name,
                        model_tag,
                        namespace=None,
                        image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_describe(service_name=service_name)


def train_kube_shell(model_name,
                     model_tag,
                     namespace=None,
                     image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_shell(service_name=service_name,
                   namespace=namespace)


# ie. http://localhost:6970/train-kube-start/mnist/a/
@app.route("/train-kube-start/<string:model_name>/<string:model_tag>/<string:input_host_path>/<string:output_host_path>/", methods=['GET'])
def train_kube_start(model_name,
                     model_tag,
                     input_host_path,
                     output_host_path,
                     model_chip=None,
                     train_args='',
                     master_replicas=1,
                     ps_replicas=1,
                     worker_replicas=1,
                     stream_logger_url=None,
                     stream_logger_topic=None,
                     stream_input_url=None,
                     stream_input_topic=None,
                     stream_output_url=None,
                     stream_output_topic=None,
                     image_registry_url=None,
                     image_registry_repo=None,
                     image_registry_namespace=None,
                     image_registry_base_tag=None,
                     image_registry_base_chip=None,
                     pipeline_templates_path=None,
                     namespace=None,
                     worker_memory_limit='2Gi',
                     worker_core_limit='2000m'):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_chip:
        model_chip = _default_model_chip

    if input_host_path:
        input_host_path = _os.path.expandvars(input_host_path)
        input_host_path = _os.path.expanduser(input_host_path)
        input_host_path = _os.path.abspath(input_host_path)
        input_host_path = _os.path.normpath(input_host_path)

    if output_host_path:
        output_host_path = _os.path.expandvars(output_host_path)
        output_host_path = _os.path.expanduser(output_host_path)
        output_host_path = _os.path.abspath(output_host_path)
        output_host_path = _os.path.normpath(output_host_path)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)

    if not namespace:
        namespace = _default_namespace

    generated_yaml_path = _create_train_kube_yaml(model_name=model_name,
                                                  model_tag=model_tag,
                                                  model_chip=model_chip,
                                                  input_host_path=input_host_path,
                                                  output_host_path=output_host_path,
                                                  train_args=train_args,
                                                  stream_logger_url=stream_logger_url,
                                                  stream_logger_topic=stream_logger_topic,
                                                  stream_input_url=stream_input_url,
                                                  stream_input_topic=stream_input_topic,
                                                  stream_output_url=stream_output_url,
                                                  stream_output_topic=stream_output_topic,
                                                  master_replicas=master_replicas,
                                                  ps_replicas=ps_replicas,
                                                  worker_replicas=worker_replicas,
                                                  image_registry_url=image_registry_url,
                                                  image_registry_repo=image_registry_repo,
                                                  image_registry_namespace=image_registry_namespace,
                                                  image_registry_base_tag=image_registry_base_tag,
                                                  image_registry_base_chip=image_registry_base_chip,
                                                  pipeline_templates_path=pipeline_templates_path,
                                                  namespace=namespace,
                                                  worker_memory_limit=worker_memory_limit,
                                                  worker_core_limit=worker_core_limit)

    generated_yaml_path = _os.path.normpath(generated_yaml_path)

    # For now, only handle '-deploy' and '-svc' yaml's
    _kube_apply(yaml_path=generated_yaml_path,
                namespace=namespace)


# TODO:  Implement this by re-constructing the yaml (same as train_kube_start) and calling `kubectl delete -f`
#        There is already a _service_stop that can be re-used?
def train_kube_stop(model_name,
                    model_tag,
                    namespace=None,
                    image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_stop(service_name=service_name,
                  namespace=namespace)


# TODO:  Implement this by re-constructing the yaml (same as train_kube_start) and calling `kubectl logs` or something
#        There is already a _service_logs that can be re-used?
def train_kube_logs(model_name,
                    model_tag,
                    model_type,
                    model_runtime=None,
                    model_chip=None,
                    namespace=None,
                    image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_runtime:
        model_runtime = _get_default_model_runtime(model_type)

    if not model_chip:
        model_chip = _default_model_chip

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_logs(service_name=service_name,
                  namespace=namespace)


# TODO:  Implement this by re-constructing the yaml (same as train_kube_start) and calling `kubectl scale` or something
#        Scaling in the train context should just involve scaling the workers
#        TensorFlow doesn't support scaling of workers, btw.
#        There is already a _service_scale method that can be reused?
def train_kube_scale(model_name,
                     model_tag,
                     replicas,
                     model_runtime=None,
                     model_chip=None,
                     namespace=None,
                     image_registry_namespace=None):

    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_scale(service_name=service_name,
                   replicas=replicas,
                   namespace=namespace)


def predict_sage_start(model_name,
                       model_tag,
                       aws_iam_arn,
                       model_type=None,
                       model_runtime=None,
                       model_chip=None,
                       stream_logger_url=None,
                       stream_logger_topic=None,
                       stream_input_url=None,
                       stream_input_topic=None,
                       stream_output_url=None,
                       stream_output_topic=None,
#                       memory_limit='2Gi',
#                       core_limit='1000m',
#                       target_core_util_percentage='50',
#                       min_replicas='1',
#                       max_replicas='2',
                       namespace=None,
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       image_registry_base_tag=None,
                       image_registry_base_chip=None,
                       pipeline_templates_path=None,
                       timeout_seconds=1200):

    model_tag = _validate_and_prep_model_tag(model_tag)

#    if not model_runtime:
#        model_runtime = _get_default_model_runtime(model_type)

#    if not model_chip:
#        model_chip = _default_model_chip

    if not namespace:
        namespace = _default_namespace

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    # Create Model
    from datetime import datetime

    begin_time = datetime.now()

    sagemaker_admin_client = _boto3.client('sagemaker')
    response = sagemaker_admin_client.create_model(
        ModelName='%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
        PrimaryContainer={
            'ContainerHostname': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'Image': '%s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag),
            'Environment': {
            }
        },
        ExecutionRoleArn='%s' % aws_iam_arn,
        Tags=[
            {
                'Key': 'PIPELINE_MODEL_NAME',
                'Value': '%s' % model_name
            },
            {
                'Key': 'PIPELINE_MODEL_TAG',
                'Value': '%s' % model_tag
            },
#            {
#                'Key': 'PIPELINE_MODEL_TYPE',
#                'Value': '%s' % model_type
#            },
#            {
#                'Key': 'PIPELINE_MODEL_RUNTIME',
#                'Value': '%s' % model_runtime
#            },
#            {
#                'Key': 'PIPELINE_MODEL_CHIP',
#                'Value': '%s' % model_chip
#            },
        ]
    )

    model_region = 'UNKNOWN_REGION'
    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        model_arn = response['ModelArn']
        print("")
        print("ModelArn: '%s'" % model_arn)
        model_region = model_arn.split(':')[3]
        print("")
    else:
        return 

    end_time = datetime.now()

    total_time = end_time - begin_time
    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return _get_sage_endpoint_url(model_name=model_name,
                                  model_region=model_region,
                                  image_registry_namespace=image_registry_namespace)


# TODO:  Verify that this works now that AWS SageMaker has fixed a bug 
#
#   aws sagemaker update-endpoint-weights-and-capacities --endpoint-name=arn:aws:sagemaker:us-west-2:954636985443:endpoint-config/predict-mnist --desired-weights-and-capacities='[{"VariantName": "predict-mnist-gpu", "DesiredWeight": 100, "DesiredInstanceCount": 1}]'
#
#   aws sagemaker update-endpoint-weights-and-capacities --endpoint-name=arn:aws:sagemaker:us-west-2:954636985443:endpoint-config/predict-mnist --desired-weights-and-capacities=VariantName=predict-mnist-gpu,DesiredWeight=100,DesiredInstanceCount=1
#
def predict_sage_route(model_name,
                       aws_instance_type_dict,
                       model_split_tag_and_weight_dict,
                       pipeline_templates_path=None,
                       image_registry_namespace=None):

    # Instance Types: 
    #   'ml.c4.2xlarge'|'ml.c4.8xlarge'|'ml.c4.xlarge'|'ml.c5.2xlarge'|'ml.c5.9xlarge'|'ml.c5.xlarge'|'ml.m4.xlarge'|'ml.p2.xlarge'|'ml.p3.2xlarge'|'ml.t2.medium',
    if type(aws_instance_type_dict) is str:
        aws_instance_type_dict = _base64.b64decode(aws_instance_type_dict)
        aws_instance_type_dict = _json.loads(aws_instance_type_dict)

    if type(model_split_tag_and_weight_dict) is str:
        model_split_tag_and_weight_dict = _base64.b64decode(model_split_tag_and_weight_dict)
        model_split_tag_and_weight_dict = _json.loads(model_split_tag_and_weight_dict)

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    _validate_and_prep_model_split_tag_and_weight_dict(model_split_tag_and_weight_dict)

    model_tag_list = [ _validate_and_prep_model_tag(model_tag) for model_tag in model_split_tag_and_weight_dict.keys() ]

    sagemaker_admin_client = _boto3.client('sagemaker')

    from datetime import datetime

    begin_time = datetime.now()

    if not _get_sage_endpoint_config(model_name):
        # Create Endpoint Configuration
        tag_weight_dict_list = []

        for model_tag in model_tag_list:
            tag_weight_dict = {
            'VariantName': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'ModelName': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'InitialInstanceCount': 1,
            'InstanceType': '%s' % aws_instance_type_dict[model_tag],
            'InitialVariantWeight': model_split_tag_and_weight_dict[model_tag],
            }

            tag_weight_dict_list += [tag_weight_dict]

        print(tag_weight_dict_list)

        response = sagemaker_admin_client.create_endpoint_config(
            EndpointConfigName='%s-%s' % (image_registry_namespace, model_name),
            ProductionVariants=tag_weight_dict_list,
            Tags=[
            {
                'Key': 'PIPELINE_MODEL_NAME',
                'Value': '%s' % model_name
            },
            {
                'Key': 'PIPELINE_MODEL_TAG',
                'Value': '%s' % model_tag
            },
            ]
        )

        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("")
            print("EndpointConfigArn: '%s'" % response['EndpointConfigArn'])
            print("")
        else:
            return
    else:
        tag_weight_dict_list = []

        for model_tag in model_tag_list:
            tag_weight_dict = {
            'VariantName': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'DesiredWeight': model_split_tag_and_weight_dict[model_tag],
            'DesiredInstanceCount': 1
            }

            tag_weight_dict_list += [tag_weight_dict]

        print(tag_weight_dict_list)

        response = sagemaker_admin_client.update_endpoint_weights_and_capacities(
            EndpointName='%s-%s' % (image_registry_namespace, model_name),
            DesiredWeightsAndCapacities=tag_weight_dict_list,
        )

        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("")
            print("EndpointArn: '%s'" % response['EndpointArn'])
            print("")
        else:
            print(response['ResponseMetadata']['HTTPStatusCode'])
            return

    if not _get_sage_endpoint(model_name):
        # Create Endpoint (Models + Endpoint Configuration)
        response = sagemaker_admin_client.create_endpoint(
            EndpointName='%s-%s' % (image_registry_namespace, model_name),
            EndpointConfigName='%s-%s' % (image_registry_namespace, model_name),
            Tags=[
            {
                'Key': 'PIPELINE_MODEL_NAME',
                'Value': '%s' % model_name
            },
            {
                'Key': 'PIPELINE_MODEL_TAG',
                'Value': '%s' % model_tag
            },
            ]
        )

        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("")
            print("EndpointArn: '%s'" % response['EndpointArn'])
            print("")
        else:
            return

    end_time = datetime.now()

    total_time = end_time - begin_time

    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")


def _get_sage_endpoint_config(model_name,
                              image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    sagemaker_admin_client = _boto3.client('sagemaker')

    from datetime import datetime

    begin_time = datetime.now()

    try:
        response = sagemaker_admin_client.describe_endpoint_config(
            EndpointConfigName='%s-%s' % (image_registry_namespace, model_name),
        )
    except _ClientError as ce:
        return None

    end_time = datetime.now()

    total_time = end_time - begin_time

    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("")
        print("EndpointConfigArn: '%s'" % response['EndpointConfigArn'])
        print("")
    else:
        print(response['ResponseMetadata']['HTTPStatusCode'])
        return

    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return response['EndpointConfigArn']


def _get_sage_endpoint(model_name,
                       image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    sagemaker_admin_client = _boto3.client('sagemaker')

    from datetime import datetime

    begin_time = datetime.now()
 
    try:
        response = sagemaker_admin_client.describe_endpoint(
            EndpointName='%s-%s' % (image_registry_namespace, model_name),
        )
    except _ClientError as ce:
        return None

    end_time = datetime.now()

    total_time = end_time - begin_time

    model_region = 'UNKNOWN_REGION'
    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("")
        model_arn = response['EndpointArn']
        print("EndpointArn: '%s'" % model_arn)
        model_region = model_arn.split(':')[3]
    else:
        print(response['ResponseMetadata']['HTTPStatusCode'])
        return

    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return _get_sage_endpoint_url(model_name,
                                  model_region,
                                  image_registry_namespace) 


# TODO:  Fix this - doesn't work quite like i want
def _image_to_json(image_path,
                   image_format):

    image_path = _os.path.expandvars(image_path)
    image_path = _os.path.expanduser(image_path)
    image_path = _os.path.abspath(image_path)
    image_path = _os.path.normpath(image_path)

    print('image_path: %s' % image_path)
    print('image_format: %s' % image_format)

    #image = Image.open(image_path)
    #image_str = BytesIO()
    #image.save(image_str, format=image_format)
    #return _json.dumps(str(image_str.getvalue()))
#    import numpy as np
#    img = Image.open("input.png")
#    arr = np.array(img)
#    return arr


def _image_to_numpy(image_path):
    """Convert image to np array.
    Returns:
        Numpy array of size (1, 28, 28, 1) with MNIST sample images.
    """
    image_as_numpy = np.zeros((1, 28, 28))
    print(image_as_numpy.shape)
    for idx, image_path in enumerate(image_path):
        image_read = skimage.io.imread(fname=image_path, as_grey=True)
        print(image_read.shape)
        image_as_numpy[idx, :, :] = image_read

    return _json.dumps(list(image_as_numpy.flatten()))


# Derived from the following:
#  https://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow
def _image_to_json2(image_path):
    image_path = _os.path.expandvars(image_path)
    image_path = _os.path.expanduser(image_path)
    image_path = _os.path.abspath(image_path)
    image_path = _os.path.normpath(image_path)

    img_base64 = base64.b64encode(open(image_path, "rb").read())
    return json.dumps({"key":"0", "image_bytes": {"b64": img_base64}})


# cli_command: predict-kube-endpoint --model_name=mnist
#    cHJlZGljdC1rdWJlLWVuZHBvaW50IC0tbW9kZWwtbmFtZT1tbmlzdA==
# cli_command: predict-server-build --model-name=mnist --model-tag=cpu --model-path=tensorflow/mnist-cpu/model --model-type=tensorflow --model-runtime=tfserving --model-chip=cpu
#    cHJlZGljdC1zZXJ2ZXItYnVpbGQgLS1tb2RlbC1uYW1lPW1uaXN0IC0tbW9kZWwtdGFnPWNwdSAtLW1vZGVsLXBhdGg9dGVuc29yZmxvdy9tbmlzdC1jcHUvbW9kZWwgLS1tb2RlbC10eXBlPXRlbnNvcmZsb3cgLS1tb2RlbC1ydW50aW1lPXRmc2VydmluZyAtLW1vZGVsLWNoaXA9Y3B1

@app.route('/stream/<string:cli_command>/')
def _stream(cli_command):
    if _is_base64_encoded(cli_command):
        cli_command = _decode_base64(cli_command)
    
    g = _proc.Group()

    print('Running "pipeline %s"...' % cli_command)
    # Note:  If calling a python process (ie. PipelineAI CLI!), you'll need to pass `-u` as follows:
    #   p = g.run( [ "python", "-u", "slow.py" ] )
    # See https://mortoray.com/2014/03/04/http-streaming-of-command-output-in-python-flask/
    #p = g.run( [ "bash", "-c", "for ((i=0;i<100;i=i+1)); do echo $i; sleep 1; done" ] )
    #p = g.run( [ "python", "-u", "cli_pipeline.py ..." ] )
    # Note:  This PIPELINE_END_STREAM is used by ./static/stream-page.html to stop the EventSource polling
    #        If you update this, please update stream-page.html, as well
    p = g.run(["bash", "-c", "pipeline %s && echo '\nPIPELINE_END_STREAM\n'" % cli_command])
    #p = g.run( [ "bash", "-c", "curl localhost:6970/predict-kube-endpoints/" ] )
    def read_process():
        initial_time = time.time()
        trigger_time = initial_time + 5
        while g.is_pending():
            lines = g.readlines()
            for _proc, line in lines:
                if _http_mode:
                    yield 'data:%s\n'.encode('utf-8') % line
                else:
                    yield '%s'.encode('utf-8') % line
            now = time.time()
            if now > trigger_time:
                if _http_mode:
                    yield 'data:...%d seconds have passed...\n\n'.encode('utf-8') % int(trigger_time - initial_time)
                else:
                    yield '...%d seconds have passed...\n'.encode('utf-8') % int(trigger_time - initial_time)
                trigger_time = now + 5


    if _http_mode:
        return _Response(_stream_with_context(read_process()), mimetype= 'text/event-stream' )
    else:
        return _Response(_stream_with_context(read_process()), mimetype= 'text/plain' )


@app.route('/stream-page/<string:cli_command>/')
def _stream_page(cli_command):
    return _redirect(_url_for('static', filename='stream-page.html', cli_command=cli_command))


# Http Mode:
#     pipeline http <port> <debug=True|False> <_model_base_path>
# Http Mode with Stream:
#     gunicorn --bind 0.0.0.0:6970 --pythonpath <cli_pipeline_module_path> -k gevent cli_pipeline:app http <debug=True|False> <_model_base_path>
def _main():
    global _http_mode
    global _model_base_path

    print(_sys.argv)

    if len(_sys.argv) == 1:
        return help()

    if len(_sys.argv) >= 2 and _sys.argv[1] == 'http':
        print("")
        print("Http mode is enabled.")
        port = 6970

        if len(_sys.argv) >= 3:
            port = int(_sys.argv[2])
        print(port)

        debug = "False"

        if len(_sys.argv) >= 4:
            debug = _sys.argv[3]
        if (debug == "False" or debug == "false"):
           debug = False
        else:
           debug = True
        print(debug)
        
        if len(_sys.argv) >= 5:
            _model_base_path = _sys.argv[4]
            _model_base_path = _os.path.expandvars(_model_base_path)
            _model_base_path = _os.path.expanduser(_model_base_path)
            _model_base_path = _os.path.abspath(_model_base_path)
            _model_base_path = _os.path.normpath(_model_base_path)
        print(_model_base_path)
      
        cli_pipeline_module_path = _os.path.dirname(_os.path.realpath(__file__))
        print(cli_pipeline_module_path)

        cmd = 'gunicorn --bind 0.0.0.0:%s --pythonpath %s -k gevent cli_pipeline:app http %s %s' % (port, cli_pipeline_module_path, debug, _model_base_path)
        _subprocess.call(cmd, shell=True)
    else:
        _http_mode = False
        _fire.Fire()


if __name__ == '__main__':
    _main()
