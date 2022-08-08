from sqlalchemy.engine import url
from sqlalchemy_cubrid.dialect import CubridDialect


def test_cubrid_connection_string():
    dialect = CubridDialect()
    username = "dba"
    password = f"1234"
    host = "127.0.0.1"
    port = 33000
    database = "demodb"
    u = url.make_url(
        f"cubrid://{username}:{password}@{host}:{port}/{database}"
    )
    args, _ = dialect.create_connect_args(u)

    assert args[0] == f"CUBRID:127.0.0.1:33000:demodb:::"
    assert args[1] == f"dba"
    assert args[2] == f"1234"
