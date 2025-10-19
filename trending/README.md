# Trending News Generator

This directory contains an automated trending news generation system that creates AI-powered news articles every hour using GitHub Actions.

## 🚀 How It Works

1. **GitHub Actions Automation**: The workflow runs every hour at the top of the hour
2. **AI Content Generation**: Uses advanced AI models to generate trending news articles
3. **Automatic Publishing**: Generated articles are automatically committed and pushed to the repository
4. **Web Integration**: Articles appear on the trending news section of the website

## 📁 Directory Structure

```
trending/
├── scripts/
│   ├── news_generator.py      # Main Python script for generating news
│   ├── requirements.txt       # Python dependencies
│   ├── test_setup.py         # Test script to validate setup
│   ├── daily_topics.json    # Daily topics tracking (auto-generated)
│   └── __pycache__/         # Python cache files
├── posts/                   # Generated news articles (auto-generated)
├── index.html              # Main trending news page
└── README.md               # This file
```

## ⚙️ GitHub Actions Workflow

The automation is handled by `.github/workflows/update-trending-news.yml` which:

- **Schedule**: Runs every hour (`0 * * * *`)
- **Manual Trigger**: Can be manually triggered via GitHub Actions UI
- **Dependencies**: Installs all required Python packages
- **AI Models**: Caches AI models for faster execution
- **Git Operations**: Automatically commits and pushes new content

## 🔧 Configuration

### Environment Variables
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `HF_HOME`: Hugging Face model cache directory
- `PYTHONPATH`: Python path configuration

### Python Dependencies
The script requires several packages (see `requirements.txt`):
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `feedparser`: RSS feed parsing
- `transformers`: AI model support
- `torch`: Machine learning framework
- And more...

## 🧪 Testing

To test the setup locally:

```bash
cd trending/scripts
python test_setup.py
```

To test the news generator:

```bash
cd trending/scripts
python news_generator.py
```

## 📊 Features

- **AI-Powered Content**: Uses advanced language models for content generation
- **Multi-Source Aggregation**: Pulls from various news sources and feeds
- **SEO Optimization**: Generated content is optimized for search engines
- **Duplicate Prevention**: Tracks daily topics to avoid duplicate content
- **Automatic Cleanup**: Removes old articles to keep content fresh
- **Responsive Design**: Articles are formatted for web display

## 🔄 Automation Schedule

- **Frequency**: Every hour
- **Timing**: At the top of each hour (00:00, 01:00, 02:00, etc.)
- **Timezone**: UTC (GitHub Actions default)
- **Failure Handling**: Workflow includes timeout and error handling

## 📝 Generated Content

Each generated article includes:
- **Title**: SEO-optimized headline
- **Content**: Full article with multiple paragraphs
- **Sources**: Referenced news sources
- **Metadata**: Publication time, search volume, etc.
- **HTML Format**: Ready for web display

## 🚨 Troubleshooting

### Common Issues:
1. **Workflow Fails**: Check GitHub Actions logs for error details
2. **No New Content**: May indicate no new trending topics found
3. **Permission Errors**: Ensure GitHub Actions has write permissions
4. **Dependency Issues**: Check if all packages are properly installed

### Manual Intervention:
- Use "workflow_dispatch" to manually trigger the workflow
- Check the Actions tab in GitHub for execution logs
- Verify the Python script runs locally before debugging workflow issues

## 🔐 Security

- Uses GitHub's built-in token authentication
- No sensitive API keys required
- All operations are contained within the repository
- AI models are cached locally during execution

## 📈 Monitoring

Monitor the system through:
- **GitHub Actions**: Check workflow execution status
- **Commit History**: See when new articles are generated
- **Website**: Verify articles appear on the trending page
- **Logs**: Review execution logs for any issues
- ⚡ **Fast Loading**: Static HTML files for quick loading

## Setup Instructions

### 1. Fork and Clone
- Fork this repository to your GitHub account
- Clone your forked repository locally

### 2. Customize Domain (Optional)
- Update the `CNAME` file with your domain
- Update `base_url` in `scripts/news_generator.py` with your domain

### 3. Enable GitHub Pages
1. Go to your repository **Settings**
2. Click **Pages** in the sidebar
3. Under **Source**, select **GitHub Actions**

### 4. Manual First Run
1. Go to **Actions** tab in your repository
2. Select **Update Trending News** workflow
3. Click **Run workflow**

## How It Works

1. **Every hour**, GitHub Actions runs the Python script
2. **Fetches trending topics** from Google Trends RSS
3. **Gathers information** from Wikipedia and DuckDuckGo APIs
4. **Generates original articles** using template-based AI generation
5. **Creates HTML files** for each article in `/posts/` folder
6. **Updates homepage** with latest posts
7. **Auto-cleans** old posts (keeps only latest 100)

## File Structure
