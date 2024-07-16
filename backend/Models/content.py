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

from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime, func, Integer
from Models import db_metadata

class content(db_metadata):
    __tablename__ = 'api_content'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    api_code = Column(BigInteger, nullable=False)
    id_campaign = Column(Integer, ForeignKey('api_campaign.id'))
    id_company = Column(Integer, ForeignKey('api_company.id'))
    user_type = Column(String(45), nullable=False)
    to = Column(String(255), nullable=True)
    mailer = Column(String(255), nullable=False)
    subject = Column(String(512), nullable=False)
    sent_at = Column(DateTime, nullable=False)
    token = Column(String(100), nullable=False)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    inserted = Column(DateTime, nullable=False, default=func.now())

    