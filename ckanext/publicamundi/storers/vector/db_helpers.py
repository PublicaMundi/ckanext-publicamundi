import psycopg2
import urlparse  
class DB:    
  
    def __init__(self,db_conn_params):
	result = urlparse.urlparse(db_conn_params)
	user = result.username
	password = result.password
	database = result.path[1:]
	hostname = result.hostname
	self.conn = psycopg2.connect(database=database, user=user, password=password,host=hostname)
        self.cursor=self.conn.cursor()
    def check_if_table_exists(self,table_name):
	self.cursor.execute("SELECT * FROM information_schema.tables WHERE table_name='%s'"%table_name)
	table_exists=bool(self.cursor.rowcount)
	if table_exists:
	    return True
	else:
	    return False
    def create_table(self,table_name,fin,geometry,srs,coordinate_dimension):
        self.cursor.execute("CREATE TABLE \"%s\" (_id serial PRIMARY KEY%s);"%(table_name,fin))
        self.cursor.execute("SELECT AddGeometryColumn ('%s','the_geom',%s,'%s',%s);"%(table_name,srs,geometry,coordinate_dimension))        
    
    def insert_to_table(self,table,fields,geometry_text,convert_to_multi,srs):
	if convert_to_multi:
	    insert=("INSERT INTO \"%s\" VALUES (%s ST_Multi(ST_GeomFromText('%s',%s)));"%(table,fields,geometry_text,srs))
	else:
	    insert=("INSERT INTO \"%s\" VALUES (%s ST_GeomFromText('%s',%s));"%(table,fields,geometry_text,srs)) 
	self.cursor.execute(insert)
    
    def create_spatial_index(self,table):
	indexing=("CREATE INDEX \"%s_the_geom_idx\" ON \"%s\" USING GIST(the_geom);"%(table,table)) 
	self.cursor.execute(indexing)
    
    def drop_table(self,table):
	indexing=("DROP TABLE \"%s\";"%(table)) 
	self.cursor.execute(indexing)
	
    def commit_and_close(self):
	self.conn.commit()
	self.cursor.close()
	self.conn.close()