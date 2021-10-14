
class Object():
    __tablename__ = "object"

    aid = None  # id alerce
    oid = None  # oid survey
    sid = None  # survey ZTF=1, ATLAS=2
    lastmjd = None
    firstmjd = None
    meanra = None
    meandec = None
    sigmara = None
    sigmadec = None

    def __repr__(self):
        return "<Object(aid='%s')>" % (self.alerce_id)

class Detection():
    __tablename__ = "detection"

    aid = None  # id alerce
    sid = None  # survey ZTF or ATLAS
    candid = None
    mjd = None
    fid = None
    ra = None
    dec = None
    rb = None
    mag = None
    sigmag = None
    extra_fields = None

    def __repr__(self):
        return "<Detection(candid='%i', fid='%i', aid='%s')>" % (
            self.candid,
            self.fid,
            self.aid,
        )

class NonDetection():
    __tablename__ = "non_detection"

    aid = None
    sid = None
    mjd = None
    diffmaglim = None
    fid = None
    extra_fields = None

class Classification():
    __tablename__ = "classification"

    alerce_id = None
    survey_id = None
    classifier_name = None
    classifier_version = None
    class_name = None
    probabilty = None
    ranking = None
    probabilities = None
    last_updated = None
    created_on = None

class Features():
    __tablename__ = "features"

    alerce_id = None
    survey_id = None
    features = None
    created_on = None
    last_updated = None

class Xmatch():
    __tablename__ = "xmatch"

    alerce_id = None
    survey_id = None
    catalog_name = None
    catalog_id = None
