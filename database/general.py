from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# async database engine, and use aiomysql as operation core
#
# Notice:
# If you want to use async with sqlalchemy,
# then the operation core must be async-competible
# engine = create_async_engine(
#     f"mysql+aiomysql://"
#     f"{configs.sql.username}:{configs.sql.password}"
#     f"@{configs.sql.host}/{configs.sql.dbname}"
# )

# # async version sessionmaker
# session_maker = async_sessionmaker(_engine_instance)
