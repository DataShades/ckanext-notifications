from sqlalchemy.ext.declarative import declarative_base

import ckan.model as model

Base = declarative_base(metadata=model.meta.metadata)
