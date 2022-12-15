from pymongo import ASCENDING, DESCENDING, GEOSPHERE, IndexModel
from .orm import Field, SpecialField, ModelMetaClass


class BaseModel(dict, metaclass=ModelMetaClass):
    def __init__(self, **kwargs):
        model = {}
        if "_id" in kwargs and "_id" not in self._meta.fields:
            model["_id"] = kwargs["_id"]
        for field, fclass in self._meta.fields.items():
            try:
                try:
                    model[field] = fclass.callback(**kwargs)
                except AttributeError:
                    model[field] = kwargs[field]
            except KeyError:
                raise AttributeError(
                    f"{self.__class__.__name__} model needs {field} attribute"
                )
        super().__init__(**model)


class BaseModelWithExtraFields(BaseModel):
    @classmethod
    def create_extra_fields(cls, **kwargs):
        if "extra_fields" in kwargs:
            return kwargs["extra_fields"]
        else:
            return {k: v for k, v in kwargs.items() if k not in cls._meta.fields}


class Object(BaseModel):
    """Mongo implementation of the Object class.

    Contains definitions of indexes and custom attributes like loc.
    """

    _id = SpecialField(
        lambda **kwargs: kwargs.get("aid") or kwargs["_id"]
    )  # ALeRCE object ID (unique ID in database)
    oid = Field()  # List with all OIDs
    tid = Field()  # List with all telescopes the object has been observed with
    corrected = Field()
    stellar = Field()
    firstmjd = Field()
    lastmjd = Field()
    ndet = Field()
    meanra = Field()
    sigmara = Field()
    meandec = Field()
    sigmadec = Field()
    loc = SpecialField(
        lambda **kwargs: {
            "type": "Point",
            "coordinates": [kwargs["meanra"] - 180, kwargs["meandec"]],
        }
    )
    magstats = SpecialField(lambda **kwargs: kwargs.get("magstats", []))
    features = SpecialField(lambda **kwargs: kwargs.get("features", []))
    probabilities = SpecialField(lambda **kwargs: kwargs.get("probabilities", []))
    xmatch = SpecialField(lambda **kwargs: kwargs.get("xmatch", []))

    __table_args__ = [
        IndexModel([("oid", ASCENDING)]),
        IndexModel([("tid", ASCENDING)]),
        IndexModel([("lastmjd", DESCENDING)]),
        IndexModel([("firstmjd", DESCENDING)]),
        IndexModel([("loc", GEOSPHERE)]),
        IndexModel(
            [
                ("probabilities.ranking", DESCENDING),
                ("probabilities.classifier_name", ASCENDING),
                ("probabilities.classifier_version", DESCENDING),
                ("probabilities.class_name", DESCENDING),
                ("probabilities.probability", DESCENDING),
            ],
        ),
    ]
    __tablename__ = "object"


class Detection(BaseModelWithExtraFields):
    @classmethod
    def create_extra_fields(cls, **kwargs):
        kwargs = super().create_extra_fields(**kwargs)
        kwargs.pop("candid", None)  # Prevents candid being duplicated in extra_fields
        return kwargs

    _id = SpecialField(lambda **kwargs: kwargs.get("candid") or kwargs["_id"])
    tid = Field()  # Telescope ID
    aid = Field()
    oid = Field()
    mjd = Field()
    fid = Field()
    ra = Field()
    e_ra = Field()
    dec = Field()
    e_dec = Field()
    mag = Field()  # magpsf in ZTF alerts
    e_mag = Field()  # sigmapsf in ZTF alerts
    mag_corr = Field()  # magpsf_corr in ZTF alerts
    e_mag_corr = Field()  # sigmapsf_corr in ZTF alerts
    isdiffpos = Field()
    corrected = Field()
    dubious = Field()
    parent_candidate = Field()
    has_stamp = Field()
    step_id_corr = Field()

    __table_args__ = [
        IndexModel([("aid", ASCENDING), ("oid", ASCENDING)]),
        IndexModel([("tid", ASCENDING)]),
    ]
    __tablename__ = "detection"


class NonDetection(BaseModelWithExtraFields):
    @classmethod
    def create_extra_fields(cls, **kwargs):
        kwargs = super().create_extra_fields(**kwargs)
        kwargs.pop("candid", None)  # Prevents candid being duplicated in extra_fields
        return kwargs

    _id = SpecialField(lambda **kwargs: kwargs.get("candid") or kwargs["_id"])
    aid = Field()
    tid = Field()
    oid = Field()
    mjd = Field()
    fid = Field()
    diffmaglim = Field()

    __table_args__ = [
        IndexModel([("aid", ASCENDING), ("oid", ASCENDING)]),
        IndexModel([("tid", ASCENDING)]),
    ]
    __tablename__ = "non_detection"


class Taxonomy(BaseModel):
    classifier_name = Field()
    classifier_version = Field()
    classes = Field()

    __table_args__ = [
        IndexModel(
            [("classifier_name", ASCENDING), ("classifier_version", DESCENDING)]
        ),
    ]
    __tablename__ = "taxonomy"


class Step(BaseModel):
    step_id = Field()
    name = Field()
    version = Field()
    comments = Field()
    date = Field()

    __table_args__ = [
        IndexModel([("step_id", ASCENDING)]),
    ]
    __tablename__ = "step"


class FeatureVersion(BaseModel):
    version = Field()
    step_id_feature = Field()
    step_id_preprocess = Field()

    __table_args__ = [
        IndexModel([("version", ASCENDING)]),
    ]
    __tablename__ = "feature_version"


class Pipeline(BaseModel):
    pipeline_id = Field()
    step_id_corr = Field()
    step_id_feat = Field()
    step_id_clf = Field()
    step_id_out = Field()
    step_id_stamp = Field()
    date = Field()

    __table_args__ = [
        IndexModel([("pipeline_id", ASCENDING)]),
    ]
    __tablename__ = "pipeline"
