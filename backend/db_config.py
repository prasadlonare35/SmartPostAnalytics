from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
import os
from dotenv import load_dotenv

load_dotenv()

# DataStax connection configuration
DATASTAX_CLIENT_ID = os.getenv('DATASTAX_CLIENT_ID')
DATASTAX_CLIENT_SECRET = os.getenv('DATASTAX_CLIENT_SECRET')
KEYSPACE = "social_media_analytics"

def get_cluster():
    """Create and return a connection to the DataStax cluster"""
    cloud_config = {
        'secure_connect_bundle': 'secure-connect-social-media-analytics.zip'
    }
    
    auth_provider = PlainTextAuthProvider(DATASTAX_CLIENT_ID, DATASTAX_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    return cluster

def get_session():
    """Get a session to the DataStax cluster"""
    cluster = get_cluster()
    session = cluster.connect()
    session.row_factory = dict_factory
    return session

def init_database(session=None):
    """Initialize the database with required tables"""
    if session is None:
        session = get_session()
    
    try:
        # Create keyspace if not exists
        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
            WITH replication = {{
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }}
        """)
        
        # Switch to the keyspace
        session.set_keyspace(KEYSPACE)
        
        # Create posts table
        session.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id text PRIMARY KEY,
                type text,
                content text,
                likes int,
                shares int,
                comments int,
                timestamp timestamp,
                comment_list list<text>
            )
        """)
        
        # Create analytics table
        session.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                post_id text,
                date date,
                hour int,
                engagement_count int,
                sentiment_score float,
                PRIMARY KEY ((post_id), date, hour)
            )
        """)
        
        # Create user_engagement table
        session.execute("""
            CREATE TABLE IF NOT EXISTS user_engagement (
                user_id text,
                post_id text,
                engagement_type text,
                timestamp timestamp,
                PRIMARY KEY ((user_id, post_id))
            )
        """)
        
        # Create content_performance table
        session.execute("""
            CREATE TABLE IF NOT EXISTS content_performance (
                post_type text,
                date date,
                hour int,
                total_engagement int,
                avg_sentiment float,
                PRIMARY KEY ((post_type), date, hour)
            )
        """)
        
        print("Database initialized successfully")
        return session
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
