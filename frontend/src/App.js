import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Card, 
  CardContent,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Paper,
  Tab,
  Tabs
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [postType, setPostType] = useState('carousel');
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [posts, setPosts] = useState([]);
  const [insights, setInsights] = useState([]);
  const [timeAnalytics, setTimeAnalytics] = useState([]);
  const [trendingHashtags, setTrendingHashtags] = useState([]);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [postsRes, timeRes, hashtagsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/posts`),
          axios.get(`${API_BASE_URL}/time-analytics`),
          axios.get(`${API_BASE_URL}/trending-hashtags`)
        ]);
        setPosts(postsRes.data);
        setTimeAnalytics(timeRes.data);
        setTrendingHashtags(hashtagsRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch data. Please try again later.');
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const fetchAnalyticsAndInsights = async () => {
      setLoading(true);
      setError(null);
      try {
        const [analyticsRes, insightsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/analytics/${postType}`),
          axios.get(`${API_BASE_URL}/insights/${postType}`)
        ]);
        setAnalytics(analyticsRes.data);
        setInsights(insightsRes.data.insights);
      } catch (error) {
        console.error('Error fetching analytics:', error);
        setError('Failed to fetch analytics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsAndInsights();
  }, [postType]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const chartData = analytics ? [
    {
      name: 'Engagement Metrics',
      Likes: Math.round(analytics.average_likes),
      Shares: Math.round(analytics.average_shares),
      Comments: Math.round(analytics.average_comments),
    }
  ] : [];

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Social Media Analytics Dashboard
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} centered>
            <Tab label="Overview" />
            <Tab label="Time Analysis" />
            <Tab label="Trending" />
          </Tabs>
        </Box>

        {activeTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <FormControl fullWidth>
                    <InputLabel>Post Type</InputLabel>
                    <Select
                      value={postType}
                      label="Post Type"
                      onChange={(e) => setPostType(e.target.value)}
                    >
                      <MenuItem value="carousel">Carousel</MenuItem>
                      <MenuItem value="reel">Reel</MenuItem>
                      <MenuItem value="static">Static Image</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Engagement Metrics for {postType.charAt(0).toUpperCase() + postType.slice(1)} Posts
                  </Typography>
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                      <CircularProgress />
                    </Box>
                  ) : analytics && (
                    <Box sx={{ width: '100%', height: 400 }}>
                      <ResponsiveContainer>
                        <BarChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="Likes" fill="#8884d8" />
                          <Bar dataKey="Shares" fill="#82ca9d" />
                          <Bar dataKey="Comments" fill="#ffc658" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI-Generated Insights
                  </Typography>
                  <List>
                    {insights.map((insight, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={insight} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Posts
                  </Typography>
                  <Grid container spacing={2}>
                    {posts.filter(post => post.type === postType).map((post) => (
                      <Grid item xs={12} sm={6} md={4} key={post.id}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                              Post #{post.id}
                            </Typography>
                            <Typography variant="body2" component="p">
                              Likes: {post.likes}
                            </Typography>
                            <Typography variant="body2" component="p">
                              Shares: {post.shares}
                            </Typography>
                            <Typography variant="body2" component="p">
                              Comments: {post.comments}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {activeTab === 1 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Engagement by Time of Day
              </Typography>
              <Box sx={{ width: '100%', height: 400 }}>
                <ResponsiveContainer>
                  <LineChart data={timeAnalytics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="carousel" stroke="#8884d8" />
                    <Line type="monotone" dataKey="reel" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="static" stroke="#ffc658" />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        )}

        {activeTab === 2 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Trending Hashtags
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {trendingHashtags.map((hashtag, index) => (
                  <Chip
                    key={index}
                    label={`${hashtag.tag} (${hashtag.count})`}
                    color="primary"
                    variant={index < 3 ? "filled" : "outlined"}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  );
}

export default App;
