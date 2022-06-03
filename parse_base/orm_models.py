import datetime
import os
import psycopg2
from sqlalchemy import Table, create_engine, Column, Integer, String, \
    UniqueConstraint, Index, Date, DateTime, Float, ForeignKey, BigInteger, select
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

postgres_url = os.environ.get('ENGINE')
engine = create_engine(postgres_url)

# engine = create_engine("postgresql://tesseractmaks:Vfrcvfrc1@localhost/parse")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base(bind=engine)


class Lids(Base):
    __tablename__ = "lids"
    category_id = Column(Integer, ForeignKey("categories.id_categories"), nullable=False)
    Category = relationship("Category", back_populates="lids")


    # __tableargs__ = (Index("common_index", "short_name", "full_name", "inn", "ogrn", "email",
    #                        "phone", "type_lids", "status_registration_eis", "date_registration_eis",
    #                        "created_on", "updated_on", "address_yur", "address_postal"))

    id = Column(Integer, primary_key=True)
    short_name = Column(String(400), index=True)
    full_name = Column(String(400), nullable=False, default='char', index=True)
    inn = Column(BigInteger, nullable=False, default=0,  index=True)
    kpp = Column(BigInteger)
    ogrn = Column(BigInteger, index=True)
    email = Column(String(400))
    phone = Column(String(400))
    number_in_reestr = Column(BigInteger)
    date_registration_ifns = Column(Date())
    status_registration_eis = Column(String(20))
    date_registration_eis = Column(Date())
    created_on = Column(Date(), default=datetime.datetime.now)
    updated_on = Column(DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    address_yur = Column(String(400))
    # блок фильтров
    ooo_address_index = Column(BigInteger, index=True)
    ooo_address_city = Column(String(400), index=True)
    ooo_address_street = Column(String(400), index=True)
    ip_first_name = Column(String(100))
    ip_last_name = Column(String(100))
    ip_middle_name = Column(String(100))
    region = Column(String(100))
    fed_okrug = Column(String(100))

    # коды
    region_kod = Column(BigInteger)
    fed_okrug_kod = Column(Integer)
    postal_index_region_kod = Column(BigInteger) # первые две цифры индекса это регион
    ifns_kod = Column(Integer)

    # данные из статистики
    region_kod_rabot = Column(Integer)
    zakazchiki_inn = Column(BigInteger)
    okpd_2 = Column(Float)

    def __repr__(self):
        return f"{self.id}, {self.short_name}, {self}, {self.full_name}, {self.inn}," \
               f" {self.kpp}, {self.ogrn}, {self.email}, {self.phone}, {self.type_lids}, {self.number_in_reestr}," \
               f" {self.date_registration_ifns}, {self.status_registration_eis}, {self.date_registration_eis}," \
               f" {self.created_on}, {self.updated_on}, {self.address_yur}, {self.ooo_address_index}," \
               f" {self.ooo_address_city}, {self.ooo_address_city}, {self.ip_first_name}, {self.ip_last_name}," \
               f" {self.ip_middle_name}, {self.region}, {self.fed_okrug}, {self.region_kod}, {self.fed_okrug_kod}," \
               f" {self.postal_index_region_kod}, {self.ifns_kod}, {self.region_kod_rabot}, {self.zakazchiki_inn}," \
               f" {self.okpd_2}"


class Category(Base):
    __tablename__ = "categories"
    id_categories = Column(Integer, primary_key=True)
    name = Column(String(100))
    lids = relationship("Lids", back_populates="Category", cascade="all, delete")

    def __repr__(self):
        return f"{self.id}, {self.name}"


if __name__ == "__main__":
    Base.metadata.create_all()
    cat = Category(name="ooo")
    catip = Category(name="ip")
    session.add(cat)
    session.add(catip)
    session.commit()

# q = session.query(Lids.full_name).filter(Lids.ogrn == 318112100016750).delete()
# print(q)
# err = session.query(Lids).filter_by(ogrn=ip["ogrn"]).one()
# sel = select(Lids)
# conn = engine.connect()
# result = conn.execute(sel)
#
# print(result)
#
# for ogrn in result:
#     print(ogrn)






# lids = Table("lids")
# x=default=datetime.date.today()
# print(x)
# print(len("7705860470"))