from datetime import datetime, date
from db_config import get_session, KEYSPACE, init_database
from cassandra.query import SimpleStatement
import pandas as pd

class DataStaxService:
    def __init__(self):
        self.session = get_session()
        # Initialize database (create keyspace and tables)
        init_database(self.session)
        # Set keyspace after creation
        self.session.set_keyspace(KEYSPACE)
    
    def save_post(self, post_data):
        """Save a post to DataStax"""
        query = """
            INSERT INTO posts (
                id, type, content, likes, shares, comments, timestamp, comment_list
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.session.execute(query, (
            post_data["id"],
            post_data["type"],
            post_data["content"],
            post_data["likes"],
            post_data["shares"],
            post_data["comments"],
            datetime.fromisoformat(post_data["timestamp"]),
            post_data.get("comment_list", [])
        ))
    
    def get_post(self, post_id):
        """Retrieve a post by ID"""
        query = "SELECT * FROM posts WHERE id = %s"
        result = self.session.execute(query, (post_id,))
        return result.one()
    
    def save_analytics(self, post_id, engagement_count, sentiment_score):
        """Save analytics data"""
        now = datetime.now()
        query = """
            INSERT INTO analytics (
                post_id, date, hour, engagement_count, sentiment_score
            ) VALUES (%s, %s, %s, %s, %s)
        """
        self.session.execute(query, (
            post_id,
            date(now.year, now.month, now.day),
            now.hour,
            engagement_count,
            sentiment_score
        ))
    
    def get_performance_by_type(self, post_type, start_date, end_date):
        """Get performance metrics for a post type within a date range"""
        query = """
            SELECT date, hour, total_engagement, avg_sentiment
            FROM content_performance
            WHERE post_type = %s AND date >= %s AND date <= %s
        """
        return self.session.execute(query, (post_type, start_date, end_date))
    
    def get_engagement_trends(self):
        """Get engagement trends across all post types"""
        query = """
            SELECT post_type, date, SUM(total_engagement) as total_engagement
            FROM content_performance
            GROUP BY post_type, date
            ALLOW FILTERING
        """
        return self.session.execute(query)
    
    def save_user_engagement(self, user_id, post_id, engagement_type):
        """Save user engagement data"""
        query = """
            INSERT INTO user_engagement (
                user_id, post_id, engagement_type, timestamp
            ) VALUES (%s, %s, %s, %s)
        """
        self.session.execute(query, (
            user_id,
            post_id,
            engagement_type,
            datetime.now()
        ))
    
    def get_user_engagement_history(self, user_id):
        """Get engagement history for a user"""
        query = """
            SELECT post_id, engagement_type, timestamp
            FROM user_engagement
            WHERE user_id = %s
        """
        return self.session.execute(query, (user_id,))
    
    def update_content_performance(self, post_type, engagement_delta, sentiment_score):
        """Update content performance metrics"""
        now = datetime.now()
        today = date(now.year, now.month, now.day)
        
        query = """
            UPDATE content_performance
            SET total_engagement = total_engagement + %s,
                avg_sentiment = %s
            WHERE post_type = %s AND date = %s AND hour = %s
        """
        self.session.execute(query, (
            engagement_delta,
            sentiment_score,
            post_type,
            today,
            now.hour
        ))
    
    def get_analytics_dataframe(self, start_date, end_date):
        """Get analytics data as a pandas DataFrame"""
        query = """
            SELECT post_id, date, hour, engagement_count, sentiment_score
            FROM analytics
            WHERE date >= %s AND date <= %s
            ALLOW FILTERING
        """
        rows = self.session.execute(query, (start_date, end_date))
        return pd.DataFrame(list(rows))

    def close(self):
        """Close the DataStax session"""
        if self.session:
            self.session.shutdown()
