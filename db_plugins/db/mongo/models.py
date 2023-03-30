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

    __table_args__ = [
        IndexModel([("oid", ASCENDING)]),
        IndexModel([("tid", ASCENDING)]),
        IndexModel([("lastmjd", DESCENDING)]),
        IndexModel([("firstmjd", DESCENDING)]),
        IndexModel([("loc", GEOSPHERE)]),
    ]
    __tablename__ = "object"


class Probability(BaseModel):
    aid = Field()
    classifier_name = Field()
    classifier_version = Field()
    class_name = Field()
    probability = Field()
    ranking = Field()

    __table_args__ = [
        IndexModel([("aid", ASCENDING)]),
        IndexModel(
            [
                ("classifier_name", ASCENDING),
                ("class_name", ASCENDING),
                ("classifier_version", ASCENDING),
                ("aid", ASCENDING),
            ],
            unique=True,
        ),
        IndexModel(
            [("probability", DESCENDING)], partialFilterExpression={"ranking": 1}
        ),
    ]
    __tablename__ = "probability"


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
    e_mag_corr_ext = Field()  # sigmapsf_corr_ext in ZTF alerts
    isdiffpos = Field()
    corrected = Field()
    dubious = Field()
    stellar = Field()
    has_stamp = Field()

    __table_args__ = [
        IndexModel([("aid", ASCENDING)]),
        IndexModel([("oid", ASCENDING)]),
        IndexModel([("tid", ASCENDING)]),
        IndexModel([("mjd", ASCENDING)]),
    ]
    __tablename__ = "detection"


class NonDetection(BaseModelWithExtraFields):
    aid = Field()
    tid = Field()
    oid = Field()
    mjd = Field()
    fid = Field()
    diffmaglim = Field()

    __table_args__ = [
        IndexModel([("aid", ASCENDING)]),
        IndexModel([("tid", ASCENDING)]),
        IndexModel(
            [("oid", ASCENDING), ("fid", ASCENDING), ("mjd", ASCENDING)], unique=True
        ),
    ]
    __tablename__ = "non_detection"


class Taxonomy(BaseModel):
    classifier_name = Field()
    classifier_version = Field()
    classes = Field()

    __table_args__ = [
        IndexModel(
            [("classifier_name", ASCENDING), ("classifier_version", DESCENDING)],
            unique=True,
        ),
    ]
    __tablename__ = "taxonomy"
