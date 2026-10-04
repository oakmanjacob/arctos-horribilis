import dataclasses
import datetime
import enum


class LifeStage(enum.StrEnum):
    ADULT = "adult"
    SUBADULT = "subadult"
    JUVENILE = "juvenile"
    EMBRYO = "embryo"
    VIEW_DOCUMENTATION = "* View Documentation"

    @classmethod
    def from_string(cls, life_stage: str) -> LifeStage:
        life_stage = life_stage.strip(". ").lower()

        if life_stage in ["adult", "ad", "young adult"]:
            return cls.ADULT

        if life_stage in ["subadult", "immature", "imm", "im", "yg", "yng"]:
            return cls.SUBADULT

        if life_stage in ["juvenile", "juv", "jv", "j"]:
            return cls.JUVENILE

        if life_stage in ["embryo", "emb"]:
            return cls.EMBRYO

        if life_stage == "* view documentation":
            return cls.VIEW_DOCUMENTATION

        raise ValueError("Invalid lifestage value: ", life_stage)


class Sex(enum.StrEnum):
    FEMALE = "female"
    MALE = "male"
    INTERSEX = "intersex"
    UNKNOWN = "unknown"


class DataSource(enum.StrEnum):
    RANGES = "ranges"
    ARCTOS = "arctos"


@dataclasses.dataclass
class MetricSpecimen:
    # Length measurements are stored in mm
    # Mass measurements are stored in g

    guid: str
    scientific_name: str
    collectors: str
    collected_date: datetime.date | None

    country: str | None
    state_prov: str | None
    county: str | None
    spec_locality: str | None
    dec_lat: float | None
    dec_long: float | None
    coordinate_uncertainty: float | None

    sex: Sex | None
    total_length: float | None
    tail_length: float | None
    hind_foot_with_claw: float | None
    ear_from_notch: float | None
    ear_from_crown: float | None
    tragus_length: float | None
    forearm_length: float | None
    weight: float | None
    unformatted_measurements: str | None

    life_stage: LifeStage | None
    testes_length: float | None
    testes_width: float | None
    embryo_count: int | None
    embryo_count_left: int | None
    embryo_count_right: int | None
    crown_rump_length: float | None
    scars: str
    reproductive_data: str | None

    source: DataSource
    ranges_date: datetime.date | None
    initials: str | None


@dataclasses.dataclass
class PartialSpecimen:
    guid: str
    scientific_name: str
    collectors: str
    collected_date: datetime.date | None

    country: str | None
    state_prov: str | None
    county: str | None
    spec_locality: str | None
    dec_lat: float | None
    dec_long: float | None
    coordinate_uncertainty: float | None

    sex: Sex | None
