"""API Blueprint

This is a subclass of Flask's Blueprint

It provides added features:

- Decorators to specify Marshmallow schema for view functions I/O

- API documentation registration

Documentation process works in several steps:

- At import time

  - When a MethodView or a function is decorated, relevant information
    is added to the object's `_apispec` attribute.

  - The `route` decorator registers the endpoint in the Blueprint and gathers
    all information about the endpoint in `Blueprint._docs[endpoint]`

- At initialization time

  - Schema instances are replaced either by their reference in the `definition`
    section of the spec if applicable, otherwise by their json representation.

  - Endpoints documentation is registered in the APISpec object
"""

from collections import OrderedDict
from copy import deepcopy

from flask import Blueprint as FlaskBlueprint
from flask.views import MethodViewType

from apispec.ext.marshmallow.swagger import __location_map__

from .utils import deepupdate
from .args_parser import parser
from .response import response
from .exceptions import (
    EndpointMethodDocAlreadyRegisted, InvalidLocation, MultiplePaginationModes)


# This is the order in which the methods are presented in the spec
HTTP_METHODS = [
    'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE']


class Blueprint(FlaskBlueprint):
    """Blueprint that registers info in API documentation"""

    def __init__(self, *args, **kwargs):

        self.description = kwargs.pop('description', '')

        super().__init__(*args, **kwargs)

        # _docs is an ordered dict storing endpoints documentation:
        # {endpoint: {
        #     'get': documentation,
        #     'post': documentation,
        #     ...
        #     }
        # }
        self._docs = OrderedDict()

    def _store_endpoint_docs(self, endpoint, obj, **kwargs):
        """Store view or function doc info"""

        endpoint_doc = self._docs.setdefault(endpoint, OrderedDict())

        def store_method_docs(method, function):
            doc = getattr(function, '_apidoc', {})
            # Add function doc to table for later registration
            method_l = method.lower()
            # Check another doc was not already registed for endpoint/method
            if method_l in endpoint_doc and endpoint_doc[method_l] is not doc:
                # If multiple routes point to the same endpoint, the doc may
                # be already registered.
                # Only trigger exception if a different doc is passed.
                raise EndpointMethodDocAlreadyRegisted(
                    "Another doc is already registered for endpoint '{}' "
                    "method {}".format(endpoint, method_l.upper()))
            endpoint_doc[method_l] = doc

        # MethodView (class)
        if isinstance(obj, MethodViewType):
            for method in HTTP_METHODS:
                if method in obj.methods:
                    func = getattr(obj, method.lower())
                    store_method_docs(method, func)
        # Function
        else:
            methods = kwargs.pop('methods', None) or ['GET']
            for method in methods:
                store_method_docs(method, obj)

    def register_views_in_doc(self, app, spec):
        """Register views information in documentation

        If a schema in a parameter or a response appears in the spec
        `definitions` section, it is replaced by a reference to its definition
        in the parameter or response documentation:

        "schema":{"$ref": "#/definitions/MySchema"}
        """
        for endpoint, doc in self._docs.items():
            # doc is a dict of documentation per method for the endpoint
            # {'get': documentation, 'post': documentation,...}

            # Prepend Blueprint name to endpoint
            endpoint = '.'.join((self.name, endpoint))

            # Tag each operation with Blueprint name
            for operation in doc.values():
                operation.update({'tags': [self.name]})

            # TODO: Do we support multiple rules per endpoint?
            # https://github.com/marshmallow-code/apispec/issues/181
            for rule in app.url_map.iter_rules(endpoint):
                # We need to deepcopy operations here
                # because it can be modified in add_path, which causes
                # issues if there are multiple rules for the same endpoint
                spec.add_path(app=app, rule=rule, operations=deepcopy(doc))

    def route(self, rule, **options):
        """Decorator to register url rule in application

        Also stores doc info for later registration

        Use this to decorate a MethodView or a resource function
        """
        def decorator(func):

            # By default, endpoint for User is 'user'
            # TODO: Remove lower() (Breaking change)
            endpoint = options.pop('endpoint', func.__name__.lower())

            # MethodView (class)
            if isinstance(func, MethodViewType):
                # This decorator may be called multiple times on the same
                # MethodView, but Flask will complain if different views are
                # mapped to the same endpoint, so we should call 'as_view' only
                # once and keep the result in MethodView._view_func
                if not getattr(func, '_view_func', None):
                    func._view_func = func.as_view(endpoint)
                view_func = func._view_func
            # Function
            else:
                view_func = func

            # Add URL rule in Flask and store endpoint documentation
            self.add_url_rule(rule, view_func=view_func, **options)
            self._store_endpoint_docs(endpoint, func, **options)

            return func

        return decorator

    @staticmethod
    def doc(**kwargs):
        """Decorator adding description attributes to a view function

        Values passed as kwargs are copied verbatim in the docs

            Example: ::

                @blp.doc("description": "Return pets based on ID",
                        "summary": "Find pets by ID")
                def get(...):
        """
        def decorator(func):
            func._apidoc = deepupdate(getattr(func, '_apidoc', {}), kwargs)
            return func
        return decorator

    @staticmethod
    def arguments(schema, *, location='json', required=True, **kwargs):
        """Decorator specifying the schema used to deserialize parameters

        :param type|Schema schema: A marshmallow Schema class or instance.
        :param str location: The location of the parameter, in webargs terms.
            https://webargs.readthedocs.io/en/latest/quickstart.html#request-locations
            Allows values: 'query' or 'querystring', 'json', 'form', 'headers',
            'cookies', 'files'.
            Defaults to 'json', which means 'body'.
            Note that unlike webargs, flask-rest-api allows only one location
            for a parameter.
        :param bool required: Whether this set of arguments is required.
            Defaults to True.
            This only affects json/body arguments as, in this case, the docs
            expose the whole schema as a required parameter.
            For other locations, the schema is turned into an array of
            parameters and their required value is grabbed from their Field.

        The kwargs are passed to webargs's Parser.use_args.

        Upon endpoint access, the parameters are deserialized into a dictionary
        that is injected as a positional argument to the view function.

        This decorator can be called several times on a resource function,
        for instance to accept both body and query parameters.

            Example: ::

                @blp.route('/', methods=('POST', ))
                @blp.arguments(DocSchema)
                @blp.arguments(QueryArgsSchema, location='query')
                def post(document, query_args):

        The order of the decorator calls matter as it determines the order in
        which the parameters are passed to the view function.
        """
        if isinstance(schema, type):
            schema = schema()

        try:
            openapi_location = __location_map__[location]
        except KeyError:
            raise InvalidLocation(
                "{} is not a valid location".format(location))

        # At this stage, put schema instance in doc dictionary. Il will be
        # replaced later on by $ref or json.
        parameters = {
            'in': openapi_location,
            'required': required,
            'schema': schema,
        }

        def decorator(func):
            # Call use_args (from webargs) to inject params in function
            func = parser.use_args(
                schema, locations=[location], **kwargs)(func)
            # Add parameter to parameters list in doc info in function object
            func._apidoc = getattr(func, '_apidoc', {})
            func._apidoc.setdefault('parameters', []).append(parameters)
            return func

        return decorator

    @staticmethod
    def response(schema=None, *, code=200, description='',
                 paginate=False, paginate_with=None,
                 etag_schema=None, disable_etag=False):
        """Decorator generating an endpoint response, specifying the schema
        to use for serialization and others parameters.

        :param schema: :class:`Schema <marshmallow.Schema>` class or instance,
            or `None`
        :param int code: HTTP status code (default 200)
        :param bool paginate: Assume resource function returns paginated result
        :param etag_schema: :class:`Schema <marshmallow.Schema>` class
            or instance, or `None`
        :param bool disable_etag: Disable ETag feature locally even if enabled
            globally

        If the resource returns many elements, pass a Schema instance with
        "many" set to True.

            Example: ::

                @blp.response(MySchema(many=True), description: 'My objects')
                def get(...)

        When using "paginate" or "paginate_with", this is not necessary as the
        schema will be instantiated with "many" automatically.
        """
        if paginate and paginate_with is not None:
            raise MultiplePaginationModes(
                "paginate_with and paginate are mutually exclusive.")

        if isinstance(schema, type):
            schema = schema(many=(paginate or paginate_with))
        if isinstance(etag_schema, type):
            etag_schema = etag_schema(many=(paginate or paginate_with))

        def decorator(func):

            # Add schema as response in the API doc
            doc = {'responses': {code: {'description': description}}}
            if schema:
                doc['responses'][code]['schema'] = schema
            func._apidoc = deepupdate(getattr(func, '_apidoc', {}), doc)

            return response(
                schema=schema, code=code,
                paginate=paginate, paginate_with=paginate_with,
                etag_schema=etag_schema, disable_etag=disable_etag
            )(func)

        return decorator
