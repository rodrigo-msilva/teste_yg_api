'''
  "id": 1811658,
        "id_campaign": 2373,
        "campaign": "UNIFENAS PÓS GRADUAÇÃO INSCRITO INCOMPLETO EMAIL 2",
        "company": "Unifenas Pós Graduação",
        "user_type": "Lead",
        "to": "dr.sergiothome@gmail.com",
        "mailer": "FlowHubspotMailer#general",
        "subject": "Veja só que oportunidade incrível preparamos para você!",
        "sent_at": "2024-07-07T13:33:42.000-03:00",
        "token": "2V17mSFwHYgOaBKtcz3O6NIoEJcEkbGl",
        "opened_at": "2024-07-07T13:36:38.000-03:00",
        "clicked_at": null
'''

from sqlalchemy import Column, String, BigInteger, DateTime, func, Integer
from Models import db_metadata

class company(db_metadata):
    __tablename__ = 'api_company'
    id = Column(Integer, primary_key=True,autoincrement=True)
    company_name = Column(String(512), nullable=False,unique=True)
    inserted = Column(DateTime, nullable=False, default=func.now())