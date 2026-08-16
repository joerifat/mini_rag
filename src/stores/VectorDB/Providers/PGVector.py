from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnum import PGVectorDistanceMethods,PGVectorIndexingMethods,PGVectorTableschema
import logging
from sqlalchemy.sql import text as sql_text
import json
from models.schemas.minirag.postgresSchema.allschemas import Retrived_chunks


logger=logging.getLogger("uvicorn")



class PGVectorDB(VectorDBInterface):
    def __init__(self,client_db,   distance_method: str,embedding_size: int =768,
                 indexing_method: str = PGVectorIndexingMethods.HNSW.value,
                 index_threshold:int = 1000):
        
        self.client_db=client_db
        self.embedding_size=embedding_size
        self.index_threshold=index_threshold

        if distance_method not in (
            PGVectorDistanceMethods.DOT.value,
            PGVectorDistanceMethods.COSINE.value
        ):
            raise ValueError(
                f"Unsupported distance method: {distance_method}"
            )

        if indexing_method not in (
            PGVectorIndexingMethods.HNSW.value,
            PGVectorIndexingMethods.IVFFLAT.value
        ):
            raise ValueError(
                f"Unsupported indexing method: {indexing_method}"
            )

        self.indexing_method=indexing_method
        self.distance_method=distance_method

    async def deafult_index_name(self,collection_name:str):
        return f"{collection_name}_vector_index"


    async def connect(self):
        async with self.client_db() as session:
            async with session.begin():
                await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))

    async def disconnect(self):
        pass

    async def is_collection_exit(self, collection_name):
        async with self.client_db() as session:
            async with session.begin():
                query=sql_text("SELECT EXISTS(SELECT 1 FROM pg_tables WHERE tablename= :collection_name)")
                result= await session.execute(query,{"collection_name":collection_name})

        return result.scalar()

    async def list_all_collections(self):
        async with self.client_db() as session:
            async with session.begin():
                query=sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                result=await session.execute(query,{"prefix":f"{PGVectorTableschema._PREFIX.value}%"})

        return result.scalars().all()

    async def get_collection_info(self, collection_name):
        async with self.client_db() as session:
            async with session.begin():
                query=sql_text("SELECT schemaname, tablename, tableowner, tablespace, hasindexes FROM pg_tables " \
                "WHERE tablename= :collection_name")
                counts_table=sql_text(f"SELECT COUNT(*) FROM {collection_name}")

                collection_exists= await  self.is_collection_exit(collection_name=collection_name)
                if not collection_exists:
                    raise ValueError(f"no collection name : {collection_name}")

                result_query= await session.execute(query,{"collection_name":collection_name})
                result_count= await session.execute(counts_table)

                table_info=result_query.fetchone()
                table_rows=result_count.scalar_one()

        return {
            "Table_info":{
                "table_name":table_info.tablename,
                "schema_name":table_info.schemaname,
                "table_owner":table_info.tableowner,
                "table_space":table_info.tablespace,
                "hasindexes":table_info.hasindexes,
            },
            "rows_count":table_rows
        }

    async def delete_collection(self, collection_name):
        async with self.client_db() as session:
            async with session.begin():
                logger.info(f"Deleting table : {collection_name}")

                query=sql_text(f"DROP TABLE IF EXISTS {collection_name}")
                result= await session.execute(query)

                logger.info(f"The table has been deleted")

        return True


    async def create_collection(self, collection_name, embedding_size, do_rest):
        if do_rest:
            await self.delete_collection(collection_name=collection_name)

        collection_exists=await self.is_collection_exit(collection_name=collection_name)
        if collection_exists:
            raise ValueError(f"The collection with name {collection_name} exists")
        async with self.client_db() as session:
            async with session.begin():

                query=sql_text(f"CREATE TABLE {collection_name}("
                               f"{PGVectorTableschema.ID.value} BIGSERIAL PRIMARY KEY,"
                               f"{PGVectorTableschema.TEXT.value} TEXT,"
                               f"{PGVectorTableschema.VECTOR.value} VECTOR({embedding_size}),"
                               f"{PGVectorTableschema.CHUNK_ID.value} INTEGER,"
                               f"{PGVectorTableschema.METADATA.value} JSONB DEFAULT \'{{}}\',"
                               f'FOREIGN KEY ({PGVectorTableschema.CHUNK_ID.value}) REFERENCES "Chunks"("Chunks_id")'
                            ")")

                await session.execute(query)
            return True
        return False


    async def is_index_exists(self,collection_name:str) -> bool:
        index_name=await self.deafult_index_name(collection_name=collection_name)
        collection_exists=await self.is_collection_exit(collection_name=collection_name)
        if not collection_exists:
            raise ValueError(f"The collection with name {collection_name} does't exists")

        async with self.client_db() as session:
            async with session.begin():
                query=sql_text("""SELECT 1 FROM pg_indexes WHERE tablename= :collection_name
                                AND indexname= :index_name""")#انا عايز اشوف هل بيحتوي عل ال index اللي انا عملتو ولا لا 

                result= await session.execute(query,{"collection_name":collection_name,"index_name":index_name})

        return bool(result.scalar_one_or_none())


    async def create_vector_index(self,collection_name:str,index_type:str =PGVectorIndexingMethods.HNSW.value):
        collection_exists=await self.is_collection_exit(collection_name=collection_name)
        if not collection_exists:
            raise ValueError(f"The collection with name {collection_name} does't exists")

        index_exist=await self.is_index_exists(collection_name=collection_name)
        if index_exist:
            return False

        index_name=await self.deafult_index_name(collection_name=collection_name)

        async with self.client_db() as session:
            async with session.begin():
                create_query=sql_text(f"""
                        CREATE INDEX {index_name} ON {collection_name}
                        USING {index_type}
                        ({PGVectorTableschema.VECTOR.value} {self.distance_method})
                        """)
                count_query=sql_text(f"SELECT COUNT(*) FROM {collection_name}")

                count_result=await session.execute(count_query)
                if count_result.scalar()<self.index_threshold:
                    logger.error("The number of the rows in the table is less than the required number to create index")
                    return False

                await session.execute(create_query)

                return True
        return False


    async def reset_index_vector(self,collection_name:str , index_type:str =PGVectorIndexingMethods.HNSW.value):
        collection_exists=await self.is_collection_exit(collection_name=collection_name)
        if not collection_exists:
            raise ValueError(f"The collection with name {collection_name} does't exists")
        index_name=await self.deafult_index_name(collection_name=collection_name)

        async with self.client_db() as session:
            async with session.begin():
                logger.info("Reseting index")
                reset_sql=sql_text(f"DROP INDEX IF EXISTS {index_name}")
                await session.execute(reset_sql)


        return await self.create_vector_index(collection_name=collection_name,index_type=index_type)



    async def insert_one(self, collection_name, text, vector, metadata = None, record_id = None):
        collection_exist= await self.is_collection_exit(collection_name=collection_name)
        if not collection_exist:
            raise ValueError(f"This Table {collection_name} does't exist")

        if not record_id:
            raise ValueError("Can't insert Chunk without vector_id")
        
        async with self.client_db() as session:
            async with session.begin():
                query=sql_text(f""" 
                                INSERT INTO {collection_name}
                                ({PGVectorTableschema.TEXT.value},{PGVectorTableschema.VECTOR.value},{PGVectorTableschema.METADATA.value},{PGVectorTableschema.CHUNK_ID.value})
                                VALUES
                                (:text,:vector,:metadata,:record_id)
                                """)
                metadata_josn=json.dumps(metadata,ensure_ascii=False) if metadata is not None else "{}"
                vector=str(vector)

                result=await session.execute(query,{
                    "text":text,
                    "vector":vector,
                    "metadata":metadata_josn,
                    "record_id":record_id
                })
        await self.create_vector_index(collection_name=collection_name,index_type=PGVectorIndexingMethods.HNSW.value)
        return True



    async def insert_many(self, collection_name, text, vector, metadata = None, record_id = None, batch_size = 50):

        collection_exist= await self.is_collection_exit(collection_name=collection_name)
        if not collection_exist:
            raise ValueError(f"This Table {collection_name} does't exists")

        if record_id is None:
           raise ValueError("record_ids are required")

        if not metadata or len(metadata)==0:
            metadata=[None]*len(text)

        if not (len(text)==len(vector)==len(metadata)==len(record_id)):
            raise ValueError("texts, vectors and record_ids must have same length")


        async with self.client_db() as session:
            async with session.begin():
                
                for i in range(0,len(text),batch_size):
                    batch_text=text[i:i+batch_size]
                    batch_vector=vector[i:i+batch_size]
                    batch_metadata=metadata[i:i+batch_size]
                    batch_record_id=record_id[i:i+batch_size]

                    values=[]

                    for _text,_vector,_metadata,_record_id in zip(batch_text,batch_vector,batch_metadata,batch_record_id):
                        metadata_json=json.dumps(_metadata,ensure_ascii=False) if _metadata is not None else "{}"
                        values.append({"text":_text,"vector":_vector,"metadata":metadata_json,"chunk_id":_record_id})


                    batch_insert_sql=sql_text(f"""
                                            INSERT INTO {collection_name}
                                            ({PGVectorTableschema.TEXT.value},{PGVectorTableschema.VECTOR.value},{PGVectorTableschema.METADATA.value},{PGVectorTableschema.CHUNK_ID.value})
                                            VALUES
                                            (:text, :vector, :metadata, :chunk_id)                              
                                                """)

                    await session.execute(batch_insert_sql,values)
        await self.create_vector_index(collection_name=collection_name,index_type=PGVectorIndexingMethods.HNSW.value)
        return True

                

    async def search_by_vector(self, collection_name, vector, limit):
        collection_exist= await self.is_collection_exit(collection_name=collection_name)
        if not collection_exist:
            raise ValueError(f"This Table {collection_name} does't exists")


        vector=str(vector)

        async with self.client_db() as session:
            async with session.begin():
                search_query=sql_text(f"""
                                       SELECT {PGVectorTableschema.TEXT.value}, 1-({PGVectorTableschema.VECTOR.value}<=> :vector) as score
                                       FROM {collection_name}
                                       ORDER BY score DESC
                                       LIMIT {limit} 
                                        """)

                result=await session.execute(search_query,{"vector":vector})
                records=result.fetchall()

        return [Retrived_chunks(
            text=record.text,
            score=record.score)
            for record in records]

        

                    
                


                        

                
                






                



                    
                        

