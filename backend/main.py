from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from datetime import datetime, timedelta
import random
from fastapi.responses import FileResponse, StreamingResponse
import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import UploadFile, File
from io import BytesIO
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from io import BytesIO
from datastax_service import DataStaxService
from db_config import init_database

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DataStax connection
db = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    global db
    try:
        db = DataStaxService()
        print("Database connection established")
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    global db
    if db:
        db.close()
        print("Database connection closed")

class Post(BaseModel):
    id: str
    type: str
    likes: int
    shares: int
    comments: int
    timestamp: datetime
    content: Optional[str] = None
    comment_list: Optional[List[str]] = []

class BatchPostInput(BaseModel):
    posts: List[Post]

@app.get("/")
async def read_root():
    return {"message": "Social Media Analytics API"}

@app.get("/posts")
async def get_posts():
    posts = db.get_all_posts()
    return posts

@app.get("/analytics/{post_type}")
async def get_analytics(post_type: str):
    filtered_posts = db.get_posts_by_type(post_type)
    if not filtered_posts:
        return {
            "average_likes": 0,
            "average_shares": 0,
            "average_comments": 0
        }
    
    avg_likes = sum(post["likes"] for post in filtered_posts) / len(filtered_posts)
    avg_shares = sum(post["shares"] for post in filtered_posts) / len(filtered_posts)
    avg_comments = sum(post["comments"] for post in filtered_posts) / len(filtered_posts)
    
    return {
        "average_likes": avg_likes,
        "average_shares": avg_shares,
        "average_comments": avg_comments
    }

@app.get("/performance-analysis")
async def get_performance_analysis():
    # Get analytics for each post type
    post_types = ["carousel", "reel", "static"]
    analytics = {}
    
    for post_type in post_types:
        analytics[post_type] = await get_analytics(post_type)
    
    # Calculate engagement rates
    engagement_rates = {}
    for post_type, metrics in analytics.items():
        engagement_rate = (metrics["average_likes"] + metrics["average_shares"] + metrics["average_comments"]) / 3
        engagement_rates[post_type] = engagement_rate
    
    # Prepare data for Gemini analysis
    analysis_prompt = f"""
    Analyze the performance of different post types on social media with the following metrics:
    
    Carousel Posts:
    - Average Likes: {analytics['carousel']['average_likes']:.1f}
    - Average Shares: {analytics['carousel']['average_shares']:.1f}
    - Average Comments: {analytics['carousel']['average_comments']:.1f}
    - Engagement Rate: {engagement_rates['carousel']:.1f}
    
    Reel Posts:
    - Average Likes: {analytics['reel']['average_likes']:.1f}
    - Average Shares: {analytics['reel']['average_shares']:.1f}
    - Average Comments: {analytics['reel']['average_comments']:.1f}
    - Engagement Rate: {engagement_rates['reel']:.1f}
    
    Static Posts:
    - Average Likes: {analytics['static']['average_likes']:.1f}
    - Average Shares: {analytics['static']['average_shares']:.1f}
    - Average Comments: {analytics['static']['average_comments']:.1f}
    - Engagement Rate: {engagement_rates['static']:.1f}
    
    Please provide:
    1. A comparison of performance between different post types
    2. Recommendations for content strategy
    3. Key insights about engagement patterns
    4. Suggestions for improvement
    """
    
    try:
        response = model.generate_content(analysis_prompt)
        ai_analysis = response.text
    except Exception as e:
        ai_analysis = "Error generating AI analysis. Please try again later."
    
    return {
        "analytics": analytics,
        "engagement_rates": engagement_rates,
        "ai_analysis": ai_analysis
    }

@app.get("/insights/{post_type}")
async def get_insights(post_type: str):
    analytics = await get_analytics(post_type)
    insights = generate_insights(post_type, analytics)
    return {"insights": insights}

@app.get("/time-analytics")
async def get_time_analytics():
    time_periods = ['Morning', 'Afternoon', 'Evening']
    time_data = []
    for period in time_periods:
        period_data = {
            'period': period,
            'carousel': random.randint(50, 200),
            'reel': random.randint(100, 300),
            'static': random.randint(30, 150)
        }
        time_data.append(period_data)
    return time_data

@app.get("/trending-hashtags")
async def get_trending_hashtags():
    hashtags = [
        {"tag": "#digitalmarketing", "count": random.randint(100, 1000)},
        {"tag": "#socialmedia", "count": random.randint(100, 1000)},
        {"tag": "#contentcreator", "count": random.randint(100, 1000)},
        {"tag": "#marketing", "count": random.randint(100, 1000)},
        {"tag": "#business", "count": random.randint(100, 1000)}
    ]
    return sorted(hashtags, key=lambda x: x['count'], reverse=True)

@app.post("/posts")
async def create_post(post: Post):
    """Create a new post with DataStax integration"""
    post_dict = post.dict()
    db.save_post(post_dict)
    
    # Calculate initial engagement metrics
    total_engagement = post.likes + post.shares + post.comments
    
    # Save initial analytics
    db.save_analytics(
        post_dict["id"],
        total_engagement,
        0.0  # Initial neutral sentiment score
    )
    
    return {"message": "Post created successfully", "post": post_dict}

@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    """Get a post by ID from DataStax"""
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/analytics/performance/{post_type}")
async def get_type_performance(
    post_type: str,
    start_date: str,
    end_date: str
):
    """Get performance metrics for a post type"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        performance_data = db.get_performance_by_type(post_type, start, end)
        return list(performance_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/trends")
async def get_trends():
    """Get engagement trends from DataStax"""
    try:
        trends_data = db.get_engagement_trends()
        return list(trends_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sentiment-analysis/{post_id}")
async def get_sentiment_analysis(post_id: str):
    # Find the post
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Prepare comments for analysis
    comments = post.get("comment_list", [])
    if not comments:
        return {"message": "No comments to analyze"}
    
    # Prepare prompt for Gemini
    analysis_prompt = f"""
    Analyze the sentiment and key themes in these comments for a {post['type']} post about "{post['content']}":

    Comments:
    {chr(10).join('- ' + comment for comment in comments)}

    Please provide:
    1. Overall sentiment (positive, negative, or neutral)
    2. Key themes or topics mentioned
    3. Common feedback points
    4. Suggestions based on the comments
    5. Engagement quality analysis
    
    Format the response in a clear, structured way.
    """
    
    try:
        response = model.generate_content(analysis_prompt)
        sentiment_analysis = response.text
    except Exception as e:
        sentiment_analysis = "Error generating sentiment analysis. Please try again later."
    
    return {
        "post_type": post["type"],
        "content": post["content"],
        "comment_count": len(comments),
        "sentiment_analysis": sentiment_analysis
    }

@app.get("/content-calendar")
async def get_content_calendar():
    # Analyze existing post performance
    post_types = ["carousel", "reel", "static"]
    performance_data = {}
    
    for post_type in post_types:
        analytics = await get_analytics(post_type)
        performance_data[post_type] = analytics
    
    # Prepare prompt for content calendar recommendations
    calendar_prompt = f"""
    Based on this performance data for different post types:

    {json.dumps(performance_data, indent=2)}

    Please provide:
    1. Recommended posting schedule for next week
    2. Content ideas for each post type
    3. Best times to post each type of content
    4. Content themes that might perform well
    5. Engagement strategies for each post type
    
    Consider current engagement rates and platform best practices.
    """
    
    try:
        response = model.generate_content(calendar_prompt)
        calendar_recommendations = response.text
    except Exception as e:
        calendar_recommendations = "Error generating recommendations. Please try again later."
    
    return {
        "performance_data": performance_data,
        "calendar_recommendations": calendar_recommendations
    }

@app.post("/batch-posts")
async def create_batch_posts(batch: BatchPostInput):
    """
    Add multiple posts at once.
    Example:
    {
        "posts": [
            {
                "id": "7",
                "type": "reel",
                "likes": 300,
                "shares": 80,
                "comments": 45,
                "timestamp": "2024-12-31T14:00:00",
                "content": "New feature demo",
                "comment_list": ["Great feature!", "Very useful"]
            },
            {
                "id": "8",
                "type": "carousel",
                "likes": 250,
                "shares": 60,
                "comments": 35,
                "timestamp": "2024-12-31T15:00:00",
                "content": "Product updates",
                "comment_list": ["Awesome updates!", "Can't wait"]
            }
        ]
    }
    """
    added_posts = []
    for post in batch.posts:
        post_dict = post.dict()
        db.save_post(post_dict)
        added_posts.append(post_dict)
    
    return {
        "message": f"Successfully added {len(added_posts)} posts",
        "added_posts": added_posts
    }

@app.post("/import-csv")
async def import_csv(file: UploadFile = File(...)):
    """
    Import posts from a CSV file.
    CSV should have headers:
    id,type,likes,shares,comments,timestamp,content
    """
    try:
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        
        # Convert DataFrame to posts
        new_posts = []
        for _, row in df.iterrows():
            post = {
                "id": str(row["id"]),
                "type": row["type"],
                "likes": int(row["likes"]),
                "shares": int(row["shares"]),
                "comments": int(row["comments"]),
                "timestamp": row["timestamp"],
                "content": row["content"],
                "comment_list": []  # Initialize empty comment list for imported posts
            }
            db.save_post(post)
            new_posts.append(post)
        
        return {
            "message": f"Successfully imported {len(new_posts)} posts from CSV",
            "imported_posts": new_posts
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")

@app.get("/export-csv")
async def export_csv():
    """Export all posts to CSV format"""
    posts = db.get_all_posts()
    df = pd.DataFrame(posts)
    
    # Create CSV in memory
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Return CSV file
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=posts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("../frontend/public/favicon.ico")

@app.get("/optimize-content/{post_id}")
async def optimize_content(post_id: str):
    """
    Analyze a post's content and provide optimization suggestions using Gemini AI.
    """
    # Find the post
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Prepare prompt for content optimization
    optimization_prompt = f"""
    Analyze this social media post and provide content optimization suggestions:

    Post Type: {post['type']}
    Content: "{post['content']}"
    Current Performance:
    - Likes: {post['likes']}
    - Shares: {post['shares']}
    - Comments: {post['comments']}

    Please provide:
    1. Content Strengths: What works well in this post
    2. Areas for Improvement: Specific suggestions to enhance engagement
    3. SEO Optimization: Keywords and hashtag suggestions
    4. Call-to-Action: Suggestions for better engagement
    5. Visual Elements: Recommendations for {post['type']} format
    """
    
    try:
        response = model.generate_content(optimization_prompt)
        optimization_analysis = response.text
        
        return {
            "post_id": post_id,
            "post_type": post["type"],
            "original_content": post["content"],
            "optimization_suggestions": optimization_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating optimization suggestions: {str(e)}")

@app.get("/generate-hashtags")
async def generate_hashtags(content: str, category: str = "general"):
    """
    Generate relevant hashtags for a given content and category using Gemini AI.
    """
    hashtag_prompt = f"""
    Generate relevant and trending hashtags for this social media content:

    Content: "{content}"
    Category: {category}

    Please provide:
    1. Popular Hashtags: Widely used hashtags in this category
    2. Niche Hashtags: More specific to the content
    3. Trending Hashtags: Currently popular related hashtags
    4. Brand-building Hashtags: For consistent branding
    5. Engagement Hashtags: To increase post visibility

    Format the response as a structured list with categories.
    """
    
    try:
        response = model.generate_content(hashtag_prompt)
        hashtag_suggestions = response.text
        
        return {
            "content": content,
            "category": category,
            "hashtag_suggestions": hashtag_suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating hashtags: {str(e)}")

@app.get("/analyze-audience")
async def analyze_audience():
    """
    Analyze audience behavior and engagement patterns using Gemini AI.
    """
    # Calculate engagement metrics for analysis
    engagement_data = {}
    post_types = ["carousel", "reel", "static"]
    
    for post_type in post_types:
        filtered_posts = db.get_posts_by_type(post_type)
        if filtered_posts:
            avg_likes = sum(post["likes"] for post in filtered_posts) / len(filtered_posts)
            avg_shares = sum(post["shares"] for post in filtered_posts) / len(filtered_posts)
            avg_comments = sum(post["comments"] for post in filtered_posts) / len(filtered_posts)
            engagement_data[post_type] = {
                "avg_likes": avg_likes,
                "avg_shares": avg_shares,
                "avg_comments": avg_comments
            }
    
    audience_prompt = f"""
    Analyze this audience engagement data and provide insights:

    Engagement Metrics by Post Type:
    {json.dumps(engagement_data, indent=2)}

    Please provide:
    1. Audience Behavior Patterns: What content resonates most
    2. Peak Engagement Times: When audience is most active
    3. Content Preferences: What types of content perform best
    4. Engagement Strategy: How to improve audience interaction
    5. Growth Opportunities: Areas for audience expansion
    """
    
    try:
        response = model.generate_content(audience_prompt)
        audience_analysis = response.text
        
        return {
            "engagement_data": engagement_data,
            "audience_insights": audience_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing audience: {str(e)}")

@app.post("/predict-performance")
async def predict_performance(
    post_type: str,
    content: str,
    time_of_day: str,
    target_audience: str = "general"
):
    """
    Predict potential performance of a post before publishing using Gemini AI.
    """
    # Get historical performance data for this post type
    similar_posts = db.get_posts_by_type(post_type)
    if not similar_posts:
        raise HTTPException(status_code=400, detail="No historical data for this post type")
    
    avg_performance = {
        "likes": sum(post["likes"] for post in similar_posts) / len(similar_posts),
        "shares": sum(post["shares"] for post in similar_posts) / len(similar_posts),
        "comments": sum(post["comments"] for post in similar_posts) / len(similar_posts)
    }
    
    prediction_prompt = f"""
    Predict the performance of this social media post:

    Post Details:
    - Type: {post_type}
    - Content: "{content}"
    - Time of Day: {time_of_day}
    - Target Audience: {target_audience}

    Historical Average Performance for {post_type}:
    - Likes: {avg_performance['likes']:.1f}
    - Shares: {avg_performance['shares']:.1f}
    - Comments: {avg_performance['comments']:.1f}

    Please provide:
    1. Performance Prediction: Expected engagement levels
    2. Success Factors: What might drive engagement
    3. Potential Challenges: What might limit performance
    4. Optimization Tips: How to improve potential performance
    5. Best Posting Strategy: Recommendations for maximum impact
    """
    
    try:
        response = model.generate_content(prediction_prompt)
        performance_prediction = response.text
        
        return {
            "post_type": post_type,
            "content": content,
            "historical_performance": avg_performance,
            "prediction_analysis": performance_prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting performance: {str(e)}")

@app.get("/visualize/engagement-trends")
async def visualize_engagement_trends():
    """
    Generate interactive visualizations for engagement trends across different post types.
    """
    # Prepare data for visualization
    post_types = ["carousel", "reel", "static"]
    metrics = {
        "likes": [],
        "shares": [],
        "comments": []
    }
    
    for post_type in post_types:
        filtered_posts = db.get_posts_by_type(post_type)
        if filtered_posts:
            metrics["likes"].append(sum(post["likes"] for post in filtered_posts) / len(filtered_posts))
            metrics["shares"].append(sum(post["shares"] for post in filtered_posts) / len(filtered_posts))
            metrics["comments"].append(sum(post["comments"] for post in filtered_posts) / len(filtered_posts))
    
    # Create subplot with 3 metrics
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Average Likes", "Average Shares", "Average Comments"),
        vertical_spacing=0.1
    )
    
    # Add bar traces for each metric
    fig.add_trace(go.Bar(x=post_types, y=metrics["likes"], name="Likes"), row=1, col=1)
    fig.add_trace(go.Bar(x=post_types, y=metrics["shares"], name="Shares"), row=2, col=1)
    fig.add_trace(go.Bar(x=post_types, y=metrics["comments"], name="Comments"), row=3, col=1)
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Engagement Metrics by Post Type",
        template="plotly_dark"
    )
    
    return fig.to_json()

@app.get("/visualize/performance-heatmap")
async def visualize_performance_heatmap():
    """
    Generate a heatmap showing performance patterns across different dimensions.
    """
    # Extract hour from timestamp and categorize performance
    performance_data = []
    for post in db.get_all_posts():
        timestamp = datetime.fromisoformat(post["timestamp"])
        hour = timestamp.hour
        total_engagement = post["likes"] + post["shares"] + post["comments"]
        performance_data.append({
            "hour": hour,
            "type": post["type"],
            "engagement": total_engagement
        })
    
    # Create pivot table for heatmap
    df = pd.DataFrame(performance_data)
    pivot_table = df.pivot_table(
        values="engagement",
        index="type",
        columns="hour",
        aggfunc="mean",
        fill_value=0
    )
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale="Viridis"
    ))
    
    fig.update_layout(
        title="Engagement Heatmap: Post Type vs. Hour of Day",
        xaxis_title="Hour of Day",
        yaxis_title="Post Type",
        template="plotly_dark"
    )
    
    return fig.to_json()

@app.get("/visualize/content-impact")
async def visualize_content_impact():
    """
    Generate a bubble chart showing the impact of different content types.
    """
    # Prepare data for visualization
    content_data = []
    for post in db.get_all_posts():
        engagement = post["likes"] + post["shares"] + post["comments"]
        virality = post["shares"] / (post["likes"] + 1)  # Adding 1 to avoid division by zero
        content_data.append({
            "type": post["type"],
            "engagement": engagement,
            "virality": virality,
            "comments": post["comments"]
        })
    
    df = pd.DataFrame(content_data)
    
    # Create bubble chart
    fig = px.scatter(
        df,
        x="engagement",
        y="virality",
        size="comments",
        color="type",
        hover_name="type",
        title="Content Impact Analysis",
        labels={
            "engagement": "Total Engagement",
            "virality": "Virality Score",
            "comments": "Number of Comments"
        }
    )
    
    fig.update_layout(template="plotly_dark")
    
    return fig.to_json()

@app.get("/visualize/sentiment-distribution/{post_id}")
async def visualize_sentiment_distribution(post_id: str):
    """
    Generate a pie chart showing sentiment distribution in comments.
    """
    post = db.get_post(post_id)
    if not post or not post.get("comment_list"):
        raise HTTPException(status_code=404, detail="Post or comments not found")
    
    # Analyze sentiment for each comment
    sentiment_prompt = f"""
    Analyze the sentiment of these comments and categorize them as Positive, Negative, or Neutral.
    Return only the numbers in this format: positive,negative,neutral

    Comments:
    {chr(10).join(post['comment_list'])}
    """
    
    try:
        response = model.generate_content(sentiment_prompt)
        sentiments = response.text.strip().split(',')
        positive, negative, neutral = map(int, sentiments)
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Positive', 'Negative', 'Neutral'],
            values=[positive, negative, neutral],
            hole=.3
        )])
        
        fig.update_layout(
            title=f"Sentiment Distribution for Post {post_id}",
            template="plotly_dark"
        )
        
        return fig.to_json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiments: {str(e)}")

def generate_insights(post_type, analytics_data):
    insights = []
    avg_likes = analytics_data['average_likes']
    avg_shares = analytics_data['average_shares']
    avg_comments = analytics_data['average_comments']
    
    engagement_rate = (avg_likes + avg_shares + avg_comments) / 3
    best_time = random.choice(['morning', 'afternoon', 'evening'])
    
    insights.append(f"{post_type.capitalize()} posts have an average engagement rate of {round(engagement_rate, 2)}")
    insights.append(f"Best posting time for {post_type} content appears to be during {best_time}")
    
    if post_type == 'carousel':
        insights.append("Carousel posts with 3-5 slides perform better than longer ones")
    elif post_type == 'reel':
        insights.append("Reels under 30 seconds get 2.5x more engagement")
    else:
        insights.append("Static posts with compelling captions drive 50% more comments")
    
    return insights

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
