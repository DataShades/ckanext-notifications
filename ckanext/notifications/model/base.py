from sqlalchemy.ext.declarative import declarative_base

from ckan import model

Base = declarative_base(metadata=model.meta.metadata)
