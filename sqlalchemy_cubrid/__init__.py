from sqlalchemy.dialects import registry

__version__ = '0.0.1'
registry.register("cubrid", "sqlalchemy_cubrid.dialect", "CubridDialect")
