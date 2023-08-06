from flask import request, json
from flask_restful import Resource
from flask_sqlalchemy import Pagination

from flask_restalchemy.serialization.modelserializer import ModelSerializer
from .utils import query_from_request


class BaseResource(Resource):

    def __init__(self, declarative_model, serializer, session_getter):
        """
        The Base class for ORM resources

        :param class declarative_model: the SQLAlchemy declarative class.

        :param ModelSchema serializer: Marshmallow schema for serialization. If `None`, a default serializer will be
            created.

        :param callable session_getter: a callable that returns the DB session. A callable is used since a reference to
            DB session may not be available on the resource initialization.
        """
        self._resource_model = declarative_model
        self._serializer = serializer
        self._serializer.strict = True
        assert isinstance(self._serializer, ModelSerializer), 'Invalid serializer instance: {}'.format(serializer)
        self._session_getter = session_getter

    def save_from_request(self, extra_attrs={}):
        session = self._session_getter()
        model_obj = self._serializer.load(load_request_data())
        for attr_name, value in extra_attrs.items():
            setattr(model_obj, attr_name, value)
        session.add(model_obj)
        session.commit()
        return self._serializer.dump(model_obj).data

    def _save_model(self, model_obj, method):
        session = self._session_getter()
        session.add(model_obj)

        # run pre commit hooks
        if method == 'POST':
            self._serializer.before_post_commit(model_obj, session)

        session.commit()

        # run pos commit hooks
        if method == 'POST':
            self._serializer.after_post_commit(model_obj, session)

    def _save_serialized(self, serialized_data, existing_model=None):
        model_obj = self._serializer.load(serialized_data, existing_model)

        method = 'PUT' if existing_model else 'POST'
        self._save_model(model_obj, method)

        return self._serializer.dump(model_obj)

    @property
    def _db_session(self):
        return self._session_getter()


class ItemResource(BaseResource):
    """
    flask-restful resource class that receives receives a SQLAlchemy model class and define the API to provide GET,
    UPDATE and DELETE over a single data identified by id
    """

    def get(self, id):
        data = self._resource_model.query.get(id)
        if data is None:
            return NOT_FOUND_ERROR, 404
        return self._serializer.dump(data)

    def put(self, id):
        data = self._resource_model.query.get(id)
        if data is None:
            return NOT_FOUND_ERROR, 404
        serialized = self._serializer.dump(data)
        serialized.update(load_request_data())
        self._save_serialized(serialized, data)
        return serialized

    def delete(self, id):
        data = self._resource_model.query.get(id)
        if data is None:
            return NOT_FOUND_ERROR, 404
        session = self._db_session
        session.delete(data)
        session.commit()
        return '', 204


class CollectionResource(BaseResource):
    """
    flask-restful resource class that receives a SQLAlchemy model class and define the API to provide LIST and
    CREATE over data of that class
    """

    def get(self):
        data = query_from_request(self._resource_model, self._serializer, request)
        if isinstance(data, Pagination):
            return {
                'page': data.page,
                'per_page': data.per_page,
                'count': data.total,
                'results': [self._serializer.dump(item) for item in data.items]
            }
        else:
            return [self._serializer.dump(item) for item in data]


    def post(self):
        saved = self._save_serialized(load_request_data())
        return saved, 201


class CollectionRelationResource(BaseResource):
    """
    flask-restful resource class that receives two SQLAlchemy models, a parent model and a child model,
    and define the API to provide LIST and CREATE over data of the child model associated with a specific
    element of the parent model.
    """

    def __init__(self, relation_property, serializer, session_getter):
        """
        The Base class for ORM resources

        :param class declarative_model: the SQLAlchemy declarative class.

        :param ModelSchema serializer: Marshmallow schema for serialization. If `None`, a default serializer will be
            created.

        :param callable session_getter: a callable that returns the DB session. A callable is used since a reference to
            DB session may not be available on the resource initialization.
        """
        resource_model = relation_property.prop.mapper.class_
        super(CollectionRelationResource, self).__init__(resource_model, serializer, session_getter)
        self._relation_property = relation_property
        self._related_model = relation_property.class_


    def get(self, relation_id):
        session = self._db_session()
        related_obj = session.query(self._related_model).get(relation_id)
        if related_obj is None:
            return NOT_FOUND_ERROR, 404
        # TODO: Is there a more efficient way than using getattr?
        data = getattr(related_obj, self._relation_property.key)
        collection = [self._serializer.dump(item) for item in data]
        return collection


    def post(self, relation_id):
        session = self._db_session()
        related_obj = session.query(self._related_model).get(relation_id)
        if not related_obj:
            return NOT_FOUND_ERROR, 404
        collection = getattr(related_obj, self._relation_property.key)
        new_obj = self._serializer.load(load_request_data())
        collection.append(new_obj)

        self._save_model(new_obj, 'POST')
        return self._serializer.dump(new_obj), 201


class ItemRelationResource(BaseResource):
    """
    flask-restful resource class that receives two SQLAlchemy models, a parent model and a child model,
    and define the API to provide GET, PUT and DELETE operations over data of the child model associated with a
    specific element of the parent model.
    """

    def __init__(self, relation_property, serializer, session_getter):
        """
        The Base class for ORM resources

        :param class declarative_model: the SQLAlchemy declarative class.

        :param ModelSchema serializer: Marshmallow schema for serialization. If `None`, a default serializer will be
            created.

        :param callable session_getter: a callable that returns the DB session. A callable is used since a reference to
            DB session may not be available on the resource initialization.
        """
        resource_model = relation_property.prop.mapper.class_
        super(ItemRelationResource, self).__init__(resource_model, serializer, session_getter)
        self._relation_property = relation_property
        self._related_model = relation_property.class_

    def get(self, relation_id, id):
        requested_obj = self._query_related_obj(relation_id, id)
        if not requested_obj:
            return NOT_FOUND_ERROR, 404
        return self._serializer.dump(requested_obj), 200

    def put(self, relation_id, id):
        requested_obj = self._query_related_obj(relation_id, id)
        if not requested_obj:
            return NOT_FOUND_ERROR, 404
        serialized = self._serializer.dump(requested_obj)
        serialized.update(load_request_data())
        return self._save_serialized(serialized, requested_obj)

    def delete(self, relation_id, id):
        requested_obj = self._query_related_obj(relation_id, id)
        if not requested_obj:
            return NOT_FOUND_ERROR, 404
        session = self._db_session()
        session.delete(requested_obj)
        session.commit()
        return '', 204

    def _query_related_obj(self, relation_id, id):
        """
        Query resource model by ID but also add the relationship as a query constrain.

        :param relation_id: id of the related model
        :param id: id of the model being required
        :return: model with 'id' that has a related model with 'related_id'
        """

        # This checks if the relationship uses a secondary table. The existence of a relation between the models is
        # constrained differently in either case.  If the relationship_property expression has a 'right' parameter, the
        # relation uses no secondary table, and the model points directly to the related model with the id on 'right'.
        if hasattr(self._relation_property.expression, 'right'):
            return self._db_session.query(self._resource_model).filter(
                self._resource_model.id == id,
                self._relation_property.expression.right == relation_id,
            ).one_or_none()
        else:
            return self._db_session.query(self._resource_model).filter(
                self._resource_model.id == id,
                self._relation_property.any(self._related_model.id == relation_id, id=id),
            ).one_or_none()


class CollectionPropertyResource(CollectionRelationResource):

    def __init__(self, declarative_model, related_model, property_name, serializer, session_getter):
        super(CollectionRelationResource, self).__init__(declarative_model, serializer, session_getter)
        self._related_model = related_model
        self._property_name = property_name

    def get(self, relation_id):
        session = self._db_session()
        related_obj = session.query(self._related_model).get(relation_id)
        if related_obj is None:
            return NOT_FOUND_ERROR, 404
        data = getattr(related_obj, self._property_name)
        collection = [self._serializer.dump(item) for item in data]
        return collection

    def post(self, relation_id):
        return 'POST not allowed for property resources', 405


class RequestException(Exception):
    def __init__(self, msg, error_code):
        self.msg = msg
        self.error_code = error_code


def load_request_data():
    if request.data:
        return json.loads(request.data.decode('utf-8'))
    else:
        return request.form.to_dict()


NOT_FOUND_ERROR = 'Resource not found in the database!'
